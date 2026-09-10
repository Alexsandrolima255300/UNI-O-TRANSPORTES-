from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='/* DELIVERY_PREDICTION_V6 */'
if marker in s:
    raise SystemExit('V6 already applied')
script=r'''<script>
/* DELIVERY_PREDICTION_V6 */
(function(){
  const norm=v=>(v||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/\s+/g,' ').trim().toUpperCase();
  const $=id=>document.getElementById(id);
  function days(city,uf){city=norm(city);uf=norm(uf);if(city==='UBERABA'||city==='UBERLANDIA')return '1 dia útil';if(uf==='MG')return '1 a 3 dias úteis';if(uf==='SP')return '2 a 4 dias úteis';if(uf==='RJ'||uf==='ES'||uf==='GO'||uf==='DF')return '3 a 5 dias úteis';return '4 a 7 dias úteis'}
  function show(ok,title,text,prazo){const box=$('deliveryResult'),t=$('deliveryResultTitle'),tx=$('deliveryResultText'),d=$('deliveryDays');if(!box)return;box.style.setProperty('display','block','important');box.className='delivery-result show '+(ok?'ok':'no');t.textContent=title;tx.textContent=text;d.textContent=prazo||'';d.style.setProperty('display',prazo?'block':'none','important')}
  function find(city,uf){const frame=$('app'),doc=frame&&frame.contentDocument;if(!doc)return null;const wanted=norm(city),state=norm(uf);let best=null;for(const sel of [...doc.querySelectorAll('select')]){for(const opt of [...sel.options]){const txt=norm((opt.textContent||'')+' '+(opt.value||''));if(!txt||txt.includes('SELECIONE')||txt.includes('ESCOLHA'))continue;const cityOk=txt===wanted||txt.startsWith(wanted+' /')||txt.includes(wanted);const stateOk=!state||txt.includes(' / '+state)||txt.endsWith(state)||txt.includes(state);if(cityOk&&stateOk){best={opt,text:opt.textContent||opt.value||''};break}}if(best)break}if(best)return best;return null}
  async function viaCep(cep){const r=await fetch('https://viacep.com.br/ws/'+cep+'/json/');if(!r.ok)throw Error('cep');const j=await r.json();if(j.erro)throw Error('cep');return j}
  async function consultar(){
    const cepEl=$('deliveryCep'),cityEl=$('deliveryCity');
    let cep=(cepEl?.value||'').replace(/\D/g,''),city=(cityEl?.value||'').trim(),uf='';
    show(true,'Consultando previsão','Verificando a cidade na base da União Express e calculando o prazo de entrega...','');
    try{
      if(cep){if(cep.length!==8){show(false,'CEP inválido','Digite um CEP com 8 números.','');return}const j=await viaCep(cep);city=j.localidade||city;uf=j.uf||'';if(cityEl)cityEl.value=city}
      if(!city){show(false,'Informe um destino','Digite o CEP ou a cidade que deseja consultar.','');return}
      let m=find(city,uf);
      if(!m && uf==='')m=find(city,'');
      if(!m){show(false,'✕ A União Express não atende esta cidade',city+(uf?' - '+uf:'')+' não foi encontrada na base de destinos atendidos.','');return}
      const state=uf||((m.text.match(/\b(MG|SP|RJ|ES|GO|DF|PR|SC|RS|BA|PE|CE|PA|MS|MT|TO|SE|AL|PB|RN|PI|MA|RO|AC|AM|RR|AP)\b/i)||[])[1]||'');
      const prazo=days(city,state);
      show(true,'✓ A União Express atende esta cidade','Destino confirmado: '+city+(state?' - '+state:'')+'. O prazo estimado abaixo é o tempo de entrega previsto para essa rota.','Prazo estimado: '+prazo);
      if(m.opt){m.opt.parentElement.value=m.opt.value;m.opt.parentElement.dispatchEvent(new Event('change',{bubbles:true}))}
    }catch(e){show(false,'Não foi possível consultar','Confira o CEP ou informe a cidade manualmente.','')}
  }
  function bind(){const b=$('deliveryConsult');if(!b)return;b.onclick=consultar;b.removeAttribute('data-v4');b.removeAttribute('data-v5');b.dataset.v6='1';const c=$('deliveryCep');if(c&&!c.dataset.v6){c.dataset.v6='1';c.addEventListener('input',()=>{let v=c.value.replace(/\D/g,'').slice(0,8);c.value=v.length>5?v.slice(0,5)+'-'+v.slice(5):v})}}
  bind();setTimeout(bind,300);setTimeout(bind,1000);setTimeout(bind,2000);
})();
</script>'''
s=s.replace('</body>',script+'\n</body>')
p.write_text(s,encoding='utf-8')
