// Atributos de itens no formato do Dofus 1: "efeitoHex#param1Hex#param2Hex#param3Hex#dados", separados por virgula.
const L = require('./lang');

// Atributos editaveis no painel: [id do efeito positivo, id do efeito negativo (ou null), rotulo, grupo]
const STATS = [
  [111, 168, 'PA', 'Principais'],
  [128, 169, 'PM', 'Principais'],
  [117, 116, 'Alcance', 'Principais'],
  [182, null, 'Invocações', 'Principais'],
  [125, 153, 'Vitalidade', 'Características'],
  [124, 156, 'Sabedoria', 'Características'],
  [118, 157, 'Força', 'Características'],
  [126, 155, 'Inteligência', 'Características'],
  [123, 152, 'Sorte', 'Características'],
  [119, 154, 'Agilidade', 'Características'],
  [174, 175, 'Iniciativa', 'Características'],
  [176, 177, 'Prospecção', 'Características'],
  [158, 159, 'Pods', 'Características'],
  [112, 145, 'Danos', 'Dano'],
  [138, 186, '% Danos', 'Dano'],
  [115, 171, 'Críticos', 'Dano'],
  [178, 179, 'Curas', 'Dano'],
  [225, null, 'Danos de armadilha', 'Dano'],
  [226, null, '% Danos de armadilha', 'Dano'],
  [220, null, 'Reenvio de danos', 'Dano'],
  [214, 219, '% Res. Neutro', 'Resistências'],
  [210, 215, '% Res. Terra', 'Resistências'],
  [213, 218, '% Res. Fogo', 'Resistências'],
  [211, 216, '% Res. Água', 'Resistências'],
  [212, 217, '% Res. Ar', 'Resistências'],
  [244, 249, 'Res. Neutro', 'Resistências'],
  [240, 245, 'Res. Terra', 'Resistências'],
  [243, 248, 'Res. Fogo', 'Resistências'],
  [241, 246, 'Res. Água', 'Resistências'],
  [242, 247, 'Res. Ar', 'Resistências'],
  [160, 162, 'Esquiva PA', 'Resistências'],
  [161, 163, 'Esquiva PM', 'Resistências'],
];

const byPositive = new Map(STATS.map((s) => [s[0], s]));
const byNegative = new Map(STATS.filter((s) => s[1]).map((s) => [s[1], s]));

function parseLine(line) {
  const [idHex, p1 = '0', p2 = '0', p3 = '0', dice = ''] = line.split('#');
  return { id: parseInt(idHex, 16), p1: parseInt(p1, 16) || 0, p2: parseInt(p2, 16) || 0, p3: parseInt(p3, 16) || 0, dice, raw: line };
}

// Valor fixo de um efeito de item (objetos ja criados guardam o valor em param1; o dado "0d0+N" tambem traz N).
function lineValue(e) {
  const m = /^(\d+)d(\d+)\+(-?\d+)$/.exec(e.dice || '');
  if (e.p1) return e.p1;
  if (m && m[1] === '0') return +m[3];
  return 0;
}

// Separa os atributos conhecidos (editaveis) dos demais efeitos (dano de arma, textos, etc.), que sao preservados.
function split(stats) {
  const values = {};
  const others = [];
  for (const line of String(stats || '').split(',').filter(Boolean)) {
    const e = parseLine(line);
    if (byPositive.has(e.id)) values[e.id] = (values[e.id] || 0) + lineValue(e);
    else if (byNegative.has(e.id)) { const s = byNegative.get(e.id); values[s[0]] = (values[s[0]] || 0) - lineValue(e); }
    else others.push({ raw: line, text: describe(e) });
  }
  return { values, others };
}

const hex = (n) => Math.abs(Math.trunc(n)).toString(16);

// Monta a string de atributos a partir dos valores do formulario + efeitos preservados.
function build(values, others = []) {
  const lines = [];
  for (const [pos, neg] of STATS) {
    const v = Math.trunc(Number(values[pos]) || 0);
    if (!v) continue;
    const id = v > 0 || !neg ? pos : neg;
    lines.push(`${hex(id)}#${hex(v)}#0#0#0d0+${Math.abs(v)}`);
  }
  return [...lines, ...others.map((o) => (typeof o === 'string' ? o : o.raw))].join(',');
}

function describe(e) {
  const tpl = L.effects[e.id]?.d;
  if (!tpl) return `Efeito ${e.id} (${e.raw})`;
  const args = { 1: e.p1, 2: e.p2, 3: e.p3 };
  return tpl
    .replace(/\{~1~2 a \}/g, e.p2 ? ` a ` : '')
    .replace(/#(\d)\{[^}]*\}/g, (_, n) => args[n] || '')
    .replace(/#(\d)/g, (_, n) => (args[n] || n === '2' ? (args[n] || '') : ''))
    .replace(/\s+/g, ' ')
    .trim();
}

// Valores maximos de um modelo de item (ex.: "76#1#14#0#1d20+0" -> Forca 20); usado no botao "stats maximos".
function templateMax(stats) {
  const values = {};
  for (const line of String(stats || '').split(',').filter(Boolean)) {
    const e = parseLine(line);
    const v = Math.max(e.p1, e.p2);
    if (byPositive.has(e.id)) values[e.id] = (values[e.id] || 0) + v;
    else if (byNegative.has(e.id)) { const s = byNegative.get(e.id); values[s[0]] = (values[s[0]] || 0) - Math.min(e.p1 || v, e.p2 || v); }
  }
  return values;
}

function describeAll(stats) {
  return String(stats || '').split(',').filter(Boolean).map((l) => describe(parseLine(l)));
}

module.exports = { STATS, split, build, describe, describeAll, parseLine, templateMax };
