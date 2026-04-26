"use strict";

const DATA_URL = "assets/data/provinces.json";

const MODES = {
  STUDY_COMMUNITIES: "study_communities",
  STUDY_PROVINCES: "study_provinces",
  QUIZ_COMMUNITIES: "quiz_communities",
  QUIZ_PROVINCES: "quiz_provinces"
};

const PALETTE = [
  "#dbeafe", "#dcfce7", "#fef3c7", "#fae8ff",
  "#ffedd5", "#ccfbf1", "#e0e7ff", "#fee2e2"
];

const UI = {
  en: {
    htmlLang: "en",
    appTitle: "Spain Study Map",
    studyCommunities: "Study communities",
    studyProvinces: "Study provinces",
    quizCommunities: "Quiz 5 communities",
    quizProvinces: "Quiz 8 provinces",
    subtitleStudyCommunities: "Study Spain's autonomous communities with visible names.",
    subtitleStudyProvinces: "Study Spain's provinces with visible names.",
    subtitleQuizCommunities: "Find 5 randomly selected autonomous communities.",
    subtitleQuizProvinces: "Find 8 randomly selected provinces.",
    loading: "Loading local map data...",
    loadError: "The local map assets could not be loaded. Run fetch-assets.sh before uploading, then serve this directory from a web server or GitHub Pages.",
    quiz: "Quiz",
    restart: "Restart",
    noQuizLoaded: "No quiz loaded",
    chooseQuiz: "Choose one of the quiz modes to generate random questions.",
    question: "Question",
    clickThisArea: "Click this area",
    labelsHidden: "Map labels are deliberately hidden during quizzes.",
    quizBadge: "Quiz mode: names hidden",
    finalScore: "Final score",
    correct: "Correct",
    clicked: "Clicked",
    studyMode: "Study mode",
    selectedCommunity: "Selected community",
    selectedProvince: "Selected province",
    instruction: "Instruction",
    studyInstruction: "Click a region on the map. In this mode, names are visible so you can study before quizzing.",
    communityDetails: "{name} is an autonomous community of Spain.",
    cityDetails: "{name} is an autonomous city of Spain.",
    provinceDetails: "{province} belongs to {community}.",
    note: ""
  },
  es: {
    htmlLang: "es",
    appTitle: "Mapa de estudio de España",
    studyCommunities: "Estudiar comunidades",
    studyProvinces: "Estudiar provincias",
    quizCommunities: "Prueba: 5 comunidades",
    quizProvinces: "Prueba: 8 provincias",
    subtitleStudyCommunities: "Estudia las comunidades autónomas de España con nombres visibles.",
    subtitleStudyProvinces: "Estudia las provincias de España con nombres visibles.",
    subtitleQuizCommunities: "Encuentra 5 comunidades autónomas elegidas al azar.",
    subtitleQuizProvinces: "Encuentra 8 provincias elegidas al azar.",
    loading: "Cargando datos locales del mapa...",
    loadError: "No se pudieron cargar los archivos locales del mapa. Ejecuta fetch-assets.sh antes de subirlo y sirve esta carpeta desde un servidor web o GitHub Pages.",
    quiz: "Prueba",
    restart: "Reiniciar",
    noQuizLoaded: "No hay prueba cargada",
    chooseQuiz: "Elige uno de los modos de prueba para generar preguntas aleatorias.",
    question: "Pregunta",
    clickThisArea: "Haz clic en esta zona",
    labelsHidden: "Los nombres del mapa están ocultos deliberadamente durante las pruebas.",
    quizBadge: "Modo prueba: nombres ocultos",
    finalScore: "Puntuación final",
    correct: "Correcto",
    clicked: "Marcaste",
    studyMode: "Modo de estudio",
    selectedCommunity: "Comunidad seleccionada",
    selectedProvince: "Provincia seleccionada",
    instruction: "Instrucción",
    studyInstruction: "Haz clic en una región del mapa. En este modo, los nombres son visibles para estudiar antes de la prueba.",
    communityDetails: "{name} es una comunidad autónoma de España.",
    cityDetails: "{name} es una ciudad autónoma de España.",
    provinceDetails: "{province} pertenece a {community}.",
    note: ""
  },
  ca: {
    htmlLang: "ca",
    appTitle: "Mapa d'estudi d'Espanya",
    studyCommunities: "Estudia comunitats",
    studyProvinces: "Estudia províncies",
    quizCommunities: "Test: 5 comunitats",
    quizProvinces: "Test: 8 províncies",
    subtitleStudyCommunities: "Estudia les comunitats autònomes d'Espanya amb noms visibles.",
    subtitleStudyProvinces: "Estudia les províncies d'Espanya amb noms visibles.",
    subtitleQuizCommunities: "Troba 5 comunitats autònomes triades a l'atzar.",
    subtitleQuizProvinces: "Troba 8 províncies triades a l'atzar.",
    loading: "Carregant les dades locals del mapa...",
    loadError: "No s'han pogut carregar els fitxers locals del mapa. Executa fetch-assets.sh abans de pujar-los i serveix aquesta carpeta des d'un servidor web o GitHub Pages.",
    quiz: "Test",
    restart: "Reinicia",
    noQuizLoaded: "No hi ha cap test carregat",
    chooseQuiz: "Tria un dels modes de test per generar preguntes aleatòries.",
    question: "Pregunta",
    clickThisArea: "Fes clic en aquesta zona",
    labelsHidden: "Els noms del mapa s'oculten deliberadament durant els tests.",
    quizBadge: "Mode test: noms ocults",
    finalScore: "Puntuació final",
    correct: "Correcte",
    clicked: "Has marcat",
    studyMode: "Mode d'estudi",
    selectedCommunity: "Comunitat seleccionada",
    selectedProvince: "Província seleccionada",
    instruction: "Instrucció",
    studyInstruction: "Fes clic en una regió del mapa. En aquest mode, els noms són visibles per estudiar abans del test.",
    communityDetails: "{name} és una comunitat autònoma d'Espanya.",
    cityDetails: "{name} és una ciutat autònoma d'Espanya.",
    provinceDetails: "{province} pertany a {community}.",
    note: ""
  }
};

