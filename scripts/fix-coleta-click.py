from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
marker='/* COLETA_CLICK_FINAL */'
if marker in s:
    print('already patched')
    raise SystemExit(0)

patch=r'''
<script>
/* COLETA_CLICK_FINAL */
(function(){
  function normalize(v){
    return String(v||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/\s+/g,' ').trim().toUpperCase();
  }
  function bindColeta(){
    var frame=document.getElementById('app');
    if(!frame) return false;
    try{
      var doc=frame.contentDocument || (frame.contentWindow && frame.contentWindow.document);
      if(!doc || !doc.body) return false;
      if(doc.__coletaFinalBound) return true;
      doc.__coletaFinalBound=true;
      function handler(ev){
        var el=ev.target;
        while(el && el!==doc.body){
          var text=normalize(el.textContent);
          var label=normalize(el.getAttribute && (el.getAttribute('aria-label')||el.getAttribute('title')));
          if(text==='COLETA' || label==='COLETA'){
            ev.preventDefault();
            ev.stopPropagation();
            ev.stopImmediatePropagation();
            if(typeof window.openColetaModal==='function') window.openColetaModal();
            return false;
          }
          el=el.parentElement;
        }
      }
      doc.addEventListener('click',handler,true);
      doc.addEventListener('pointerup',handler,true);
      var items=doc.querySelectorAll('.ue-nav-item');
      items.forEach(function(item){
        if(normalize(item.textContent)==='COLETA'){
          item.addEventListener('click',function(ev){
            ev.preventDefault();ev.stopPropagation();ev.stopImmediatePropagation();
            if(typeof window.openColetaModal==='function') window.openColetaModal();
          },true);
          item.style.cursor='pointer';
        }
      });
      return true;
    }catch(e){ return false; }
  }
  function start(){
    bindColeta();
    var frame=document.getElementById('app');
    if(frame){
      frame.addEventListener('load',function(){bindColeta();setTimeout(bindColeta,100);setTimeout(bindColeta,500);});
    }
    var tries=0;
    var timer=setInterval(function(){
      tries++;
      if(bindColeta() || tries>30) clearInterval(timer);
    },300);
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',start); else start();
})();
</script>
'''
s=s.replace('</body>',patch+'\n</body>',1)
p.write_text(s,encoding='utf-8')
print('collection click patch applied')
