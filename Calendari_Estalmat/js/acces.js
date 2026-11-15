/* Dates d’obertura i mode de proves. No hi ha autenticació ni servidor. */
const AdventAccess = (() => {
  const year = 2026;
  const timeZone = 'Europe/Madrid';
  const totalDays = 24;
  const isAdmin = new URLSearchParams(window.location.search).get('admin') === '1';
  let simulatedDate = null;
  let allDaysOpen = false;

  // Data civil de Catalunya, independent de la zona horària del navegador.
  function realDate(now = new Date()) {
    const parts = new Intl.DateTimeFormat('en-GB', {
      timeZone, year: 'numeric', month: '2-digit', day: '2-digit'
    }).formatToParts(now);
    const part = name => parts.find(p => p.type === name).value;
    return `${part('year')}-${part('month')}-${part('day')}`;
  }

  function validDate(value) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
    const date = new Date(`${value}T12:00:00Z`);
    return Number.isFinite(date.getTime()) && date.toISOString().slice(0, 10) === value;
  }

  // Els reptes continuen oberts després del 24 de desembre i en anys posteriors.
  function dayLimit(isoDate) {
    if (!validDate(isoDate) || isoDate < `${year}-12-01`) return 0;
    if (isoDate >= `${year}-12-24`) return totalDays;
    return Number(isoDate.slice(8, 10));
  }

  function currentDate() {
    return simulatedDate || realDate();
  }

  function availableUntil() {
    return isAdmin && allDaysOpen ? totalDays : dayLimit(currentDate());
  }

  // Dies civils fins a l’estrena: no dividim hores locals (canvis d’hora).
  function daysUntilOpening(isoDate = currentDate()) {
    if (!validDate(isoDate)) return null;
    const opening = Date.parse(`${year}-12-01T00:00:00Z`);
    const day = Date.parse(`${isoDate}T00:00:00Z`);
    return Math.max(0, Math.round((opening - day) / 86400000));
  }

  function canOpen(day) {
    return Number.isInteger(day) && day >= 1 && day <= availableUntil();
  }

  // Aquestes opcions només tenen efecte quan s’ha obert la pàgina amb ?admin=1.
  function simulate(value) {
    if (!isAdmin || !validDate(value)) return false;
    simulatedDate = value;
    allDaysOpen = false;
    return true;
  }

  function showAll() {
    if (isAdmin) allDaysOpen = true;
  }

  function useRealDate() {
    simulatedDate = null;
    allDaysOpen = false;
  }

  function mode() {
    return allDaysOpen ? 'all' : (simulatedDate ? 'date' : 'real');
  }

  return Object.freeze({
    year, timeZone, totalDays, isAdmin, realDate, validDate, dayLimit,
    currentDate, availableUntil, daysUntilOpening, canOpen, simulate, showAll, useRealDate, mode
  });
})();