const NAMES = {
  communities: {
    "01": { en: "Andalusia", es: "Andalucía", ca: "Andalusia" },
    "02": { en: "Aragon", es: "Aragón", ca: "Aragó" },
    "03": { en: "Asturias", es: "Asturias", ca: "Astúries" },
    "04": { en: "Balearic Islands", es: "Islas Baleares", ca: "Illes Balears" },
    "05": { en: "Canary Islands", es: "Canarias", ca: "Illes Canàries" },
    "06": { en: "Cantabria", es: "Cantabria", ca: "Cantàbria" },
    "07": { en: "Castile and León", es: "Castilla y León", ca: "Castella i Lleó" },
    "08": { en: "Castilla-La Mancha", es: "Castilla-La Mancha", ca: "Castella-la Manxa" },
    "09": { en: "Catalonia", es: "Cataluña", ca: "Catalunya" },
    "10": { en: "Valencian Community", es: "Comunidad Valenciana", ca: "Comunitat Valenciana" },
    "11": { en: "Extremadura", es: "Extremadura", ca: "Extremadura" },
    "12": { en: "Galicia", es: "Galicia", ca: "Galícia" },
    "13": { en: "Community of Madrid", es: "Comunidad de Madrid", ca: "Comunitat de Madrid" },
    "14": { en: "Region of Murcia", es: "Región de Murcia", ca: "Regió de Múrcia" },
    "15": { en: "Navarre", es: "Navarra", ca: "Navarra" },
    "16": { en: "Basque Country", es: "País Vasco", ca: "País Basc" },
    "17": { en: "La Rioja", es: "La Rioja", ca: "La Rioja" },
    "18": { en: "Ceuta", es: "Ceuta", ca: "Ceuta" },
    "19": { en: "Melilla", es: "Melilla", ca: "Melilla" }
  },
  provinces: {
    "01": { en: "Álava", es: "Álava", ca: "Àlaba" },
    "02": { en: "Albacete", es: "Albacete", ca: "Albacete" },
    "03": { en: "Alicante", es: "Alicante", ca: "Alacant" },
    "04": { en: "Almería", es: "Almería", ca: "Almeria" },
    "05": { en: "Ávila", es: "Ávila", ca: "Àvila" },
    "06": { en: "Badajoz", es: "Badajoz", ca: "Badajoz" },
    "07": { en: "Balearic Islands", es: "Islas Baleares", ca: "Illes Balears" },
    "08": { en: "Barcelona", es: "Barcelona", ca: "Barcelona" },
    "09": { en: "Burgos", es: "Burgos", ca: "Burgos" },
    "10": { en: "Cáceres", es: "Cáceres", ca: "Càceres" },
    "11": { en: "Cádiz", es: "Cádiz", ca: "Cadis" },
    "12": { en: "Castellón", es: "Castellón", ca: "Castelló" },
    "13": { en: "Ciudad Real", es: "Ciudad Real", ca: "Ciudad Real" },
    "14": { en: "Córdoba", es: "Córdoba", ca: "Còrdova" },
    "15": { en: "A Coruña", es: "A Coruña", ca: "la Corunya" },
    "16": { en: "Cuenca", es: "Cuenca", ca: "Conca" },
    "17": { en: "Girona", es: "Girona", ca: "Girona" },
    "18": { en: "Granada", es: "Granada", ca: "Granada" },
    "19": { en: "Guadalajara", es: "Guadalajara", ca: "Guadalajara" },
    "20": { en: "Gipuzkoa", es: "Gipuzkoa", ca: "Guipúscoa" },
    "21": { en: "Huelva", es: "Huelva", ca: "Huelva" },
    "22": { en: "Huesca", es: "Huesca", ca: "Osca" },
    "23": { en: "Jaén", es: "Jaén", ca: "Jaén" },
    "24": { en: "León", es: "León", ca: "Lleó" },
    "25": { en: "Lleida", es: "Lleida", ca: "Lleida" },
    "26": { en: "La Rioja", es: "La Rioja", ca: "La Rioja" },
    "27": { en: "Lugo", es: "Lugo", ca: "Lugo" },
    "28": { en: "Madrid", es: "Madrid", ca: "Madrid" },
    "29": { en: "Málaga", es: "Málaga", ca: "Màlaga" },
    "30": { en: "Murcia", es: "Murcia", ca: "Múrcia" },
    "31": { en: "Navarre", es: "Navarra", ca: "Navarra" },
    "32": { en: "Ourense", es: "Ourense", ca: "Ourense" },
    "33": { en: "Asturias", es: "Asturias", ca: "Astúries" },
    "34": { en: "Palencia", es: "Palencia", ca: "Palència" },
    "35": { en: "Las Palmas", es: "Las Palmas", ca: "Las Palmas" },
    "36": { en: "Pontevedra", es: "Pontevedra", ca: "Pontevedra" },
    "37": { en: "Salamanca", es: "Salamanca", ca: "Salamanca" },
    "38": { en: "Santa Cruz de Tenerife", es: "Santa Cruz de Tenerife", ca: "Santa Cruz de Tenerife" },
    "39": { en: "Cantabria", es: "Cantabria", ca: "Cantàbria" },
    "40": { en: "Segovia", es: "Segovia", ca: "Segòvia" },
    "41": { en: "Seville", es: "Sevilla", ca: "Sevilla" },
    "42": { en: "Soria", es: "Soria", ca: "Sòria" },
    "43": { en: "Tarragona", es: "Tarragona", ca: "Tarragona" },
    "44": { en: "Teruel", es: "Teruel", ca: "Terol" },
    "45": { en: "Toledo", es: "Toledo", ca: "Toledo" },
    "46": { en: "Valencia", es: "Valencia", ca: "València" },
    "47": { en: "Valladolid", es: "Valladolid", ca: "Valladolid" },
    "48": { en: "Biscay", es: "Bizkaia", ca: "Biscaia" },
    "49": { en: "Zamora", es: "Zamora", ca: "Zamora" },
    "50": { en: "Zaragoza", es: "Zaragoza", ca: "Saragossa" },
    "51": { en: "Ceuta", es: "Ceuta", ca: "Ceuta" },
    "52": { en: "Melilla", es: "Melilla", ca: "Melilla" }
  }
};

