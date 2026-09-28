// Acesso ao MariaDB do StarLoco (bancos starloco_login e starloco_game).
const crypto = require('crypto');
const mysql = require('mysql2/promise');
const L = require('./lang');

const pool = mysql.createPool({
  host: '127.0.0.1', port: 3306, user: 'root', password: '',
  charset: 'latin1_swedish_ci', connectionLimit: 5, supportBigNumbers: true, bigNumberStrings: false, dateStrings: true,
});

const q = async (sql, params) => (await pool.query(sql, params))[0];

// Mesmo algoritmo do login StarLoco: SHA-512(MD5(senha)) em hex.
function hashPassword(pass) {
  const md5 = crypto.createHash('md5').update(pass).digest('hex');
  return crypto.createHash('sha512').update(md5).digest('hex');
}

async function listAccounts() {
  const accounts = await q('SELECT guid, account, pseudo, logged FROM starloco_login.world_accounts ORDER BY guid');
  const players = await listPlayers();
  return accounts.map((a) => ({ ...a, players: players.filter((p) => p.account === a.guid) }));
}

async function createAccounts(prefix, count, password, start = 1) {
  const created = [];
  for (let i = start; i < start + count; i++) {
    const name = `${prefix}${i}`;
    const exists = await q('SELECT guid FROM starloco_login.world_accounts WHERE account = ?', [name]);
    if (exists.length) continue;
    await q(`INSERT INTO starloco_login.world_accounts (account, pass, pseudo, email, lastIP, lastConnectionDate, friends, enemy, dateRegister)
             VALUES (?, ?, ?, '', '', '', '', '', DATE_FORMAT(NOW(), '%d/%m/%Y'))`, [name, hashPassword(password), name]);
    created.push(name);
  }
  return created;
}

async function setPassword(accountId, password) {
  await q('UPDATE starloco_login.world_accounts SET pass = ? WHERE guid = ?', [hashPassword(password), accountId]);
}

async function listPlayers() {
  const rows = await q(`SELECT id, name, account, class, sexe, level, xp, kamas, groupe, logged, capital, spellboost, map, jobs, objets, spells
                        FROM starloco_login.world_players ORDER BY account, id`);
  return rows.map((p) => ({
    ...p, className: L.className(p.class),
    itemCount: String(p.objets || '').split('|').filter(Boolean).length,
    spellCount: String(p.spells || '').split(',').filter(Boolean).length,
    objets: undefined, spells: undefined,
  }));
}

async function getPlayer(id) {
  const [p] = await q('SELECT * FROM starloco_login.world_players WHERE id = ?', [id]);
  return p || null;
}

async function setGroupOffline(playerId, group) {
  await q('UPDATE starloco_login.world_players SET groupe = ? WHERE id = ?', [group, playerId]);
}

// Inventario: world_players.objets = "id|id|..." -> world_objects
async function inventory(playerId) {
  const p = await getPlayer(playerId);
  if (!p) return [];
  const ids = String(p.objets || '').split('|').map(Number).filter(Boolean);
  if (!ids.length) return [];
  const rows = await q('SELECT id, template, quantity, position, stats FROM starloco_login.world_objects WHERE id IN (?)', [ids]);
  return rows.map((o) => ({
    ...o, name: L.itemName(o.template), type: L.items.u[o.template]?.t, typeName: L.itemTypeName(L.items.u[o.template]?.t),
    level: L.items.u[o.template]?.l, equipped: o.position !== -1,
  })).sort((a, b) => (b.equipped - a.equipped) || a.name.localeCompare(b.name));
}

async function getObject(id) {
  const [o] = await q('SELECT id, template, quantity, position, stats FROM starloco_login.world_objects WHERE id = ?', [id]);
  return o ? { ...o, name: L.itemName(o.template) } : null;
}

async function getItemTemplate(id) {
  const [t] = await q('SELECT id, type, name, level, statsTemplate, panoplie, conditions, armesInfos FROM starloco_game.item_template WHERE id = ?', [id]);
  return t ? { ...t, namePt: L.itemName(t.id) } : null;
}

async function setItemTemplateStats(id, statsTemplate) {
  await q('UPDATE starloco_game.item_template SET statsTemplate = ? WHERE id = ?', [statsTemplate, id]);
}

// Fila de comandos executada pelo PanelBridge dentro do servidor de jogo.
async function queueCommand(player, command) {
  const r = await q('INSERT INTO starloco_login.panel_commands (player, command) VALUES (?, ?)', [player, command]);
  return r.insertId;
}

async function listCommands(limit = 40) {
  return q('SELECT id, player, command, status, result, created_at, done_at FROM starloco_login.panel_commands ORDER BY id DESC LIMIT ?', [limit]);
}

async function cancelCommand(id) {
  await q("UPDATE starloco_login.panel_commands SET status = 'cancelled' WHERE id = ? AND status = 'pending'", [id]);
}

// ---- Drops ----
async function dropsByMonster(monsterId) {
  const rows = await q('SELECT * FROM starloco_game.drops WHERE monsterId = ?', [monsterId]);
  return rows.map((d) => ({ ...d, itemName: L.itemName(d.objectId), monsterNamePt: L.monsterName(d.monsterId) }));
}

async function dropsByItem(itemId) {
  const rows = await q('SELECT * FROM starloco_game.drops WHERE objectId = ?', [itemId]);
  return rows.map((d) => ({ ...d, itemName: L.itemName(d.objectId), monsterNamePt: d.monsterId ? L.monsterName(d.monsterId) : 'Qualquer monstro' }));
}

async function updateDrop(monsterId, objectId, percents, ceil) {
  const [p1, p2, p3, p4, p5] = percents;
  await q(`UPDATE starloco_game.drops SET percentGrade1=?, percentGrade2=?, percentGrade3=?, percentGrade4=?, percentGrade5=?, ceil=?
           WHERE monsterId=? AND objectId=?`, [p1, p2, p3, p4, p5, ceil, monsterId, objectId]);
}

async function addDrop(monsterId, objectId, percent, ceil) {
  await q(`INSERT INTO starloco_game.drops (monsterName, monsterId, objectName, objectId, percentGrade1, percentGrade2, percentGrade3, percentGrade4, percentGrade5, ceil, action, level)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, -1, -1)`,
  [L.monsterName(monsterId), monsterId, L.itemName(objectId), objectId, percent, percent, percent, percent, percent, ceil]);
}

async function deleteDrop(monsterId, objectId) {
  await q('DELETE FROM starloco_game.drops WHERE monsterId = ? AND objectId = ?', [monsterId, objectId]);
}

async function monster(id) {
  const [m] = await q('SELECT id, name, grades, pdvs, points, exps, minKamas, maxKamas, capturable, isBoss FROM starloco_game.monsters WHERE id = ?', [id]);
  return m || null;
}

// ---- Familiares ----
async function pets() {
  const rows = await q('SELECT * FROM starloco_game.pets');
  return rows.map((p) => ({ ...p, name: L.itemName(p.TemplateID), deadName: p.DeadTemplate ? L.itemName(p.DeadTemplate) : null }));
}

module.exports = {
  pool, q, hashPassword, listAccounts, createAccounts, setPassword, listPlayers, getPlayer, setGroupOffline,
  inventory, getObject, getItemTemplate, setItemTemplateStats, queueCommand, listCommands, cancelCommand,
  dropsByMonster, dropsByItem, updateDrop, addDrop, deleteDrop, monster, pets,
};
