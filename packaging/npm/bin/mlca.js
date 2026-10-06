#!/usr/bin/env node
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const { spawn } = require('node:child_process');
const metadata = require('../package.json');

function resolveUv(env = process.env) {
  const windows = process.platform === 'win32';
  const binary = windows ? 'uv.exe' : 'uv';
  const home = env.USERPROFILE || env.HOME || os.homedir();
  const dirs = (env.PATH || '').split(path.delimiter).filter(Boolean);
  dirs.push(path.join(home, '.local', 'bin'), path.join(home, '.cargo', 'bin'));
  if (env.UV_INSTALL_DIR) dirs.unshift(env.UV_INSTALL_DIR);
  for (const directory of dirs) {
    const file = path.join(directory, binary);
    try { fs.accessSync(file, windows ? fs.constants.F_OK : fs.constants.X_OK); return file; }
    catch { /* Try the next official installation location. */ }
  }
  return null;
}

function launch(args = process.argv.slice(2)) {
  const uv = resolveUv();
  if (!uv) {
    const command = process.platform === 'win32'
      ? 'powershell -NoProfile -Command "irm https://astral.sh/uv/install.ps1 | iex"'
      : 'curl -LsSf https://astral.sh/uv/install.sh | sh';
    console.error(`uv is missing. Install it, then rerun MLCA:\n${command}`);
    process.exitCode = 1;
    return;
  }
  const argv = ['tool', 'run', '--from', `${metadata.mlca.pythonName}==${metadata.version}`, 'mlca', ...args];
  if (process.env.MLCA_LAUNCHER_DEBUG === '1') console.error(JSON.stringify({ command: uv, args: argv }));
  const child = spawn(uv, argv, { stdio: 'inherit', shell: false });
  const handlers = new Map();
  for (const signal of ['SIGINT', 'SIGTERM']) {
    const handler = () => child.kill(signal);
    handlers.set(signal, handler);
    process.on(signal, handler);
  }
  child.on('error', (error) => { console.error(`Cannot run uv: ${error.message}`); process.exitCode = 1; });
  child.on('exit', (code, signal) => {
    for (const [name, handler] of handlers) process.removeListener(name, handler);
    if (signal && process.platform !== 'win32') process.kill(process.pid, signal);
    else process.exitCode = code ?? (signal === 'SIGINT' ? 130 : 143);
  });
}
if (require.main === module) launch();
module.exports = { resolveUv, launch };