const PROVINCE_COMMUNITY = {
  "01": "16", "02": "08", "03": "10", "04": "01", "05": "07", "06": "11", "07": "04",
  "08": "09", "09": "07", "10": "11", "11": "01", "12": "10", "13": "08", "14": "01",
  "15": "12", "16": "08", "17": "09", "18": "01", "19": "08", "20": "16", "21": "01",
  "22": "02", "23": "01", "24": "07", "25": "09", "26": "17", "27": "12", "28": "13",
  "29": "01", "30": "14", "31": "15", "32": "12", "33": "03", "34": "07", "35": "05",
  "36": "12", "37": "07", "38": "05", "39": "06", "40": "07", "41": "01", "42": "07",
  "43": "09", "44": "02", "45": "08", "46": "10", "47": "07", "48": "16", "49": "07",
  "50": "02", "51": "18", "52": "19"
};

const state = {
  mode: MODES.STUDY_COMMUNITIES,
  lang: "en",
  selectedId: null,
  questions: [],
  currentIndex: 0,
  answers: [],
  lastAnswer: null,
  topology: null,
  loadError: null,
  colorCache: new Map()
};

const map = document.getElementById("map");
const sidePanel = document.getElementById("side-panel");
const subtitle = document.getElementById("subtitle");
const appTitle = document.getElementById("app-title");
const modeButtons = Array.from(document.querySelectorAll(".mode-controls button"));
const languageButtons = Array.from(document.querySelectorAll(".language-controls button"));

