from pathlib import Path
p=Path('app.html')
s=p.read_text(encoding='utf-8')
marker='/* COLETA_DIRECT_FINAL */'
if marker in s:
    print('already patched')
    raise SystemExit(0)
patch=r'''<script>
/* COLETA_DIRECT_FINAL */
(function(){
  function openColeta(){
    try{
      if(window.parent && typeof window.parent.openColetaModal==='function'){
        window.parent.openColetaModal();
        return true;
      }
    }catch(e){}
    return false;
  }
  function bind(){
    var items=document.querySelectorAll('.ue-nav-item');
    for(var i=0;i<items.length;i++){
      var t=(items[i].textContent||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').trim().toUpperCase();
      if(t==='COLETA' && !items[i].__coletaBound){
        items[i].__coletaBound=true;
        items[i].onclick=function(e){e.preventDefault();e.stopPropagation();openColeta();return false;};
        items[i].addEventListener('click',function(e){e.preventDefault();e.stopImmediatePropagation();openColeta();},true);
        items[i].style.cursor='pointer';
      }
    }
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',bind);else bind();
  setTimeout(bind,100);setTimeout(bind,500);setInterval(bind,1000);
})();
</script>
'''
s=s.replace('</body>',patch+'</body>',1)
p.write_text(s,encoding='utf-8')
print('direct collection binding applied - trigger')
