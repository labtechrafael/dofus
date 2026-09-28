// Painel local do servidor Dofus (StarLoco). Abre em http://127.0.0.1:8080
const fs = require('fs');
const path = require('path');
const express = require('express');

const L = require('./lib/lang');
const G = require('./lib/game');
const S = require('./lib/stats');
const J = require('./lib/jobs');
const store = require('./lib/store');
const proc = require('./lib/proc');

const app = express();
app.use(express.json({ limit: '2mb' }));

// Arquivos lang do cliente (o config.xml do cliente aponta para http://127.0.0.1:8080/)
app.use('/lang', express.static(path.join(__dirname, '..', 'server', 'web', 'lang')));
app.use(express.static(path.join(__dirname, 'public')));

const api = express.Router();
app.use('/api', api);

const wrap = (fn) => (req, res) => Promise.resolve(fn(req, res))
  .then((data) => { if (!res.headersSent) res.json(data ?? { ok: true }); })
  .catch((e) => { console.error(e); res.status(500).json({ error: e.message }); });

const int = (v, def = 0) => (Number.isFinite(+v) ? Math.trunc(+v) : def);

async function playerById(id) {
  const p = await G.getPlayer(int(id));
  if (!p) throw new Error('Personagem não encontrado');
  return p;
}

async function send(player, command, label) {
  const id = await G.queueCommand(player.name, command);
  store.log(label || 'comando', `${player.name}: ${command}`);
  return { queued: id, command };
}

// ---------- Servidor ----------
api.get('/status', wrap(async () => ({
  ...(await proc.status()), config: proc.readGameConfig(), levelCap: proc.readLevelCap(),
})));

api.post('/server/:target/:action', wrap(async (req) => {
  const { target, action } = req.params;
  const r = {};
  const start = { mariadb: proc.startMariaDB, login: proc.startLogin, game: proc.startGame };
  const stop = { mariadb: proc.stopMariaDB, login: proc.stopLogin, game: () => proc.stopGame(G) };
  const order = target === 'all' ? ['mariadb', 'login', 'game'] : [target];
  if (action === 'stop' || action === 'restart') for (const t of [...order].reverse()) r[t + '_stop'] = await stop[t]();
  if (action === 'start' || action === 'restart') for (const t of order) r[t] = await start[t]();
  store.log(`servidor ${action}`, target);
  return r;
}));

api.post('/server/save', wrap(async () => ({ queued: await G.queueCommand('*', 'SAVE') })));
api.get('/logs/:name', wrap(async (req) => ({ text: proc.tailLog(req.params.name.replace(/\W/g, ''), 120) })));

api.get('/config', wrap(async () => ({ config: proc.readGameConfig(), levelCap: proc.readLevelCap() })));
api.post('/config', wrap(async (req) => {
  const allowed = [
    'system.server.game.rate.xp', 'system.server.game.rate.drop', 'system.server.game.rate.kamas',
    'system.server.game.rate.job', 'system.server.game.rate.honor', 'system.server.game.rate.fm',
    'system.server.game.start.level', 'system.server.game.start.kamas', 'system.server.game.allZaap',
    'system.server.game.allEmotes', 'system.server.game.timeByTurn', 'system.server.game.start.message',
  ];
  const changes = {};
  for (const k of allowed) if (k in (req.body.config || {})) changes[k] = String(req.body.config[k]).trim();
  for (const k of allowed.filter((k) => k.includes('.rate.'))) {
    if (k in changes && !(int(changes[k]) >= 1 && int(changes[k]) <= 32767)) throw new Error(`Valor inválido para ${k} (1 a 32767)`);
  }
  proc.writeGameConfig(changes);
  if (req.body.levelCap) {
    const cap = int(req.body.levelCap);
    if (cap < 200 || cap > 2000) throw new Error('Nível máximo deve ficar entre 200 e 2000');
    proc.writeLevelCap(cap);
  }
  store.log('config', { changes, levelCap: req.body.levelCap });
  return { ok: true, note: 'Reinicie o servidor de jogo para aplicar.' };
}));

api.post('/clients/open', wrap(async (req) => {
  const count = Math.min(8, Math.max(1, int(req.body.count, 1)));
  proc.openClients(count);
  return { opened: count };
}));

