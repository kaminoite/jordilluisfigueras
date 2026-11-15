#!/usr/bin/env python3
"""Comprovacions independents dels 24 resultats, per enumeració o càlcul exacte."""
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
problems = json.loads((ROOT / 'data/problemes.json').read_text(encoding='utf-8'))
assert [p['day'] for p in problems] == list(range(1, 25))
for p in problems:
    assert len(p['options']) == len(set(p['options'])) == 5
    assert 0 <= p['answer'] < 5
    assert p['question'] and p['hint'] and p['solution'] and p['source'].startswith('https://')
    if 'diagram' in p:
        assert (ROOT / 'assets/figures' / (p['diagram'] + '.svg')).is_file()


def check(day, expected):
    p = problems[day - 1]
    assert p['options'][p['answer']] == expected, (day, expected)
    print(f"Dia {day:02}: {expected} — correcte")

check(1, f'{120 + (520 - 120) // 2} g')
check(2, str(next(n for n in range(10) if 9 + 2 * n == 17)))
# Valor de cada frase per al follet i per al trol, respectivament.
truth = [(False, False), (True, False), (False, True), (False, True), (True, True)]
assert [i for i, pair in enumerate(truth) if pair == (True, False)] == [problems[2]['answer']]
check(3, 'Jo sempre dic la veritat.')
check(4, str(next((n - 2) ** 2 for n in range(2, 33) if 4 * n - 4 == 32)))
possible = {4 * a + 7 * b for a in range(5) for b in range(3)}
assert set([8, 11, 13, 14, 15]) - possible == {13}
check(5, '13 anelles')
# Hexàgon = 6 triangles equilàters; figura final = 12 triangles iguals.
check(6, f'{int(Fraction(3, 6) * 12)} cm²')
check(7, f'{(92 + 24) // 2} cm')
check(8, f'{next(t for t in range(20) if 23 + 3 * t > 40 + t)} anys')
check(9, str(sum(2 if n % 2 else 1 for n in range(1, 32))))
# Existeix una tria de 5 símbols diferents; no en pot existir cap de 6.
assert len(set(range(5))) == 5
assert all(len(set(draw)) < 6 for draw in product(range(5), repeat=6))
check(10, '6')
assert [n for n in [15, 17, 19, 24, 25] if n not in {1 + 2 * k for k in range(13)}] == [24]
check(11, '24')
check(12, str(len(list(combinations(range(5), 3)))))
check(13, f'{4 * 2 * 8} cm')
check(14, str(sum(max(0, 7 - n) for n in [2, 6, 8, 12])))
assert [2 + 5, 6 + 1, 8 - 1, 12 - 5] == [7] * 4
sums = {sum(x) for x in product([1, 3, 5, 7, 9, 11], repeat=3)}
assert set([13, 21, 25, 30, 33]) - sums == {30}
check(15, '30')
counts = [n for n in range(16) if n + 3 in [3, 6, 8, 10, 12] and n - 2 in [3, 6, 8, 10, 12]]
assert counts == [5]
check(16, str(counts[0]))
check(17, str(11 * 3))
solutions = [(c, d, t) for c, d, t in product(range(4), repeat=3) if d + t == c + t == c + d == 2]
assert solutions == [(1, 1, 1)]
check(18, str(sum(solutions[0])))
check(19, f'{22 + (42 - 22) // (8 - 3) * (6 - 3)} cm')
culprits = [c for c in range(4) if sum([c == 1, c == 2, c != 2, c != 3]) == 1]
assert culprits == [3]
check(20, 'La Dina')
check(21, f'{int(3 * 4 * Fraction(20, 100) / (1 * 3) * 100)} cm')
first_saturdays = [s for s in range(1, 8) if sum(d % 2 == 0 for d in range(s, 31, 7)) == 3]
assert first_saturdays == [2]
assert (25 - first_saturdays[0]) % 7 == 2  # Dos dies després de dissabte.
check(22, 'Dilluns')
check(23, str(len({sum(v) for v in product([1, 6], [2, 7], [3, 8])})))
# Retirar l’última perd: una jugada guanyadora ha de deixar una posició perdedora no buida.
winning = {1: False}
for n in range(2, 20):
    winning[n] = any(not winning[n - k] for k in range(1, min(4, n - 1) + 1))
leaves = [19 - k for k in range(1, 5) if not winning[19 - k]]
assert leaves == [16]
check(24, str(leaves[0]))
print('24/24 resultats comprovats. Estructura de dades i figures: correctes.')
