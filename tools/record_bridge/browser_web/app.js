"use strict";
const $ = id => document.getElementById(id);
const token = location.hash.slice(1) || sessionStorage.getItem("voxis-browser-token") || "";
if (location.hash) { sessionStorage.setItem("voxis-browser-token", token); history.replaceState(null, "", "/"); }
let rows = [], selected = null, info = null, selectionVersion = 0, refreshVersion = 0;
const friendly = value => ({structure_checked:"Structure checked",invalid:"Invalid",unsupported:"Unsupported",invalidated:"Invalidated",not_assessed:"Not assessed",prohibited:"Prohibited"}[value] || value || "Not recorded");
const producer = format => format === "voxis.stem-session/1" ? "Stem Lab" : format === "VOXIS.configuration-export.v1" ? "WXR-003" : "Other";
function notify(message, error = false) { $("message").textContent = message; $("message").classList.toggle("error", error); $("message").hidden = !message; }
async function api(path, body) {
  const options = {headers:{"X-VOXIS-Token":token}};
  if (body !== undefined) { options.method = "POST"; options.headers["Content-Type"] = "application/json"; options.body = JSON.stringify(body); }
  let response;
  try { response = await fetch(path, options); } catch { throw new Error("Browser session is unavailable. Relaunch Record Browser and try again."); }
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Could not complete this action.");
  return data;
}
function resetDetail(message = "Select a record") {
  selectionVersion++; selected = null; $("detail").hidden = true; $("placeholder").hidden = false;
  $("placeholder").querySelector("h2").textContent = message;
  $("placeholder").querySelector("p").textContent = "Inspect its contents and provenance, or export the preserved original.";
}
function icon(kind) {
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("viewBox", kind === "file" ? "0 0 24 30" : "0 0 14 18"); svg.setAttribute("aria-hidden","true");
  const path = document.createElementNS(svg.namespaceURI,"path");
  path.setAttribute("d", kind === "file" ? "M3 1h11l7 7v21H3z M14 1v8h7" : "M4 2l6 7-6 7"); svg.append(path);
  if (kind !== "file") svg.classList.add("chevron"); return svg;
}
function renderList() {
  const query = $("search").value.toLowerCase(), format = $("format").value;
  const filtered = rows.filter(r => (!format || (format === "other" ? producer(r.format) === "Other" : r.format === format)) && [r.name,r.id,r.format,r.status,...r.search_session_refs].join(" ").toLowerCase().includes(query));
  $("records").replaceChildren();
  for (const row of filtered) {
    const button = document.createElement("button"); button.className = "record"; button.setAttribute("aria-pressed", String(selected?.record.id === row.id));
    const copy = document.createElement("span"); copy.className = "record-copy";
    const name = document.createElement("span"); name.className = "name"; name.textContent = row.name;
    const meta = document.createElement("span"); meta.className = "meta"; meta.textContent = `${producer(row.format)}  ·  ${friendly(row.status)}`;
    copy.append(name,meta); button.append(icon("file"),copy,icon("chevron")); button.addEventListener("click",()=>selectRecord(row)); $("records").append(button);
  }
  $("count").textContent = filtered.length === rows.length ? `${rows.length} record${rows.length === 1 ? "" : "s"}` : `${filtered.length} of ${rows.length} records`;
  if (!filtered.length && rows.length) listMessage("No matching records. Clear the search or choose another format.");
}
function listMessage(text) { const p=document.createElement("p"); p.className="list-message";p.textContent=text;$("records").append(p); }
async function refresh() {
  const version=++refreshVersion; $("refresh").disabled=true; notify(""); resetDetail();
  try {
    const data=await api("/api/records"); if(version!==refreshVersion)return;
    rows=data.records; renderList();
    if(data.state === "missing") {listMessage("No index found. Use Record Bridge to import your first record, then refresh. No database was created.");resetDetail("No index yet");}
    else if(data.state === "empty") {listMessage("This index has no records. Import a JSON with Record Bridge, then refresh.");resetDetail("No records yet");}
  } catch(e) { rows=[];renderList();resetDetail("Index unavailable");notify(e.message,true); }
  finally { $("refresh").disabled=false; }
}
function addFact(label,value,hash=false) {const dt=document.createElement("dt"),dd=document.createElement("dd");dt.textContent=label;dd.textContent=value;if(hash)dd.className="hash";$("facts").append(dt,dd);}
function tab(which,focus=false) {
  for(const name of ["overview","native"]) {const active=name===which;$(name).hidden=!active;$(name+"-tab").setAttribute("aria-selected",String(active));$(name+"-tab").tabIndex=active?0:-1;}
  if(focus)$(which+"-tab").focus();
}
async function selectRecord(row) {
  resetDetail("Loading record…"); const version=selectionVersion;notify("");renderList();
  try {
    const data=await api("/api/record?id="+encodeURIComponent(row.id));if(version!==selectionVersion)return;
    selected=data; const s=data.summary,r=data.record;
    $("record-name").textContent=r.name;$("record-meta").textContent=`${s.producer || producer(r.format)} · Imported ${r.imported_at}`;
    $("facts").replaceChildren();addFact("Format",r.format);addFact("Record ID",r.id,true);addFact("Search Session",r.search_session_refs.join(", ")||"Unassigned");addFact("Structural status",friendly(r.status));addFact("Evidence eligibility",friendly(s.research_eligibility));
    if(s.captured_at)addFact("Captured",s.captured_at);
    $("boundary").textContent=r.status === "invalidated" ? "Invalidated history. Evidentiary use is prohibited." : r.status === "invalid" ? "Invalid record. Original bytes are preserved; research use is excluded." : r.status === "unsupported" ? "Unsupported format or version. Original bytes are preserved; no validation is implied." : "Structure checked does not validate geometry or manuscript meaning.";
    $("warnings").replaceChildren();for(const message of s.warnings||[]) {const li=document.createElement("li");li.textContent=message;$("warnings").append(li);}
    $("summary").textContent=JSON.stringify(s,null,2);$("native-text").textContent=data.native;$("encoding").textContent=data.encoding_note;
    $("overview").querySelector("details").open=false;tab("overview");$("placeholder").hidden=true;$("detail").hidden=false;renderList();
  } catch(e) {if(version===selectionVersion){resetDetail("Record unavailable");notify(e.message,true);}}
}
$("search").addEventListener("input",renderList);$("format").addEventListener("change",renderList);$("refresh").addEventListener("click",refresh);
for(const name of ["overview","native"]) {$(name+"-tab").addEventListener("click",()=>tab(name));$(name+"-tab").addEventListener("keydown",e=>{if(["ArrowLeft","ArrowRight","Home","End"].includes(e.key)){e.preventDefault();tab(e.key==="Home"?"overview":e.key==="End"?"native":name==="overview"?"native":"overview",true);}});}
$("index-info").addEventListener("click",async()=>{try{info=await api("/api/info");$("version").textContent=info.version;$("index-path").value=info.index;$("info-dialog").showModal();}catch(e){notify(e.message,true);}});
$("close-info").addEventListener("click",()=>$("info-dialog").close());
$("export").addEventListener("click",async()=>{
  if(!selected)return;
  try {info=info||await api("/api/info"); const sep=info.export_folder.includes("\\")?"\\":"/";
    $("destination").value=info.export_folder+sep+`voxis-${selected.record.id.slice(0,12)}-original.json`;$("export-error").hidden=true;$("export-dialog").showModal();$("destination").focus();
  }catch(e){notify(e.message,true);}
});
$("cancel-export").addEventListener("click",()=>$("export-dialog").close());
$("export-form").addEventListener("submit",async e=>{
  e.preventDefault();if(!selected)return;$("save-export").disabled=true;$("cancel-export").disabled=true;$("export-error").hidden=true;
  try {const result=await api("/api/export",{id:selected.record.id,path:$("destination").value});$("export-dialog").close();notify(`Original exported · ${result.bytes.toLocaleString()} bytes · ${result.path}`);}
  catch(e){$("export-error").textContent=e.message;$("export-error").hidden=false;}
  finally{$("save-export").disabled=false;$("cancel-export").disabled=false;}
});
$("export-dialog").addEventListener("cancel",e=>{if($("save-export").disabled)e.preventDefault();});
$("stop").addEventListener("click",()=>$("stop-dialog").showModal());$("cancel-stop").addEventListener("click",()=>$("stop-dialog").close());
$("confirm-stop").addEventListener("click",async()=>{try{await api("/api/stop",{});$("stop-dialog").close();sessionStorage.removeItem("voxis-browser-token");resetDetail("Browser stopped");rows=[];renderList();notify("This session has ended. You can close this tab. Relaunch Record Browser to return.");for(const b of document.querySelectorAll("button,input,select"))b.disabled=true;}catch(e){$("stop-dialog").close();notify(e.message,true);}});
refresh();
