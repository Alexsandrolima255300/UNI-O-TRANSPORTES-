/* COLETA — implementação única e final */
(function () {
  'use strict';

  const WHATSAPP = '553433148566';
  const API_BASE = 'https://brasilapi.com.br/api/cnpj/v1/';
  const $ = (id) => document.getElementById(id);

  function onlyDigits(value) { return String(value || '').replace(/\D/g, ''); }

  function formatCNPJ(value) {
    const n = onlyDigits(value).slice(0, 14);
    if (n.length <= 2) return n;
    if (n.length <= 5) return n.slice(0, 2) + '.' + n.slice(2);
    if (n.length <= 8) return n.slice(0, 2) + '.' + n.slice(2, 5) + '.' + n.slice(5);
    if (n.length <= 12) return n.slice(0, 2) + '.' + n.slice(2, 5) + '.' + n.slice(5, 8) + '/' + n.slice(8);
    return n.slice(0, 2) + '.' + n.slice(2, 5) + '.' + n.slice(5, 8) + '/' + n.slice(8, 12) + '-' + n.slice(12);
  }

  function validCNPJ(value) {
    const cnpj = onlyDigits(value);
    if (cnpj.length !== 14 || /^([0-9])\1{13}$/.test(cnpj)) return false;
    let sum = 0, pos = 5;
    for (let i = 0; i < 12; i++) { sum += Number(cnpj[i]) * pos; pos--; if (pos < 2) pos = 9; }
    let digit = sum % 11 < 2 ? 0 : 11 - (sum % 11);
    if (digit !== Number(cnpj[12])) return false;
    sum = 0; pos = 6;
    for (let i = 0; i < 13; i++) { sum += Number(cnpj[i]) * pos; pos--; if (pos < 2) pos = 9; }
    digit = sum % 11 < 2 ? 0 : 11 - (sum % 11);
    return digit === Number(cnpj[13]);
  }

  function setStatus(message, type) {
    const el = $('coletaCnpjStatus');
    if (!el) return;
    el.textContent = message || '';
    el.style.color = type === 'error' ? '#c62828' : type === 'success' ? '#168447' : '#0758b7';
  }

  function setMinimumDate() {
    const date = $('coletaData');
    if (!date) return;
    const now = new Date();
    const local = new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
    date.min = local;
  }

  function buildModal() {
    let modal = $('coletaModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'coletaModal';
      modal.className = 'coleta-modal';
      modal.setAttribute('aria-hidden', 'true');
      document.body.appendChild(modal);
    }

    modal.innerHTML = `
      <div class="coleta-card coleta-card-final" role="dialog" aria-modal="true" aria-labelledby="coletaTitle">
        <div class="coleta-head">
          <div>
            <h2 id="coletaTitle">Solicitar coleta</h2>
            <p>Informe o CNPJ e os dados da coleta. O endereço encontrado pode ser editado antes do envio.</p>
          </div>
          <button class="coleta-close" id="coletaClose" type="button" aria-label="Fechar">Fechar</button>
        </div>
        <form class="coleta-form" id="coletaForm" novalidate>
          <div class="coleta-field">
            <label for="coletaCnpj">CNPJ da empresa *</label>
            <input id="coletaCnpj" inputmode="numeric" autocomplete="off" maxlength="18" placeholder="00.000.000/0000-00" required>
            <div class="coleta-status" id="coletaCnpjStatus" aria-live="polite"></div>
          </div>

          <div class="coleta-field">
            <label for="coletaEmpresa">Razão social ou nome fantasia *</label>
            <input id="coletaEmpresa" placeholder="Nome da empresa" autocomplete="organization" required>
          </div>

          <div class="coleta-company-grid">
            <div class="coleta-field"><label for="coletaLogradouro">Endereço cadastrado</label><input id="coletaLogradouro" placeholder="Rua / Avenida"></div>
            <div class="coleta-field"><label for="coletaNumero">Número</label><input id="coletaNumero" placeholder="Número"></div>
            <div class="coleta-field"><label for="coletaComplemento">Complemento</label><input id="coletaComplemento" placeholder="Sala, galpão, etc."></div>
            <div class="coleta-field"><label for="coletaBairro">Bairro</label><input id="coletaBairro" placeholder="Bairro"></div>
            <div class="coleta-field"><label for="coletaCidade">Cidade</label><input id="coletaCidade" placeholder="Cidade"></div>
            <div class="coleta-field"><label for="coletaUf">UF</label><input id="coletaUf" maxlength="2" placeholder="MG"></div>
            <div class="coleta-field"><label for="coletaCep">CEP</label><input id="coletaCep" inputmode="numeric" maxlength="9" placeholder="00000-000"></div>
          </div>

          <div class="coleta-field">
            <label for="coletaEndereco">Endereço da coleta *</label>
            <input id="coletaEndereco" placeholder="Informe o endereço onde a coleta realmente acontecerá" required>
            <div class="coleta-help">Este campo é editável mesmo quando o endereço da empresa for encontrado pela BrasilAPI.</div>
          </div>

          <div class="coleta-row">
            <div class="coleta-field"><label for="coletaData">Data da coleta *</label><input id="coletaData" type="date" required></div>
            <div class="coleta-field"><label for="coletaHora">Horário da coleta *</label><input id="coletaHora" type="time" required></div>
          </div>

          <button class="coleta-submit" type="submit">Solicitar coleta pelo WhatsApp</button>
          <div class="coleta-note">Os dados são usados para montar a solicitação e abrir o WhatsApp. A mensagem não é enviada automaticamente sem sua confirmação no WhatsApp.</div>
        </form>
      </div>`;

    if (!document.getElementById('coletaFinalStyle')) {
      const style = document.createElement('style');
      style.id = 'coletaFinalStyle';
      style.textContent = `
        .coleta-modal{position:fixed!important;inset:0!important;z-index:50000!important;background:rgba(8,25,45,.68)!important;backdrop-filter:blur(6px)!important;display:none;align-items:center;justify-content:center;padding:18px!important}
        .coleta-modal.show{display:flex!important}
        .coleta-card-final{width:min(720px,100%)!important;max-height:92vh!important;overflow:auto!important;background:#fff!important;border-radius:24px!important;padding:28px!important;box-shadow:0 28px 90px rgba(0,30,70,.35)!important;color:#10233f!important}
        .coleta-head{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;margin-bottom:20px}.coleta-head h2{margin:0;font-size:24px;letter-spacing:-.03em}.coleta-head p{margin:6px 0 0;color:#64758b;font-size:13px;line-height:1.5}.coleta-close{border:0;background:#edf5fd;color:#0758b7;border-radius:10px;padding:9px 12px;font-weight:900;cursor:pointer}.coleta-form{display:grid;gap:14px}.coleta-field{display:flex;flex-direction:column;gap:7px}.coleta-field label{font-size:12px;font-weight:900}.coleta-field input{width:100%;padding:13px;border:1px solid #cfd9e5;border-radius:11px;font-size:15px;outline:0;background:#fff}.coleta-field input:focus{border-color:#007ECB;box-shadow:0 0 0 4px rgba(0,126,203,.12)}.coleta-company-grid{display:grid;grid-template-columns:2fr 1fr;gap:12px}.coleta-company-grid .coleta-field:nth-child(3){grid-column:1/2}.coleta-row{display:grid;grid-template-columns:1fr 1fr;gap:12px}.coleta-status{font-size:11px;font-weight:800;min-height:15px}.coleta-help{font-size:10px;color:#7a8a9c}.coleta-submit{border:0;border-radius:12px;padding:14px 16px;background:#007ECB;color:#fff;font-weight:900;cursor:pointer}.coleta-submit:hover{background:#006eb5}.coleta-note{font-size:10px;color:#7a8a9c;line-height:1.5}@media(max-width:600px){.coleta-card-final{padding:22px!important;border-radius:20px!important;max-height:94vh!important}.coleta-company-grid,.coleta-row{grid-template-columns:1fr}.coleta-company-grid .coleta-field:nth-child(3){grid-column:auto}.coleta-head h2{font-size:21px}}
      `;
      document.head.appendChild(style);
    }

    $('coletaCnpj').addEventListener('input', onCnpjInput);
    $('coletaCnpj').addEventListener('blur', onCnpjBlur);
    $('coletaForm').addEventListener('submit', submitColeta);
    $('coletaClose').addEventListener('click', closeColeta);
    modal.addEventListener('click', (event) => { if (event.target === modal) closeColeta(); });
    document.addEventListener('keydown', (event) => { if (event.key === 'Escape' && modal.classList.contains('show')) closeColeta(); });
    setMinimumDate();
  }

  function onCnpjInput(event) {
    event.target.value = formatCNPJ(event.target.value);
    const digits = onlyDigits(event.target.value);
    if (digits.length < 14) setStatus('', 'info');
    if (digits.length === 14) lookupCNPJ(digits);
  }

  function onCnpjBlur(event) {
    const digits = onlyDigits(event.target.value);
    if (digits && !validCNPJ(digits)) setStatus('Informe um CNPJ válido.', 'error');
  }

  let lookupSequence = 0;
  async function lookupCNPJ(cnpj) {
    const sequence = ++lookupSequence;
    if (!validCNPJ(cnpj)) { setStatus('Informe um CNPJ válido.', 'error'); return; }
    setStatus('Consultando CNPJ…', 'info');
    try {
      const response = await fetch(API_BASE + cnpj, { headers: { Accept: 'application/json' } });
      if (sequence !== lookupSequence) return;
      if (response.status === 404) { setStatus('Não foi possível localizar este CNPJ. Verifique os números e tente novamente.', 'error'); return; }
      if (!response.ok) throw new Error('HTTP_' + response.status);
      const data = await response.json();
      if (!data || (!data.razao_social && !data.nome_fantasia)) {
        setStatus('Não foi possível localizar este CNPJ. Verifique os números e tente novamente.', 'error'); return;
      }
      $('coletaEmpresa').value = data.razao_social || data.nome_fantasia || '';
      $('coletaLogradouro').value = data.logradouro || '';
      $('coletaNumero').value = data.numero || '';
      $('coletaComplemento').value = data.complemento || '';
      $('coletaBairro').value = data.bairro || '';
      $('coletaCidade').value = data.municipio || data.cidade || '';
      $('coletaUf').value = data.uf || '';
      $('coletaCep').value = formatCEP(data.cep || '');
      const address = [data.logradouro, data.numero, data.complemento, data.bairro, data.municipio || data.cidade, data.uf, formatCEP(data.cep || '')].filter(Boolean).join(', ');
      $('coletaEndereco').value = address;
      setStatus('✓ CNPJ encontrado — dados preenchidos automaticamente.', 'success');
    } catch (error) {
      if (sequence !== lookupSequence) return;
      setStatus('Não foi possível consultar o CNPJ agora. Você pode preencher os dados manualmente.', 'error');
    }
  }

  function formatCEP(value) {
    const n = onlyDigits(value).slice(0, 8);
    return n.length > 5 ? n.slice(0, 5) + '-' + n.slice(5) : n;
  }

  function openColeta() {
    buildModal();
    const modal = $('coletaModal');
    modal.classList.add('show');
    modal.setAttribute('aria-hidden', 'false');
    setMinimumDate();
    setTimeout(() => $('coletaCnpj')?.focus(), 50);
  }

  function closeColeta() {
    const modal = $('coletaModal');
    if (!modal) return;
    modal.classList.remove('show');
    modal.setAttribute('aria-hidden', 'true');
  }

  function submitColeta(event) {
    event.preventDefault();
    const cnpj = $('coletaCnpj').value.trim();
    const empresa = $('coletaEmpresa').value.trim();
    const endereco = $('coletaEndereco').value.trim();
    const data = $('coletaData').value;
    const hora = $('coletaHora').value;
    if (!validCNPJ(cnpj)) { setStatus('Informe um CNPJ válido.', 'error'); $('coletaCnpj').focus(); return; }
    if (!empresa) { $('coletaEmpresa').focus(); return; }
    if (!endereco) { $('coletaEndereco').focus(); return; }
    if (!data) { $('coletaData').focus(); return; }
    if (!hora) { $('coletaHora').focus(); return; }
    const [year, month, day] = data.split('-');
    const formattedDate = `${day}/${month}/${year}`;
    const message = `Olá! Quero solicitar uma coleta.\n\nEmpresa: ${empresa}\nCNPJ: ${cnpj}\nEndereço da coleta: ${endereco}\nData da coleta: ${formattedDate}\nHorário da coleta: ${hora}`;
    const url = `https://wa.me/${WHATSAPP}?text=${encodeURIComponent(message)}`;
    window.open(url, '_blank', 'noopener,noreferrer');
    closeColeta();
  }

  // O app está dentro de iframe. O clique é tratado no próprio documento do iframe.
  function bindIframeColeta() {
    const frame = $('app');
    if (!frame) return;
    try {
      const doc = frame.contentDocument || frame.contentWindow.document;
      if (!doc || !doc.body || doc.__coletaSingleHandler) return;
      doc.__coletaSingleHandler = true;
      const handler = (event) => {
        let node = event.target;
        while (node && node !== doc.body) {
          const text = String(node.textContent || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').trim().toUpperCase();
          if (text === 'COLETA') {
            event.preventDefault();
            event.stopPropagation();
            event.stopImmediatePropagation();
            openColeta();
            return false;
          }
          node = node.parentElement;
        }
      };
      doc.addEventListener('click', handler, true);
      doc.addEventListener('pointerup', handler, true);
    } catch (_) {}
  }

  window.openColetaModal = openColeta;
  window.closeColetaModal = closeColeta;
  window.bindColetaButton = bindIframeColeta;

  function init() {
    buildModal();
    bindIframeColeta();
    const frame = $('app');
    if (frame) {
      frame.addEventListener('load', () => { setTimeout(bindIframeColeta, 50); setTimeout(bindIframeColeta, 300); setTimeout(bindIframeColeta, 1000); });
    }
    setTimeout(bindIframeColeta, 300);
    setTimeout(bindIframeColeta, 1000);
    setTimeout(bindIframeColeta, 2000);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
