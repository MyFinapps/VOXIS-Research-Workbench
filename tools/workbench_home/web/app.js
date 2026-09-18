'use strict';
const $ = id => document.getElementById(id);
const token = location.hash.slice(1) || sessionStorage.getItem('voxis-home-token') || '';
if(location.hash){sessionStorage.setItem('voxis-home-token',token);history.replaceState(null,'','/');}
let state, editing, busy=false, closed=false;
let browserTab=null, browserURL=null, browserAttempted=false;
const paths = {
 browser:'M7 3h15l7 7v27H7z M22 3v8h7 M12 17h12 M12 23h12 M12 29h12',
 bridge:'M3 12h29m-6-6 6 6-6 6 M32 28H3m6-6-6 6 6 6',
 stem:'M5 36V23h5v13z M16 36V14h5v22z M27 36V4h5v32z',
 wxr:'M4 5h23v23H4z M16 16h19v20H16z',
 resonance:'M14 4h9l2 6 6-1 4 8-4 5 1 7-8 5-6-3-6 2-6-6 2-7-3-6 5-6 5 1z M26 20a7 7 0 1 1-14 0 7 7 0 0 1 14 0'
};
async function api(path,body){
 const options={headers:{'X-VOXIS-Token':token}};
 if(body!==undefined){options.method='POST';options.headers['Content-Type']='application/json';options.body=JSON.stringify(body);}
 let response;try{response=await fetch(path,options);}catch{throw new Error('Home is unavailable. Reopen it with Start-Workbench-Home.cmd.');}
 const data=await response.json();if(!response.ok)throw new Error(data.error||'Could not complete this action.');return data;
}
function notify(text,error=false,url){$('message').replaceChildren(document.createTextNode(text));$('message').classList.toggle('error',error);$('message').hidden=!text;
 if(url){const a=document.createElement('a');a.href=url;a.target='_blank';a.rel='noopener noreferrer';a.textContent='Open instrument session';$('message').append(a);}}
function icon(id){const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('viewBox','0 0 40 42');svg.setAttribute('aria-hidden','true');const p=document.createElementNS(svg.namespaceURI,'path');p.setAttribute('d',paths[id]);svg.append(p);return svg;}
function render(){
 $('rows').replaceChildren();
 for(const row of state.instruments){
  const item=document.createElement('article');item.className='instrument';item.setAttribute('aria-label',row.title);
  const copy=document.createElement('div');copy.className='copy';const title=document.createElement('h3');title.textContent=row.title;const purpose=document.createElement('p');purpose.textContent=row.purpose;copy.append(title,purpose);
  const status=document.createElement('span');status.className='status '+row.state;status.textContent=row.detail;
  const configure=document.createElement('button');configure.className='configure';configure.textContent='Configure';configure.setAttribute('aria-label','Configure '+row.title);configure.onclick=()=>configureEntry(row);configure.disabled=busy;
  const launch=document.createElement('button');launch.className='launch'+(row.can_open?' primary':'');launch.textContent=row.state==='running'&&row.id==='browser'?'Return':'Open';launch.setAttribute('aria-label',launch.textContent+' '+row.title);launch.disabled=!row.can_open||busy;launch.onclick=()=>openInstrument(row);
  item.append(icon(row.id),copy,status,configure,launch);
  if(row.error){const p=document.createElement('p');p.className='row-error';p.textContent=row.error;item.append(p);}
  $('rows').append(item);
 }
 $('config-path').textContent=state.config_path;
}
async function refresh(){if(closed||busy)return;try{const next=await api('/api/state');if(JSON.stringify(next)!==JSON.stringify(state)){state=next;render();}}catch(e){notify(e.message,true);}}
function configureEntry(row){editing=row;$('config-title').textContent='Configure '+row.title;$('target').value=row.target;$('version').value=row.version;
 const help={browser:'Paste the full path to Start-Record-Browser.cmd or browser.py in the existing Browser folder.',bridge:'Paste the full path to Start-Record-Bridge.cmd or bridge.py in the existing Bridge folder.',stem:'Paste the full path to the existing Stem Lab HTML file.',wxr:'Paste the confirmed HTTPS address of WXR-003. Home does not verify its deployed build or Quest behavior.',resonance:'Paste the full path to the existing launcher (.py, .exe, .cmd, .bat or .ps1). Do not guess a location.'};
 $('config-help').textContent=help[row.id];$('entry-hash').textContent=row.sha256||'Not measured';$('verification').textContent=row.verification;$('config-error').hidden=true;
 $('reminder').hidden=!row.can_clear;$('closed-confirm').checked=false;$('save-config').disabled=['running','unconfirmed'].includes(row.state);$('target').disabled=$('save-config').disabled;$('version').disabled=$('save-config').disabled;
 $('config-dialog').showModal();$('target').focus();}