let projection = null;
let path = null;

const FEATURE_TRANSFORMS = {
  communities: {
    "18": { scale: 8, dx: -22, dy: 10 },
    "19": { scale: 15, dx: 6, dy: -4 }
  },
  provinces: {
    "51": { scale: 8, dx: -22, dy: 10 },
    "52": { scale: 15, dx: 6, dy: -4 }
  }
};

const LABEL_OFFSETS = {
  communities: {
    "06": { dx: -8, dy: 12 },
    "16": { dx: 10, dy: -12 }
  },
  provinces: {
    "20": { dx: 8, dy: -8 },
    "48": { dx: -10, dy: 10 }
  }
};

function t(key) {
  return UI[state.lang][key] || UI.en[key] || key;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function interpolate(template, values) {
  let output = template;
  Object.keys(values).forEach((key) => {
    output = output.split("{" + key + "}").join(values[key] || "");
  });
  return output;
}

function normalizeId(id) {
  return String(id).padStart(2, "0");
}

function nameFor(typeKey, id, fallback) {
  const normalized = normalizeId(id);
  return (NAMES[typeKey] && NAMES[typeKey][normalized] && NAMES[typeKey][normalized][state.lang]) ||
    (NAMES[typeKey] && NAMES[typeKey][normalized] && NAMES[typeKey][normalized].en) ||
    fallback ||
    normalized;
}

function getConfig() {
  const isCommunities = state.mode === MODES.STUDY_COMMUNITIES || state.mode === MODES.QUIZ_COMMUNITIES;
  const isQuiz = state.mode === MODES.QUIZ_COMMUNITIES || state.mode === MODES.QUIZ_PROVINCES;
  return {
    isCommunities,
    isQuiz,
    showLabels: !isQuiz,
    objectName: isCommunities ? "autonomous_regions" : "provinces",
    typeKey: isCommunities ? "communities" : "provinces"
  };
}

function getGeometries(config) {
  if (!state.topology) return [];
  const object = state.topology.objects[config.objectName];
  if (!object) return [];
  return object.geometries.filter((geometry) => {
    const id = normalizeId(geometry.id);
    if (config.typeKey === "provinces") return id !== "54";
    return id !== "20";
  });
}

function getFeatures(config) {
  if (!state.topology) return [];
  const geometries = getGeometries(config);
  return topojson
    .feature(state.topology, { type: "GeometryCollection", geometries })
    .features;
}

function featureById(config, id) {
  return getFeatures(config).find((feature) => normalizeId(feature.id) === normalizeId(id));
}

function regionName(feature, config) {
  return nameFor(config.typeKey, feature.id, feature.properties && feature.properties.name);
}

function regionNameById(typeKey, id) {
  return nameFor(typeKey, id, id);
}

function regionTransformConfig(config, id) {
  const normalized = normalizeId(id);
  return FEATURE_TRANSFORMS[config.typeKey] && FEATURE_TRANSFORMS[config.typeKey][normalized];
}

function regionTransform(feature, config) {
  const transform = regionTransformConfig(config, feature.id);
  if (!transform) return null;

  const centroid = path.centroid(feature);
  return `translate(${transform.dx} ${transform.dy}) translate(${centroid[0]} ${centroid[1]}) scale(${transform.scale}) translate(${-centroid[0]} ${-centroid[1]})`;
}

function labelPosition(feature, config) {
  const centroid = path.centroid(feature);
  const transform = regionTransformConfig(config, feature.id);
  const labelOffset = LABEL_OFFSETS[config.typeKey] && LABEL_OFFSETS[config.typeKey][normalizeId(feature.id)];
  const dx = (transform ? transform.dx : 0) + (labelOffset ? labelOffset.dx : 0);
  const dy = (transform ? transform.dy : 0) + (labelOffset ? labelOffset.dy : 0);
  return [centroid[0] + dx, centroid[1] + dy];
}

function computeColorMap(config) {
  const cacheKey = config.typeKey;
  if (state.colorCache.has(cacheKey)) return state.colorCache.get(cacheKey);

  const geometries = getGeometries(config);
  const neighbors = topojson.neighbors(geometries);
  const colorIndexes = [];

  geometries.forEach((geometry, index) => {
    const forbidden = new Set(
      neighbors[index]
        .map((neighborIndex) => colorIndexes[neighborIndex])
        .filter((value) => value !== undefined)
    );

    let colorIndex = 0;
    while (forbidden.has(colorIndex)) colorIndex += 1;
    colorIndexes[index] = colorIndex;
  });

  const colorMap = new Map();
  geometries.forEach((geometry, index) => {
    colorMap.set(normalizeId(geometry.id), PALETTE[colorIndexes[index] % PALETTE.length]);
  });

  if (config.typeKey === "provinces" && colorMap.get("35") === colorMap.get("38")) {
    colorMap.set("38", PALETTE[(colorIndexes[geometries.findIndex((geometry) => normalizeId(geometry.id) === "38")] + 1) % PALETTE.length]);
  }

  state.colorCache.set(cacheKey, colorMap);
  return colorMap;
}

function shuffle(items) {
  const copy = items.slice();
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    const temp = copy[i];
    copy[i] = copy[j];
    copy[j] = temp;
  }
  return copy;
}

