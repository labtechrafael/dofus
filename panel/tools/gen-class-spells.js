// Uso: cd tools && node gen-class-spells.js
// Gera data/class-spells.json a partir de Constant.java (getStartSorts + onLevelUpSpells + sort especial).
const fs = require('fs');
const src = fs.readFileSync('../../server/game/src/org/starloco/locos/kernel/Constant.java', 'latin1');
const ids = { FECA:1, OSAMODAS:2, ENUTROF:3, SRAM:4, XELOR:5, ECAFLIP:6, ENIRIPSA:7, IOP:8, CRA:9, SADIDA:10, SACRIEUR:11, PANDAWA:12 };
const out = {}; for (const k in ids) out[ids[k]] = [];
const learnLevel = {};
function section(name) {
  const i = src.indexOf(name); const j = src.indexOf('\n    public static', i + 10);
  return src.slice(i, j);
}
for (const [fn, re] of [['getStartSorts(int classID)', /start\.put\((\d+),/], ['onLevelUpSpells(Player perso, int lvl)', /learnSpell\((\d+),/]]) {
  let cls = null, lvl = 1;
  for (const line of section(fn).split('\n')) {
    const c = line.match(/case CLASS_(\w+):/); if (c) { cls = ids[c[1]]; lvl = 1; }
    const l = line.match(/lvl == (\d+)/); if (l) lvl = +l[1];
    const m = line.match(re);
    if (m && cls && !out[cls].includes(+m[1])) { out[cls].push(+m[1]); learnLevel[m[1]] = lvl; }
  }
}
let cls = null;
for (const line of section('getSpecialSpellByClasse(int classe)').split('\n')) {
  const c = line.match(/case Constant\.CLASS_(\w+):/); if (c) cls = ids[c[1]];
  const m = line.match(/return (\d+);/); if (m && cls) { if (!out[cls].includes(+m[1])) out[cls].push(+m[1]); cls = null; }
}
fs.writeFileSync('../data/class-spells.json', JSON.stringify(out, null, 1));
fs.writeFileSync('../data/spell-learn-level.json', JSON.stringify(learnLevel));
for (const k in out) console.log(k, out[k].length, out[k].join(','));
