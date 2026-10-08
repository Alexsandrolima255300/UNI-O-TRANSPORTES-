export default async function handler(req, res) {
  const cnpj = String(req.query?.cnpj || '').replace(/\D/g, '');
  if (req.method !== 'GET') return res.status(405).json({ error: 'Método não permitido.' });
  if (!/^\d{14}$/.test(cnpj)) return res.status(400).json({ error: 'CNPJ inválido.' });

  const sleep = (ms) => new Promise(r => setTimeout(r, ms));
  const fetchJson = async (url, options = {}, timeoutMs = 7000) => {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: { Accept: 'application/json', ...(options.headers || {}) }
      });
      const text = await response.text();
      let data = null;
      try { data = text ? JSON.parse(text) : null; } catch (_) {}
      return { response, data };
    } finally {
      clearTimeout(timer);
    }
  };

  // BrasilAPI é a fonte principal. Tentamos novamente apenas em falhas transitórias.
  let lastStatus = 502;
  for (let attempt = 0; attempt < 2; attempt++) {
    try {
      const result = await fetchJson(`https://brasilapi.com.br/api/cnpj/v1/${cnpj}`);
      lastStatus = result.response.status;
      if (result.response.ok && result.data) {
        res.setHeader('Cache-Control', 's-maxage=300, stale-while-revalidate=3600');
        return res.status(200).json(result.data);
      }
      if (result.response.status >= 400 && result.response.status < 500 && result.response.status !== 429) break;
    } catch (_) {}
    if (attempt === 0) await sleep(250);
  }

  // Fallback somente se a BrasilAPI estiver indisponível/instável.
  try {
    const fallback = await fetchJson(`https://publica.cnpj.ws/cnpj/${cnpj}`);
    if (fallback.response.ok && fallback.data?.estabelecimento) {
      const e = fallback.data.estabelecimento;
      const normalized = {
        cnpj: e.cnpj || cnpj,
        razao_social: fallback.data.razao_social || '',
        nome_fantasia: e.nome_fantasia || '',
        logradouro: e.logradouro || '',
        numero: e.numero || '',
        complemento: e.complemento || '',
        bairro: e.bairro || '',
        municipio: e.cidade?.nome || '',
        uf: e.estado?.sigla || '',
        cep: e.cep || '',
        situacao_cadastral: e.situacao_cadastral || ''
      };
      res.setHeader('Cache-Control', 's-maxage=300, stale-while-revalidate=3600');
      return res.status(200).json(normalized);
    }
  } catch (_) {}

  return res.status(lastStatus >= 400 ? lastStatus : 502).json({
    error: 'Não foi possível consultar o CNPJ agora.',
    provider: 'brasilapi'
  });
}
