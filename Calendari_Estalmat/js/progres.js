/* Progrés local, compatible amb la versió anterior del calendari. */
const KEY = 'advent_cangur_1ESO_demo_v1';
let saved = {};
try {
  saved = JSON.parse(localStorage.getItem(KEY) || '{}') || {};
} catch (error) {
  saved = {};
}
function persist() {
  try {
    localStorage.setItem(KEY, JSON.stringify(saved));
  } catch (error) {
    // El calendari continua funcionant si el navegador bloqueja l'emmagatzematge.
  }
}