// ---------- Contas e personagens ----------
api.get('/accounts', wrap(() => G.listAccounts()));
api.post('/accounts', wrap(async (req) => {
  const { prefix = 'conta', count = 8, password, start = 1 } = req.body;
  if (!password || password.length < 3) throw new Error('Informe uma senha com pelo menos 3 caracteres');
  if (!/^[a-z0-9]{2,20}$/i.test(prefix)) throw new Error('Prefixo deve ter apenas letras e números');
  const created = await G.createAccounts(prefix.toLowerCase(), Math.min(20, int(count, 8)), password, Math.max(1, int(start, 1)));
  store.log('contas criadas', created.join(', '));
  return { created };
}));
api.post('/accounts/:id/password', wrap(async (req) => {
  if (!req.body.password) throw new Error('Senha vazia');
  await G.setPassword(int(req.params.id), req.body.password);
}));

api.get('/players', wrap(() => G.listPlayers()));
api.get('/players/:id', wrap(async (req) => {
  const p = await playerById(req.params.id);
  const spells = String(p.spells || '').split(',').filter(Boolean).map((s) => {
    const [id, level, pos] = s.split(';');
    return { id: +id, level: +level, pos, name: L.spellName(id) };
  });
  const jobs = String(p.jobs || '').split(';').filter(Boolean).map((s) => {
    const [id, xp] = s.split(',');
    return { id: +id, xp: +xp, name: L.jobName(id) };
  });
  return {
    id: p.id, name: p.name, account: p.account, class: p.class, className: L.className(p.class), level: p.level, xp: p.xp,
    kamas: p.kamas, groupe: p.groupe, logged: p.logged, capital: p.capital, spellboost: p.spellboost,
    base: { vitalidade: p.vitalite, forca: p.force, sabedoria: p.sagesse, inteligencia: p.intelligence, sorte: p.chance, agilidade: p.agilite },
    spells, jobs,
  };
}));
api.get('/players/:id/inventory', wrap(async (req) => (await G.inventory(int(req.params.id))).map((o) => ({ ...o, lines: S.describeAll(o.stats) }))));

// Acoes no personagem (executadas pelo servidor assim que o personagem estiver online)
api.post('/players/:id/action', wrap(async (req) => {
  const p = await playerById(req.params.id);
  const b = req.body;
  switch (b.action) {
    case 'level': return send(p, `LEVEL ${int(b.level)} ${p.name}`, 'nível');
    case 'kamas': return send(p, `KAMAS ${int(b.amount)} ${p.name}`, 'kamas');
    case 'capital': return send(p, `CAPITAL ${int(b.amount)} ${p.name}`, 'capital');
    case 'spellpoints': return send(p, `SPELLPOINT ${int(b.amount)} ${p.name}`, 'pontos de feitiço');
    case 'spells': {
      const ids = (b.ids || []).map(Number).filter(Boolean);
      if (!ids.length) throw new Error('Nenhum feitiço selecionado');
      return send(p, `PSPELLS ${Math.min(6, Math.max(1, int(b.level, 6)))} ${ids.join(',')}`, 'feitiços');
    }
    case 'classSpells': {
      const ids = b.scope === 'all' ? Object.values(L.classSpells).flat() : L.classSpells[p.class] || [];
      return send(p, `PSPELLS ${Math.min(6, Math.max(1, int(b.level, 6)))} ${ids.join(',')}`, b.scope === 'all' ? 'todos os feitiços' : 'feitiços da classe');
    }
    case 'item': {
      const tpl = int(b.template);
      if (!L.items.u[tpl]) throw new Error('Item não existe');
      // Certificado de montaria: o comando ITEM do servidor ja cria o dragossauro com tudo no maximo.
      if (L.items.u[tpl].t === 97) return send(p, `ITEM ${tpl} ${Math.max(1, int(b.qty, 1))}`, 'montaria');
      const stats = b.values ? S.build(b.values, b.others || []) : '';
      return send(p, `PITEM ${tpl} ${Math.max(1, int(b.qty, 1))} ${b.max ? 'MAX' : 'RAND'}${stats ? ' ' + stats : ''}`, 'item');
    }
    case 'itemset': return send(p, `ITEMSET ${int(b.set)}${b.max ? ' MAX' : ''}`, 'conjunto');
    case 'kit': {
      const kit = store.getKit(int(b.kit));
      if (!kit) throw new Error('Kit não encontrado');
      const ids = [];
      for (const it of kit.items) {
        const stats = it.stats ? ` ${it.stats}` : '';
        ids.push((await send(p, `PITEM ${it.template} ${it.qty || 1} ${it.max ? 'MAX' : 'RAND'}${stats}`, `kit ${kit.name}`)).queued);
      }
      return { queued: ids };
    }
    case 'setstats': {
      const stats = S.build(b.values || {}, b.others || []);
      return send(p, `PSETSTATS ${int(b.object)} ${stats}`, 'atributos');
    }
    case 'job': return send(p, `LJOB ${int(b.job)} ${p.name}`, 'profissão');
    case 'jobxp': return send(p, `XPJOB ${int(b.job)} ${int(b.xp)} ${p.name}`, 'xp profissão');
    case 'gm': {
      const group = int(b.group, 1);
      await G.setGroupOffline(p.id, group);
      return send(p, `SETGROUPE ${group} ${p.name}`, 'grupo GM');
    }
    case 'master': return send(p, b.on === false ? 'PMASTER OFF' : 'PMASTER ON', b.on === false ? 'modo escravo desligado' : 'modo escravo ligado');
    case 'bar': return send(p, `PBAR ${int(b.classe, 1)}`, 'barra de feitiços por raça');
    case 'autopass': return send(p, 'PPASS', 'passar turno automático');
    case 'raw': {
      if (!b.command) throw new Error('Comando vazio');
      return send(p, String(b.command).trim(), 'comando livre');
    }
    default: throw new Error('Ação desconhecida');
  }
}));

