// Painel Dofus - interface (JS puro, sem build).
const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const fmt = (n) => Number(n || 0).toLocaleString('pt-BR');
const main = $('#main');

async function api(url, method = 'GET', body) {
  const res = await fetch('/api' + url, { method, headers: body ? { 'Content-Type': 'application/json' } : {}, body: body ? JSON.stringify(body) : undefined });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || res.statusText);
  return data;
}

let toastTimer;
function toast(msg, err = false) {
  const t = $('#toast');
  t.textContent = msg;
  t.className = 'toast show' + (err ? ' err' : '');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => (t.className = 'toast'), err ? 6000 : 3500);
}
const run = (fn) => async (...a) => { try { await fn(...a); } catch (e) { toast(e.message, true); } };

function modal(html) {
  $('#modalBody').innerHTML = html;
  $('#modal').classList.remove('hidden');
  return $('#modalBody');
}
const closeModal = () => $('#modal').classList.add('hidden');
$('#modalClose').onclick = closeModal;
$('#modal').onclick = (e) => { if (e.target.id === 'modal') closeModal(); };

const debounce = (fn, ms = 250) => { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; };

// Personagens (cache para os seletores)
let playersCache = [];
async function loadPlayers() { playersCache = await api('/players'); return playersCache; }
function playerSelect(id = 'selPlayer', selected) {
  return `<select id="${id}">${playersCache.map((p) => `<option value="${p.id}" ${+selected === p.id ? 'selected' : ''}>${esc(p.name)} (${esc(p.className)} ${p.level})</option>`).join('')}</select>`;
}
const onlineNote = '<div class="note">As ações entram numa fila e são aplicadas assim que o personagem estiver <b>online</b> no jogo (em até 1 segundo). Acompanhe em "Fila e histórico".</div>';

async function queued(r) {
  toast(Array.isArray(r.queued) ? `${r.queued.length} comandos na fila` : `Na fila: ${r.command}`);
  refreshPills();
}

// ---------------- Status ----------------
async function refreshPills() {
  try {
    const s = await api('/status');
    const cmds = await api('/commands');
    const pending = cmds.filter((c) => c.status === 'pending').length;
    const pill = (label, on, wait) => `<span class="pill ${on ? 'on' : wait ? 'wait' : 'off'}">${label}</span>`;
    $('#statusPills').innerHTML = pill('Banco', s.mariadb) + pill('Login', s.login) + pill(s.gameStarting ? 'Jogo carregando…' : 'Jogo', s.game, s.gameStarting)
      + (pending ? `<span class="pill wait">${pending} na fila</span>` : '');
    return s;
  } catch { $('#statusPills').innerHTML = '<span class="pill off">Painel sem resposta</span>'; }
}
setInterval(refreshPills, 5000);

// ---------------- Inicio ----------------
const RATE_FIELDS = [
  ['system.server.game.rate.xp', 'XP'], ['system.server.game.rate.drop', 'Drop'], ['system.server.game.rate.kamas', 'Kamas'],
  ['system.server.game.rate.job', 'XP de profissão'], ['system.server.game.rate.honor', 'Honra'], ['system.server.game.rate.fm', 'Forjamagia'],
  ['system.server.game.start.level', 'Nível inicial'], ['system.server.game.start.kamas', 'Kamas iniciais'], ['system.server.game.timeByTurn', 'Segundos por turno'],
];

async function viewHome() {
  const s = await refreshPills() || {};
  const cfg = s.config || {};
  main.innerHTML = `
  <div class="grid">
    <div class="card">
      <h2>Servidor</h2>
      <div class="row">
        <button class="btn primary" data-srv="all/start">Ligar tudo</button>
        <button class="btn" data-srv="all/stop">Desligar tudo</button>
        <button class="btn" data-srv="game/restart">Reiniciar jogo</button>
        <button class="btn" id="btnSave">Salvar agora</button>
      </div>
      <p class="note">Ordem: Banco → Login → Jogo. O jogo leva 1–2 minutos para carregar o mundo. "Desligar" salva tudo antes de fechar.</p>
      <h3>Jogar</h3>
      <div class="row"><label>Quantos clientes</label></div>
      <div class="row"><input type="number" id="nClients" value="8" min="1" max="8"><button class="btn primary" id="btnClients">Abrir clientes</button></div>
      <p class="note">Cada janela é um cliente Dofus. Faça login com <b>conta1</b> … <b>conta8</b> (crie na aba Contas). O servidor aparece como <b>Eratz</b>.</p>
    </div>
    <div class="card">
      <h2>Rates e regras</h2>
      <div class="statgrid">
        ${RATE_FIELDS.map(([k, l]) => `<div><label>${l}</label><input data-cfg="${k}" value="${esc(cfg[k] ?? '')}"></div>`).join('')}
        <div><label>Nível máximo</label><input id="levelCap" type="number" min="200" max="2000" value="${s.levelCap || 200}"></div>
        <div><label>Todos os zaaps</label><select data-cfg="system.server.game.allZaap"><option ${cfg['system.server.game.allZaap'] === 'true' ? 'selected' : ''}>true</option><option ${cfg['system.server.game.allZaap'] !== 'true' ? 'selected' : ''}>false</option></select></div>
        <div><label>Todas as emotes</label><select data-cfg="system.server.game.allEmotes"><option ${cfg['system.server.game.allEmotes'] === 'true' ? 'selected' : ''}>true</option><option ${cfg['system.server.game.allEmotes'] !== 'true' ? 'selected' : ''}>false</option></select></div>
      </div>
      <div class="row" style="margin-top:12px"><button class="btn primary" id="btnCfg">Salvar e reiniciar o jogo</button><button class="btn" id="btnCfgOnly">Só salvar</button></div>
      <p class="note">Rates multiplicam o ganho normal (ex.: XP 10 = dez vezes mais rápido). Nível máximo acima de 200 usa uma tabela de XP estendida.</p>
    </div>
  </div>
  <div class="card">
    <h2>Modo escravo (seguir o líder)</h2>
    <p class="note">Escolha o personagem que você vai comandar. Todos os outros personagens online entram no grupo dele e passam a <b>seguir</b>: andam junto, trocam de mapa junto, usam zaap junto e <b>entram nas lutas dele</b> automaticamente. Todos precisam estar online.</p>
    <div class="row"><label>Líder</label><select id="msLeader"></select>
      <button class="btn primary" id="msOn">Ligar modo escravo</button><button class="btn" id="msOff">Desligar</button></div>
    <div class="row"><label>Seguidor</label><select id="msFollower"></select><button class="btn" id="msPass">Liga/desliga passar turno automático</button></div>
    <p class="note">Na luta, o turno de cada seguidor ainda é jogado na janela dele. Se quiser que um seguidor só acompanhe (sem jogar), ligue "passar turno automático" para ele. Dentro do jogo também funciona digitando <code>.maitre</code> no chat do líder.</p>
  </div>
  <div class="card">
    <div class="row"><h2 style="margin:0">Logs</h2>
      <select id="logSel"><option value="game">Jogo</option><option value="login">Login</option><option value="mariadb">Banco</option></select>
      <button class="btn small" id="btnLog">Atualizar</button></div>
    <pre class="log" id="logBox"></pre>
  </div>`;

  $$('[data-srv]').forEach((b) => (b.onclick = run(async () => {
    const [t, a] = b.dataset.srv.split('/');
    b.disabled = true; toast('Aguarde…');
    try { const r = await api(`/server/${t}/${a}`, 'POST'); toast(Object.entries(r).map(([k, v]) => `${k}: ${v}`).join(' · ')); }
    finally { b.disabled = false; refreshPills(); }
  })));
  $('#btnSave').onclick = run(async () => { await api('/server/save', 'POST'); toast('Salvamento pedido ao servidor'); });
  $('#btnClients').onclick = run(async () => { const r = await api('/clients/open', 'POST', { count: +$('#nClients').value }); toast(`Abrindo ${r.opened} cliente(s)…`); });
  const saveCfg = async (restart) => {
    const config = {};
    $$('[data-cfg]').forEach((i) => (config[i.dataset.cfg] = i.value));
    const r = await api('/config', 'POST', { config, levelCap: +$('#levelCap').value });
    if (restart) { toast('Reiniciando o jogo…'); await api('/server/game/restart', 'POST'); toast('Jogo reiniciando, aguarde carregar'); }
    else toast(r.note);
  };
  $('#btnCfg').onclick = run(() => saveCfg(true));
  $('#btnCfgOnly').onclick = run(() => saveCfg(false));
  loadPlayers().then((ps) => {
    const opts = ps.map((p) => `<option value="${p.id}">${esc(p.name)} (${esc(p.className)} ${p.level})${p.logged ? ' · online' : ''}</option>`).join('');
    $('#msLeader').innerHTML = opts; $('#msFollower').innerHTML = opts;
  });
  $('#msOn').onclick = run(async () => queued(await api(`/players/${$('#msLeader').value}/action`, 'POST', { action: 'master', on: true })));
  $('#msOff').onclick = run(async () => queued(await api(`/players/${$('#msLeader').value}/action`, 'POST', { action: 'master', on: false })));
  $('#msPass').onclick = run(async () => queued(await api(`/players/${$('#msFollower').value}/action`, 'POST', { action: 'autopass' })));
  const loadLog = run(async () => { $('#logBox').textContent = (await api('/logs/' + $('#logSel').value)).text || '(vazio)'; $('#logBox').scrollTop = 1e9; });
  $('#btnLog').onclick = loadLog; $('#logSel').onchange = loadLog; loadLog();
}

