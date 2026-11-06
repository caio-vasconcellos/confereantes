const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

function fixture() {
  const target = { value: '', addEventListener() {} };
  const status = {};
  const nodes = { 'original-text': target, 'original-image-status': status };
  let resolve;
  const pending = new Promise(r => { resolve = r; });
  const context = vm.createContext({
    document: { getElementById: id => nodes[id] || null, querySelectorAll: () => [], querySelector: () => null },
    fetch: () => pending, FormData: class { append() {} },
  });
  vm.runInContext(fs.readFileSync(path.join(__dirname, '../src/confereantes/static/app.js'), 'utf8'), context);
  const file = { size: 100 };
  const input = { id: 'original-image', dataset: { ocrTarget: 'original-text' }, files: [file] };
  return { context, input, target, status, finish: () => resolve({ ok: true, json: async () => ({ ok: true, text: 'Extraído' }) }) };
}

test('OCR atrasado preserva uma edição feita durante o upload', async () => {
  const f = fixture();
  const task = f.context.extractImage(f.input);
  f.target.value = 'Texto revisado pelo usuário';
  f.finish();
  await task;
  assert.equal(f.target.value, 'Texto revisado pelo usuário');
  assert.match(f.status.textContent, /preservado/);
});

test('OCR de arquivo substituído não sobrescreve a nova seleção', async () => {
  const f = fixture();
  const task = f.context.extractImage(f.input);
  f.input.files = [{ size: 200 }];
  f.finish();
  await task;
  assert.equal(f.target.value, '');
});
