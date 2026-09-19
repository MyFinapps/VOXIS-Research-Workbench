// Tests actual Home client launch flow with isolated window/API contracts.
const {test}=require('node:test');
const assert=require('node:assert/strict');
const vm=require('node:vm');
const fs=require('node:fs');
const path=require('node:path');
function harness(){
 const tabs=[],messages=[],calls=[];
 let blocked=false,url='http://127.0.0.1:43210/#fixture';
 const element={classList:{toggle(){}},replaceChildren(){},append(){}};
 const ctx=vm.createContext({document:{getElementById:()=>({...element}),addEventListener(){},hidden:false},location:{hash:''},sessionStorage:{getItem:()=>'',setItem(){},removeItem(){}},history:{},setInterval(){},window:{open(){if(blocked)return null;const t={closed:false,focuses:0,navigations:[],location:{},focus(){this.focuses++},close(){this.closed=true}};Object.defineProperty(t.location,'href',{set(v){if(t.denyNavigation)throw Error('Denied '+v);t.navigations.push(v);t.selection=null;}});tabs.push(t);return t;}}});
 let src=fs.readFileSync(path.join(__dirname,'web/app.js'),'utf8');
 src=src.replace(/refresh\(\);\s*$/, '');
 vm.runInContext(src,ctx);
 ctx.testNotify=m=>messages.push(m);ctx.testAPI=async(p,b)=>{calls.push(b);return {url,message:'ready'}};
 vm.runInContext('render=()=>{};refresh=async()=>{};notify=testNotify;api=testAPI;',ctx);
 return {tabs,messages,calls,ctx,open:(state='configured')=>vm.runInContext(`openInstrument({id:'browser',title:'Record Browser',state:'${state}'})`,ctx),block:v=>blocked=v,url:v=>url=v};
}
test('Return focuses original tab without resetting its context or opening duplicates',async()=>{
 const h=harness();await h.open();const t=h.tabs[0];t.selection={record:'fixture',filter:'stem',detail:'native'};
 await h.open('running');await h.open('running');
 assert.equal(h.tabs.length,1);assert.equal(t.navigations.length,1);assert.equal(t.focuses,2);
 assert.deepEqual(t.selection,{record:'fixture',filter:'stem',detail:'native'});
});
test('stopped session opens a fresh tab without navigating detached old tab',async()=>{
 const h=harness();await h.open();h.tabs[0].denyNavigation=true;h.url('http://127.0.0.1:43211/#next');await h.open();
 assert.equal(h.tabs.length,2);assert.equal(h.tabs[0].navigations.length,1);assert.equal(h.tabs[1].navigations.length,1);
});
test('closed Browser tab explicitly opens a fresh view',async()=>{
 const h=harness();await h.open();h.tabs[0].close();await h.open('running');
 assert.equal(h.tabs.length,2);assert.match(h.messages.at(-1),/fresh Browser view/);
});
test('Home reload does not fabricate an existing view or make duplicates',async()=>{
 const h=harness();await h.open('running');assert.equal(h.tabs.length,0);assert.equal(h.calls.length,0);
 assert.match(h.messages.at(-1),/Switch to its existing tab/);
});
test('popup blocked permits gesture retry without a duplicate fallback link',async()=>{
 const h=harness();h.block(true);await h.open();assert.match(h.messages.at(-1),/Popup blocked/);
 h.block(false);await h.open('running');assert.equal(h.tabs.length,1);await h.open('running');assert.equal(h.tabs.length,1);
});
test('failed Return does not close a previously opened tab',async()=>{
 const h=harness();await h.open();vm.runInContext("api=async()=>{throw Error('unavailable')}",h.ctx);
 await h.open('running');assert.equal(h.tabs[0].closed,false);assert.equal(h.tabs[0].navigations.length,1);
});

test('stale running state across restart never navigates old tab; retry opens new session',async()=>{
 const h=harness();await h.open();h.tabs[0].denyNavigation=true;h.url('http://127.0.0.1:43211/#next');
 await h.open('running');assert.equal(h.tabs.length,1);assert.match(h.messages.at(-1),/Click Return again/);
 await h.open('running');assert.equal(h.tabs.length,2);assert.equal(h.tabs[1].navigations.length,1);
});
test('popup blocking on restart does not reuse stopped tab',async()=>{
 const h=harness();await h.open();h.tabs[0].denyNavigation=true;h.url('http://127.0.0.1:43211/#next');h.block(true);await h.open();
 h.block(false);await h.open('running');assert.equal(h.tabs.length,2);assert.equal(h.tabs[0].navigations.length,1);
});
test('navigation exception never exposes session URL and retry remains possible',async()=>{
 const h=harness();const pending=h.open();h.tabs[0].denyNavigation=true;await pending;
 assert.equal(h.tabs[0].closed,true);assert.ok(h.messages.every(m=>!m.includes('#fixture')&&!m.includes('43210')));
 await h.open('running');assert.equal(h.tabs.length,2);assert.equal(h.tabs[1].navigations.length,1);
});