// ---------------- Contas ----------------
async function viewAccounts() {
  const accounts = await api('/accounts');
  main.innerHTML = `
  <div class="grid">
    <div class="card">
      <h2>Criar contas</h2>
      <div class="row">
        <div><label>Prefixo</label><input id="accPrefix" value="conta"></div>
        <div><label>Quantidade</label><input id="accCount" type="number" value="8" min="1" max="20"></div>
        <div><label>Começar em</label><input id="accStart" type="number" value="1" min="1"></div>
        <div><label>Senha (igual para todas)</label><input id="accPass" value="123"></div>
      </div>
      <div class="row"><button class="btn primary" id="btnAcc">Criar</button></div>
      <p class="note">Cria conta1, conta2, … Contas que já existem são puladas. Todo personagem novo já nasce GM (acesso a todos os comandos).</p>
    </div>
  </div>
  <div class="card"><h2>Contas</h2>
    <table><tr><th>Login</th><th>Personagens</th><th></th></tr>
    ${accounts.map((a) => `<tr><td><b>${esc(a.account)}</b><div class="note">#${a.guid}</div></td>
      <td>${a.players.map((p) => `<span class="tag">${esc(p.name)} · ${esc(p.className)} ${p.level}</span>`).join('') || '<span class="note">nenhum</span>'}</td>
      <td class="num"><button class="btn small" data-pass="${a.guid}">Trocar senha</button></td></tr>`).join('')}
    </table></div>`;
  $('#btnAcc').onclick = run(async () => {
    const r = await api('/accounts', 'POST', { prefix: $('#accPrefix').value, count: +$('#accCount').value, start: +$('#accStart').value, password: $('#accPass').value });
    toast(r.created.length ? `Criadas: ${r.created.join(', ')}` : 'Nenhuma conta nova (já existiam)');
    viewAccounts();
  });
  $$('[data-pass]').forEach((b) => (b.onclick = run(async () => {
    const pass = prompt('Nova senha:');
    if (pass) { await api(`/accounts/${b.dataset.pass}/password`, 'POST', { password: pass }); toast('Senha alterada'); }
  })));
}

// ---------------- Personagens ----------------
async function viewPlayers() {
  const players = await loadPlayers();
  main.innerHTML = `<div class="card"><h2>Personagens</h2>
    ${players.length ? '' : '<p class="note">Nenhum personagem ainda. Entre no jogo com uma conta e crie um.</p>'}
    <table><tr><th>Nome</th><th>Classe</th><th class="num">Nível</th><th class="num">Kamas</th><th class="num">Itens</th><th>GM</th><th>Online</th></tr>
    ${players.map((p) => `<tr class="click" data-p="${p.id}"><td><b>${esc(p.name)}</b></td><td>${esc(p.className)}</td><td class="num">${p.level}</td>
      <td class="num">${fmt(p.kamas)}</td><td class="num">${p.itemCount}</td><td>${p.groupe > 0 ? '<span class="tag good">GM</span>' : ''}</td><td>${p.logged ? '<span class="tag good">online</span>' : ''}</td></tr>`).join('')}
    </table></div><div id="playerDetail"></div>`;
  $$('[data-p]').forEach((tr) => (tr.onclick = () => viewPlayer(+tr.dataset.p)));
}

async function viewPlayer(id) {
  const p = await api('/players/' + id);
  const box = $('#playerDetail');
  box.innerHTML = `
  <div class="card">
    <h2>${esc(p.name)} <span class="muted">${esc(p.className)} · nível ${p.level} · ${fmt(p.kamas)} kamas · capital ${p.capital} · pontos de feitiço ${p.spellboost}</span></h2>
    ${onlineNote}
    <div class="grid" style="margin-top:12px">
      <div>
        <h3>Progresso</h3>
        <div class="row"><input type="number" id="aLevel" value="${Math.max(p.level, 200)}"><button class="btn" data-act="level">Definir nível</button></div>
        <div class="row"><input type="number" id="aKamas" value="1000000"><button class="btn" data-act="kamas">Dar kamas</button></div>
        <div class="row"><input type="number" id="aCapital" value="100"><button class="btn" data-act="capital">Dar capital</button></div>
        <div class="row"><input type="number" id="aSpellPts" value="50"><button class="btn" data-act="spellpoints">Dar pontos de feitiço</button></div>
      </div>
      <div>
        <h3>Feitiços</h3>
        <div class="row"><label>Grau</label><select id="aSpellLvl">${[6, 5, 4, 3, 2, 1].map((l) => `<option>${l}</option>`).join('')}</select></div>
        <div class="row"><button class="btn primary" data-act="classSpells">Todos da classe</button><button class="btn" data-act="allSpells">Todos de todas as classes</button></div>
        <p class="note">Para escolher feitiços um a um, use a aba Feitiços.</p>
        <h3>Barra de feitiços por raça</h3>
        <div class="row"><select id="aBarClass">${['Feca', 'Osamodas', 'Enutrof', 'Sram', 'Xelor', 'Ecaflip', 'Eniripsa', 'Iop', 'Cra', 'Sadida', 'Sacrier', 'Pandawa'].map((n, i) => `<option value="${i + 1}">${n}</option>`).join('')}</select><button class="btn" data-act="bar">Montar barra</button></div>
        <p class="note">Coloca na barra os feitiços daquela raça que o personagem já sabe (ideal para o LabTech). No jogo: <b>.raca iop</b>.</p>
        <h3>Profissões</h3>
        <div class="row"><select id="aJob"></select></div>
        <div class="row"><button class="btn" data-act="job">Aprender</button><input type="number" id="aJobXp" value="600000"><button class="btn" data-act="jobxp">Dar XP</button></div>
      </div>
      <div>
        <h3>Outros</h3>
        <div class="row"><button class="btn" data-act="gm">Tornar GM (grupo 1)</button></div>
        <div class="row"><input id="aRaw" placeholder="ex.: TP 7411 311" class="wide"></div>
        <div class="row"><button class="btn" data-act="raw">Enviar comando GM</button></div>
        <h3>Feitiços atuais (${p.spells.length})</h3>
        <div class="list" style="max-height:160px">${p.spells.map((s) => `<span class="tag">${esc(s.name)} ${s.level}</span>`).join('')}</div>
        ${p.jobs.length ? `<h3>Profissões atuais</h3>${p.jobs.map((j) => `<span class="tag">${esc(j.name)}</span>`).join('')}` : ''}
      </div>
    </div>
  </div>
  <div class="card"><div class="row"><h2 style="margin:0">Inventário</h2><button class="btn small" id="btnInv">Atualizar</button></div>
    <p class="note">O inventário mostrado vem do último salvamento. Para ver mudanças recentes, clique em "Salvar agora" no Início.</p>
    <div id="inv"></div></div>`;
  box.scrollIntoView({ behavior: 'smooth' });

  api('/jobs').then((jobs) => { $('#aJob').innerHTML = jobs.map((j) => `<option value="${j.id}">${esc(j.name)}</option>`).join(''); });
  const act = async (body) => queued(await api(`/players/${id}/action`, 'POST', body));
  const map = {
    level: () => act({ action: 'level', level: +$('#aLevel').value }),
    kamas: () => act({ action: 'kamas', amount: +$('#aKamas').value }),
    capital: () => act({ action: 'capital', amount: +$('#aCapital').value }),
    spellpoints: () => act({ action: 'spellpoints', amount: +$('#aSpellPts').value }),
    classSpells: () => act({ action: 'classSpells', scope: 'class', level: +$('#aSpellLvl').value }),
    allSpells: () => act({ action: 'classSpells', scope: 'all', level: +$('#aSpellLvl').value }),
    bar: () => act({ action: 'bar', classe: +$('#aBarClass').value }),
    job: () => act({ action: 'job', job: +$('#aJob').value }),
    jobxp: () => act({ action: 'jobxp', job: +$('#aJob').value, xp: +$('#aJobXp').value }),
    gm: () => act({ action: 'gm', group: 1 }),
    raw: () => act({ action: 'raw', command: $('#aRaw').value }),
  };
  $$('[data-act]', box).forEach((b) => (b.onclick = run(map[b.dataset.act])));
  const loadInv = run(async () => {
    const inv = await api(`/players/${id}/inventory`);
    $('#inv').innerHTML = inv.length ? `<table><tr><th>Item</th><th>Tipo</th><th class="num">Qtd</th><th>Atributos</th><th></th></tr>
      ${inv.map((o) => `<tr><td><b>${esc(o.name)}</b>${o.equipped ? ' <span class="tag good">equipado</span>' : ''}<div class="note">#${o.id}</div></td><td>${esc(o.typeName)}</td>
      <td class="num">${o.quantity}</td><td>${o.lines.map((l) => `<span class="tag">${esc(l)}</span>`).join('')}</td>
      <td><button class="btn small" data-edit="${o.id}">Editar atributos</button></td></tr>`).join('')}</table>` : '<p class="note">Inventário vazio (ou ainda não salvo).</p>';
    $$('[data-edit]').forEach((b) => (b.onclick = run(() => statsEditor({ mode: 'object', objectId: +b.dataset.edit, playerId: id }))));
  });
  $('#btnInv').onclick = loadInv; loadInv();
}