api.get('/commands', wrap(() => G.listCommands(60)));
api.post('/commands/:id/cancel', wrap((req) => G.cancelCommand(int(req.params.id))));

// ---------- Itens ----------
api.get('/itemtypes', wrap(() => Object.entries(L.items.t).map(([id, t]) => ({ id: +id, name: t.n })).sort((a, b) => a.name.localeCompare(b.name))));
api.get('/items', wrap((req) => L.searchItems(String(req.query.q || ''), { type: req.query.type, limit: int(req.query.limit, 80) })));
api.get('/items/:id', wrap(async (req) => {
  const id = int(req.params.id);
  const it = L.items.u[id];
  if (!it) throw new Error('Item não existe');
  const tpl = await G.getItemTemplate(id);
  const setId = it.s;
  return {
    id, name: it.n, description: it.d, level: it.l, type: it.t, typeName: L.itemTypeName(it.t), conditions: it.c || '',
    template: tpl && { stats: tpl.statsTemplate, lines: S.describeAll(tpl.statsTemplate), ...S.split(tpl.statsTemplate), max: S.templateMax(tpl.statsTemplate) },
    set: setId ? { id: setId, name: L.setName(setId), items: (L.itemsets[setId]?.i || []).map((i) => ({ id: i, name: L.itemName(i) })) } : null,
    recipe: J.recipe(id),
    usedIn: Object.entries(L.crafts).filter(([, r]) => r.some(([ing]) => ing === id)).slice(0, 40).map(([rid]) => ({ id: +rid, name: L.itemName(rid) })),
    drops: await G.dropsByItem(id),
  };
}));
api.post('/items/:id/template-stats', wrap(async (req) => {
  const id = int(req.params.id);
  const stats = S.build(req.body.values || {}, req.body.others || []);
  await G.setItemTemplateStats(id, stats);
  store.log('modelo de item', `${id}: ${stats}`);
  return { stats, note: 'Vale para itens criados depois de reiniciar o servidor de jogo.' };
}));
api.get('/objects/:id', wrap(async (req) => {
  const o = await G.getObject(int(req.params.id));
  if (!o) throw new Error('Objeto não encontrado');
  return { ...o, ...S.split(o.stats), lines: S.describeAll(o.stats) };
}));
api.get('/stats', wrap(() => S.STATS.map(([id, neg, label, group]) => ({ id, neg, label, group }))));
api.post('/stats/preview', wrap((req) => {
  const stats = S.build(req.body.values || {}, req.body.others || []);
  return { stats, lines: S.describeAll(stats) };
}));