function makeQuiz(mode) {
  if (!state.topology) return [];
  const oldMode = state.mode;
  state.mode = mode;
  const config = getConfig();
  const ids = getFeatures(config).map((feature) => normalizeId(feature.id));
  state.mode = oldMode;

  if (mode === MODES.QUIZ_COMMUNITIES) return shuffle(ids).slice(0, 5);
  if (mode === MODES.QUIZ_PROVINCES) return shuffle(ids).slice(0, 8);
  return [];
}

function setMode(nextMode) {
  state.mode = nextMode;
  state.selectedId = null;
  state.questions = makeQuiz(nextMode);
  state.currentIndex = 0;
  state.answers = [];
  state.lastAnswer = null;
  render();
}

function setLanguage(nextLang) {
  state.lang = nextLang;
  document.documentElement.lang = UI[nextLang].htmlLang;
  render();
}

function restartQuiz() {
  state.selectedId = null;
  state.questions = makeQuiz(state.mode);
  state.currentIndex = 0;
  state.answers = [];
  state.lastAnswer = null;
  render();
}

function statusFor(id) {
  const answer = state.lastAnswer;
  const normalized = normalizeId(id);
  if (answer && answer.clicked === normalized && answer.correct) return "correct";
  if (answer && answer.clicked === normalized && !answer.correct) return "incorrect";
  if (answer && answer.expected === normalized && !answer.correct) return "correct";
  if (state.selectedId === normalized) return "selected";
  return "";
}

