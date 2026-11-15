/* Comportament de la interfície del calendari (sense dependències externes). */
const calendar = document.getElementById('calendar');
const modal = document.getElementById('challenge');
const content = document.getElementById('modal-content');
const labels = ['A', 'B', 'C', 'D', 'E'];
let active = null;
let chosen = null;

// Actualitza el recompte, la barra de progrés i les finestretes resoltes.
function update() {
  const correct = problems.filter(p => saved[p.day] === p.answer).length;
  document.getElementById('count').textContent = `${correct} de ${problems.length} reptes resolts`;
  document.getElementById('fill').style.width = (correct / problems.length * 100) + '%';
  document.querySelectorAll('.door').forEach(btn => {
    const p = problems[Number(btn.dataset.day) - 1];
    const won = p.question && saved[p.day] === p.answer;
    btn.classList.toggle('solved', Boolean(won));
    btn.querySelector('.door-mark').textContent = won ? '✓' : (p.question ? '✦' : '·');
  });
}

// Crea les 24 finestretes a partir de les dades.
function render() {
  calendar.innerHTML = '';
  for (const p of problems) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'door' + (!p.question ? ' pending' : '');
    btn.dataset.day = p.day;
    btn.setAttribute('aria-label', `Dia ${p.day}: ${p.title}`);
    btn.innerHTML = `<span class="door-mark">✦</span><span class="door-number">${p.day}</span><span class="door-label">${p.question ? p.short : p.subject}</span>`;
    btn.addEventListener('click', () => openDay(p.day));
    calendar.append(btn);
  }
  update();
}

// Obre un problema i connecta els botons de resposta, pista i solució.
function openDay(day) {
  active = problems[day - 1];
  chosen = null;
  document.getElementById('modal-tag').textContent =
    `DIA ${String(day).padStart(2, '0')} · ${active.subject}` +
    (active.difficulty ? ' · ' + ['', 'Fàcil', 'Intermedi', 'Repte'][active.difficulty] : '');
  document.getElementById('modal-title').textContent = active.title;

  if (!active.question) {
    content.innerHTML = `<p class="question">Aquesta finestreta està reservada per a un problema de ${active.subject.toLowerCase()} d'una edició antiga del Cangur.</p><p>No hi ha cap problema associat a aquesta finestreta.</p>`;
    modal.showModal();
    return;
  }
  const diag = active.diagram ? `<div class="diagram">${diagrams[active.diagram]}</div>` : '';
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
    document.getElementById('reveals').innerHTML = `<div class="reveal"><strong>Pista ·</strong> ${active.hint}</div>`;
  });
  document.getElementById('solution').addEventListener('click', () => {
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
if (startBtn) startBtn.addEventListener('click', () => openDay(1));
document.getElementById('print').addEventListener('click', () => window.print());
render();
