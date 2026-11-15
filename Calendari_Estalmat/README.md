# Calendari Estalmat

Calendari d’advent de 24 reptes per a l’alumnat d’Estalmat Catalunya i per a qui voldria participar-hi en el futur.

## Obrir el calendari

Descomprimeix el projecte i obre `index.html` amb un navegador modern. No cal instal·lar res ni posar en marxa cap servidor. Els problemes, les figures, els logotips i les fonts són locals; només cal connexió per visitar els enllaços externs.

Si vols compartir un únic fitxer, utilitza `dist/Calendari_Estalmat.html`, que conté tots els recursos incorporats.

## On s’edita cada cosa?

| Fitxer o carpeta | Contingut editable |
| --- | --- |
| `index.html` | Capçalera, títols, públic destinatari, instruccions i peu amb els logotips |
| `css/estils.css` | Colors, tipografia, disseny, mòbil i impressió; agrupats en vuit seccions |
| `data/problemes.json` | Els 24 problemes: enunciat, opcions, resposta, pista, solució i font |
| `assets/figures/*.svg` | Les tres figures geomètriques, en fitxers independents |
| `assets/` | Logotips d’Estalmat Catalunya, FEEMCAT i SCM |
| `assets/fonts/` | Tipografies locals Cirka i Titillium Web |
| `js/acces.js` | Any, zona horària, dates d’obertura, compte enrere i mode de proves |
| `js/portada.js` | Alternança entre la portada d’expectativa i el calendari |
| `js/progres.js` | Lectura i desament del progrés; proves separades del progrés real |
| `js/calendari.js` | Finestretes, diàleg, respostes, pistes, solucions i botons |
| `scripts/build.py` | Generació dels fitxers derivats i de l’HTML autocontingut |
| `scripts/verifica.py` | Comprovacions matemàtiques independents dels 24 resultats |
| `scripts/test_acces.cjs` | Proves de dates, zona horària i mode admin amb Node.js, sense paquets externs |
| `docs/REVISIO.md` | Revisió matemàtica, precisions introduïdes i correspondència amb les fonts |
| `docs/RECURSOS.md` | Procedència dels logotips i les fonts |

`data/problemes.js`, `js/diagrames.js` i `dist/Calendari_Estalmat.html` són fitxers **generats**. Cal editar les fonts de la taula i regenerar-los; així no hi ha dues còpies per mantenir manualment.

## Modificar un problema

Edita l’objecte corresponent al dia dins de `data/problemes.json`.

- `day`: número de dia, de l’1 al 24.
- `short`, `title`, `subject`: text de la finestreta, títol i tema.
- `difficulty`: 1 = fàcil; 2 = intermedi; 3 = repte.
- `question`, `options`: enunciat i cinc respostes possibles.
- `answer`: índex de l’opció correcta, començant per **0**: A = 0, B = 1, C = 2, D = 3, E = 4.
- `hint`, `solution`: pista i explicació raonada.
- `year`, `model`, `number`, `source`: referència a la prova original del Cangur.
- `diagram`: nom del fitxer SVG sense extensió, si hi ha figura.

El JSON utilitza cometes dobles i no admet comentaris ni comes després de l’últim element. Els textos s’introdueixen al DOM com a HTML: edita’ls només amb contingut de confiança.

Des de la carpeta del projecte:

```bash
python3 scripts/build.py
python3 scripts/verifica.py
```

Només es necessita Python 3, sense paquets externs. Si canvies les dades matemàtiques d’un problema, actualitza també el càlcul independent corresponent de `verifica.py`.

## Decisions de funcionament