api.get('/sets', wrap((req) => {
  const nq = L.norm(req.query.q || '');
  return Object.entries(L.itemsets)
    .map(([id, s]) => ({ id: +id, name: s.n, items: (s.i || []).map((i) => ({ id: i, name: L.itemName(i), level: L.items.u[i]?.l })) }))
    .filter((s) => !nq || L.norm(s.name).includes(nq))
    .map((s) => ({ ...s, level: Math.max(0, ...s.items.map((i) => i.level || 0)) }))
    .sort((a, b) => a.level - b.level);
}));

api.get('/kits', wrap(() => store.listKits().map((k) => ({ ...k, items: k.items.map((i) => ({ ...i, name: L.itemName(i.template) })) }))));
api.post('/kits', wrap((req) => {
  const { name, items } = req.body;
  if (!name || !Array.isArray(items) || !items.length) throw new Error('Informe nome e itens do kit');
  return { id: Number(store.saveKit(name, items.map((i) => ({ template: int(i.template), qty: Math.max(1, int(i.qty, 1)), max: !!i.max, stats: i.stats || '' })))) };
}));
api.delete('/kits/:id', wrap((req) => store.deleteKit(int(req.params.id))));

// ---------- Feiticos ----------
api.get('/spells/classes', wrap(() => L.listSpellsByClass()));
api.get('/spells', wrap((req) => {
  const nq = L.norm(req.query.q || '');
  return Object.entries(L.spells).filter(([, s]) => s.n && (!nq || L.norm(s.n).includes(nq))).slice(0, 80)
    .map(([id, s]) => ({ id: +id, name: s.n, description: s.d }));
}));

// ---------- Monstros e drops ----------
api.get('/monsters', wrap((req) => L.searchMonsters(String(req.query.q || ''), 80)));
api.get('/monsters/:id', wrap(async (req) => {
  const id = int(req.params.id);
  const m = L.monsters[id];
  const db = await G.monster(id);
  return {
    id, name: L.monsterName(id),
    // Graus vindos do banco do servidor: grades "nivel@res;...|...", pdvs "vida|...", points "pa;pm|...", exps "xp|..."
    grades: db ? String(db.grades || '').split('|').filter(Boolean).map((g, i) => ({
      grade: i + 1, level: +g.split('@')[0], life: +String(db.pdvs || '').split('|')[i] || null,
      ap: +(String(db.points || '').split('|')[i] || '').split(';')[0] || null, mp: +(String(db.points || '').split('|')[i] || '').split(';')[1] || null,
      xp: +String(db.exps || '').split('|')[i] || 0,
    })) : [],
    kamas: db ? [db.minKamas, db.maxKamas] : null, capturable: !!db?.capturable,
    subAreas: (L.monsterSubAreas[id] || []).filter((sa) => !String(L.maps.sa[sa]?.n || '').startsWith('//'))
      .map((sa) => ({ id: sa, name: L.subAreaName(sa), area: L.maps.a[L.maps.sa[sa]?.a]?.n })),
    drops: await G.dropsByMonster(id),
    rates: { drop: +proc.readGameConfig()['system.server.game.rate.drop'] || 1 },
  };
}));
api.post('/drops', wrap(async (req) => {
  const { monsterId, objectId, percents, ceil = 0 } = req.body;
  await G.updateDrop(int(monsterId), int(objectId), (percents || []).map(Number), int(ceil));
  store.log('drop editado', req.body);
}));
api.put('/drops', wrap(async (req) => {
  const { monsterId, objectId, percent, ceil = 0 } = req.body;
  if (!L.items.u[int(objectId)]) throw new Error('Item não existe');
  await G.addDrop(int(monsterId), int(objectId), Number(percent), int(ceil));
  store.log('drop adicionado', req.body);
}));
api.delete('/drops', wrap(async (req) => {
  await G.deleteDrop(int(req.body.monsterId), int(req.body.objectId));
  store.log('drop removido', req.body);
}));

