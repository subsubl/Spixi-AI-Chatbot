async function apiCall(method, params = {}) {
  const body = JSON.stringify({ method, params });
  try {
    const res = await fetch('/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body,
    });
    return await res.json();
  } catch (e) {
    console.error('API call failed', e);
    throw e;
  }
}

function setStatus(text) {
  document.getElementById('status').textContent = text;
}

async function refreshContacts() {
  const listEl = document.getElementById('contacts-list');
  const sel = document.getElementById('chat-recipient');
  listEl.innerHTML = 'Loading...';
  sel.innerHTML = '';
  try {
    const r = await apiCall('contacts', {});
    const friends = r.result || [];
    listEl.innerHTML = '';
    if (friends.length === 0) listEl.innerHTML = '<div style="padding:8px;color:#666">No contacts</div>';
    friends.forEach(f => {
      const div = document.createElement('div');
      div.className = 'contact';
      const meta = document.createElement('div');
      meta.className = 'meta';
      meta.innerHTML = `<strong>${escapeHtml(f.displayName || f.walletAddress)}</strong><div>${escapeHtml(f.walletAddress)}</div>`;
      const actions = document.createElement('div');
      const btn = document.createElement('button');
      btn.textContent = 'Select';
      btn.onclick = () => { selectRecipient(f); };
      actions.appendChild(btn);
      div.appendChild(meta);
      div.appendChild(actions);
      listEl.appendChild(div);

      const opt = document.createElement('option');
      opt.value = f.walletAddress;
      opt.textContent = f.displayName || f.walletAddress;
      sel.appendChild(opt);
    });
  } catch (e) {
    listEl.innerHTML = '<div style="padding:8px;color:#900">Failed to load</div>';
  }
}

function escapeHtml(s){ if(!s) return ''; return s.replace(/[&<>"']/g, c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"})[c]); }

function selectRecipient(friend){
  const sel = document.getElementById('chat-recipient');
  for (let i=0;i<sel.options.length;i++){if (sel.options[i].value===friend.walletAddress) sel.selectedIndex=i}
  loadLastMessages();
}

async function addContact() {
  const addr = document.getElementById('new-address').value.trim();
  const name = document.getElementById('new-name').value.trim();
  if (!addr) return alert('Address required');
  try {
    const confirmed = await askConfirmation(`Add contact ${addr}?`);
    if (!confirmed) return;
    const params = { address: addr };
    const r = await apiCall('addContact', params);
    if (r.error) return alert('Error: '+(r.error.message||r.error.code));
    await refreshContacts();
  } catch (e){ alert('Add contact failed'); }
}

async function sendMessage() {
  const sel = document.getElementById('chat-recipient');
  const addr = sel.value;
  const channel = document.getElementById('chat-channel').value || '0';
  const msg = document.getElementById('chat-message').value;
  if (!addr) return alert('Select recipient');
  if (!msg) return alert('Type a message');
  try {
    const confirmed = await askConfirmation(`Send message to ${addr}?`);
    if (!confirmed) return;
    const r = await apiCall('sendChatMessage', { address: addr, channel: channel.toString(), message: msg });
    if (r.error) return alert('Error: '+(r.error.message||r.error.code));
    document.getElementById('chat-message').value = '';
    await loadLastMessages();
  } catch (e) { alert('Send failed'); }
}

async function loadLastMessages() {
  const sel = document.getElementById('chat-recipient');
  const addr = sel.value;
  const container = document.getElementById('last-messages');
  container.innerHTML = 'Loading...';
  if (!addr) { container.innerHTML='No recipient selected'; return; }
  try {
    const r = await apiCall('getLastMessages', { address: addr, count: '20', channel: document.getElementById('chat-channel').value || '0' });
    if (r.error) { container.innerHTML = 'Error loading messages'; return; }
    const msgs = r.result || [];
    container.innerHTML = '';
    msgs.forEach(m => {
      const d = document.createElement('div');
      d.className = 'message';
      const when = new Date((m.ts||0)*1000).toLocaleString();
      d.innerHTML = `<div><strong>${escapeHtml(m.from||'me')}</strong> <span style="color:#666;font-size:12px">${when}</span></div><div>${escapeHtml(m.message)}</div>`;
      container.appendChild(d);
    });
  } catch (e) { container.innerHTML = 'Failed to load messages'; }
}

async function refreshStatus(){
  try{
    const r = await apiCall('status', {});
    if (r.error){ setStatus('Node: error'); document.getElementById('node-info').textContent = JSON.stringify(r.error, null, 2); return; }
    setStatus('Node: online');
    document.getElementById('node-info').textContent = JSON.stringify(r.result, null, 2);
  }catch(e){ setStatus('Node: unreachable'); document.getElementById('node-info').textContent = String(e); }
}

// wire ui
window.addEventListener('load', async () => {
  document.getElementById('add-contact').addEventListener('click', addContact);
  document.getElementById('send-message').addEventListener('click', sendMessage);
  document.getElementById('refresh-status').addEventListener('click', refreshStatus);
  document.getElementById('chat-channel').value = '0';

  try{
    await refreshContacts();
    await refreshStatus();
    setStatus('Connected');
  }catch(e){ setStatus('Disconnected'); }

  // poll presence messages
  setInterval(refreshStatus, 15000);
});