// ---------------- Editor de atributos ----------------
let statsDef = null;
async function statsEditor({ mode, objectId, playerId, template }) {
  statsDef ||= await api('/stats');
  let values = {}, others = [], title = '', maxValues = {};
  if (mode === 'object') {
    const o = await api('/objects/' + objectId);
    values = o.values; others = o.others; title = `${o.name} (#${o.id})`;
    const it = await api('/items/' + o.template); maxValues = it.template?.max || {};
  } else {
    const it = await api('/items/' + template);
    title = it.name; maxValues = it.template?.max || {};
    values = { ...maxValues }; others = it.template?.others || [];
  }
  await loadPlayers();
  const groups = [...new Set(statsDef.map((s) => s.group))];
  const body = modal(`
    <h2>${mode === 'template' ? 'Editar modelo: ' : mode === 'create' ? 'Criar item: ' : 'Atributos: '}${esc(title)}</h2>
    ${mode === 'template' ? '<div class="warnbox">Modo <b>modelo</b>: muda o item para todos os drops/crafts futuros (depois de reiniciar o jogo). Itens que já existem não mudam.</div>' : ''}
    ${mode === 'create' ? `<div class="row"><label>Para</label>${playerSelect('stPlayer', playerId)}<label>Qtd</label><input type="number" id="stQty" value="1" min="1"></div>` : ''}
    <div class="row" style="margin:8px 0">
      <button class="btn small" data-pre="pa">+1 PA</button><button class="btn small" data-pre="pm">+1 PM</button>
      <button class="btn small" data-pre="po">+1 Alcance</button><button class="btn small" data-pre="max">Stats máximos do item</button>
      <button class="btn small" data-pre="zero">Zerar</button>
    </div>
    ${groups.map((g) => `<h3>${g}</h3><div class="statgrid">${statsDef.filter((s) => s.group === g).map((s) =>
      `<div><label>${esc(s.label)}</label><input type="number" data-stat="${s.id}" value="${values[s.id] || ''}" placeholder="0"></div>`).join('')}</div>`).join('')}
    ${others.length ? `<h3>Outros efeitos (mantidos)</h3>${others.map((o, i) => `<label style="display:flex;gap:6px;align-items:center;color:var(--ink)"><input type="checkbox" data-other="${i}" checked> ${esc(o.text)}</label>`).join('')}` : ''}
    <h3>Prévia</h3><div id="stPreview" class="note"></div><div id="stWarn"></div>
    <div class="row" style="margin-top:12px"><button class="btn primary" id="stSave">${mode === 'template' ? 'Salvar modelo' : mode === 'create' ? 'Criar e enviar' : 'Aplicar no item'}</button></div>
    ${mode !== 'template' ? onlineNote : ''}`);

  const read = () => {
    const v = {};
    $$('[data-stat]', body).forEach((i) => { if (+i.value) v[i.dataset.stat] = +i.value; });
    const keep = others.filter((_, i) => $(`[data-other="${i}"]`, body)?.checked);
    return { values: v, others: keep };
  };
  const preview = debounce(run(async () => {
    const r = await api('/stats/preview', 'POST', read());
    $('#stPreview', body).innerHTML = r.lines.map((l) => `<span class="tag">${esc(l)}</span>`).join('') || '(sem atributos)';
    const big = Object.entries(read().values).some(([id, v]) => Math.abs(v) > ([111, 128, 117, 182].includes(+id) ? 12 : 5000));
    $('#stWarn', body).innerHTML = big ? '<div class="warnbox">Valores muito altos podem aparecer estranhos no cliente ou desequilibrar lutas. Funciona, mas teste.</div>' : '';
  }), 200);
  $$('input', body).forEach((i) => i.addEventListener('input', preview));
  const setVal = (id, fn) => { const i = $(`[data-stat="${id}"]`, body); i.value = fn(+i.value || 0) || ''; };
  $$('[data-pre]', body).forEach((b) => (b.onclick = () => {
    const k = b.dataset.pre;
    if (k === 'pa') setVal(111, (v) => v + 1);
    if (k === 'pm') setVal(128, (v) => v + 1);
    if (k === 'po') setVal(117, (v) => v + 1);
    if (k === 'max') $$('[data-stat]', body).forEach((i) => (i.value = maxValues[i.dataset.stat] || ''));
    if (k === 'zero') $$('[data-stat]', body).forEach((i) => (i.value = ''));
    preview();
  }));
  preview();
  $('#stSave', body).onclick = run(async () => {
    const data = read();
    if (mode === 'object') queued(await api(`/players/${playerId}/action`, 'POST', { action: 'setstats', object: objectId, ...data }));
    else if (mode === 'create') queued(await api(`/players/${$('#stPlayer', body).value}/action`, 'POST', { action: 'item', template, qty: +$('#stQty', body).value, ...data }));
    else { const r = await api(`/items/${template}/template-stats`, 'POST', data); toast(r.note); }
    closeModal();
  });
}

