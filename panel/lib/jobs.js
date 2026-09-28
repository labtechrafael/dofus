// Profissoes: recursos de coleta (scripts Lua do servidor) + receitas (lang) + formula de XP de craft
// (mesma logica de Formulas.calculXpWinCraft e JobConstant.getTotalCaseByJobLevel do StarLoco).
const fs = require('fs');
const path = require('path');
const L = require('./lang');

const skillsDir = path.join(__dirname, '..', '..', 'server', 'game', 'scripts', 'data', 'skills');
const jobConst = fs.readFileSync(path.join(__dirname, '..', '..', 'server', 'game', 'scripts', 'data', 'Jobs.lua'), 'utf8');
const jobIdByName = Object.fromEntries([...jobConst.matchAll(/^(\w+Job) = (\d+)/gm)].map((m) => [m[1], +m[2]]));

// Recursos coletaveis por profissao: {id, minLvl, itemID, xp}
const gather = {};
for (const file of fs.readdirSync(skillsDir)) {
  const src = fs.readFileSync(path.join(skillsDir, file), 'utf8');
  const job = jobIdByName[(src.match(/local jobID = (\w+)/) || [])[1]];
  if (!job) continue;
  for (const [line] of src.matchAll(/^\s*\{id=\d+,.*$/gm)) {
    const field = (name) => (line.match(new RegExp(`\\b${name}=(\\d+)`)) || [])[1];
    const items = field('itemID') ? [+field('itemID')] : ((line.match(/fishes=\{([\d,\s]+)\}/) || [])[1] || '').split(',').map(Number).filter(Boolean);
    if (!items.length) continue;
    (gather[job] ||= []).push({
      skill: +field('id'), minLvl: +field('minLvl'), xp: +field('xp'),
      item: items[0], itemName: items.map((i) => L.itemName(i)).join(', '),
    });
  }
}

const slotsAt = (lvl) => (lvl < 10 ? 2 : lvl >= 100 ? 9 : Math.floor(lvl / 20) + 3);

function craftXp(lvl, ingredients) {
  if (lvl >= 100) return 0;
  switch (ingredients) {
    case 1: return lvl < 40 ? 1 : 0;
    case 2: return lvl < 60 ? 10 : 0;
    case 3: return lvl > 9 && lvl < 80 ? 25 : 0;
    case 4: return lvl > 19 ? 50 : 0;
    case 5: return lvl > 39 ? 100 : 0;
    case 6: return lvl > 59 ? 250 : 0;
    case 7: return lvl > 79 ? 500 : 0;
    case 8: return lvl > 99 ? 1000 : 0;
    default: return 0;
  }
}

// Faixas de nivel e a melhor quantidade de ingredientes para cada uma.
const LEVEL_BANDS = [[1, 9], [10, 19], [20, 39], [40, 59], [60, 79], [80, 99]];
function craftRoute() {
  return LEVEL_BANDS.map(([from, to]) => {
    const slots = slotsAt(from);
    let best = 1;
    for (let n = 1; n <= Math.min(slots, 8); n++) if (craftXp(from, n) >= craftXp(from, best)) best = n;
    return { from, to, slots, bestIngredients: best, xp: craftXp(from, best) };
  });
}

function recipe(itemId) {
  const r = L.crafts[itemId];
  if (!r) return null;
  return r.map(([id, qty]) => ({ id, qty, name: L.itemName(id) }));
}

function listJobs() {
  return Object.entries(L.jobInfo).map(([id, j]) => ({
    id: +id, name: L.jobName(id), crafts: j.crafts.size, harvest: (gather[id] || []).length,
  })).sort((a, b) => a.name.localeCompare(b.name));
}

function jobDetail(id) {
  const j = L.jobInfo[id];
  if (!j) return null;
  const crafts = [...j.crafts].map((itemId) => {
    const ing = recipe(itemId) || [];
    return { id: itemId, name: L.itemName(itemId), level: L.items.u[itemId]?.l, ingredients: ing, count: ing.length };
  }).sort((a, b) => a.count - b.count || (a.level || 0) - (b.level || 0));
  return {
    id: +id, name: L.jobName(id), skills: j.skills,
    harvest: (gather[id] || []).slice().sort((a, b) => a.minLvl - b.minLvl),
    crafts, route: craftRoute(),
  };
}

module.exports = { gather, slotsAt, craftXp, craftRoute, recipe, listJobs, jobDetail };
