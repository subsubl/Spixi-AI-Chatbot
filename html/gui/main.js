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
