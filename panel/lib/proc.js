// Controle dos processos locais: MariaDB, login, game e clientes do jogo.
const fs = require('fs');
const net = require('net');
const path = require('path');
const { spawn, execFile } = require('child_process');

const ROOT = path.resolve(__dirname, '..', '..');
const P = {
  mariadbBin: path.join(ROOT, 'runtime', 'mariadb', 'bin'),
  mariadbIni: path.join(ROOT, 'runtime', 'mariadb-data', 'my.ini'),
  java: path.join(ROOT, 'runtime', 'jdk21', 'bin', 'java.exe'),
  login: path.join(ROOT, 'server', 'login'),
  game: path.join(ROOT, 'server', 'game'),
  client: path.join(ROOT, 'server', 'client-starloco', 'resources', 'app', 'retroclient'),
  logs: path.join(ROOT, 'logs'),
  gameConfig: path.join(ROOT, 'server', 'game', 'game.config.properties'),
  experience: path.join(ROOT, 'server', 'game', 'scripts', 'data', 'Experience.lua'),
};
fs.mkdirSync(P.logs, { recursive: true });

const PORTS = { mariadb: 3306, login: 450, game: 5555 };

function portOpen(port) {
  return new Promise((resolve) => {
    const s = net.connect({ host: '127.0.0.1', port });
    s.setTimeout(700);
    s.once('connect', () => { s.destroy(); resolve(true); });
    s.once('timeout', () => { s.destroy(); resolve(false); });
    s.once('error', () => resolve(false));
  });
}

async function status() {
  const out = {};
  for (const [k, port] of Object.entries(PORTS)) out[k] = await portOpen(port);
  out.gameStarting = !out.game && (await javaPids('game.jar')).length > 0;
  return out;
}

function runDetached(name, exe, args, cwd) {
  const logFile = path.join(P.logs, `${name}.log`);
  const fd = fs.openSync(logFile, 'a');
  fs.writeSync(fd, `\n===== ${new Date().toISOString()} iniciando ${name} =====\n`);
  const child = spawn(exe, args, { cwd, detached: true, stdio: ['ignore', fd, fd], windowsHide: true });
  child.unref();
  fs.closeSync(fd);
  return child.pid;
}

function powershell(cmd) {
  return new Promise((resolve) => execFile('powershell.exe', ['-NoProfile', '-Command', cmd], { windowsHide: true },
    (err, stdout) => resolve(String(stdout || '').trim())));
}

async function javaPids(jar) {
  const out = await powershell(`Get-CimInstance Win32_Process -Filter "Name='java.exe'" | Where-Object { $_.CommandLine -like '*${jar}*' } | ForEach-Object { $_.ProcessId }`);
  return out.split(/\s+/).filter(Boolean).map(Number);
}

async function killJava(jar) {
  for (const pid of await javaPids(jar)) await powershell(`Stop-Process -Id ${pid} -Force`);
}

const wait = (ms) => new Promise((r) => setTimeout(r, ms));
async function waitFor(fn, timeoutMs, stepMs = 1000) {
  const end = Date.now() + timeoutMs;
  while (Date.now() < end) { if (await fn()) return true; await wait(stepMs); }
  return false;
}

async function startMariaDB() {
  if (await portOpen(PORTS.mariadb)) return 'já estava ligado';
  runDetached('mariadb', path.join(P.mariadbBin, 'mysqld.exe'), [`--defaults-file=${P.mariadbIni}`, '--console'], P.mariadbBin);
  return (await waitFor(() => portOpen(PORTS.mariadb), 30000)) ? 'ligado' : 'não respondeu em 30s (veja logs/mariadb.log)';
}

async function startLogin() {
  if (await portOpen(PORTS.login)) return 'já estava ligado';
  runDetached('login', P.java, ['-jar', 'build/libs/login.jar'], P.login);
  return (await waitFor(() => portOpen(PORTS.login), 30000)) ? 'ligado' : 'não respondeu em 30s (veja logs/login.log)';
}

async function startGame() {
  if (await portOpen(PORTS.game)) return 'já estava ligado';
  if ((await javaPids('game.jar')).length) return 'já está iniciando';
  runDetached('game', P.java, ['-Xmx2g', '-jar', 'build/libs/game.jar'], P.game);
  return 'iniciando (leva ~1-2 min para carregar o mundo)';
}

// Parada limpa do jogo: pede ao PanelBridge para salvar e desligar; se nao responder, forca.
async function stopGame(game) {
  if (await portOpen(PORTS.game)) {
    await game.queueCommand('*', 'STOP');
    if (await waitFor(async () => !(await javaPids('game.jar')).length, 60000, 1500)) return 'salvo e desligado';
  }
  await killJava('game.jar');
  return 'desligado';
}

async function stopLogin() { await killJava('login.jar'); return 'desligado'; }

async function stopMariaDB() {
  await new Promise((r) => execFile(path.join(P.mariadbBin, 'mariadb-admin.exe'), ['-u', 'root', 'shutdown'], { windowsHide: true }, () => r()));
  return 'desligado';
}

function openClients(count) {
  const exe = path.join(P.client, 'Dofus.exe');
  for (let i = 0; i < count; i++) {
    setTimeout(() => spawn(exe, [], { cwd: P.client, detached: true, stdio: 'ignore' }).unref(), i * 1500);
  }
}

function tailLog(name, lines = 80) {
  const file = path.join(P.logs, `${name}.log`);
  if (!fs.existsSync(file)) return '';
  const data = fs.readFileSync(file, 'utf8');
  return data.split(/\r?\n/).slice(-lines).join('\n');
}

// ---- Configuracao do servidor de jogo (rates etc.) ----
function readGameConfig() {
  const out = {};
  for (const line of fs.readFileSync(P.gameConfig, 'utf8').split(/\r?\n/)) {
    const m = line.match(/^([\w.]+)\s(.*)$/);
    if (m && !line.startsWith('#')) out[m[1]] = m[2];
  }
  return out;
}

function writeGameConfig(changes) {
  const lines = fs.readFileSync(P.gameConfig, 'utf8').split(/\r?\n/);
  const done = new Set();
  const out = lines.map((line) => {
    const m = line.match(/^([\w.]+)\s/);
    if (m && m[1] in changes) { done.add(m[1]); return `${m[1]} ${changes[m[1]]}`; }
    return line;
  });
  for (const [k, v] of Object.entries(changes)) if (!done.has(k)) out.push(`${k} ${v}`);
  fs.writeFileSync(P.gameConfig, out.join('\n'));
}

function readLevelCap() {
  const m = fs.readFileSync(P.experience, 'utf8').match(/PlayerLevelCap = (\d+)/);
  return m ? +m[1] : 200;
}

function writeLevelCap(cap) {
  const s = fs.readFileSync(P.experience, 'utf8').replace(/PlayerLevelCap = \d+/, `PlayerLevelCap = ${cap}`);
  fs.writeFileSync(P.experience, s);
}

module.exports = {
  P, status, startMariaDB, startLogin, startGame, stopGame, stopLogin, stopMariaDB, openClients, tailLog,
  readGameConfig, writeGameConfig, readLevelCap, writeLevelCap, portOpen,
};
