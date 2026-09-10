from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
start=s.find('function bindDeliveryButton(){')
end=s.find('\napp.addEventListener(\'load\'', start)
if start<0 or end<0:
    raise SystemExit('bindDeliveryButton block not found')
new="""function bindDeliveryButton(){
  try{
    const d=app.contentDocument;
    if(!d||!d.body)return;
    if(d.__deliveryDelegate)return;
    d.__deliveryDelegate=true;
    d.addEventListener('click',function(e){
      const el=e.target && e.target.closest ? e.target.closest('.ue-nav-item, a, button, [role=\"button\"], div, span') : null;
      if(!el)return;
      const text=normal(el.textContent||'');
      if(text.includes('PREVISAO DE ENTREGA')){
        e.preventDefault();
        e.stopPropagation();
        if(typeof openDeliveryModal==='function')openDeliveryModal();
      }
    },true);
  }catch(e){}
}
"""
s=s[:start]+new+s[end:]
old="function showApp(){loginScreen.style.display='none';loadingScreen.style.display='flex';app.style.display='block';setTimeout(()=>{try{setup()}catch(e){}bindDeliveryButton();hideLoading();tools.style.display='flex'},700)}"
newshow="function showApp(){loginScreen.style.display='none';loadingScreen.style.display='flex';app.style.display='block';setTimeout(()=>{try{bindDeliveryButton();setup()}catch(e){}setTimeout(bindDeliveryButton,150);setTimeout(bindDeliveryButton,500);hideLoading();tools.style.display='flex'},700)}"
if old not in s:
    raise SystemExit('showApp block not found')
s=s.replace(old,newshow,1)
p.write_text(s,encoding='utf-8')
print('patched')
