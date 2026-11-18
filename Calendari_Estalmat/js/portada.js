/* Portada d’espera i compte enrere. El calendari no es mostra abans de l’estrena. */
function updateLanding(availableDays) {
  const waiting = availableDays === 0;
  document.getElementById('teaser').hidden = !waiting;
  document.getElementById('calendar-stage').hidden = waiting;
  document.getElementById('start').hidden = waiting;
  document.body.classList.toggle('prelaunch', waiting);

  const nav = document.getElementById('calendar-nav');
  nav.textContent = waiting ? 'Ben aviat' : 'El calendari';
  nav.href = waiting ? '#teaser' : '#calendari';
  document.getElementById('hero-subtitle').textContent = waiting
    ? 'Aquest desembre, cada dia una descoberta.'
    : '24 dies, 24 reptes per descobrir.';
  if (waiting) {
    const days = AdventAccess.daysUntilOpening();
    document.getElementById('countdown').hidden = days === null;
    document.getElementById('countdown-days').textContent = days === null ? '' : String(days);
    document.getElementById('countdown-label').textContent = days === 1
      ? 'dia per començar'
      : 'dies per començar';
  }
}