// ---------------- Itens, sets e kits ----------------
let kitDraft = [];
async function viewItems() {
  await loadPlayers();
  const types = await api('/itemtypes');
  main.innerHTML = `
  <div class="card">
    <h2>Itens</h2>
    <div class="row"><input id="iq" class="wide" placeholder="Buscar item pelo nome (ex.: gelano, coruja, dofus)" style="flex:1">
      <select id="it"><option value="">Todos os tipos</option>${types.map((t) => `<option value="${t.id}">${esc(t.name)}</option>`).join('')}</select></div>
    <div id="iRes" class="list" style="margin-top:8px"></div>
  </div>
  <div class="grid">
    <div class="card"><h2>Conjuntos (sets)</h2>
      <div class="row"><input id="sq" placeholder="Buscar conjunto" style="flex:1"></div>
      <div class="row"><label>Para</label>${playerSelect('sPlayer')}<label><input type="checkbox" id="sMax" checked> stats máximos</label></div>
      <div id="sRes" class="list" style="margin-top:8px"></div></div>
    <div class="card"><h2>Kits favoritos</h2>
      <div id="kitDraft"></div>
      <div id="kits"></div></div>
  </div>`;
  const search = debounce(run(async () => {
    const r = await api(`/items?q=${encodeURIComponent($('#iq').value)}&type=${$('#it').value}`);
    $('#iRes').innerHTML = `<table><tr><th>Item</th><th>Tipo</th><th class="num">Nível</th></tr>
      ${r.map((i) => `<tr class="click" data-item="${i.id}"><td><b>${esc(i.name)}</b> <span class="note">#${i.id}</span></td><td>${esc(i.typeName)}</td><td class="num">${i.level ?? ''}</td></tr>`).join('')}</table>`;
    $$('[data-item]').forEach((tr) => (tr.onclick = run(() => itemModal(+tr.dataset.item))));
  }));
  $('#iq').oninput = search; $('#it').onchange = search;
  const sets = debounce(run(async () => {
    const r = await api(`/sets?q=${encodeURIComponent($('#sq').value)}`);
    $('#sRes').innerHTML = r.map((s) => `<div class="row" style="justify-content:space-between;border-bottom:1px solid var(--line);padding:6px 0">
      <div><b>${esc(s.name)}</b> <span class="note">nível ${s.level} · ${s.items.length} peças</span><div class="note">${s.items.map((i) => esc(i.name)).join(', ')}</div></div>
      <button class="btn small primary" data-set="${s.id}">Dar</button></div>`).join('');
    $$('[data-set]').forEach((b) => (b.onclick = run(async () => queued(await api(`/players/${$('#sPlayer').value}/action`, 'POST', { action: 'itemset', set: +b.dataset.set, max: $('#sMax').checked })))));
  }));
  $('#sq').oninput = sets; sets(); search();
  renderKits();
}

async function renderKits() {
  if (!$('#kits')) return;
  $('#kitDraft').innerHTML = kitDraft.length ? `<h3>Kit em montagem</h3>${kitDraft.map((k, i) => `<span class="tag">${esc(k.name)} ×${k.qty}${k.max ? ' (máx)' : ''} <a href="#" data-rm="${i}">×</a></span>`).join('')}
    <div class="row"><input id="kitName" placeholder="Nome do kit"><button class="btn primary small" id="kitSave">Salvar kit</button></div>` : '<p class="note">Abra um item e clique em "Adicionar ao kit" para montar um kit.</p>';
  $$('[data-rm]').forEach((a) => (a.onclick = (e) => { e.preventDefault(); kitDraft.splice(+a.dataset.rm, 1); renderKits(); }));
  if ($('#kitSave')) $('#kitSave').onclick = run(async () => {
    await api('/kits', 'POST', { name: $('#kitName').value || 'Kit', items: kitDraft });
    kitDraft = []; toast('Kit salvo'); renderKits();
  });
  const kits = await api('/kits');
  $('#kits').innerHTML = kits.length ? `<h3>Salvos</h3><div class="row"><label>Para</label>${playerSelect('kPlayer')}</div>` + kits.map((k) => `<div class="row" style="justify-content:space-between;border-bottom:1px solid var(--line);padding:6px 0">
    <div><b>${esc(k.name)}</b><div class="note">${k.items.map((i) => `${esc(i.name)} ×${i.qty}`).join(', ')}</div></div>
    <div><button class="btn small primary" data-kit="${k.id}">Dar</button> <button class="btn small danger" data-kdel="${k.id}">Apagar</button></div></div>`).join('') : '';
  $$('[data-kit]').forEach((b) => (b.onclick = run(async () => queued(await api(`/players/${$('#kPlayer').value}/action`, 'POST', { action: 'kit', kit: +b.dataset.kit })))));
  $$('[data-kdel]').forEach((b) => (b.onclick = run(async () => { if (confirm('Apagar kit?')) { await api('/kits/' + b.dataset.kdel, 'DELETE'); renderKits(); } })));
}

async function itemModal(id) {
  const it = await api('/items/' + id);
  await loadPlayers();
  const rate = +(await api('/config')).config['system.server.game.rate.drop'] || 1;
  const body = modal(`
    <h2>${esc(it.name)} <span class="muted">#${it.id} · ${esc(it.typeName)} · nível ${it.level ?? '?'}</span></h2>
    <p class="note">${esc(it.description || '')}</p>
    ${it.template?.lines?.length ? `<div>${it.template.lines.map((l) => `<span class="tag">${esc(l)}</span>`).join('')}</div>` : ''}
    ${it.conditions ? `<p class="note">Condições: ${esc(it.conditions)}</p>` : ''}
    <h3>Dar para um personagem</h3>
    <div class="row">${playerSelect('imPlayer')}<label>Qtd</label><input type="number" id="imQty" value="1" min="1"><label><input type="checkbox" id="imMax" checked> stats máximos</label>
      <button class="btn primary" id="imGive">Dar</button></div>
    <div class="row"><button class="btn" id="imCustom">Dar com atributos personalizados…</button><button class="btn" id="imTpl">Editar modelo do item…</button><button class="btn" id="imKit">Adicionar ao kit</button></div>
    ${it.set ? `<h3>Conjunto: ${esc(it.set.name)}</h3><div>${it.set.items.map((i) => `<span class="tag">${esc(i.name)}</span>`).join('')}</div>` : ''}
    ${it.recipe ? `<h3>Receita</h3><div>${it.recipe.map((r) => `<span class="tag">${r.qty}× ${esc(r.name)}</span>`).join('')}</div>` : ''}
    <h3>Quem dropa (rate atual ×${rate})</h3>
    ${it.drops.length ? `<table><tr><th>Monstro</th><th class="num">Chance base (grau 1→5)</th><th class="num">Com a rate</th><th class="num">Prospecção mínima</th></tr>
      ${it.drops.map((d) => `<tr><td>${esc(d.monsterNamePt)}</td><td class="num">${[1, 2, 3, 4, 5].map((g) => (+d['percentGrade' + g]).toFixed(2)).join(' / ')}%</td>
      <td class="num">${Math.min(100, d.percentGrade1 * rate).toFixed(2)}%–${Math.min(100, d.percentGrade5 * rate).toFixed(2)}%</td><td class="num">${d.ceil || '-'}</td></tr>`).join('')}</table>` : '<p class="note">Nenhum monstro dropa este item (pode vir de craft, loja ou missão).</p>'}
    ${it.usedIn.length ? `<h3>Usado em</h3><div>${it.usedIn.map((u) => `<span class="tag">${esc(u.name)}</span>`).join('')}</div>` : ''}`);
  $('#imGive', body).onclick = run(async () => queued(await api(`/players/${$('#imPlayer', body).value}/action`, 'POST', { action: 'item', template: id, qty: +$('#imQty', body).value, max: $('#imMax', body).checked })));
  $('#imCustom', body).onclick = run(() => statsEditor({ mode: 'create', template: id, playerId: +$('#imPlayer', body).value }));
  $('#imTpl', body).onclick = run(() => statsEditor({ mode: 'template', template: id }));
  $('#imKit', body).onclick = () => { kitDraft.push({ template: id, name: it.name, qty: +$('#imQty', body).value || 1, max: $('#imMax', body).checked }); toast('Adicionado ao kit (veja em Itens e sets)'); renderKits(); };
}

