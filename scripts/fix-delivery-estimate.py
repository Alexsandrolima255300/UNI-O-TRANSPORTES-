from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='/* DELIVERY_ESTIMATE_FIX_V4 */'
if marker in s: raise SystemExit('already patched')
needle='</script>'
patch=r'''/* DELIVERY_ESTIMATE_FIX_V4 */
(function(){
  function getDeliveryApp(){try{return document.getElementById('app').contentDocument}catch(e){return null}}
  function clean(v){return (v||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/\s+/g,' ').trim().toUpperCase()}
  function getDays(uf,city){uf=clean(uf);city=clean(city);if(city==='UBERABA'||city==='UBERLANDIA')return '1 dia útil';if(uf==='MG')return '1 a 3 dias úteis';if(uf==='SP')return '2 a 4 dias úteis';if(uf==='RJ'||uf==='ES'||uf==='GO'||uf==='DF')return '3 a 5 dias úteis';return '4 a 7 dias úteis'}
  function setResult(ok,title,text,days){const box=document.getElementById('deliveryResult'),t=document.getElementById('deliveryResultTitle'),tx=document.getElementById('deliveryResultText'),d=document.getElementById('deliveryDays');if(!box)return;box.classList.remove('ok','no');box.classList.add('show',ok?'ok':'no');t.textContent=title||'';tx.textContent=text||'';d.textContent=days||''}
  function findDestination(city,uf){const d=getDeliveryApp();if(!d)return null;const wanted=clean(city),state=clean(uf);for(const sel of [...d.querySelectorAll('select')])for(const opt of [...sel.options]){const text=clean(opt.textContent||opt.value||'');if(!text||text.includes('SELECIONE')||text.includes('ESCOLHA'))continue;if(text.includes(wanted)&&(!state||text.includes(state)))return {text,opt}}return null}
  async function lookupCep(cep){const r=await fetch('https://viacep.com.br/ws/'+cep+'/json/');if(!r.ok)throw Error('CEP');const j=await r.json();if(j.erro)throw Error('CEP');return j}
  window.consultDelivery=function(){const cepEl=document.getElementById('deliveryCep'),cityEl=document.getElementById('deliveryCity'),cep=(cepEl?.value||'').replace(/\D/g,''),result=document.getElementById('deliveryResult');let city=(cityEl?.value||'').trim();if(result){result.classList.add('show');document.getElementById('deliveryResultTitle').textContent='Consultando...';document.getElementById('deliveryResultText').textContent='Verificando o destino e calculando a previsão de entrega.';document.getElementById('deliveryDays').textContent=''};(async()=>{try{let uf='';if(cep.length===8){const j=await lookupCep(cep);city=j.localidade||city;uf=j.uf||'';if(cityEl)cityEl.value=city}if(!city){setResult(false,'Informe a cidade ou o CEP','Digite uma cidade ou um CEP válido para consultar.','');return}let match=findDestination(city,uf);if(!match&&!uf){const d=getDeliveryApp(),wanted=clean(city);const opts=d?[...d.querySelectorAll('select option')]:[];match=opts.map(opt=>({text:clean(opt.textContent||opt.value||''),opt})).find(x=>x.text.includes(wanted));if(match){const m=match.text.match(/\b(MG|SP|RJ|ES|GO|DF|PR|SC|RS|BA|PE|CE|PA|MS|MT|TO|SE|AL|PB|RN|PI|MA|RO|AC|AM|RR|AP)\b/);uf=m?m[1]:''}}if(!match){setResult(false,'A União Express não atende esta cidade','Não encontramos '+city+(uf?' - '+uf:'')+' na base de destinos atendidos.','');return}const days=getDays(uf,city);setResult(true,'A União Express atende esta cidade','Destino confirmado: '+city+(uf?' - '+uf:'')+'. A previsão abaixo é estimada em dias úteis.',days)}catch(e){setResult(false,'Não foi possível consultar','Confira o CEP informado ou digite a cidade manualmente para fazer a consulta.','')}})()}
  function bindConsult(){const b=document.getElementById('deliveryConsult');if(b&&!b.dataset.v4){b.dataset.v4='1';b.addEventListener('click',window.consultDelivery)}}
  function formatCep(){const i=document.getElementById('deliveryCep');if(i&&!i.dataset.v4){i.dataset.v4='1';i.addEventListener('input',()=>{let v=i.value.replace(/\D/g,'').slice(0,8);if(v.length>5)v=v.slice(0,5)+'-'+v.slice(5);i.value=v})}}
  bindConsult();formatCep();setTimeout(bindConsult,300);setTimeout(formatCep,300);setTimeout(bindConsult,1000);setTimeout(formatCep,1000)
})();
'''
if needle not in s: raise SystemExit('script end not found')
s=s.replace(needle,patch+needle,1)
p.write_text(s,encoding='utf-8')