El calendari correspon al desembre de **2026**. Abans de l’1 de desembre es mostra una portada d’expectativa amb un compte enrere en dies. La graella, el progrés i el botó d’obertura queden ocults des de l’HTML inicial, sense aparèixer breument mentre es carrega la pàgina. Es mantenen visibles la presentació, la informació sobre Estalmat i els tres logotips. L’1 de desembre la portada dona pas automàticament al calendari. De l’1 al 24 s’obre el repte del dia i es conserven els anteriors. Després del 24, inclosos els anys següents, tots continuen disponibles. L’obertura segueix la mitjanit de Catalunya (`Europe/Madrid`), a partir del rellotge del dispositiu. Una pestanya oberta es revisa cada 30 segons i en recuperar el focus.

El fitxer `js/acces.js` concentra l’any i la zona horària. Si canvies l’edició, actualitza també l’any dels textos d’`index.html` i les dates esperades de les proves. El progrés és local a cada navegador; no s’envia a cap servidor. Es conserva la clau d’emmagatzematge anterior per mantenir la compatibilitat si el calendari s’allotja al mateix origen. Obrir-lo des d’una altra ubicació o navegador pot iniciar un progrés nou.

Les preguntes continuen sent adaptacions de Cangur de 1r d’ESO. La invitació a participar s’adreça tant a l’alumnat actual d’Estalmat com al futur alumnat i no pressuposa haver fet el programa.

## Mode d’administració per fer proves

Afegeix `?admin=1` al final de l’adreça, **abans** de qualsevol `#calendari`. Si l’adreça ja té paràmetres, afegeix `&admin=1`.

- Projecte modular: `index.html?admin=1`.
- Fitxer autònom: `Calendari_Estalmat.html?admin=1`.
- Si el servidor serveix `index.html` per defecte: `.../calendari/?admin=1`.

Apareix un panell destacat amb les opcions següents:

| Control | Efecte |
| --- | --- |
| Data simulada | Permet provar qualsevol data. El 30/11/2026: cap repte; el 05/12/2026: dies 1–5; el 24/12/2026: tots. |
| Mostra la portada | Simula el 30/11/2026 per comprovar la portada, amb un dia de compte enrere. |
| Obre tots els dies | Desbloqueja els 24 reptes només en aquesta vista de proves. |
| Data real | Torna a les obertures corresponents al dia actual; el panell segueix actiu. |
| Surt del mode de proves | Elimina el paràmetre `admin` i torna a la vista habitual. |

El mode de proves s’inicia amb la data real. No conserva la data simulada en recarregar. El seu progrés és temporal i independent: resoldre problemes o reiniciar-lo no modifica el progrés habitual.

És un **mode de previsualització, sense contrasenya ni autenticació**. No comparteixis l’enllaç de proves amb l’alumnat si no vols que hi accedeixi fàcilment. En una web estàtica, els enunciats i les respostes ja són als fitxers descarregats; el bloqueig temporal és de la interfície. No és una protecció contra qui inspeccioni el codi, canviï el rellotge o afegeixi `admin=1`. Per mantenir realment secrets els problemes futurs caldria servir-los des d’un servidor amb data pròpia i autenticació per a l’administració.

Per verificar les dates sense instal·lar cap paquet extern, des de la carpeta del projecte:

```bash
node scripts/test_acces.cjs
```

Les proves cobreixen tots els dies de desembre, el període anterior i posterior, el canvi d’any, la mitjanit a Catalunya, dates invàlides, el compte enrere i les opcions d’administració.


## Dies de la setmana i autoria

El calendari es distribueix en set columnes, de dilluns a diumenge, amb les dates a la columna que correspon. L’1 de desembre de 2026 és dimarts i el 24 és dijous. Les caselles buides anteriors a l’1 i posteriors al 24 no són interactives. La graella no afegeix nous reptes.

En mòbils s’utilitzen les abreviatures dl., dt., dc., dj., dv., ds. i dg. Les finestretes mostren el número i l’estat; el nom complet del dia i el títol del problema continuen disponibles en l’etiqueta accessible i en obrir el repte. La capçalera dels dies queda oculta juntament amb el calendari abans de l’estrena.

El peu de pàgina inclou el crèdit «Autor: Jordi-Lluís Figueras Romero», visible també a la portada d’expectativa i en imprimir.