// ---------------- Feiticos ----------------
async function viewSpells() {
  await loadPlayers();
  const classes = await api('/spells/classes');
  main.innerHTML = `
  <div class="card">
    <h2>Ensinar feitiços (de qualquer classe)</h2>
    <div class="row"><label>Personagem</label>${playerSelect('spPlayer')}<label>Grau</label><select id="spLvl">${[6, 5, 4, 3, 2, 1].map((l) => `<option>${l}</option>`).join('')}</select>
      <button class="btn primary" id="spTeach">Ensinar selecionados (<span id="spCount">0</span>)</button>
      <button class="btn" id="spClear">Limpar seleção</button></div>
    ${onlineNote}
    <p class="note">Depois de aprender, arraste o feitiço do livro de feitiços para a barra dentro do jogo. Grau 6 = nível máximo do feitiço.</p>
  </div>
  <div class="grid">${classes.map((c) => `<div class="card"><div class="row" style="justify-content:space-between"><h3 style="margin:0">${esc(c.className)}</h3>
    <button class="btn small" data-all="${c.classId}">Marcar todos</button></div>
    ${c.spells.map((s) => `<label style="display:flex;gap:6px;align-items:center;color:var(--ink);margin:3px 0"><input type="checkbox" data-sp="${s.id}" data-cls="${c.classId}">
      ${esc(s.name)} <span class="note">${s.learnLevel ? 'nv ' + s.learnLevel : 'especial'}</span></label>`).join('')}</div>`).join('')}</div>`;
  const count = () => ($('#spCount').textContent = $$('[data-sp]:checked').length);
  $$('[data-sp]').forEach((i) => (i.onchange = count));
  $$('[data-all]').forEach((b) => (b.onclick = () => { $$(`[data-cls="${b.dataset.all}"]`).forEach((i) => (i.checked = true)); count(); }));
  $('#spClear').onclick = () => { $$('[data-sp]').forEach((i) => (i.checked = false)); count(); };
  $('#spTeach').onclick = run(async () => {
    const ids = $$('[data-sp]:checked').map((i) => +i.dataset.sp);
    queued(await api(`/players/${$('#spPlayer').value}/action`, 'POST', { action: 'spells', ids, level: +$('#spLvl').value }));
  });
}

// ---------------- Monstros e drops ----------------
async function viewMonsters() {
  main.innerHTML = `<div class="card"><h2>Monstros e drops</h2>
    <div class="row"><input id="mq" placeholder="Buscar monstro (ex.: papatudo, tofu, dragão porco)" style="flex:1"></div>
    <div id="mRes" class="list" style="margin-top:8px"></div></div><div id="mDetail"></div>`;
  const search = debounce(run(async () => {
    const r = await api('/monsters?q=' + encodeURIComponent($('#mq').value));
    $('#mRes').innerHTML = `<table><tr><th>Monstro</th><th>Níveis</th></tr>${r.map((m) => `<tr class="click" data-m="${m.id}"><td><b>${esc(m.name)}</b> <span class="note">#${m.id}</span></td><td>${m.levels.join(', ')}</td></tr>`).join('')}</table>`;
    $$('[data-m]').forEach((tr) => (tr.onclick = run(() => monsterDetail(+tr.dataset.m))));
  }));
  $('#mq').oninput = search; search();
}

async function monsterDetail(id) {
  const m = await api('/monsters/' + id);
  const box = $('#mDetail');
  box.innerHTML = `<div class="card">
    <h2>${esc(m.name)} <span class="muted">#${m.id}${m.kamas ? ` · ${m.kamas[0]}–${m.kamas[1]} kamas` : ''}</span></h2>
    <div class="grid">
      <div><h3>Graus</h3><table><tr><th>Grau</th><th class="num">Nível</th><th class="num">Vida</th><th class="num">PA</th><th class="num">PM</th></tr>
        ${m.grades.map((g) => `<tr><td>${g.grade}</td><td class="num">${g.level}</td><td class="num">${g.life ?? ''}</td><td class="num">${g.ap ?? ''}</td><td class="num">${g.mp ?? ''}</td></tr>`).join('')}</table></div>
      <div><h3>Onde encontrar</h3>${m.subAreas.length ? m.subAreas.map((s) => `<span class="tag">${esc(s.name)}${s.area ? ' · ' + esc(s.area) : ''}</span>`).join('') : '<p class="note">Sem subárea conhecida (pode ser de masmorra ou invocação).</p>'}</div>
    </div>
    <h3>Drops</h3>
    <div class="row"><label>Sua prospecção</label><input type="number" id="mPros" value="100"><span class="note">Rate de drop atual: ×${m.rates.drop}. Chance final = % do grau × (prospecção ÷ 100) × rate.</span></div>
    <table id="dropTable"><tr><th>Item</th><th class="num">G1 %</th><th class="num">G2 %</th><th class="num">G3 %</th><th class="num">G4 %</th><th class="num">G5 %</th><th class="num">Prosp. mín.</th><th class="num">Chance real (G1–G5)</th><th></th></tr>
      ${m.drops.map((d) => `<tr data-obj="${d.objectId}"><td><b>${esc(d.itemName)}</b></td>
        ${[1, 2, 3, 4, 5].map((g) => `<td class="num"><input type="number" step="0.01" style="width:70px" data-g="${g}" value="${+d['percentGrade' + g]}"></td>`).join('')}
        <td class="num"><input type="number" style="width:70px" data-ceil value="${d.ceil}"></td><td class="num" data-real></td>
        <td><button class="btn small" data-dsave>Salvar</button> <button class="btn small danger" data-ddel>×</button></td></tr>`).join('')}
    </table>
    <h3>Adicionar drop</h3>
    <div class="row"><input id="dItemQ" placeholder="Buscar item"><select id="dItem"></select><label>%</label><input type="number" id="dPct" value="10" step="0.01"><button class="btn" id="dAdd">Adicionar</button></div>
    <p class="note">Mudanças de drop valem depois de reiniciar o servidor de jogo. Para aumentar tudo de uma vez, use a rate de drop no Início.</p>
  </div>`;
  box.scrollIntoView({ behavior: 'smooth' });
  const calc = () => {
    const pros = Math.max(1, (+$('#mPros').value || 100) / 100);
    $$('#dropTable tr[data-obj]').forEach((tr) => {
      const vals = $$('[data-g]', tr).map((i) => Math.min(100, (+i.value || 0) * pros * m.rates.drop));
      $('[data-real]', tr).textContent = `${vals[0].toFixed(1)}% – ${vals[4].toFixed(1)}%`;
    });
  };
  $('#mPros').oninput = calc; $$('#dropTable input').forEach((i) => (i.oninput = calc)); calc();
  $$('[data-dsave]').forEach((b) => (b.onclick = run(async () => {
    const tr = b.closest('tr');
    await api('/drops', 'POST', { monsterId: id, objectId: +tr.dataset.obj, percents: $$('[data-g]', tr).map((i) => +i.value), ceil: +$('[data-ceil]', tr).value });
    toast('Drop salvo (reinicie o jogo para aplicar)');
  })));
  $$('[data-ddel]').forEach((b) => (b.onclick = run(async () => {
    if (!confirm('Remover este drop?')) return;
    await api('/drops', 'DELETE', { monsterId: id, objectId: +b.closest('tr').dataset.obj }); monsterDetail(id);
  })));
  $('#dItemQ').oninput = debounce(run(async () => {
    const r = await api('/items?limit=30&q=' + encodeURIComponent($('#dItemQ').value));
    $('#dItem').innerHTML = r.map((i) => `<option value="${i.id}">${esc(i.name)}</option>`).join('');
  }));
  $('#dAdd').onclick = run(async () => {
    await api('/drops', 'PUT', { monsterId: id, objectId: +$('#dItem').value, percent: +$('#dPct').value });
    toast('Drop adicionado'); monsterDetail(id);
  });
}

// ---------------- Guia ----------------
const GUIDE_TABS = [['labtech', 'Mundo LabTech'], ['start', 'Começo rápido'], ['mounts', 'Montarias'], ['pets', 'Familiares'], ['jobs', 'Profissões'], ['drops', 'Drops'], ['gm', 'Comandos GM'], ['notes', 'Minhas anotações']];
let guideTab = 'labtech';
async function viewGuide() {
  main.innerHTML = `<div class="subtabs">${GUIDE_TABS.map(([k, l]) => `<button data-g="${k}" class="${k === guideTab ? 'active' : ''}">${l}</button>`).join('')}</div><div id="gBody" class="guide"></div>`;
  $$('[data-g]').forEach((b) => (b.onclick = () => { guideTab = b.dataset.g; viewGuide(); }));
  await run(GUIDE[guideTab])();
}