function splitLabel(name, maxLength) {
  if (name.length <= maxLength) return [name];
  const words = name.replaceAll("/", " ").replaceAll("-", " ").split(" ").filter(Boolean);
  if (words.length <= 1) return [name];
  const lines = [];
  let current = "";

  words.forEach((word) => {
    const candidate = current ? current + " " + word : word;
    if (candidate.length <= maxLength || !current) {
      current = candidate;
    } else {
      lines.push(current);
      current = word;
    }
  });

  if (current) lines.push(current);
  if (lines.length <= 2) return lines;
  return [lines[0], lines.slice(1).join(" ")];
}

function setupProjection() {
  if (!window.d3 || typeof d3.geoConicConformalSpain !== "function") return false;
  projection = d3.geoConicConformalSpain();
  path = d3.geoPath(projection);
  return true;
}

function drawMapMessage(message) {
  map.textContent = "";
  const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
  text.setAttribute("x", "480");
  text.setAttribute("y", "310");
  text.setAttribute("text-anchor", "middle");
  text.setAttribute("class", "map-message");
  text.textContent = message;
  map.appendChild(text);
}

function drawMap(config) {
  if (state.loadError) {
    drawMapMessage(t("loadError"));
    return;
  }

  if (!state.topology || !path) {
    drawMapMessage(t("loading"));
    return;
  }

  const svg = d3.select(map);
  svg.selectAll("*").remove();

  const features = getFeatures(config);
  const colorMap = computeColorMap(config);
  const layer = svg.append("g").attr("class", "map-layer");

  layer
    .selectAll("path.region")
    .data(features, (feature) => normalizeId(feature.id))
    .join("path")
    .attr("class", (feature) => "region " + statusFor(feature.id))
    .attr("fill", (feature) => colorMap.get(normalizeId(feature.id)) || PALETTE[0])
    .attr("d", path)
    .attr("transform", (feature) => regionTransform(feature, config))
    .attr("tabindex", 0)
    .attr("role", "button")
    .attr("aria-label", (feature) => regionName(feature, config))
    .on("click", (_, feature) => handleRegionClick(normalizeId(feature.id)))
    .on("keydown", (event, feature) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        handleRegionClick(normalizeId(feature.id));
      }
    })
    .each(function(feature) {
      if (config.showLabels) {
        d3.select(this).append("title").text(regionName(feature, config));
      }
    });

  if (typeof projection.getCompositionBorders === "function") {
    svg
      .append("path")
      .attr("class", "composition-border")
      .attr("d", projection.getCompositionBorders());
  }

  if (config.showLabels) {
    const labelLayer = svg.append("g").attr("class", "labels");
    const maxLength = config.isCommunities ? 18 : 14;

    labelLayer
      .selectAll("text.label")
      .data(features, (feature) => normalizeId(feature.id))
      .join("text")
      .attr("class", config.isCommunities ? "label community" : "label province")
      .attr("x", (feature) => labelPosition(feature, config)[0])
      .attr("y", (feature) => labelPosition(feature, config)[1])
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "middle")
      .each(function(feature) {
        const text = d3.select(this);
        const centroid = labelPosition(feature, config);
        const lines = splitLabel(regionName(feature, config), maxLength);
        const y = centroid[1] - (lines.length - 1) * (config.isCommunities ? 7 : 5);
        text.attr("y", y);
        lines.forEach((line, index) => {
          text
            .append("tspan")
            .attr("x", centroid[0])
            .attr("dy", index === 0 ? 0 : (config.isCommunities ? 14 : 9))
            .text(line);
        });
      });
  } else {
    const badge = svg.append("g");
    badge
      .append("rect")
      .attr("x", 690)
      .attr("y", 24)
      .attr("width", 238)
      .attr("height", 38)
      .attr("rx", 12)
      .attr("fill", "#ffffff")
      .attr("stroke", "#d1d5db");
    badge
      .append("text")
      .attr("x", 809)
      .attr("y", 49)
      .attr("text-anchor", "middle")
      .attr("class", "badge-text")
      .text(t("quizBadge"));
  }
}