async function openInstrument(row){
 if(busy)return;
 // After a Home reload we cannot recover a WindowProxy safely. Never guess
 // that opening another tab restores the existing view's selection/filter state.
 if(row.id==='browser'&&row.state==='running'&&!browserTab&&!browserAttempted){
  notify('Browser is already running. Switch to its existing tab. Home was reloaded and cannot focus that tab; no new tab was opened.');return;
 }
 let tab,created=false;
 if(row.id==='browser'){
  browserAttempted=true;
  if(browserTab&&!browserTab.closed){tab=browserTab;tab.focus();}
  else{tab=window.open('about:blank','_blank');created=!!tab;if(tab)tab.opener=null;}
 }else if(row.id==='wxr'){tab=window.open('about:blank','_blank');created=!!tab;if(tab)tab.opener=null;}
 busy=true;render();notify('Opening '+row.title+'…');
 try{
  const result=await api('/api/launch',{id:row.id});
  if(row.id==='browser'&&result.url){
   if(tab){
    // Focus only for an existing session: assigning its URL would reset context.
    if(created||browserURL!==result.url)tab.location.href=result.url;
    browserTab=tab;browserURL=result.url;
    notify(created&&row.state==='running'?'Opened a fresh Browser view because its previous tab was closed or unavailable.': 'Browser tab ready. If your browser does not switch tabs automatically, select the Record Browser tab.');
   }else notify('Popup blocked. Allow popups for Home, then click Return to open Browser.');
  }else{
   if(result.url&&tab)tab.location.href=result.url;else if(created)tab.close();
   notify(result.message,false,result.url);
  }
 }catch(e){if(created&&tab)tab.close();notify(e.message,true);}
 finally{busy=false;render();await refresh();}
}
$('config-form').onsubmit=async e=>{e.preventDefault();$('save-config').disabled=true;$('config-error').hidden=true;
 try{await api('/api/configure',{id:editing.id,entry:{target:$('target').value,version:$('version').value}});$('config-dialog').close();notify(editing.title+' location saved.');await refresh();}
 catch(e){$('config-error').textContent=e.message;$('config-error').hidden=false;}
 finally{$('save-config').disabled=false;}};
$('cancel-config').onclick=()=>$('config-dialog').close();
$('clear-reminder').onclick=async()=>{try{await api('/api/clear',{id:editing.id,confirmed:$('closed-confirm').checked});$('config-dialog').close();notify('Launch reminder cleared. No process was stopped.');await refresh();}catch(e){$('config-error').textContent=e.message;$('config-error').hidden=false;}};
$('help').onclick=()=>$('help-dialog').showModal();$('done-help').onclick=()=>$('help-dialog').close();
$('close').onclick=()=>$('close-dialog').showModal();$('cancel-close').onclick=()=>$('close-dialog').close();
$('confirm-close').onclick=async()=>{try{const r=await api('/api/stop',{});closed=true;sessionStorage.removeItem('voxis-home-token');$('close-dialog').close();notify(r.message);for(const control of document.querySelectorAll('button,input'))control.disabled=true;}catch(e){$('close-dialog').close();notify(e.message,true);}};
document.addEventListener('visibilitychange',()=>{if(!document.hidden)refresh();});
setInterval(()=>{if(!document.hidden&&!document.querySelector('dialog[open]'))refresh();},5000);
refresh();