const GUIDE = {
  async labtech() {
    const w = await api('/labtech');
    await loadPlayers();
    $('#gBody').innerHTML = `<div class="card"><h2>Mundo LabTech</h2>
    <p><b>Enquanto os outros nasciam abençoados pelos deuses, os LabTechs nasciam curiosos demais para aceitar que não tinham poderes.</b>
    Com jaleco, cerveja e teimosia, construíram a <b>Manopla Gambiarra</b>, capaz de canalizar os poderes das 12 classes. Ninguém sabe como funciona. Nem eles. Mas funciona.</p>
    <p>A ilha fica a leste no mapa-múndi (perto da Ilha dos Wabbits). Todo personagem novo nasce no <b>Laboratório LabTech</b>. O <b>Estagiário</b> (o robozinho) leva você para qualquer lugar da ilha.</p>
    <h3>Como ganhar os poderes das 12 classes (sem trapaça)</h3><ol>
      <li>Fale com o <b>Mestre Malte</b> no Laboratório → "É perigoso ir sozinho?" → ganhe a <b>Manopla Mk I</b>.</li>
      <li>Derrote os 12 chefes e pegue os <b>12 núcleos</b>: Gobball Real, Wa Wabbit, Escarafeio Dourado, Rato Preto, Crackler Lendário, Rato Branco, Mob Esponja, Minotororo, Lorde Corvo, Treechnid Ancestral, Vlad Sombrio, Tanukouï San.</li>
      <li>Volte ao Mestre Malte → encaixe os núcleos → <b>Manopla Mk XII</b> (+1 PA, alcance 2).</li>
      <li>Leve 10 Malte, 10 Lúpulo e 10 Levedura → ele forja o <b>Dofus Fermentado</b> (+1 PA, +1 PM, +100 em cada atributo, 50% de resistência a tudo, +1000 em críticos).</li></ol>
    <p>Os <b>feitiços das 12 classes</b> chegam pelo nível, nos mesmos níveis de cada classe (graus 1 a 5 no nível em que liberam, grau 6 cem níveis depois). No livro de feitiços o nome mostra o nível: <i>Escudo Feca (nv. 80)</i>.</p>
    <p class="note">Código secreto: no Laboratório, digite no chat <code>.cima cima baixo baixo esquerda direita esquerda direita b a</code>. Cervejas: alambique da Oficina (Alquimista) ou Taverneiro Barril.</p>
    <h3>Atalhos (GM)</h3>
    <div class="row">${playerSelect('ltPlayer')}<button class="btn primary" id="ltTp">Teleportar para o Laboratório</button>
      <button class="btn" id="ltKit">Dar kit LabTech completo</button></div>
    <p class="note">Kit = Manopla Mk XII, Dofus Fermentado, Drone de IA, Conjunto Jaleco (6 peças) e 10 de cada cerveja. Os feitiços vêm pelo nível.</p>
    <h3>Mapas</h3>
    <table><tr><th>Mapa</th><th>Coordenadas</th><th>NPCs</th><th></th></tr>
    ${w.maps.map((m) => `<tr><td><b>${esc(m.name)}</b> <span class="note">#${m.id}</span></td><td>${m.x},${m.y}</td><td class="note">${m.npcs.map(esc).join(', ')}</td>
      <td><button class="btn small" data-ltmap="${m.id}" data-ltcell="${m.landing}">Ir</button></td></tr>`).join('')}</table>
    <h3>Reconstruir</h3>
    <p class="note">Depois de editar <code>panel/world/labtech/content.py</code> (textos, NPCs, itens), reconstrua e reinicie o jogo.</p>
    <div class="row"><button class="btn" id="ltBuild">Reconstruir Mundo LabTech</button></div><pre class="log" id="ltLog" style="display:none"></pre></div>`;
    const pid = () => $('#ltPlayer').value;
    $('#ltTp').onclick = run(async () => queued(await api(`/players/${pid()}/labtech`, 'POST', { what: 'tp' })));
    $('#ltKit').onclick = run(async () => queued(await api(`/players/${pid()}/labtech`, 'POST', { what: 'kit' })));
    $$('[data-ltmap]').forEach((b) => (b.onclick = run(async () => queued(await api(`/players/${pid()}/labtech`, 'POST', { what: 'tp', map: +b.dataset.ltmap, cell: +b.dataset.ltcell })))));
    $('#ltBuild').onclick = run(async () => {
      $('#ltBuild').disabled = true; toast('Reconstruindo... (leva ~1 minuto)');
      try { const r = await api('/labtech/rebuild', 'POST'); $('#ltLog').style.display = ''; $('#ltLog').textContent = r.output; toast('Pronto. Reinicie o jogo no Início.'); }
      finally { $('#ltBuild').disabled = false; }
    });
  },

  async start() {
    $('#gBody').innerHTML = `<div class="card"><h2>Começo rápido</h2><ol>
      <li><b>Início → Ligar tudo.</b> Espere a bolinha "Jogo" ficar verde (1–2 min).</li>
      <li><b>Contas → Criar</b> 8 contas (conta1…conta8, senha 123).</li>
      <li><b>Início → Abrir clientes</b> (8). Em cada janela, entre com uma conta, escolha o servidor <b>Eratz</b> e crie o personagem.</li>
      <li>Com os personagens criados e <b>online</b>, vá em <b>Personagens</b>: defina nível, dê kamas, capital e feitiços.</li>
      <li>Em <b>Itens e sets</b>, dê conjuntos completos com stats máximos, ou crie itens com atributos personalizados.</li>
      <li>Todo personagem novo já é GM. Ações do painel funcionam com o personagem online; se estiver offline, ficam esperando na fila.</li>
    </ol>
    <h3>Dicas para jogar com 8 personagens</h3><ul>
      <li>Monte um grupo: um personagem convida os outros (clique no nome → Convidar para grupo). Em luta, todos entram pelo mesmo lado.</li>
      <li>Boa composição: 1–2 Eniripsa (cura), 1 Feca (proteção), 1 Sacrier ou Iop (dano corpo a corpo), 1 Cra (distância), 1 Enutrof (prospecção = mais drop), 1 Osamodas ou Sadida (invocações), 1 Xelor (tira PA dos inimigos).</li>
      <li>Com "Todos de todas as classes" (aba Feitiços), qualquer personagem pode ter cura, proteção e dano ao mesmo tempo.</li>
      <li>Use "Todos os zaaps" (Início) para viajar para qualquer lugar pelo zaap.</li>
    </ul></div>`;
  },

  async mounts() {
    const certs = await api('/items?type=97&limit=200');
    await loadPlayers();
    $('#gBody').innerHTML = `<div class="card"><h2>Montarias (Dragossauros)</h2>
    <h3>Jeito rápido neste servidor</h3>
    <p>Dê um <b>Certificado de montaria</b> ao personagem. O servidor cria o dragossauro já com todos os medidores no máximo e pronto para montar. No jogo: abra o inventário, clique com o botão direito no certificado e escolha montar/equipar, ou coloque-o no cercado.</p>
    <div class="row">${playerSelect('mtPlayer')}<select id="mtCert">${certs.map((c) => `<option value="${c.id}">${esc(c.name)}</option>`).join('')}</select><button class="btn primary" id="mtGive">Dar certificado</button></div>
    <h3>Como funciona o treino (regras deste servidor)</h3>
    <p>O dragossauro tem medidores: <b>Serenidade</b> (de −10.000 a 10.000), <b>Resistência</b>, <b>Amor</b> e <b>Maturidade</b> (até 10.000 cada), além de <b>Energia</b> e <b>Cansaço</b> (0 a 240). Você treina colocando objetos de cercado no cercado; cada vez que o dragossauro esbarra num objeto, o efeito é aplicado:</p>
    <table><tr><th>Objeto</th><th>Efeito</th><th>Só funciona se…</th></tr>
      <tr><td>Esbofeteador / Bofetador</td><td>Diminui a Serenidade</td><td>sempre</td></tr>
      <tr><td>Acalmador</td><td>Aumenta a Serenidade</td><td>sempre</td></tr>
      <tr><td>Lançador de Raios</td><td>Aumenta a Resistência</td><td>Serenidade <b>negativa</b></td></tr>
      <tr><td>Dragotraseiro</td><td>Aumenta o Amor</td><td>Serenidade <b>positiva</b></td></tr>
      <tr><td>Bebedouro</td><td>Aumenta a Maturidade</td><td>Serenidade entre −2.000 e 2.000</td></tr>
      <tr><td>Manjedoura</td><td>Tira 20 de Cansaço e dá Energia</td><td>sempre</td></tr></table>
    <ul>
      <li>Cada objeto usado soma +1 de Cansaço. Acima de 160 o ganho cai, e em 240 o dragossauro para de usar objetos. Use a Manjedoura para descansar.</li>
      <li><b>Montável</b> quando a Maturidade está no máximo e o Cansaço está abaixo de 240.</li>
      <li><b>Reprodução</b>: Amor ≥ 7.500, Resistência ≥ 7.500, Maturidade no máximo e nível ≥ 5. Cada dragossauro pode reproduzir até 20 vezes.</li>
      <li>Ordem sugerida: Bebedouro (maturidade, perto do zero) → Esbofeteador até ficar negativo → Lançador de Raios (resistência) → Acalmador até ficar positivo → Dragotraseiro (amor).</li>
      <li>A montaria ganha XP quando você dá parte do seu XP para ela (opção na ficha da montaria). Com XP alta no servidor isso é rápido.</li>
    </ul></div>`;
    $('#mtGive').onclick = run(async () => queued(await api(`/players/${$('#mtPlayer').value}/action`, 'POST', { action: 'item', template: +$('#mtCert').value, qty: 1 })));
  },

  async pets() {
    const pets = await api('/pets');
    $('#gBody').innerHTML = `<div class="card"><h2>Familiares (pets)</h2>
    <p>O familiar ganha atributos quando você o alimenta com a comida certa. Cada comida aumenta um atributo específico. Regras deste servidor (lidas do código):</p>
    <ul>
      <li><b>Cada refeição correta dá bônus</b> (aqui é 1 refeição por bônus; no oficial eram 3).</li>
      <li>Respeite o <b>intervalo mínimo</b> entre refeições. Se alimentar antes, ele fica <b>gordo</b>; se repetir gordo, perde vida.</li>
      <li>Se passar do <b>intervalo máximo</b> sem comer, ele fica <b>magro</b> e perde vida. Magro, você pode alimentar várias vezes seguidas para recuperar.</li>
      <li>O total de pontos tem limite (coluna "Máx."). Cada refeição soma o "Ganho".</li>
      <li>Familiar morto vira fantasma. Um GM pode ressuscitar com o comando <code>PETSRES</code> (id do item).</li>
    </ul>
    <div class="row"><input id="petQ" placeholder="Filtrar familiar ou comida" style="flex:1"></div>
    <div id="petList"></div></div>`;
    const render = () => {
      const q = $('#petQ').value.toLowerCase();
      const rows = pets.filter((p) => !q || JSON.stringify(p).toLowerCase().includes(q));
      $('#petList').innerHTML = `<table><tr><th>Familiar</th><th>Intervalo (h)</th><th class="num">Máx.</th><th class="num">Ganho</th><th>Comida → atributo</th></tr>
        ${rows.map((p) => `<tr><td><b>${esc(p.name)}</b></td><td>${esc(p.gap ? p.gap.replace(',', ' a ') : '-')}</td><td class="num">${p.max || p.statsMax || '-'}</td><td class="num">${p.gain || '-'}</td>
        <td>${p.foods.length ? p.foods.map((f) => `<div><b>${esc(f.stat)}</b>: ${f.foods.map((x) => esc(x.name)).join(', ')}</div>`).join('') : '<span class="note">não precisa comer / bônus fixo</span>'}</td></tr>`).join('')}</table>`;
    };
    $('#petQ').oninput = render; render();
  },

  async jobs() {
    const jobs = await api('/jobs');
    await loadPlayers();
    $('#gBody').innerHTML = `<div class="card"><h2>Profissões</h2>
    <p>No Dofus 1, o XP de craft depende da <b>quantidade de ingredientes diferentes</b> da receita e do seu nível. Quanto mais ingredientes a receita tem, mais XP, mas você só pode usar receitas que cabem nos seus espaços de craft. A tabela abaixo usa a fórmula real do servidor.</p>
    <div class="row"><select id="jSel">${jobs.map((j) => `<option value="${j.id}">${esc(j.name)}</option>`).join('')}</select>
      <label>Seu nível na profissão</label><input type="number" id="jLvl" value="1" min="1" max="100"></div>
    <div id="jBody"></div>
    <h3>Atalho de GM</h3><div class="row">${playerSelect('jPlayer')}<button class="btn" id="jLearn">Aprender profissão</button><input type="number" id="jXp" value="600000"><button class="btn" id="jGiveXp">Dar XP (600.000 ≈ nível 100)</button></div>
    </div>`;
    const render = run(async () => {
      const d = await api('/jobs/' + $('#jSel').value);
      const lvl = +$('#jLvl').value || 1;
      const slots = lvl < 10 ? 2 : lvl >= 100 ? 9 : Math.floor(lvl / 20) + 3;
      const xpFor = (n) => { if (lvl >= 100) return 0; return ({ 1: lvl < 40 ? 1 : 0, 2: lvl < 60 ? 10 : 0, 3: lvl > 9 && lvl < 80 ? 25 : 0, 4: lvl > 19 ? 50 : 0, 5: lvl > 39 ? 100 : 0, 6: lvl > 59 ? 250 : 0, 7: lvl > 79 ? 500 : 0, 8: lvl > 99 ? 1000 : 0 })[n] || 0; };
      const usable = d.crafts.filter((c) => c.count <= slots && c.count > 0);
      const best = Math.max(0, ...usable.map((c) => xpFor(c.count)));
      $('#jBody').innerHTML = `
        <h3>Rota mais fácil de craft (1 → 100)</h3>
        <table><tr><th>Nível</th><th class="num">Espaços</th><th>Faça receitas com</th><th class="num">XP por craft (×rate)</th></tr>
          ${d.route.map((r) => `<tr><td>${r.from}–${r.to}</td><td class="num">${r.slots}</td><td>${r.bestIngredients} ingredientes</td><td class="num">${r.xp}</td></tr>`).join('')}</table>
        <p class="note">Dica: a chance de sucesso é 100% quando a receita usa até (espaços − 2) ingredientes. No nível 100 craft não dá mais XP.</p>
        ${d.harvest.length ? `<h3>Coleta</h3><table><tr><th>Recurso</th><th class="num">Nível mín.</th><th class="num">XP por coleta</th></tr>
          ${d.harvest.map((h) => `<tr style="${h.minLvl <= lvl ? '' : 'opacity:.5'}"><td>${esc(h.itemName)}</td><td class="num">${h.minLvl}</td><td class="num">${h.xp}</td></tr>`).join('')}</table>
          <p class="note">Para coleta, colete sempre o recurso de <b>maior nível que você já pode</b>: é o que dá mais XP por ação.</p>` : ''}
        <h3>Melhores receitas agora (nível ${lvl}: ${slots} espaços, ${best} XP por craft)</h3>
        ${usable.filter((c) => xpFor(c.count) === best && best > 0).slice(0, 25).map((c) => `<div style="padding:4px 0;border-bottom:1px solid var(--line)"><b>${esc(c.name)}</b> <span class="note">${c.count} ingredientes</span><div class="note">${c.ingredients.map((i) => `${i.qty}× ${esc(i.name)}`).join(', ')}</div></div>`).join('') || '<p class="note">Nenhuma receita dá XP neste nível (ou a profissão é só de coleta/forjamagia).</p>'}`;
    });
    $('#jSel').onchange = render; $('#jLvl').oninput = debounce(render); render();
    $('#jLearn').onclick = run(async () => queued(await api(`/players/${$('#jPlayer').value}/action`, 'POST', { action: 'job', job: +$('#jSel').value })));
    $('#jGiveXp').onclick = run(async () => queued(await api(`/players/${$('#jPlayer').value}/action`, 'POST', { action: 'jobxp', job: +$('#jSel').value, xp: +$('#jXp').value })));
  },

  async drops() {
    const cfg = (await api('/config')).config;
    $('#gBody').innerHTML = `<div class="card"><h2>Como o drop funciona aqui</h2>
    <p>Fórmula do servidor: <b>chance = % do item no grau do monstro × (prospecção ÷ 100) × bônus de estrelas × desafios × rate de drop</b>.</p>
    <ul>
      <li>Prospecção abaixo de 100 conta como 100 (não piora). Enutrof e itens com Prospecção aumentam muito o drop.</li>
      <li>Monstros de grau maior (mais fortes) têm % maior.</li>
      <li>Alguns itens têm <b>prospecção mínima</b>: o grupo precisa somar essa prospecção para o item poder cair.</li>
      <li>Grupos de monstros que ficam muito tempo no mapa ganham estrelas (bônus de XP e drop).</li>
      <li>Rate de drop atual: <b>×${esc(cfg['system.server.game.rate.drop'])}</b> (mude no Início).</li>
    </ul>
    <h3>Calculadora</h3>
    <div class="row"><label>% base</label><input type="number" id="dcBase" value="1" step="0.01"><label>Prospecção</label><input type="number" id="dcPros" value="300"><label>Rate</label><input type="number" id="dcRate" value="${esc(cfg['system.server.game.rate.drop'])}"><b id="dcOut"></b></div>
    <p class="note">Para ver o que um monstro dropa, use a aba <b>Monstros e drops</b>. Para ver quem dropa um item, abra o item em <b>Itens e sets</b>.</p></div>`;
    const calc = () => { $('#dcOut').textContent = `= ${Math.min(100, (+$('#dcBase').value) * Math.max(1, (+$('#dcPros').value) / 100) * (+$('#dcRate').value)).toFixed(2)}% por monstro`; };
    $$('#gBody input').forEach((i) => (i.oninput = calc)); calc();
  },

  async gm() {
    const cmds = await api('/gm-commands');
    $('#gBody').innerHTML = `<div class="card"><h2>Comandos GM</h2>
    <p>Escolha o personagem, preencha o comando e clique em <b>Executar</b>. O comando roda como se aquele personagem tivesse digitado. Onde aparece <code>[personagem]</code>, você pode deixar em branco para agir no próprio personagem.</p>
    <div class="row">${playerSelect('gmPlayer')}<input id="gmCmd" placeholder="ex.: ITEM 2469 1 MAX" style="flex:1"><button class="btn primary" id="gmRun">Executar</button></div>
    <table><tr><th>Mais usados</th><th>O que faz</th></tr>
      <tr><td><code>ITEM id qtd MAX</code></td><td>Cria item com stats máximos</td></tr>
      <tr><td><code>ITEMSET id MAX</code></td><td>Cria um conjunto inteiro</td></tr>
      <tr><td><code>LEVEL nível</code></td><td>Sobe o nível</td></tr>
      <tr><td><code>KAMAS qtd</code></td><td>Dá kamas</td></tr>
      <tr><td><code>TP mapa célula</code> / <code>M x,y</code></td><td>Teleporta para um mapa ou coordenada</td></tr>
      <tr><td><code>ASTRUB</code> / <code>INCARNAM</code></td><td>Teleporta para as cidades iniciais</td></tr>
      <tr><td><code>SPAWN id,grauMin,grauMax</code></td><td>Cria um grupo de monstros no mapa</td></tr>
      <tr><td><code>LJOB id</code> / <code>XPJOB id xp</code></td><td>Aprende profissão / dá XP de profissão</td></tr>
      <tr><td><code>WALKFAST</code></td><td>Movimento instantâneo</td></tr>
      <tr><td><code>INV</code></td><td>Fica invisível</td></tr></table>
    <div class="row" style="margin-top:12px"><input id="gmQ" placeholder="Filtrar comandos" style="flex:1"></div><div id="gmList" class="list" style="max-height:600px"></div></div>`;
    const order = ['Personagem', 'Itens', 'Teleporte', 'Lutas e monstros', 'Missões', 'Servidor', 'Moderação', 'Edição de mapas', 'Técnico', 'Outros'];
    const render = () => {
      const q = $('#gmQ').value.toLowerCase();
      const list = cmds.filter((c) => !q || (c.name + ' ' + c.desc + ' ' + c.category).toLowerCase().includes(q));
      $('#gmList').innerHTML = order.map((cat) => {
        const rows = list.filter((c) => c.category === cat);
        if (!rows.length) return '';
        return `<h3>${cat}</h3><table>${rows.map((c) => `<tr><td style="width:40%"><code>${esc(c.name)}</code> <span class="note">${esc(c.args)}</span></td>
          <td>${esc(c.desc)}</td><td><button class="btn small" data-use="${esc(c.name)}">Usar</button></td></tr>`).join('')}</table>`;
      }).join('');
      $$('[data-use]').forEach((b) => (b.onclick = () => { $('#gmCmd').value = b.dataset.use + ' '; $('#gmCmd').focus(); window.scrollTo({ top: 0, behavior: 'smooth' }); }));
    };
    await loadPlayers();
    $('#gmPlayer').outerHTML = playerSelect('gmPlayer');
    $('#gmRun').onclick = run(async () => queued(await api(`/players/${$('#gmPlayer').value}/action`, 'POST', { action: 'raw', command: $('#gmCmd').value })));
    $('#gmQ').oninput = render; render();
  },

  async notes() {
    const n = await api('/notes/geral');
    $('#gBody').innerHTML = `<div class="card"><h2>Minhas anotações</h2><textarea id="noteText" style="min-height:300px">${esc(n.text)}</textarea>
      <div class="row"><button class="btn primary" id="noteSave">Salvar</button></div></div>`;
    $('#noteSave').onclick = run(async () => { await api('/notes/geral', 'PUT', { text: $('#noteText').value }); toast('Salvo'); });
  },
};