function handleRegionClick(clickedId) {
  const config = getConfig();

  if (!config.isQuiz) {
    state.selectedId = normalizeId(clickedId);
    state.lastAnswer = null;
    render();
    return;
  }

  if (state.currentIndex >= state.questions.length) return;

  const expected = state.questions[state.currentIndex];
  const clicked = normalizeId(clickedId);
  const answer = {
    expected,
    clicked,
    correct: clicked === expected
  };

  state.answers.push(answer);
  state.lastAnswer = answer;
  state.currentIndex += 1;
  render();
}

function renderControls() {
  modeButtons.forEach((button) => {
    button.classList.toggle("active", button.id === state.mode);
  });
  languageButtons.forEach((button) => {
    const lang = button.id.replace("lang_", "");
    button.classList.toggle("active", lang === state.lang);
  });

  document.getElementById(MODES.STUDY_COMMUNITIES).textContent = t("studyCommunities");
  document.getElementById(MODES.STUDY_PROVINCES).textContent = t("studyProvinces");
  document.getElementById(MODES.QUIZ_COMMUNITIES).textContent = t("quizCommunities");
  document.getElementById(MODES.QUIZ_PROVINCES).textContent = t("quizProvinces");
}

function renderSubtitle() {
  appTitle.textContent = t("appTitle");

  if (state.mode === MODES.STUDY_COMMUNITIES) subtitle.textContent = t("subtitleStudyCommunities");
  else if (state.mode === MODES.STUDY_PROVINCES) subtitle.textContent = t("subtitleStudyProvinces");
  else if (state.mode === MODES.QUIZ_COMMUNITIES) subtitle.textContent = t("subtitleQuizCommunities");
  else subtitle.textContent = t("subtitleQuizProvinces");
}

