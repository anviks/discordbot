// Relative, because the bot serves this page itself - same origin, no CORS needed.
const API = '/api';

// Kept in sessionStorage so it survives a reload but not a closed tab.
function getKey() {
  let key = sessionStorage.getItem('apiKey');
  while (!key) {
    key = prompt('API key (the API_KEY value from the bot\'s .env):');
    if (key === null) return null;
    key = key.trim();
  }
  sessionStorage.setItem('apiKey', key);
  return key;
}

function forgetKey() {
  sessionStorage.removeItem('apiKey');
}

// --- Toast ---

let toastTimer;
function toast(message, type = 'success') {
  const el = document.getElementById('toast');
  el.textContent = message;
  el.className = `show ${type}`;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove('show'), 3000);
}

// --- Channel status ---

async function refreshChannel() {
  try {
    const { guild, name } = await apiCall('GET', '/channel');
    document.getElementById('channel-display').textContent = `${guild} > #${name}`;
  } catch (err) {
    document.getElementById('channel-display').textContent = err.message || 'unavailable';
  }
}

document.getElementById('refresh-channel').addEventListener('click', refreshChannel);
refreshChannel();

// --- Generic form helper ---

function bindForm(formId, handler) {
  document.getElementById(formId).addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = e.target.querySelector('button[type="submit"]');
    btn.disabled = true;
    try {
      await handler(new FormData(e.target));
    } finally {
      btn.disabled = false;
    }
  });
}

async function apiCall(method, path, body) {
  const key = getKey();
  if (key === null) throw new Error('An API key is required');

  const res = await fetch(`${API}${path}`, {
    method,
    headers: { 'Content-Type': 'application/json', 'X-API-Key': key },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  if (res.status === 401) {
    forgetKey();  // wrong key - drop it so the next call re-prompts
    throw new Error('Rejected: wrong API key');
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(typeof err.detail === 'string' ? err.detail : res.statusText);
  }
  return res.json();
}

// --- Change channel ---

bindForm('form-cd', async (fd) => {
  const channel_id = fd.get('channel_id');
  try {
    const { guild, name } = await apiCall('PUT', `/channel/${channel_id}`);
    document.getElementById('channel-display').textContent = `${guild} > #${name}`;
    toast(`Switched to #${name}`);
  } catch (err) {
    toast(err.message, 'error');
  }
});

// --- Send message ---

bindForm('form-message', async (fd) => {
  try {
    await apiCall('POST', '/message', { message: fd.get('message') });
    toast('Message sent');
    document.getElementById('form-message').reset();
  } catch (err) {
    toast(err.message, 'error');
  }
});

// --- Ping ---

bindForm('form-ping', async (fd) => {
  const user_id = fd.get('user_id');
  const count = Number(fd.get('count') || 1);
  try {
    await apiCall('POST', '/ping', { user_id, count });
    toast(`Pinged ${count} time(s)`);
  } catch (err) {
    toast(err.message, 'error');
  }
});

// --- DM ---

bindForm('form-dm', async (fd) => {
  try {
    await apiCall('POST', '/dm', {
      user_id: fd.get('user_id'),
      message: fd.get('message'),
    });
    toast('DM sent');
    document.getElementById('form-dm').reset();
  } catch (err) {
    toast(err.message, 'error');
  }
});

// --- Reply ---

bindForm('form-reply', async (fd) => {
  try {
    await apiCall('POST', '/reply', {
      message_id: fd.get('message_id'),
      content: fd.get('content'),
    });
    toast('Reply sent');
    document.getElementById('form-reply').reset();
  } catch (err) {
    toast(err.message, 'error');
  }
});
