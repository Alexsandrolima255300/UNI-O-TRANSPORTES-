from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='/* DELIVERY_ESTIMATE_V5 */'
if marker in s: raise SystemExit('already patched')
patch=r'''<script>
/* DELIVERY_ESTIMATE_V5 */
(function(){
  const norm=s=>(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/\s+/g,' ').trim().toUpperCase();
  const app=()=>document.getElementById('app');
  const days=(uf,city)=>{uf=norm(uf);city=norm(city);if(city==='UBERABA'||city==='UBERLANDIA')return '1 dia útil';if(uf==='MG')return '1 a 3 dias úteis';if(uf==='SP')return '2 a 4 dias úteis';if(['RJ','ES','GO','DF'].includes(uf))return '3 a 5 dias úteis';return '4 a 7 dias úteis'};
  async function cep(c){const r=await fetch('https://viacep.com.br/ws/'+c+'/json/');if(!r.ok)throw Error();const j=await r.json();if(j.erro)throw Error();return j}
  function result(ok,title,text,d){const box=document.getElementById('deliveryResult');if(!box)return;box.classList.remove('ok','no');box.classList.add('show',ok?'ok':'no');document.getElementById('deliveryResultTitle').textContent=title;document.getElementById('deliveryResultText').textContent=text;document.getElementById('deliveryDays').textContent=d||''}
  function served(city,uf){const d=app()?.contentDocument;if(!d)return false;const wanted=norm(city);const exact=[...d.querySelectorAll('select option')].some(o=>{const t=norm(o.textContent||o.value);return t && !t.includes('SELECIONE') && t.includes(wanted) && (!uf || t.includes(norm(uf)))});if(exact)return true;const text=norm(d.body?.innerText||'');const re=new RegExp('(^|[^A-Z])'+wanted.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+'([^A-Z]|$)');return re.test(text)}
  async function consult(){const ce=document.getElementById('deliveryCep'),ci=document.getElementById('deliveryCity');let c=(ci?.value||'').trim(),u='';const raw=(ce?.value||'').replace(/\D/g,'');const box=document.getElementById('deliveryResult');if(box){box.className='delivery-result show';document.getElementById('deliveryResultTitle').textContent='Consultando...';document.getElementById('deliveryResultText').textContent='Verificando o destino e calculando o prazo...';document.getElementById('deliveryDays').textContent=''}try{if(raw.length===8){const j=await cep(raw);c=j.localidade||c;u=j.uf||'';if(ci)ci.value=c}if(!c){result(false,'Informe a cidade ou o CEP','Digite uma cidade ou um CEP válido.','');return}if(!served(c,u)){result(false,'A União Express não atende esta cidade','Não encontramos '+c+(u?' - '+u:'')+' na base de destinos atendidos.','');return}result(true,'A União Express atende esta cidade','Destino confirmado: '+c+(u?' - '+u:'')+'. Prazo estimado de entrega:',days(u,c))}catch(e){result(false,'Não foi possível consultar','Confira o CEP ou informe a cidade manualmente.','')}}
  function bind(){const b=document.getElementById('deliveryConsult');if(!b||b.dataset.v5)return;b.dataset.v5='1';const n=b.cloneNode(true);b.replaceWith(n);n.addEventListener('click',consult);const i=document.getElementById('deliveryCep');if(i&&!i.dataset.v5){i.dataset.v5='1';i.addEventListener('input',()=>{let v=i.value.replace(/\D/g,'').slice(0,8);if(v.length>5)v=v.slice(0,5)+'-'+v.slice(5);i.value=v})}}
  bind();setTimeout(bind,300);setTimeout(bind,1000);setTimeout(bind,2000);
})();
</script>
'''
needle='</body>'
if needle not in s: raise SystemExit('body end not found')
s=s.replace(needle,patch+needle,1)
p.write_text(s,encoding='utf-8')