// -- curl command helper UI --
function initCurlCommands(){
  const cmds = [
    {label:'status', cmd:`curl -X POST http://localhost:8001/ -H 'Content-Type: application/json' -d '{"method":"status","params":{}}'`} ,
    {label:'contacts', cmd:`curl -X POST http://localhost:8001/ -H 'Content-Type: application/json' -d '{"method":"contacts","params":{}}'`} ,
    {label:'addContact', cmd:`curl -X POST http://localhost:8001/ -H 'Content-Type: application/json' -d '{"method":"addContact","params":{"address":"<ADDRESS>"}}'`} ,
    {label:'acceptContact', cmd:`curl -X POST http://localhost:8001/ -H 'Content-Type: application/json' -d '{"method":"acceptContact","params":{"address":"<ADDRESS>"}}'`} ,
    {label:'myWallet', cmd:`curl http://localhost:8001/myWallet`} ,
    {label:'sendChatMessage', cmd:`curl -X POST http://localhost:8001/ -H 'Content-Type: application/json' -d '{"method":"sendChatMessage","params":{"address":"<ADDRESS>","channel":"0","message":"Hello"}}'`} ,
    {label:'getLastMessages', cmd:`curl -X POST http://localhost:8001/ -H 'Content-Type: application/json' -d '{"method":"getLastMessages","params":{"address":"<ADDRESS>","count":"20","channel":"0"}}'`} ,
  ];

  const grid = document.getElementById('curl-buttons');
  grid.innerHTML = '';
  cmds.forEach(c=>{
    const b = document.createElement('button');
    b.textContent = c.label;
    b.title = c.cmd;
    b.onclick = ()=>{ document.getElementById('curl-editor').value = c.cmd; };
    grid.appendChild(b);
  });
}

async function copyCurlEditor(){
  const txt = document.getElementById('curl-editor').value;
  try{ await navigator.clipboard.writeText(txt); alert('Copied to clipboard'); }catch(e){ alert('Copy failed — select and copy manually'); }
}

// Basic curl parser and executor (best-effort). If execution fails due to CORS/remote host, the error is shown.
async function sendCurlEditor(){
  const txt = document.getElementById('curl-editor').value.trim();
  if(!txt) return alert('No command to send');

  // If it's not a curl command, just show it
  if(!txt.startsWith('curl')){
    document.getElementById('curl-output').textContent = 'Not a curl command.' + '\n' + txt; return;
  }

  // Extract URL
  const urlMatch = txt.match(/https?:\/\/[^'"\s\)]+|https?:\/\/[^\s]+/);
  const url = urlMatch ? urlMatch[0] : null;
  // Determine method
  const method = /-X\s+([A-Z]+)/.test(txt) ? txt.match(/-X\s+([A-Z]+)/)[1] : (/(-d\s|--data|--data-raw)/.test(txt) ? 'POST' : 'GET');
  // Extract headers
  const headers = {};
  const headerRe = /-H\s+'([^:]+):\s*([^']+)'/g;
  let hmatch;
  while((hmatch = headerRe.exec(txt))){ headers[hmatch[1].trim()] = hmatch[2].trim(); }
  // Extract data
  let data = null;
  const dataRe = /(?:-d|--data|--data-raw)\s+'([^']*)'/;
  const dmatch = txt.match(dataRe);
  if(dmatch) data = dmatch[1];

  // Execute the request via fetch
  // Before executing state-changing commands, ask for confirmation
  const isStateChanging = /addContact|sendChatMessage|acceptContact/i.test(txt);
  if (isStateChanging) {
    const confirmed = await askConfirmation('This command will modify node state. Proceed?');
    if (!confirmed) {
      document.getElementById('curl-output').textContent = 'Cancelled by user';
      return;
    }
  }

  try{
    const opts = { method, headers };
    if(data){
      // try to parse JSON if content-type is json
      if((headers['Content-Type']||headers['content-type']||'').includes('application/json')){
        try{ opts.body = data; }catch(e){ opts.body = data; }
      } else { opts.body = data; }
    }
    document.getElementById('curl-output').textContent = 'Sending...';
    const res = await fetch(url || '/', opts);
    const text = await res.text();
    document.getElementById('curl-output').textContent = `HTTP ${res.status} ${res.statusText}\n\n` + text;
  }catch(e){
    document.getElementById('curl-output').textContent = 'Execution failed: ' + String(e) + '\n\nCommand copied to clipboard';
    try{ await navigator.clipboard.writeText(txt); }catch(_){ /* ignore */ }
  }
}

function askConfirmation(message){
  return new Promise((resolve)=>{
    const modal = document.getElementById('confirm-modal');
    const text = document.getElementById('confirm-text');
    const yes = document.getElementById('confirm-yes');
    const no = document.getElementById('confirm-no');
    text.textContent = message;
    modal.setAttribute('aria-hidden','false');
    function cleanup(){
      modal.setAttribute('aria-hidden','true');
      yes.removeEventListener('click', onYes);
      no.removeEventListener('click', onNo);
    }
    function onYes(){ cleanup(); resolve(true); }
    function onNo(){ cleanup(); resolve(false); }
    yes.addEventListener('click', onYes);
    no.addEventListener('click', onNo);
  });
}

// initialize curl UI after load
window.addEventListener('load', ()=>{ try{ initCurlCommands(); document.getElementById('curl-send').addEventListener('click', sendCurlEditor); document.getElementById('curl-copy').addEventListener('click', copyCurlEditor);}catch(e){console.warn('Curl UI init failed',e);} });
