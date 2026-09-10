from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# Remove old collection block if present so this patch is idempotent and can repair
# the click binding without duplicating the modal.
start=s.find('/* COLETA_V1_CSS */')
if start >= 0:
    css_end=s.find('</style>', start)
    if css_end >= 0:
        block_start=s.rfind('\n', 0, start)
        s=s[:block_start]+s[css_end:]

modal_start=s.find('<div class="coleta-modal" id="coletaModal"')
if modal_start >= 0:
    modal_end=s.find('</div>\n\n<script>', modal_start)
    if modal_end >= 0:
        modal_end += len('</div>')
        s=s[:modal_start]+s[modal_end:]

js_start=s.find('/* COLETA_V1 */')
if js_start >= 0:
    js_end=s.find('</body>', js_start)
    if js_end >= 0:
        s=s[:js_start]+s[js_end:]

css='''
/* COLETA_V2_CSS */
.coleta-modal{position:fixed;inset:0;z-index:31000;background:rgba(8,25,45,.68);backdrop-filter:blur(6px);display:none;align-items:center;justify-content:center;padding:18px}.coleta-modal.show{display:flex}.coleta-card{width:min(650px,100%);max-height:90vh;overflow:auto;background:#fff;border-radius:24px;padding:28px;box-shadow:0 28px 90px rgba(0,30,70,.35);color:#10233f}.coleta-head{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;margin-bottom:20px}.coleta-head h2{margin:0;font-size:24px;letter-spacing:-.03em}.coleta-head p{margin:6px 0 0;color:#64758b;font-size:13px;line-height:1.5}.coleta-close{border:0;background:#edf5fd;color:#0758b7;border-radius:10px;padding:9px 12px;font-weight:900;cursor:pointer}.coleta-form{display:grid;gap:14px}.coleta-field{display:flex;flex-direction:column;gap:7px}.coleta-field label{font-size:12px;font-weight:900}.coleta-field input{width:100%;padding:13px;border:1px solid #cfd9e5;border-radius:11px;font-size:15px;outline:0}.coleta-field input:focus{border-color:#007ECB;box-shadow:0 0 0 4px rgba(0,126,203,.12)}.coleta-row{display:grid;grid-template-columns:1fr 1fr;gap:12px}.coleta-status{font-size:11px;font-weight:800;min-height:15px}.coleta-submit{border:0;border-radius:12px;padding:14px 16px;background:#007ECB;color:#fff;font-weight:900;cursor:pointer}.coleta-submit:hover{background:#006eb5}.coleta-note{font-size:10px;color:#7a8a9c;line-height:1.5}@media(max-width:600px){.coleta-card{padding:22px}.coleta-row{grid-template-columns:1fr}}
'''
s=s.replace('</style>',css+'</style>',1)

modal='''
<div class="coleta-modal" id="coletaModal" aria-hidden="true"><div class="coleta-card" role="dialog" aria-modal="true" aria-labelledby="coletaTitle"><div class="coleta-head"><div><h2 id="coletaTitle">Solicitar coleta</h2><p>Preencha os dados abaixo. Ao enviar, o pedido será encaminhado pelo WhatsApp da União Express.</p></div><button class="coleta-close" id="coletaClose" type="button">Fechar</button></div><form class="coleta-form" id="coletaForm"><div class="coleta-field"><label for="coletaEndereco">Endereço da coleta</label><input id="coletaEndereco" placeholder="Rua, número, bairro, cidade e UF" required></div><div class="coleta-row"><div class="coleta-field"><label for="coletaData">Data da coleta</label><input id="coletaData" type="date" required></div><div class="coleta-field"><label for="coletaHora">Hora da coleta</label><input id="coletaHora" type="time" required></div></div><div class="coleta-field"><label for="coletaCnpj">CNPJ da empresa</label><input id="coletaCnpj" inputmode="numeric" maxlength="18" placeholder="00.000.000/0000-00" required><div class="coleta-status" id="coletaCnpjStatus"></div></div><div class="coleta-field"><label for="coletaEmpresa">Nome da empresa</label><input id="coletaEmpresa" placeholder="Preenchido automaticamente pelo CNPJ" required></div><div class="coleta-field"><label for="coletaEnderecoApi">Endereço cadastrado no CNPJ</label><input id="coletaEnderecoApi" placeholder="Será preenchido pela BrasilAPI e pode ser alterado"></div><button class="coleta-submit" type="submit">Solicitar coleta pelo WhatsApp</button><div class="coleta-note">O endereço principal acima pode ser alterado manualmente antes do envio. A consulta do CNPJ é feita pela BrasilAPI.</div></form></div></div>
'''
s=s.replace('<script>\nconst USERNAME',modal+'\n<script>\nconst USERNAME',1)

