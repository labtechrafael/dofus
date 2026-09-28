// Cliente de teste do protocolo Dofus 1 (sem interface): faz login, cria/seleciona um personagem e fica online.
// Uso: node test-client.js <conta> <senha> <nomePersonagem> <classe 1-12> [segundosOnline]
const net = require('net');

const [account, password, charName, cls = '8', seconds = '30'] = process.argv.slice(2);
if (!charName) { console.log('Uso: node test-client.js conta senha nome classe [segundos]'); process.exit(1); }

const HASH = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_';
function cryptPassword(pass, key) {
  let out = '#1';
  for (let i = 0; i < pass.length; i++) {
    const p = pass.charCodeAt(i), k = key.charCodeAt(i);
    out += HASH[(Math.floor(p / 16) + k) % 64] + HASH[((p % 16) + k) % 64];
  }
  return out;
}

function connect(port, onPacket) {
  const sock = net.connect({ host: '127.0.0.1', port });
  let buf = '';
  sock.on('data', (d) => {
    buf += d.toString('utf8');
    let i;
    while ((i = buf.indexOf('\0')) >= 0) { const pkt = buf.slice(0, i); buf = buf.slice(i + 1); if (pkt) onPacket(pkt); }
  });
  sock.sendPkt = (p) => { console.log('  >>', p.startsWith('#1') ? '#1***' : p); sock.write(p + '\n\0'); };
  return sock;
}

const log = (p) => console.log('  <<', p.length > 160 ? p.slice(0, 160) + '…' : p);

const login = connect(450, (p) => {
  log(p);
  if (p.startsWith('HC')) {
    const key = p.slice(2);
    login.sendPkt('1.39.8e');
    login.write(`${account}\n${cryptPassword(password, key)}\n\0`);
    login.sendPkt('Af');
  } else if (p.startsWith('AlK')) {
    login.sendPkt('Ax');
    login.sendPkt('AX601');
  } else if (p.startsWith('AYK')) {
    const [hostPort, ticket] = p.slice(3).split(';');
    login.end();
    game(+hostPort.split(':')[1], ticket);
  } else if (p.startsWith('AlE') || p.startsWith('AXE')) {
    console.log('Falha no login:', p); process.exit(2);
  }
});

function game(port, ticket) {
  let created = false;
  const g = connect(port, (p) => {
    const interesting = /^(HG|ATK|AV|ALK|AAK|AAE|ASK|ASE|GCK|BAT|Im|OAK|OQ|SL|AN|As|M0)/.test(p);
    if (interesting || process.env.ALL) log(p);
    if (p.startsWith('HG')) setTimeout(() => g.sendPkt('AT' + ticket), 700);
    else if (p.startsWith('ATK')) { g.sendPkt('AV'); g.sendPkt('AL'); }
    else if (p.startsWith('ALK')) {
      const chars = p.split('|').slice(2).map((c) => c.split(';'));
      const mine = chars.find((c) => (c[1] || '').toLowerCase() === charName.toLowerCase());
      if (mine) g.sendPkt('AS' + mine[0]);
      else if (!created) { created = true; g.sendPkt(`AA${charName}|${cls}|0|-1|-1|-1`); }
      else { console.log('Personagem não foi criado'); process.exit(3); }
    } else if (p.startsWith('AAK')) g.sendPkt('AL');
    else if (p.startsWith('AAE')) { console.log('Erro ao criar personagem:', p); process.exit(3); }
    else if (p.startsWith('ASK')) {
      g.sendPkt('GC1');
      console.log(`== ${charName} ONLINE por ${seconds}s ==`);
      setTimeout(() => { console.log('== saindo =='); g.end(); process.exit(0); }, +seconds * 1000);
    }
  });
  g.on('error', (e) => { console.log('erro', e.message); process.exit(4); });
}
login.on('error', (e) => { console.log('erro login', e.message); process.exit(4); });