function renderSidePanel(config) {
  if (state.loadError) {
    sidePanel.innerHTML = `
      <div class="side-header"><span>${escapeHtml(t("loading"))}</span></div>
      <div class="panel-box">
        <div class="eyebrow">Error</div>
        <p class="body-text">${escapeHtml(t("loadError"))}</p>
      </div>
    `;
    return;
  }

  if (!state.topology) {
    sidePanel.innerHTML = `
      <div class="side-header"><span>${escapeHtml(t("loading"))}</span></div>
      <div class="panel-box">
        <p class="body-text">${escapeHtml(t("loading"))}</p>
      </div>
    `;
    return;
  }

  if (config.isQuiz) {
    const hasQuestions = state.questions.length > 0;
    const isDone = hasQuestions && state.currentIndex >= state.questions.length;
    const score = state.answers.filter((answer) => answer.correct).length;

    let html = `
      <div class="side-header">
        <span>${escapeHtml(t("quiz"))}</span>
        <button class="small" type="button" id="restart">${escapeHtml(t("restart"))}</button>
      </div>
    `;

    if (!hasQuestions) {
      html += `
        <div class="panel-box">
          <div class="eyebrow">${escapeHtml(t("noQuizLoaded"))}</div>
          <p class="body-text">${escapeHtml(t("chooseQuiz"))}</p>
        </div>
      `;
    } else if (!isDone) {
      const currentId = state.questions[state.currentIndex];
      const currentName = regionNameById(config.typeKey, currentId);
      html += `
        <div class="panel-box">
          <div class="eyebrow">${escapeHtml(t("question"))} ${state.currentIndex + 1} / ${state.questions.length}</div>
          <div class="eyebrow">${escapeHtml(t("clickThisArea"))}</div>
          <div class="big">${escapeHtml(currentName)}</div>
        </div>
        <div class="muted-row">${escapeHtml(t("labelsHidden"))}</div>
      `;
    } else {
      const answers = state.answers.map((answer, index) => {
        const expectedName = regionNameById(config.typeKey, answer.expected);
        const clickedName = regionNameById(config.typeKey, answer.clicked);
        return `
          <div class="answer">
            <span><strong>${index + 1}.</strong> ${escapeHtml(expectedName)}</span>
            <span class="answer-status ${answer.correct ? "ok" : "bad"}">
              ${answer.correct ? escapeHtml(t("correct")) : escapeHtml(t("clicked") + " " + clickedName)}
            </span>
          </div>
        `;
      }).join("");

      html += `
        <div class="panel-box">
          <div class="eyebrow">${escapeHtml(t("finalScore"))}</div>
          <div class="big">${score} / ${state.questions.length}</div>
        </div>
        <div class="answer-list">${answers}</div>
      `;
    }

    sidePanel.innerHTML = html;
    document.getElementById("restart").addEventListener("click", restartQuiz);
    return;
  }

  const selected = state.selectedId ? featureById(config, state.selectedId) : null;
  let details = null;

  if (selected) {
    const name = regionName(selected, config);
    if (config.isCommunities) {
      details = {
        name,
        label: t("selectedCommunity"),
        details: interpolate((state.selectedId === "18" || state.selectedId === "19") ? t("cityDetails") : t("communityDetails"), { name })
      };
    } else {
      const communityId = PROVINCE_COMMUNITY[state.selectedId];
      const communityName = regionNameById("communities", communityId);
      details = {
        name,
        label: t("selectedProvince"),
        details: interpolate(t("provinceDetails"), { province: name, community: communityName })
      };
    }
  }

  sidePanel.innerHTML = `
    <div class="side-header"><span>${escapeHtml(t("studyMode"))}</span></div>
    <div class="panel-box">
      ${details ? `
        <div class="eyebrow">${escapeHtml(details.label)}</div>
        <div class="big">${escapeHtml(details.name)}</div>
        <p class="body-text">${escapeHtml(details.details)}</p>
      ` : `
        <div class="eyebrow">${escapeHtml(t("instruction"))}</div>
        <p class="body-text">${escapeHtml(t("studyInstruction"))}</p>
      `}
    </div>
  `;
}

function render() {
  const config = getConfig();
  renderControls();
  renderSubtitle();
  drawMap(config);
  renderSidePanel(config);
}

function loadData() {
  if (!window.d3 || !window.topojson || !setupProjection()) {
    state.loadError = true;
    render();
    return;
  }

  if (window.SPAIN_PROVINCES_TOPOLOGY) {
    state.topology = window.SPAIN_PROVINCES_TOPOLOGY;
    state.loadError = null;
    state.colorCache.clear();
    render();
    return;
  }

  render();

  d3.json(DATA_URL)
    .then((topology) => {
      state.topology = topology;
      state.loadError = null;
      state.colorCache.clear();
      if (state.mode === MODES.QUIZ_COMMUNITIES || state.mode === MODES.QUIZ_PROVINCES) {
        state.questions = makeQuiz(state.mode);
      }
      render();
    })
    .catch(() => {
      state.loadError = true;
      render();
    });
}

modeButtons.forEach((button) => {
  button.addEventListener("click", () => setMode(button.id));
});

languageButtons.forEach((button) => {
  button.addEventListener("click", () => setLanguage(button.id.replace("lang_", "")));
});

document.documentElement.lang = UI[state.lang].htmlLang;
loadData();