js='''
/* COLETA_V2 */
(function(){
 const phone='553433148566';
 const $=id=>document.getElementById(id);
 function open(){const m=$('coletaModal');if(m){m.classList.add('show');m.setAttribute('aria-hidden','false');setTimeout(()=>$('coletaCnpj')?.focus(),50)}}
 function close(){const m=$('coletaModal');if(m){m.classList.remove('show');m.setAttribute('aria-hidden','true')}}
 window.openColetaModal=open;
 function bind(){try{const d=app.contentDocument;if(!d||!d.body)return;if(d.__coletaDelegate)return;d.__coletaDelegate=true;d.addEventListener('click',function(e){const nodes=[];let el=e.target;while(el&&el!==d.body){nodes.push(el);el=el.parentElement}for(const n of nodes){const t=normal(n.textContent||'').trim();if(t==='COLETA'||t.includes(' COLETA')){e.preventDefault();e.stopPropagation();open();return}}},true)}catch(e){}}
 window.bindColetaButton=bind;
 bind();
 app.addEventListener('load',()=>{bind();setTimeout(bind,100);setTimeout(bind,500)});
 $('coletaClose').addEventListener('click',close);
 $('coletaModal').addEventListener('click',e=>{if(e.target===$('coletaModal'))close()});
 function fmtCnpj(v){v=v.replace(/\\D/g,'').slice(0,14);if(v.length<=2)return v;let o=v.slice(0,2)+'.'+v.slice(2);if(v.length>5)o=o.slice(0,6)+'.'+o.slice(6);if(v.length>8)o=o.slice(0,10)+'/'+o.slice(10);if(v.length>12)o=o.slice(0,15)+'-'+o.slice(15);return o}
 $('coletaCnpj').addEventListener('input',function(){this.value=fmtCnpj(this.value);const n=this.value.replace(/\\D/g,'');if(n.length===14)lookup(n)});
 async function lookup(cnpj){const st=$('coletaCnpjStatus');st.textContent='Consultando CNPJ…';st.style.color='#0758b7';try{const r=await fetch('https://brasilapi.com.br/api/cnpj/v1/'+cnpj);if(!r.ok)throw new Error();const d=await r.json();$('coletaEmpresa').value=d.razao_social||d.nome_fantasia||'';const end=[d.logradouro,d.numero,d.bairro,d.municipio,d.uf].filter(Boolean).join(', ');$('coletaEnderecoApi').value=end;$('coletaEndereco').value=end;st.textContent='✓ CNPJ encontrado — dados preenchidos automaticamente.';st.style.color='#168447'}catch(e){st.textContent='Não foi possível consultar o CNPJ. Confira os números e preencha os dados manualmente.';st.style.color='#c62828'}}
 $('coletaForm').addEventListener('submit',function(e){e.preventDefault();const empresa=$('coletaEmpresa').value.trim();const cnpj=$('coletaCnpj').value.trim();const endereco=$('coletaEndereco').value.trim();const data=$('coletaData').value;const hora=$('coletaHora').value;if(!empresa||!cnpj||!endereco||!data||!hora){alert('Preencha todos os campos da coleta.');return}const dt=data.split('-').reverse().join('/');const msg='Olá! Quero solicitar uma coleta.\\n\\nEmpresa: '+empresa+'\\nCNPJ: '+cnpj+'\\nEndereço da coleta: '+endereco+'\\nData da coleta: '+dt+'\\nHorário da coleta: '+hora;window.open('https://wa.me/'+phone+'?text='+encodeURIComponent(msg),'_blank');close()});
})();
'''
s=s.replace('</body>',js+'</body>',1)
p.write_text(s,encoding='utf-8')
print('patched collection v2')