// ---------------- Fila e historico ----------------
async function viewQueue() {
  const [cmds, hist] = await Promise.all([api('/commands'), api('/history')]);
  const badge = (s) => `<span class="tag ${s === 'done' ? 'good' : s === 'error' ? 'bad' : s === 'pending' ? 'warn' : ''}">${{ done: 'feito', error: 'erro', pending: 'aguardando', cancelled: 'cancelado' }[s] || s}</span>`;
  main.innerHTML = `<div class="card"><div class="row"><h2 style="margin:0">Fila de comandos</h2><button class="btn small" id="qRef">Atualizar</button></div>
    <p class="note">"Aguardando" = o personagem ainda não está online. O comando roda quando ele entrar.</p>
    <table><tr><th>#</th><th>Personagem</th><th>Comando</th><th>Status</th><th>Resultado</th><th></th></tr>
    ${cmds.map((c) => `<tr><td>${c.id}</td><td>${esc(c.player === '*' ? 'servidor' : c.player)}</td><td><code>${esc(c.command.length > 80 ? c.command.slice(0, 80) + '…' : c.command)}</code></td>
      <td>${badge(c.status)}</td><td class="note">${esc(c.result || '')}</td><td>${c.status === 'pending' ? `<button class="btn small" data-cancel="${c.id}">Cancelar</button>` : ''}</td></tr>`).join('')}</table></div>
  <div class="card"><h2>Histórico do painel</h2><table>${hist.map((h) => `<tr><td class="note">${esc(h.created_at)}</td><td><b>${esc(h.action)}</b></td><td class="note">${esc(h.detail)}</td></tr>`).join('')}</table></div>`;
  $('#qRef').onclick = run(viewQueue);
  $$('[data-cancel]').forEach((b) => (b.onclick = run(async () => { await api(`/commands/${b.dataset.cancel}/cancel`, 'POST'); viewQueue(); })));
}

// ---------------- Navegacao ----------------
const VIEWS = { home: viewHome, accounts: viewAccounts, players: viewPlayers, items: viewItems, spells: viewSpells, monsters: viewMonsters, guide: viewGuide, queue: viewQueue };
function go(tab) {
  $$('#tabs button').forEach((b) => b.classList.toggle('active', b.dataset.tab === tab));
  try { localStorage.setItem('tab', tab); } catch {}
  main.innerHTML = '<p class="note">Carregando…</p>';
  run(VIEWS[tab])();
}
$$('#tabs button').forEach((b) => (b.onclick = () => go(b.dataset.tab)));
let startTab = 'home';
try { startTab = localStorage.getItem('tab') || 'home'; } catch {}
go(VIEWS[startTab] ? startTab : 'home');
