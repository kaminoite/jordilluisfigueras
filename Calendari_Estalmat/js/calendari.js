/* Comportament de la interfície del calendari (sense dependències externes). */
const calendar = document.getElementById('calendar');
const modal = document.getElementById('challenge');
const content = document.getElementById('modal-content');
const labels = ['A', 'B', 'C', 'D', 'E'];
let active = null;
let chosen = null;

function calendarDateLabel(day) {
  const date = new Date(Date.UTC(AdventAccess.year, 11, day));
  return new Intl.DateTimeFormat('ca-ES', {
    weekday: 'long', day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC'
  }).format(date);
}

function appendCalendarBlank() {
  const blank = document.createElement('div');
  blank.className = 'calendar-blank';
  blank.setAttribute('aria-hidden', 'true');
  calendar.append(blank);
}

// Actualitza el recompte, la barra de progrés i les finestretes resoltes.
function update() {
  const limit = AdventAccess.availableUntil();
  updateLanding(limit);
  const correct = problems.filter(p => p.day <= limit && saved[p.day] === p.answer).length;
  document.getElementById('count').textContent = `${correct} de ${problems.length} reptes resolts`;
  document.getElementById('fill').style.width = (correct / problems.length * 100) + '%';
  document.querySelectorAll('.door').forEach(btn => {
    const p = problems[Number(btn.dataset.day) - 1];
    const locked = p.day > limit;
    const won = !locked && p.question && saved[p.day] === p.answer;
    const release = calendarDateLabel(p.day);
    btn.disabled = locked;
    btn.classList.toggle('locked', locked);
    btn.classList.toggle('solved', Boolean(won));
    btn.setAttribute('aria-label', locked
      ? `Dia ${p.day}, ${release}: encara no disponible`
      : `Dia ${p.day}, ${release}: ${p.title}${won ? ', resolt' : ''}`);
    btn.title = locked ? `Disponible a partir de ${release}` : `${release} · ${p.title}`;
    btn.querySelector('.door-mark').textContent = locked ? '🔒' : (won ? '✓' : '✦');
    btn.querySelector('.door-label').textContent = locked
      ? `S’OBRE EL ${String(p.day).padStart(2, '0')}/12`
      : (p.question ? p.short : p.subject);
  });

  // Si es retrocedeix en la data simulada, tanquem també un repte ja obert.
  if (active && !AdventAccess.canOpen(active.day)) {
    if (modal.open) modal.close();
    content.replaceChildren();
    active = null;
    chosen = null;
  }

  const start = document.getElementById('start');
  start.disabled = limit === 0;
  start.textContent = limit === 0 ? 'Comença l’1 de desembre' : `Obre el repte del dia ${limit} ↗`;
  document.getElementById('availability').textContent = limit === 0
    ? `El primer repte s’obrirà l’1 de desembre de ${AdventAccess.year}.`
    : limit === 24
      ? 'Ja pots obrir els 24 reptes del calendari.'
      : `${limit} ${limit === 1 ? 'repte disponible' : 'reptes disponibles'}. El següent s’obre el ${limit + 1} de desembre.`;

  if (AdventAccess.isAdmin) {
    const mode = AdventAccess.mode();
    const date = AdventAccess.currentDate().split('-').reverse().join('/');
    document.getElementById('admin-status').textContent = mode === 'all'
      ? 'Prova: tots els dies oberts. El públic continua veient les obertures segons la data real.'
      : `${mode === 'date' ? 'Data simulada' : 'Data real a Catalunya'}: ${date}. ${limit} de 24 reptes disponibles.`;
    document.getElementById('preview-date').value = AdventAccess.currentDate();
  }
}

// Crea les 24 finestretes a partir de les dades.
function render() {
  calendar.innerHTML = '';
  document.getElementById('calendar-month').textContent = `Desembre de ${AdventAccess.year}`;
  // La setmana comença en dilluns: reservem les caselles prèvies al dia 1.
  const firstWeekday = (new Date(Date.UTC(AdventAccess.year, 11, 1)).getUTCDay() + 6) % 7;
  for (let i = 0; i < firstWeekday; i++) appendCalendarBlank();
  for (const p of problems) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'door' + (!p.question ? ' pending' : '');
    btn.dataset.day = p.day;
    btn.disabled = !AdventAccess.canOpen(p.day);
    btn.setAttribute('aria-label', `Dia ${p.day}: ${p.title}`);
    btn.innerHTML = `<span class="door-mark">✦</span><span class="door-number">${p.day}</span><span class="door-label">${p.question ? p.short : p.subject}</span>`;
    btn.addEventListener('click', () => openDay(p.day));
    calendar.append(btn);
  }
  // Completem la darrera fila sense afegir dies ni reptes nous.
  while (calendar.children.length % 7) appendCalendarBlank();
  update();
}

