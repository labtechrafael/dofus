// Dados em portugues extraidos dos arquivos lang do cliente (ver tools/swf_lang.py).
const fs = require('fs');
const path = require('path');

const dir = path.join(__dirname, '..', 'data', 'lang');
const load = (name) => JSON.parse(fs.readFileSync(path.join(dir, name + '.json'), 'utf8'));

const items = load('items').I;
const spells = load('spells').S;
const monsters = load('monsters').M;
const jobs = load('jobs').J;
const itemsets = load('itemsets').IS;
const maps = load('maps').MA;
const crafts = load('crafts').CR;
const skills = load('skills').SK;
const classes = load('classes').G;
const effects = load('effects').E;
const rides = load('rides').RI;
const npcs = load('npc').N.d;
const classSpells = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'data', 'class-spells.json'), 'utf8'));
const spellLearnLevel = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'data', 'spell-learn-level.json'), 'utf8'));

const norm = (s) => String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();

function itemName(id) { return items.u[id]?.n || `Item #${id}`; }
function itemTypeName(t) { return items.t[t]?.n || `Tipo ${t}`; }
function spellName(id) { return spells[id]?.n || `Feitiço #${id}`; }
function monsterName(id) { return monsters[id]?.n || `Monstro #${id}`; }
function jobName(id) { return jobs[id]?.n || `Profissão #${id}`; }
function className(id) { return classes[id]?.sn || `Classe ${id}`; }
function subAreaName(id) { return maps.sa[id]?.n || `Subárea ${id}`; }
function setName(id) { return itemsets[id]?.n || `Conjunto #${id}`; }

// Nivel minimo para aprender um feitico em determinado grau (ultimo numero relevante do array de nivel).
function spellLevelInfo(id, grade) {
  const lv = spells[id]?.['l' + grade];
  if (!Array.isArray(lv)) return null;
  return { ap: lv[2], rangeMin: lv[3], rangeMax: lv[4], reqLevel: lv[lv.length - 3] };
}

function searchItems(q, { type, limit = 60 } = {}) {
  const nq = norm(q);
  const out = [];
  for (const [id, it] of Object.entries(items.u)) {
    if (type && String(it.t) !== String(type)) continue;
    if (nq && !norm(it.n).includes(nq) && id !== q) continue;
    out.push({ id: +id, name: it.n, level: it.l, type: it.t, typeName: itemTypeName(it.t), set: it.s || null });
    if (out.length >= limit) break;
  }
  return out;
}

function searchMonsters(q, limit = 60) {
  const nq = norm(q);
  const out = [];
  for (const [id, m] of Object.entries(monsters)) {
    if (nq && !norm(m.n).includes(nq) && id !== q) continue;
    const levels = [1, 2, 3, 4, 5, 6].map((g) => m['g' + g]?.l).filter((x) => x != null);
    out.push({ id: +id, name: m.n, levels });
    if (out.length >= limit) break;
  }
  return out;
}

// Subareas onde cada monstro aparece: lidas dos mapas Lua do servidor (map.allowedMobGrades + subArea do MapDef).
// (No lang, MA.sa[x].m e a lista de musicas da subarea, nao de monstros.)
const monsterSubAreas = {};
(function loadSpawns() {
  const dir = path.join(__dirname, '..', '..', 'server', 'game', 'scripts', 'data', 'maps');
  const walk = (d) => fs.readdirSync(d, { withFileTypes: true }).flatMap((e) => (e.isDirectory() ? walk(path.join(d, e.name)) : [path.join(d, e.name)]));
  let files = [];
  try { files = walk(dir).filter((f) => f.endsWith('.lua')); } catch { return; }
  for (const f of files) {
    const src = fs.readFileSync(f, 'utf8');
    const def = /MapDef\([\s\S]*?,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(\d+)\s*\)/.exec(src);
    const pool = src.split('allowedMobGrades')[1];
    if (!def || !pool) continue;
    const sa = +def[3];
    for (const m of new Set([...pool.matchAll(/\{\s*(\d+)\s*,\s*\d+\s*\}/g)].map((x) => +x[1]))) {
      const list = (monsterSubAreas[m] ||= []);
      if (!list.includes(sa)) list.push(sa);
    }
  }
})();

// Profissoes: recursos coletados e receitas por profissao.
const jobInfo = {};
for (const [sid, s] of Object.entries(skills)) {
  if (!s.j || s.j === 1) continue;
  const j = (jobInfo[s.j] ||= { harvest: new Set(), crafts: new Set(), skills: [] });
  j.skills.push({ id: +sid, name: s.d });
  if (s.i) j.harvest.add(s.i);
  for (const c of s.cl || []) j.crafts.add(c);
}

function listSpellsByClass() {
  return Object.entries(classSpells).map(([cls, ids]) => ({
    classId: +cls,
    className: className(cls),
    spells: ids.map((id) => ({ id, name: spellName(id), learnLevel: spellLearnLevel[id] ?? null })),
  }));
}

module.exports = {
  items, spells, monsters, jobs, itemsets, maps, crafts, skills, classes, effects, rides, classSpells, npcs,
  norm, itemName, itemTypeName, spellName, monsterName, jobName, className, subAreaName, setName,
  spellLevelInfo, searchItems, searchMonsters, monsterSubAreas, jobInfo, listSpellsByClass,
};