// ---------- Guia ----------
api.get('/pets', wrap(async () => (await G.pets()).map((p) => ({
  id: p.TemplateID, name: p.name, deadName: p.deadName, type: p.Type, gap: p.Gap, max: p.Max, gain: p.Gain, statsMax: p.StatsMax,
  foods: String(p.StatsUp || '').split(';').filter(Boolean).map((part) => {
    const [statHex, ...rest] = part.split('|');
    const stat = S.STATS.find(([pos]) => pos === parseInt(statHex, 16));
    const foodIds = rest.join('#').split('#').filter(Boolean).map(Number);
    return {
      stat: stat ? stat[2] : (L.effects[parseInt(statHex, 16)]?.d || statHex),
      foods: foodIds.map((f) => ({ id: f, name: p.Type === 1 ? L.monsterName(f) : L.itemName(f) })),
    };
  }),
}))));
api.get('/jobs', wrap(() => J.listJobs()));
api.get('/jobs/:id', wrap((req) => J.jobDetail(int(req.params.id))));
api.get('/rides', wrap(() => Object.entries(L.rides).map(([id, r]) => ({ id: +id, name: r.n })).sort((a, b) => a.name.localeCompare(b.name))));

api.get('/gm-commands', wrap(() => {
  const src = fs.readFileSync(path.join(__dirname, '..', 'server', 'game', 'scripts', 'data', 'AdminCommands.lua'), 'utf8');
  const pt = JSON.parse(fs.readFileSync(path.join(__dirname, 'data', 'gm-commands-pt.json'), 'utf8'));
  const seen = new Set();
  return [...src.matchAll(/RegisterAdminCommand\("([^"]+)",\s*"([^"]*)",\s*"((?:[^"\\]|\\.)*)"/g)]
    .filter((m) => !seen.has(m[1]) && seen.add(m[1]))
    .map((m) => {
      const [category, args, desc] = pt[m[1]] || ['Outros', m[2], m[3]];
      return { name: m[1], category, args, desc, original: m[3] };
    });
}));

// ---------- Mundo LabTech ----------
const LABTECH_DIR = path.join(__dirname, 'world', 'labtech');
api.get('/labtech', wrap(() => {
  const file = path.join(LABTECH_DIR, 'mundo_gerado.json');
  const maps = fs.existsSync(file) ? JSON.parse(fs.readFileSync(file, 'utf8')) : {};
  return {
    maps: Object.entries(maps).map(([id, m]) => ({ id: +id, name: m.nome.replace(/_/g, ' '), x: m.x, y: m.y, landing: m.chegada,
      npcs: Object.keys(m.npcs || {}).map((n) => L.npcs[n]?.n || n) })),
  };
}));
api.post('/labtech/rebuild', wrap(() => new Promise((resolve, reject) => {
  const { execFile } = require('child_process');
  execFile('python', [path.join(__dirname, 'tools', 'labtech', 'build.py')], { cwd: path.join(__dirname, 'tools', 'labtech'), maxBuffer: 1 << 22 },
    (err, stdout, stderr) => (err ? reject(new Error(stderr || err.message)) : resolve({ output: stdout })));
})));
const LABTECH_KIT = [[30002, 1], [30026, 1], [30024, 1], [30027, 1], [30028, 1], [30029, 1], [30030, 1], [30031, 1], [30032, 1],
  [30018, 10], [30019, 10], [30020, 10], [30021, 10], [30022, 10], [30023, 10]];
api.post('/players/:id/labtech', wrap(async (req) => {
  const p = await playerById(req.params.id);
  if (req.body.what === 'tp') return send(p, `TP ${req.body.map || 30001} ${req.body.cell || 283}`, 'teleporte LabTech');
  if (req.body.what === 'kit') {
    const ids = [];
    for (const [tpl, qty] of LABTECH_KIT) ids.push((await send(p, `PITEM ${tpl} ${qty} MAX`, 'kit LabTech')).queued);
    ids.push((await send(p, `PSPELLS 6 ${Object.values(L.classSpells).flat().join(',')}`, 'feitiços das 12 classes')).queued);
    return { queued: ids };
  }
  throw new Error('Ação desconhecida');
}));

api.get('/history', wrap(() => store.history(150)));
api.get('/notes/:key', wrap((req) => ({ text: store.getNote(req.params.key) })));
api.put('/notes/:key', wrap((req) => store.setNote(req.params.key, String(req.body.text || ''))));

const PORT = 8080;
app.listen(PORT, '127.0.0.1', () => console.log(`Painel em http://127.0.0.1:${PORT}`));
