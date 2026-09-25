/* ParquetView — in-browser Parquet engine (100% local, no upload) */
let hp, compressorLib = null;
try {
  hp = await import('https://cdn.jsdelivr.net/npm/hyparquet@1.31.1/+esm');
} catch (e) {
  toast('Failed to load the Parquet engine. Check your internet connection and reload.', true);
  throw e;
}

const PAGE = 50;
const MAX_LOAD = 200000;

const state = {
  fileHandle:null, fileObj:null, meta:null, schemaFields:[],
  colKind:{},
  rows:[], loaded:0, total:0,
  visibleCols:[],
  filter:'', sortCol:null, sortDir:1,
  page:0,
};

const $ = id => document.getElementById(id);
if(!$('dropzone')){ /* not on a tool page */ }
else {

function fileToAsyncBuffer(f){
  return {
    byteLength: f.size,
    slice: async (offset, length)=>{
      const blob = f.slice(offset, offset + length);
      return await blob.arrayBuffer();
    }
  };
}

async function ensureCompressors(){
  if (compressorLib) return compressorLib;
  try {
    compressorLib = await import('https://cdn.jsdelivr.net/npm/hyparquet-compressors@1.1.2/+esm');
    return compressorLib;
  } catch(e){ return null; }
}

async function handleFile(f){
  if(!f) return;
  state.fileHandle = f;
  state.fileObj = fileToAsyncBuffer(f);
  state.rows=[]; state.loaded=0; state.page=0; state.sortCol=null; state.sortDir=1; state.filter='';
  $('q').value='';
  showWorkspaceLoading(true);

  let metadata;
  try {
    metadata = await hp.parquetMetadataAsync(state.fileObj);
  } catch(e){
    toast('Could not read this as a Parquet file: ' + (e.message||e), true);
    showWorkspaceLoading(false,true);
    return;
  }
  state.meta = metadata;
  const schema = hp.parquetSchema(metadata);
  state.schemaFields = (schema.children||[]).map(c=>({name:c.element?.name ?? c.path?.join('.') ?? c.name, type: typeName(c)}));
  state.colKind = {};
  for (const fld of (metadata.schema || [])) {
    const lt = fld.logical_type || {};
    if (lt.type === 'DATE' || fld.converted_type === 'DATE') state.colKind[fld.name] = 'date';
    else if (lt.type === 'TIMESTAMP' || String(fld.converted_type||'').startsWith('TIMESTAMP')) state.colKind[fld.name] = 'timestamp';
  }
  state.total = Number(metadata.num_rows);
  state.visibleCols = state.schemaFields.map(c=>c.name);

  renderMeta(f);
  renderSchema();
  await loadMoreRows(true);
  showWorkspaceLoading(false);
}

function typeName(node){
  const e = node.element || {};
  if(e.logicalType){
    const lt = e.logicalType;
    if(lt.type) return lt.type.toLowerCase();
    return String(lt).toLowerCase();
  }
  const t = e.type ?? node.type ?? '';
  return String(t).toLowerCase().replace('_',' ');
}

async function loadMoreRows(first){
  const want = Math.min(state.loaded + (first?2000:10000), state.total, MAX_LOAD);
  if(want<=state.loaded) return;
  const lib = await ensureCompressors();
  const opts = { file:state.fileObj, rowStart:state.loaded, rowEnd:want };
  if(lib && lib.compressors) opts.compressors = lib.compressors;
  const chunk = await hp.parquetReadObjects(opts);
  state.rows.push(...chunk);
  state.loaded = want;
  state.total = Math.max(state.total, want);
  $('loadmore').style.display = (state.loaded < Math.min(state.total,MAX_LOAD)) ? '' : 'none';
  updateSizeCard();
  render();
}

function humanSize(n){
  if(n<1024) return n+' B';
  const u=['KB','MB','GB']; let i=-1;
  do{ n/=1024; i++; }while(n>=1024 && i<u.length-1);
  return n.toFixed(n<10?1:0)+' '+u[i];
}

function renderMeta(f){
  $('m-filename').textContent = f.name;
  $('m-rows').textContent = state.total.toLocaleString();
  $('m-cols').textContent = state.schemaFields.length;
  $('m-groups').textContent = state.meta.row_groups.length;
  updateSizeCard(f);
}
function updateSizeCard(f){
  f = f || state.fileHandle;
  const partial = state.loaded < state.total;
  $('m-size').innerHTML = humanSize(f.size) + (partial
    ? ` <small>${state.loaded.toLocaleString()} of ${state.total.toLocaleString()} rows loaded</small>`
    : '');
}

function renderSchema(){
  const box=$('schema'); box.innerHTML='';
  $('schemacount').textContent = state.schemaFields.length;
  state.schemaFields.forEach(c=>{
    const chip=document.createElement('span');
    chip.className='chip'+(state.visibleCols.includes(c.name)?'':' off');
    chip.innerHTML=`<span class="ty"></span><span class="nm"></span><button title="toggle">✕</button>`;
    chip.querySelector('.ty').textContent=c.type;
    chip.querySelector('.nm').textContent=c.name;
    chip.querySelector('button').onclick=(ev)=>{ev.stopPropagation();toggleCol(c.name);};
    chip.onclick=()=>toggleCol(c.name);
    box.appendChild(chip);
  });
}
function toggleCol(name){
  const i=state.visibleCols.indexOf(name);
  if(i>=0) state.visibleCols.splice(i,1); else state.visibleCols.push(name);
  renderSchema(); render();
}

function filteredRows(){
  let rows = state.rows;
  if(state.filter){
    const q=state.filter.toLowerCase();
    rows = rows.filter(r=>{
      for(const c of state.visibleCols){
        const v=r[c];
        if(v!=null && String(v).toLowerCase().includes(q)) return true;
      }
      return false;
    });
  }
  if(state.sortCol){
    const col=state.sortCol, dir=state.sortDir;
    rows=[...rows].sort((a,b)=>{
      let x=a[col], y=b[col];
      if(x==null) return 1; if(y==null) return -1;
      if(typeof x==='number'&&typeof y==='number') return (x-y)*dir;
      x=String(x); y=String(y);
      return x<y?-dir:x>y?dir:0;
    });
  }
  return rows;
}

const pad=n=>String(n).padStart(2,'0');
function fmtDate(d){ return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`; }
function fmtDateTime(d){
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
}
function fmt(v, name){
  if(v===null||v===undefined) return {text:'null',cls:'null'};
  if(v instanceof Date){
    const kind = state.colKind[name];
    if(kind==='date') return {text:fmtDate(v),cls:''};
    return {text:fmtDateTime(v),cls:''};
  }
  if(typeof v==='boolean') return {text:String(v),cls:''};
  if(typeof v==='number') return {text:(Number.isFinite(v)?v.toLocaleString(undefined,{maximumFractionDigits:6}):String(v)),cls:'num'};
  if(typeof v==='object') return {text:JSON.stringify(v),cls:'celljson'};
  return {text:String(v),cls:''};
}

function render(){
  const cols = state.visibleCols;
  const head=$('headrow'); head.innerHTML='';
  cols.forEach(c=>{
    const th=document.createElement('th');
    let arrow='↕';
    if(state.sortCol===c) arrow=state.sortDir===1?'▲':'▼';
    th.innerHTML = `${c}<span class="arr">${arrow}</span>`;
    if(state.sortCol===c) th.classList.add('sorted');
    th.onclick=()=>{
      if(state.sortCol===c) state.sortDir*=-1;
      else {state.sortCol=c;state.sortDir=1;}
      state.page=0; render();
    };
    head.appendChild(th);
  });

  const all = filteredRows();
  const pages = Math.max(1,Math.ceil(all.length/PAGE));
  if(state.page>=pages) state.page=pages-1;
  const slice = all.slice(state.page*PAGE,(state.page+1)*PAGE);

  const body=$('body'); body.innerHTML='';
  const frag=document.createDocumentFragment();
  slice.forEach(r=>{
    const tr=document.createElement('tr');
    cols.forEach(c=>{
      const td=document.createElement('td');
      const {text,cls}=fmt(r[c],c);
      td.textContent=text; if(cls) td.className=cls;
      td.title=text;
      tr.appendChild(td);
    });
    frag.appendChild(tr);
  });
  body.appendChild(frag);

  const shownStart = all.length===0?0:state.page*PAGE+1;
  const shownEnd=Math.min((state.page+1)*PAGE,all.length);
  $('pageinfo').textContent=`${shownStart.toLocaleString()}–${shownEnd.toLocaleString()} of ${all.length.toLocaleString()}`;
  $('matchbadge').textContent = state.filter
    ? `${all.length.toLocaleString()} matches (of ${state.loaded.toLocaleString()} loaded / ${state.total.toLocaleString()} total)`
    : `${all.length.toLocaleString()} loaded rows`;
  $('prev').disabled=state.page===0;
  $('next').disabled=state.page>=pages-1;
  if(state.loaded<Math.min(state.total,MAX_LOAD)) $('loadmore').style.display='';
}

function csvCell(v,name){
  if(v===null||v===undefined) return '';
  if(v instanceof Date){
    v = state.colKind[name]==='date' ? fmtDate(v) : fmtDateTime(v);
  } else if(typeof v==='object') v=JSON.stringify(v);
  v=String(v);
  if(/[",\n\r]/.test(v)) v='"'+v.replace(/"/g,'""')+'"';
  return v;
}
function download(name,blob){
  const url=URL.createObjectURL(blob);
  const a=document.createElement('a'); a.href=url; a.download=name; document.body.appendChild(a);
  a.click(); a.remove(); setTimeout(()=>URL.revokeObjectURL(url),4000);
}
function baseName(){
  const n=(state.fileHandle?.name||'data').replace(/\.(parquet|pq|parq)$/i,'');
  return n;
}
function exportCSV(){
  const rows=filteredRows(), cols=state.visibleCols;
  const lines=[cols.map(c=>csvCell(c,c)).join(',')];
  for(const r of rows) lines.push(cols.map(c=>csvCell(r[c],c)).join(','));
  const blob=new Blob(['\uFEFF'+lines.join('\r\n')],{type:'text/csv;charset=utf-8'});
  download(baseName()+'.csv',blob);
  toast(`Exported ${rows.length.toLocaleString()} rows to CSV`);
}
function exportJSON(){
  const rows=filteredRows();
  const blob=new Blob([JSON.stringify(rows,null,2)],{type:'application/json'});
  download(baseName()+'.json',blob);
  toast(`Exported ${rows.length.toLocaleString()} rows to JSON`);
}

function showWorkspaceLoading(loading,resetOnly=false){
  $('dropzone').classList.add('hidden');
  $('workspace').classList.remove('hidden');
  let btn=$('loadmore');
  if(loading){ btn.disabled=true; btn.innerHTML='<span class="spin"></span> Reading…'; }
  else { btn.disabled=false; btn.textContent='Load more rows'; btn.style.display=(state.loaded<Math.min(state.total,MAX_LOAD))?'':'none'; }
  if(resetOnly){ $('workspace').classList.add('hidden'); $('dropzone').classList.remove('hidden'); }
}

$('pickbtn').onclick=e=>{e.stopPropagation();$('fileinput').click();};
$('dropzone').onclick=()=>$('fileinput').click();
$('fileinput').onchange=e=>handleFile(e.target.files[0]);
$('resetbtn').onclick=()=>{
  $('workspace').classList.add('hidden');
  $('dropzone').classList.remove('hidden');
  $('fileinput').value='';
};
$('q').oninput=e=>{state.filter=e.target.value;state.page=0;render();};
$('prev').onclick=()=>{state.page--;render();$('tablewrap').scrollTo({top:0,left:0});};
$('next').onclick=()=>{state.page++;render();$('tablewrap').scrollTo({top:0,left:0});};
$('loadmore').onclick=async function(){
  this.disabled=true; this.innerHTML='<span class="spin"></span> Loading…';
  try{ await loadMoreRows(false); }catch(e){ toast('Load failed: '+(e.message||e),true); }
  this.disabled=false; this.textContent='Load more rows';
};
$('csvbtn').onclick=exportCSV;
$('jsonbtn').onclick=exportJSON;
$('schemahd').onclick=()=>$('schemawrap').classList.toggle('open');

['dragover','dragenter'].forEach(ev=>document.addEventListener(ev,e=>{e.preventDefault();$('dropzone').classList.add('over');}));
['dragleave','drop'].forEach(ev=>document.addEventListener(ev,e=>{e.preventDefault();if(ev==='dragleave'&&e.target!==document.documentElement)return;$('dropzone').classList.remove('over');}));
document.addEventListener('drop',e=>{const f=e.dataTransfer?.files?.[0];if(f)handleFile(f);});

let toastTimer;
function toast(msg,isErr){
  const t=$('toast'); t.textContent=msg; t.className='toast show'+(isErr?' err':'');
  clearTimeout(toastTimer); toastTimer=setTimeout(()=>t.className='toast',3200);
}
}