// Obre un problema i connecta els botons de resposta, pista i solució.
function openDay(day) {
  // No n’hi ha prou amb desactivar el botó: també comprovem l’accés aquí.
  if (!AdventAccess.canOpen(day) || !problems[day - 1]) {
    update();
    return;
  }
  active = problems[day - 1];
  chosen = null;
  document.getElementById('modal-tag').textContent =
    `DIA ${String(day).padStart(2, '0')} · ${active.subject}` +
    (active.difficulty ? ' · ' + ['', 'Fàcil', 'Intermedi', 'Repte'][active.difficulty] : '') +
    ` · ${calendarDateLabel(day)}`;
  document.getElementById('modal-title').textContent = active.title;

  if (!active.question) {
    content.innerHTML = `<p class="question">Aquesta finestreta està reservada per a un problema de ${active.subject.toLowerCase()} d'una edició antiga del Cangur.</p><p>No hi ha cap problema associat a aquesta finestreta.</p>`;
    modal.showModal();
    return;
  }
  const diag = active.diagram ? `<div class="diagram">${diagrams[active.diagram]}${active.diagramCredit ? `<p class="diagram-credit">${active.diagramCredit} <a href="https://arasaac.org/pictograms/es/9067/llama" target="_blank" rel="noopener">Font</a> · <a href="https://arasaac.org/terms-of-use" target="_blank" rel="noopener">Llicència</a><br>Il·lustració de l’animal; no representa el recompte del parc.</p>` : ''}</div>` : '';
  content.innerHTML = `${diag}<p class="question">${active.question}</p>
    <div class="choices" id="choices">${active.options.map((s, i) =>
      `<button type="button" class="choice" data-index="${i}" aria-pressed="false"><strong>${labels[i]}</strong><span>${s}</span></button>`
    ).join('')}</div>
    <div class="actions">
      <button type="button" class="primary" id="check" disabled>Comprova la resposta</button>
      <button type="button" class="secondary" id="hint">Dona'm una pista</button>
      <button type="button" class="secondary" id="solution">Mostra la solució</button>
    </div>
    <div id="feedback" aria-live="polite"></div><div id="reveals"></div>
    <div class="source">Adaptat de Cangur ${active.year}, 1r d’ESO, model ${active.model}, problema ${active.number}. <a href="${active.source}" target="_blank" rel="noopener">Consulta l'enunciat original ↗</a></div>`;

  document.querySelectorAll('.choice').forEach(b => b.addEventListener('click', () => {
    chosen = Number(b.dataset.index);
    document.querySelectorAll('.choice').forEach(t => {
      t.classList.toggle('selected', t === b);
      t.setAttribute('aria-pressed', String(t === b));
    });
    document.getElementById('check').disabled = false;
    document.getElementById('feedback').innerHTML = '';
  }));

  document.getElementById('check').addEventListener('click', () => {
    if (!active || !AdventAccess.canOpen(active.day)) { update(); return; }
    if (chosen === null) return;
    const ok = chosen === active.answer;
    document.getElementById('feedback').innerHTML = `<div class="feedback"><strong>${ok ? 'Correcte!' : 'Encara no.'}</strong> ${ok ? 'Has trobat la resposta.' : 'Pots tornar-ho a provar o consultar la pista.'}</div>`;
    document.querySelectorAll('.choice').forEach(b => {
      b.classList.toggle('right', ok && Number(b.dataset.index) === active.answer);
      b.classList.toggle('wrong', !ok && Number(b.dataset.index) === chosen);
    });
    if (ok) {
      saved[active.day] = active.answer;
      persist();
      update();
    }
  });

  document.getElementById('hint').addEventListener('click', () => {
    if (!active || !AdventAccess.canOpen(active.day)) { update(); return; }
    document.getElementById('reveals').innerHTML = `<div class="reveal"><strong>Pista ·</strong> ${active.hint}</div>`;
  });
  document.getElementById('solution').addEventListener('click', () => {
    if (!active || !AdventAccess.canOpen(active.day)) { update(); return; }
    document.getElementById('reveals').innerHTML = `<div class="reveal"><strong>Solució: ${labels[active.answer]}</strong><br>${active.solution}</div>`;
  });
  modal.showModal();
}

document.getElementById('close').addEventListener('click', () => modal.close());
modal.addEventListener('click', e => { if (e.target === modal) modal.close(); });
document.getElementById('reset').addEventListener('click', () => {
  if (confirm('Vols esborrar el progrés dels 24 reptes?')) {
    saved = {};
    persist();
    update();
  }
});
const startBtn = document.getElementById('start');
if (startBtn) startBtn.addEventListener('click', () => openDay(AdventAccess.availableUntil()));
// El panell no apareix en l’URL habitual i no desa la simulació entre visites.
if (AdventAccess.isAdmin) {
  document.getElementById('admin-panel').hidden = false;
  document.getElementById('progress-note').textContent = 'Progrés temporal de prova: no es desa ni modifica el progrés habitual.';
  document.getElementById('preview-date').addEventListener('change', event => {
    if (AdventAccess.simulate(event.target.value)) update();
    else document.getElementById('admin-status').textContent = 'Introdueix una data vàlida per fer la prova.';
  });
  document.getElementById('preview-teaser').addEventListener('click', () => {
    AdventAccess.simulate(`${AdventAccess.year}-11-30`);
    update();
  });
  document.getElementById('preview-all').addEventListener('click', () => { AdventAccess.showAll(); update(); });
  document.getElementById('preview-real').addEventListener('click', () => { AdventAccess.useRealDate(); update(); });
  const normalUrl = new URL(window.location.href);
  normalUrl.searchParams.delete('admin');
  document.getElementById('preview-exit').href = normalUrl.href;
}

render();
// Una pestanya oberta durant la nit s’actualitza sense haver de recarregar-la.
setInterval(update, 30000);
window.addEventListener('focus', update);
document.addEventListener('visibilitychange', () => { if (!document.hidden) update(); });
