'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync, spawn } = require('node:child_process');
const launcher = path.resolve(__dirname, '../bin/mlca.js');
const metadata = require('../package.json');

function fixture() {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'mlca-npm-'));
  const bin = path.join(root, 'bin'); fs.mkdirSync(bin);
  const log = path.join(root, 'calls.json');
  const script = `import json, os, sys\ndef main():\n    open(os.environ['FAKE_UV_LOG'], 'w').write(json.dumps(sys.argv[1:]))\n    sys.exit(int(os.environ.get('FAKE_UV_EXIT','0')))\n`;
  let directory = bin;
  if (process.platform === 'win32') {
    // A wheel entry point gives the fixture a real Windows .exe, rather than invoking a .cmd shell.
    const python = process.env.MLCA_TEST_PYTHON || 'python';
    const uv = process.env.MLCA_TEST_UV || 'uv';
    const envDir = path.join(root, 'env');
    const wheel = path.join(root, 'fake_uv-0.0.0-py3-none-any.whl');
    const build = `import zipfile,sys\nw=zipfile.ZipFile(sys.argv[1],'w')\nw.writestr('fake_uv.py',sys.argv[2])\nw.writestr('fake_uv-0.0.0.dist-info/METADATA','Metadata-Version: 2.1\\nName: fake-uv\\nVersion: 0.0.0\\n')\nw.writestr('fake_uv-0.0.0.dist-info/WHEEL','Wheel-Version: 1.0\\nGenerator: fixture\\nRoot-Is-Purelib: true\\nTag: py3-none-any\\n')\nw.writestr('fake_uv-0.0.0.dist-info/entry_points.txt','[console_scripts]\\nuv=fake_uv:main\\n')\nw.writestr('fake_uv-0.0.0.dist-info/RECORD','')\nw.close()`;
    let result = spawnSync(python, ['-c', build, wheel, script], {encoding:'utf8'});
    assert.equal(result.status, 0, result.stderr);
    result = spawnSync(uv, ['venv', envDir, '--python', python], {encoding:'utf8'});
    assert.equal(result.status, 0, result.stderr);
    result = spawnSync(uv, ['pip','install','--offline','--python',path.join(envDir,'Scripts','python.exe'),wheel], {encoding:'utf8'});
    assert.equal(result.status, 0, result.stderr);
    directory = path.join(envDir,'Scripts');
  } else {
    const code = `#!${process.execPath}\nconst fs=require('node:fs'); fs.writeFileSync(process.env.FAKE_UV_LOG,JSON.stringify(process.argv.slice(2))); process.exit(Number(process.env.FAKE_UV_EXIT||0));\n`;
    fs.writeFileSync(path.join(bin, 'uv'), code, {mode:0o755});
  }
  const env = {...process.env, PATH: directory, HOME:root, USERPROFILE:root, UV_INSTALL_DIR:directory, FAKE_UV_LOG:log};
  return {root,log,env,cleanup:()=>fs.rmSync(root,{recursive:true,force:true})};
}

test('forwards arguments and pins the Python artifact', () => {
  const f=fixture();
  try {
    const result=spawnSync(process.execPath,[launcher,'--project','a path with spaces','status','--json'],{env:{...f.env,MLCA_LAUNCHER_DEBUG:'1'},encoding:'utf8'});
    assert.equal(result.status,0,result.stderr);
    assert.deepEqual(JSON.parse(fs.readFileSync(f.log)),['tool','run','--from',`${metadata.mlca.pythonName}==${metadata.version}`,'mlca','--project','a path with spaces','status','--json']);
    assert.match(result.stderr,/command/);
  } finally {f.cleanup();}
});

test('forwards nonzero exit status', () => {
  const f=fixture();
  try {
    const result=spawnSync(process.execPath,[launcher],{env:{...f.env,FAKE_UV_EXIT:'7'},encoding:'utf8'});
    assert.equal(result.status,7,result.stderr);
  } finally {f.cleanup();}
});

test('missing uv prints install instructions without downloading', () => {
  const root=fs.mkdtempSync(path.join(os.tmpdir(),'mlca-missing-'));
  try {
    const result=spawnSync(process.execPath,[launcher],{env:{...process.env,PATH:root,HOME:root,USERPROFILE:root,UV_INSTALL_DIR:root},encoding:'utf8'});
    assert.equal(result.status,1);
    assert.match(result.stderr,/uv is missing/);
    assert.match(result.stderr,/astral.sh\/uv\/install/);
  } finally {fs.rmSync(root,{recursive:true,force:true});}
});

test('forwards SIGTERM to the child', {skip:process.platform==='win32'}, async () => {
  const root=fs.mkdtempSync(path.join(os.tmpdir(),'mlca-signal-'));
  const uv=path.join(root,'uv');
  const marker=path.join(root,'terminated');
  const ready=path.join(root,'ready');
  fs.writeFileSync(uv,`#!${process.execPath}\nconst fs=require('node:fs');fs.writeFileSync(process.env.READY,'yes');process.on('SIGTERM',()=>{fs.writeFileSync(process.env.MARKER,'yes');process.exit(143)});setInterval(()=>{},1000);`,{mode:0o755});
  const child=spawn(process.execPath,[launcher],{env:{...process.env,PATH:root,UV_INSTALL_DIR:root,HOME:root,READY:ready,MARKER:marker},stdio:'ignore'});
  try {
    const deadline=Date.now()+5000;
    while(!fs.existsSync(ready)&&Date.now()<deadline) await new Promise(r=>setTimeout(r,20));
    assert.ok(fs.existsSync(ready));
    const exited=new Promise(resolve=>child.once('exit',(code,signal)=>resolve({code,signal})));
    child.kill('SIGTERM');
    const result=await exited;
    assert.equal(result.code,143);
    assert.ok(fs.existsSync(marker));
  } finally {child.kill();fs.rmSync(root,{recursive:true,force:true});}
});
