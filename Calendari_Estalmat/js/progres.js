/* Progrés local, compatible amb la versió anterior del calendari. */
const KEY = 'advent_cangur_1ESO_demo_v1';
let saved = {};
try {
  if (!AdventAccess.isAdmin) {
    const stored = JSON.parse(localStorage.getItem(KEY) || '{}');
    saved = stored && typeof stored === 'object' && !Array.isArray(stored) ? stored : {};
  }
} catch (error) {
  saved = {};
}
function persist() {
  // El mode de proves utilitza només memòria temporal: mai no toca el progrés real.
  if (AdventAccess.isAdmin) return;
  try {
    localStorage.setItem(KEY, JSON.stringify(saved));
  } catch (error) {
    // El calendari continua funcionant si el navegador bloqueja l'emmagatzematge.
  }
}
