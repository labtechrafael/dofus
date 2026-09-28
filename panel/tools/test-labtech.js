// Teste do Mundo LabTech pelo protocolo: entra com um personagem, fala com o Mestre Malte (ganha a Manopla)
// e usa o elevador do Estagiario para ir ao Bar das Celebridades.
// Uso: node test-labtech.js <conta> <senha> <personagem>
const net = require('net');
const [account, password, charName] = process.argv.slice(2);
const HASH = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_';
const crypt = (pass, key) => '#1' + [...pass].map((ch, i) => { const p = ch.charCodeAt(0), k = key.charCodeAt(i); return HASH[(Math.floor(p / 16) + k) % 64] + HASH[((p % 16) + k) % 64]; }).join('');

function connect(port, onPacket) {
  const s = net.connect({ host: '127.0.0.1', port });
  let buf = '';
  s.on('data', (d) => { buf += d.toString('utf8'); let i; while ((i = buf.indexOf('\0')) >= 0) { const p = buf.slice(0, i); buf = buf.slice(i + 1); if (p) onPacket(p); } });
  s.send = (p) => { console.log('  >>', p); s.write(p + '\n\0'); };
  return s;
}
const show = (p) => console.log('  <<', p.length > 200 ? p.slice(0, 200) + '…' : p);

const login = connect(450, (p) => {
  if (p.startsWith('HC')) { login.send('1.39.8e'); login.write(`${account}\n${crypt(password, p.slice(2))}\n\0`); login.send('Af'); }
  else if (p.startsWith('AlK')) { login.send('Ax'); login.send('AX601'); }
  else if (p.startsWith('AYK')) { const [hp, t] = p.slice(3).split(';'); login.end(); game(+hp.split(':')[1], t); }
});

function game(port, ticket) {
  const npcs = {};         // templateId -> id no mapa
  let step = 'login';
  let dialog = null;       // {q, answers}
  const g = connect(port, (p) => {
    if (p.startsWith('HG')) setTimeout(() => g.send('AT' + ticket), 700);
    else if (p.startsWith('ATK')) { g.send('AV'); g.send('AL'); }
    else if (p.startsWith('ALK') && step === 'login') {
      const c = p.split('|').slice(2).map((x) => x.split(';')).find((x) => (x[1] || '').toLowerCase() === charName.toLowerCase());
      step = 'select'; g.send('AS' + c[0]);
    } else if (p.startsWith('ASK')) { g.send('GC1'); }
    else if (p.startsWith('GDM')) { show(p); g.send('GI'); }
    else if (p.startsWith('GM|')) {
      for (const e of p.slice(3).split('|')) {
        const f = e.slice(1).split(';');
        if (e[0] === '+' && f[5] === '-4') npcs[+f[4]] = f[3];   // NPC: cell;dir;0;id;template;-4;...
      }
      if (Object.keys(npcs).length && step === 'select') { show('NPCs no mapa: ' + JSON.stringify(npcs)); step = 'malte'; setTimeout(() => g.send('DC' + npcs[3000]), 300); }
      if (step === 'bar') { show('NPCs no Bar: ' + Object.keys(npcs).length); setTimeout(() => { g.end(); process.exit(0); }, 500); }
    } else if (p.startsWith('DQ')) {
      const [q, ans] = p.slice(2).split('|');
      dialog = { q: +q, answers: (ans || '').split(';').filter(Boolean).map(Number) };
      show(p);
      if (step === 'malte') {
        // boas_vindas -> "E perigoso ir sozinho?" (3a resposta); zelda -> pegar manopla (1a)
        const a = dialog.answers.length >= 3 ? dialog.answers[2] : dialog.answers[0];
        if (dialog.answers.length === 1) step = 'malte_pegou';
        g.send(`DR${dialog.q}|${a}`);
      } else if (step === 'malte_pegou') {
        g.send('DV'); step = 'estagiario'; setTimeout(() => g.send('DC' + npcs[3001]), 300);
      } else if (step === 'estagiario') {
        step = 'bar'; for (const k of Object.keys(npcs)) delete npcs[k];
        g.send(`DR${dialog.q}|${dialog.answers[4]}`);   // 5o destino = Bar das Celebridades
      }
    } else if (/^(OAK|Im|BN|DV|DCK)/.test(p)) show(p);
  });
  setTimeout(() => { console.log('timeout'); process.exit(1); }, 20000);
}
