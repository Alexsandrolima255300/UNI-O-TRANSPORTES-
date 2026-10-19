export default async function handler(req, res) {
  const cnpj = String(req.query?.cnpj || '').replace(/\D/g, '');
  if (req.method !== 'GET') {
    res.setHeader('Allow', 'GET');
    return res.status(405).json({ error: 'Método não permitido.' });
  }
  if (!/^\d{14}$/.test(cnpj)) {
    return res.status(400).json({ error: 'Informe um CNPJ válido com 14 números.' });
  }

  // As duas fontes são consultadas em paralelo para que uma API lenta
  // não deixe o formulário preso em "Consultando empresa...".
  async function fetchJson(url, timeoutMs = 5000) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    try {
      const response = await fetch(url, {
        signal: controller.signal,
        headers: { Accept: 'application/json' }
      });
      const body = await response.text();
      let data = null;
      try { data = body ? JSON.parse(body) : null; } catch (_) {}
      return { ok: response.ok, status: response.status, data };
    } finally {
      clearTimeout(timer);
    }
  }

  const [brasil, publica] = await Promise.allSettled([
    fetchJson(`https://brasilapi.com.br/api/cnpj/v1/${cnpj}`),
    fetchJson(`https://publica.cnpj.ws/cnpj/${cnpj}`)
  ]);

  const brasilResult = brasil.status === 'fulfilled' ? brasil.value : null;
  if (brasilResult?.ok && brasilResult.data && !brasilResult.data.error) {
    res.setHeader('Cache-Control', 's-maxage=300, stale-while-revalidate=3600');
    return res.status(200).json(brasilResult.data);
  }

  const fallback = publica.status === 'fulfilled' ? publica.value : null;
  if (fallback?.ok && fallback.data?.estabelecimento) {
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
      cep: String(e.cep || '').replace(/\D/g, ''),
      situacao_cadastral: e.situacao_cadastral || ''
    };
    res.setHeader('Cache-Control', 's-maxage=300, stale-while-revalidate=3600');
    return res.status(200).json(normalized);
  }

  // Distingue CNPJ inexistente de indisponibilidade das fontes de consulta.
  const statuses = [brasilResult?.status, fallback?.status].filter(Number.isInteger);
  const notFound = statuses.includes(404);
  return res.status(notFound ? 404 : 502).json({
    error: notFound
      ? 'CNPJ não localizado nas fontes consultadas. Confira os 14 números.'
      : 'As fontes de consulta estão temporariamente indisponíveis. Tente novamente em alguns segundos.',
    provider: 'brasilapi; publica.cnpj.ws'
  });
}
