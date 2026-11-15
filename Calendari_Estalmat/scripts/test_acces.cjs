// Executa: node scripts/test_acces.cjs (sense paquets externs).
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../js/acces.js'), 'utf8');
function access(search = '') {
  const context = { window: { location: { search } }, URLSearchParams, Intl, Date };
  return vm.runInNewContext(source + '\nAdventAccess;', context);
}
const normal = access();
for (const [date, count] of [
  ['2025-12-24', 0], ['2026-11-30', 0], ['2026-12-01', 1],
  ['2026-12-05', 5], ['2026-12-23', 23], ['2026-12-24', 24],
  ['2026-12-25', 24], ['2027-01-01', 24], ['2027-12-01', 24],
  ['invalid', 0], ['2026-02-30', 0], ['2026-13-01', 0]
]) assert.equal(normal.dayLimit(date), count, date);
for (let day = 1; day <= 24; day++) {
  assert.equal(normal.dayLimit(`2026-12-${String(day).padStart(2, '0')}`), day);
}
assert.equal(normal.realDate(new Date('2026-11-30T22:59:59Z')), '2026-11-30');
assert.equal(normal.realDate(new Date('2026-11-30T23:00:00Z')), '2026-12-01');
assert.equal(normal.realDate(new Date('2026-12-05T23:00:00Z')), '2026-12-06');
assert.equal(normal.realDate(new Date('2026-07-01T22:00:00Z')), '2026-07-02');
assert.equal(normal.simulate('2026-12-24'), false);
normal.showAll();
assert.equal(normal.mode(), 'real');
assert.equal(access('?admin=0').isAdmin, false);
assert.equal(access('?date=2026-12-24').isAdmin, false);
const admin = access('?admin=1');
assert.equal(admin.isAdmin, true);
assert.equal(admin.simulate('2026-12-05'), true);
assert.equal(admin.availableUntil(), 5);
for (let d = 1; d <= 24; d++) assert.equal(admin.canOpen(d), d <= 5);
for (const d of [0, 25, -1, 1.5, '1', NaN]) assert.equal(admin.canOpen(d), false);
assert.equal(admin.simulate('2026-02-30'), false);
assert.equal(admin.availableUntil(), 5);
admin.showAll();
assert.equal(admin.availableUntil(), 24);
assert.equal(admin.mode(), 'all');
admin.simulate('2026-11-30');
assert.equal(admin.availableUntil(), 0);
admin.useRealDate();
assert.equal(admin.mode(), 'real');
assert.equal(admin.availableUntil(), admin.dayLimit(admin.realDate()));
assert.equal(access('?admin=1').mode(), 'real'); // Cap simulació persistent.
console.log('OK: obertures diàries, anys, mitjanit a Catalunya, dates invàlides i mode admin.');
