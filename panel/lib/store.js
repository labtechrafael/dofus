// Banco proprio do painel (SQLite embutido do Node): kits de itens, historico e anotacoes.
const path = require('path');
const { DatabaseSync } = require('node:sqlite');

const db = new DatabaseSync(path.join(__dirname, '..', 'data', 'panel.db'));
db.exec(`
  CREATE TABLE IF NOT EXISTS kits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    items TEXT NOT NULL,            -- JSON: [{template, qty, max, stats}]
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
  );
  CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,
    detail TEXT,
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
  );
  CREATE TABLE IF NOT EXISTS notes (
    key TEXT PRIMARY KEY,
    text TEXT NOT NULL,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
  );
  CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
  );
`);

const log = (action, detail) => db.prepare('INSERT INTO history (action, detail) VALUES (?, ?)').run(action, typeof detail === 'string' ? detail : JSON.stringify(detail));
const history = (limit = 100) => db.prepare('SELECT * FROM history ORDER BY id DESC LIMIT ?').all(limit);

const listKits = () => db.prepare('SELECT * FROM kits ORDER BY name').all().map((k) => ({ ...k, items: JSON.parse(k.items) }));
const saveKit = (name, items) => db.prepare('INSERT INTO kits (name, items) VALUES (?, ?)').run(name, JSON.stringify(items)).lastInsertRowid;
const deleteKit = (id) => db.prepare('DELETE FROM kits WHERE id = ?').run(id);
const getKit = (id) => { const k = db.prepare('SELECT * FROM kits WHERE id = ?').get(id); return k && { ...k, items: JSON.parse(k.items) }; };

const getNote = (key) => db.prepare('SELECT text FROM notes WHERE key = ?').get(key)?.text || '';
const setNote = (key, text) => db.prepare(`INSERT INTO notes (key, text, updated_at) VALUES (?, ?, datetime('now', 'localtime'))
  ON CONFLICT(key) DO UPDATE SET text = excluded.text, updated_at = datetime('now', 'localtime')`).run(key, text);

const getSetting = (key, def = null) => db.prepare('SELECT value FROM settings WHERE key = ?').get(key)?.value ?? def;
const setSetting = (key, value) => db.prepare(`INSERT INTO settings (key, value) VALUES (?, ?)
  ON CONFLICT(key) DO UPDATE SET value = excluded.value`).run(key, String(value));

module.exports = { db, log, history, listKits, saveKit, deleteKit, getKit, getNote, setNote, getSetting, setSetting };
