var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);

// main.ts
var main_exports = {};
__export(main_exports, {
  default: () => RootweavePlugin
});
module.exports = __toCommonJS(main_exports);
var import_obsidian = require("obsidian");
var VIEW_TYPE = "rootweave-view";
var VIEW_TYPE_GRAPH = "rootweave-graph";
var FILES = {
  roots: ".rootweave/Roots.md",
  words: ".rootweave/Dictionary.md",
  grammar: ".rootweave/Grammar.md",
  phonology: ".rootweave/Phonology.md"
};
var DEFAULT_SETTINGS = { language: "My Conlang" };
var DEFAULT_RULES = [
  { name: "Plural", type: "suffix", form: "-iu", meaning: "plural marker", example: "vel \u2192 veliu (lights)", notes: "" },
  { name: "Past tense", type: "prefix", form: "on-", meaning: "past tense", example: "vel \u2192 onvel (was light)", notes: "" }
];
var E_DIM = 8;
var SYLL_F = E_DIM + 6;
var H1 = 64;
var H2 = 32;
var IN = SYLL_F * 3;
var MODEL_VER = 2;
var DEFAULT_PHONOLOGY = {
  vowels: [
    { symbol: "a", pron: "ah", long: false },
    { symbol: "e", pron: "eh", long: false },
    { symbol: "i", pron: "ee", long: false },
    { symbol: "o", pron: "oh", long: false },
    { symbol: "u", pron: "oo", long: false }
  ],
  consonants: [
    { symbol: "b", pron: "b", long: false },
    { symbol: "d", pron: "d", long: false },
    { symbol: "f", pron: "f", long: false },
    { symbol: "g", pron: "g", long: false },
    { symbol: "k", pron: "k", long: false },
    { symbol: "l", pron: "l", long: false },
    { symbol: "m", pron: "m", long: false },
    { symbol: "n", pron: "n", long: false },
    { symbol: "r", pron: "r", long: false },
    { symbol: "s", pron: "s", long: false },
    { symbol: "t", pron: "t", long: false },
    { symbol: "v", pron: "v", long: false }
  ],
  mode: "strict",
  banned: [],
  notes: ""
};
function escapeCell(s) {
  return (s != null ? s : "").replace(/\|/g, "\\|").replace(/\n/g, " ");
}
function unescapeCell(s) {
  return (s != null ? s : "").replace(/\\\|/g, "|");
}
function parseMdTable(content) {
  const lines = content.split("\n");
  const rows = [];
  let started = false;
  for (const line of lines) {
    if (line.trim().startsWith("|")) {
      started = true;
      rows.push(line.trim());
    } else if (started)
      break;
  }
  if (rows.length < 3)
    return [];
  const headers = rows[0].split("|").slice(1, -1).map((h) => h.trim().toLowerCase());
  return rows.slice(2).map((row) => {
    const cells = row.split("|").slice(1, -1).map((c) => unescapeCell(c.trim()));
    const obj = {};
    headers.forEach((h, i) => {
      var _a;
      obj[h] = (_a = cells[i]) != null ? _a : "";
    });
    return obj;
  });
}
function buildMdTable(headers, rows) {
  const widths = headers.map((h, i) => Math.max(h.length, ...rows.map((r) => {
    var _a;
    return ((_a = r[i]) != null ? _a : "").length;
  }), 3));
  const pad = (s, w) => s.padEnd(w);
  const sep = (w) => "-".repeat(w);
  const header = "| " + headers.map((h, i) => pad(h, widths[i])).join(" | ") + " |";
  const divider = "| " + widths.map(sep).join(" | ") + " |";
  const body = rows.map(
    (row) => "| " + headers.map((_, i) => {
      var _a;
      return pad(escapeCell((_a = row[i]) != null ? _a : ""), widths[i]);
    }).join(" | ") + " |"
  );
  return [header, divider, ...body].join("\n");
}
function parseRoots(content) {
  return parseMdTable(content).map((r) => {
    var _a, _b, _c, _d, _e;
    return {
      root: (_a = r["root"]) != null ? _a : "",
      meaning: (_b = r["meaning"]) != null ? _b : "",
      category: (_c = r["category"]) != null ? _c : "",
      notes: (_d = r["notes"]) != null ? _d : "",
      alternates: ((_e = r["alternates"]) != null ? _e : "").split(",").map((s) => s.trim()).filter(Boolean)
    };
  }).filter((r) => r.root.trim() !== "");
}
function rootsToMd(roots) {
  return [
    "# Root Lexicon",
    "",
    "Add roots here or use the Rootweave panel (\u{1F4D6} ribbon icon).",
    "",
    buildMdTable(
      ["root", "meaning", "category", "notes", "alternates"],
      roots.map((r) => [r.root, r.meaning, r.category, r.notes, r.alternates.join(", ")])
    )
  ].join("\n");
}
function parseWords(content) {
  return parseMdTable(content).map((r) => {
    var _a, _b, _c, _d;
    return {
      word: (_a = r["word"]) != null ? _a : "",
      meaning: (_b = r["meaning"]) != null ? _b : "",
      pos: (_c = r["part of speech"]) != null ? _c : "",
      roots: ((_d = r["roots"]) != null ? _d : "").split("+").map((s) => s.trim()).filter(Boolean)
    };
  }).filter((w) => w.word.trim() !== "");
}
function wordsToMd(words) {
  return [
    "# Dictionary",
    "",
    "Add words here or use the Builder tab in the Rootweave panel.",
    "",
    buildMdTable(
      ["word", "meaning", "part of speech", "roots"],
      words.map((w) => [w.word, w.meaning, w.pos, w.roots.join(" + ")])
    )
  ].join("\n");
}
function parseRules(content) {
  return parseMdTable(content).map((r) => {
    var _a, _b, _c, _d, _e, _f;
    return {
      name: (_a = r["name"]) != null ? _a : "",
      type: ["prefix", "suffix", "infix", "other"].includes((_b = r["type"]) != null ? _b : "") ? r["type"] : "suffix",
      form: (_c = r["form"]) != null ? _c : "",
      meaning: (_d = r["meaning"]) != null ? _d : "",
      example: (_e = r["example"]) != null ? _e : "",
      notes: (_f = r["notes"]) != null ? _f : ""
    };
  }).filter((r) => r.name.trim() !== "");
}
function rulesToMd(rules) {
  return [
    "# Grammar Rules",
    "",
    "Each rule describes a morphological construction \u2014 a prefix, suffix, or other affix.",
    "",
    "- **prefix** \u2014 added before the word (e.g. on- for past tense)",
    "- **suffix** \u2014 added after the word (e.g. -iu for plural)",
    "- **infix** \u2014 inserted inside the word",
    "- **other** \u2014 freeform rule or particle",
    "",
    buildMdTable(
      ["name", "type", "form", "meaning", "example", "notes"],
      rules.map((r) => [r.name, r.type, r.form, r.meaning, r.example, r.notes])
    )
  ].join("\n");
}
function parsePhonSection(content, heading) {
  const re = new RegExp(`##\\s+${heading}\\s*\\n([\\s\\S]*?)(?=\\n## |$)`, "i");
  const m = re.exec(content);
  return m ? parseMdTable(m[1]) : [];
}
function parsePhonology(content) {
  var _a, _b;
  const vowRows = parsePhonSection(content, "Vowels");
  const conRows = parsePhonSection(content, "Consonants");
  const setRows = parsePhonSection(content, "Settings");
  const settings = {};
  setRows.forEach((r) => {
    var _a2;
    if (r["key"])
      settings[r["key"]] = (_a2 = r["value"]) != null ? _a2 : "";
  });
  return {
    vowels: vowRows.map((r) => {
      var _a2, _b2;
      return { symbol: (_a2 = r["symbol"]) != null ? _a2 : "", pron: (_b2 = r["pron"]) != null ? _b2 : "", long: r["long"] === "yes" };
    }).filter((p) => p.symbol),
    consonants: conRows.map((r) => {
      var _a2, _b2;
      return { symbol: (_a2 = r["symbol"]) != null ? _a2 : "", pron: (_b2 = r["pron"]) != null ? _b2 : "", long: false };
    }).filter((p) => p.symbol),
    mode: settings["mode"] === "permissive" ? "permissive" : "strict",
    banned: ((_a = settings["banned"]) != null ? _a : "").split(",").map((s) => s.trim()).filter(Boolean),
    notes: (_b = settings["notes"]) != null ? _b : ""
  };
}
function phonologyToMd(p) {
  return [
    "# Phonology",
    "",
    "## Vowels",
    buildMdTable(["symbol", "pron", "long"], p.vowels.map((v) => [v.symbol, v.pron, v.long ? "yes" : "no"])),
    "",
    "## Consonants",
    buildMdTable(["symbol", "pron"], p.consonants.map((c) => [c.symbol, c.pron])),
    "",
    "## Settings",
    buildMdTable(["key", "value"], [
      ["mode", p.mode],
      ["banned", p.banned.join(", ")],
      ["notes", p.notes]
    ])
  ].join("\n");
}
function applyRule(rule, word) {
  const affix = rule.form.replace(/^-|-$/g, "");
  if (rule.type === "prefix")
    return affix + word;
  if (rule.type === "suffix")
    return word + affix;
  return null;
}
function escapeRe(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
function buildParser(template, fields) {
  const order = [];
  let src = "^";
  let last = 0;
  let m;
  const re = /\[(\w+)\]/g;
  while ((m = re.exec(template)) !== null) {
    const name = m[1].toLowerCase();
    if (!fields.includes(name))
      continue;
    src += escapeRe(template.slice(last, m.index)) + "(.+?)";
    order.push(name);
    last = m.index + m[0].length;
  }
  src += escapeRe(template.slice(last)) + "$";
  if (order.length === 0)
    return null;
  try {
    return { regex: new RegExp(src, "i"), order };
  } catch (e) {
    return null;
  }
}
function importRoots(template, text) {
  const p = buildParser(template, ["root", "alternates", "meaning", "category", "notes"]);
  if (!p)
    return [];
  return text.split("\n").map((l) => l.trim()).filter((l) => l && !l.startsWith("#")).flatMap((line) => {
    var _a, _b, _c;
    const m = p.regex.exec(line);
    if (!m)
      return [];
    const d = {};
    p.order.forEach((f, i) => {
      d[f] = m[i + 1].trim();
    });
    if (!d["root"])
      return [];
    return [{
      root: d["root"],
      meaning: (_a = d["meaning"]) != null ? _a : "",
      category: (_b = d["category"]) != null ? _b : "",
      notes: (_c = d["notes"]) != null ? _c : "",
      alternates: d["alternates"] ? d["alternates"].split(/[,/]/).map((s) => s.trim()).filter(Boolean) : []
    }];
  });
}
function importWords(template, text) {
  const p = buildParser(template, ["word", "meaning", "pos"]);
  if (!p)
    return [];
  return text.split("\n").map((l) => l.trim()).filter((l) => l && !l.startsWith("#")).flatMap((line) => {
    var _a, _b;
    const m = p.regex.exec(line);
    if (!m)
      return [];
    const d = {};
    p.order.forEach((f, i) => {
      d[f] = m[i + 1].trim();
    });
    if (!d["word"])
      return [];
    return [{ word: d["word"], meaning: (_a = d["meaning"]) != null ? _a : "", pos: (_b = d["pos"]) != null ? _b : "", roots: [] }];
  });
}
function ttsSpeak(text, btn, rate = 1) {
  if (window.speechSynthesis.speaking) {
    window.speechSynthesis.cancel();
    btn.setText("\u{1F50A}");
    return;
  }
  const utt = new SpeechSynthesisUtterance(text);
  utt.rate = rate;
  utt.onend = () => btn.setText("\u{1F50A}");
  utt.onerror = () => btn.setText("\u{1F50A}");
  btn.setText("\u23F9");
  window.speechSynthesis.speak(utt);
}
function stripDiacritics(str) {
  const manual = {
    "\xE6": "ae",
    "\xC6": "AE",
    "\u0153": "oe",
    "\u0152": "OE",
    "\xF8": "o",
    "\xD8": "O",
    "\u0142": "l",
    "\u0141": "L",
    "\xDF": "ss",
    "\xF0": "d",
    "\xD0": "D",
    "\xFE": "th",
    "\xDE": "TH",
    "\u014B": "n",
    "\u014A": "N",
    "\u0138": "k",
    "\u0149": "'n"
  };
  let s = str;
  for (const from of Object.keys(manual))
    s = s.split(from).join(manual[from]);
  return s.normalize("NFD").replace(/[̀-ͯ]/g, "");
}
function suggestConlangWord(englishWord, roots, phon, model) {
  var _a;
  const el = englishWord.toLowerCase();
  const meaningsOf = (m) => m.toLowerCase().split(/[\s,;/]+/).map((p) => p.trim()).filter(Boolean);
  const exactRoot = roots.find(
    (r) => meaningsOf(r.meaning).some((p) => p === el) || r.alternates.map((a) => a.toLowerCase()).indexOf(el) !== -1
  );
  if (exactRoot)
    return { form: exactRoot.root, hint: `root "${exactRoot.root}" (${exactRoot.meaning})` };
  const partialRoot = roots.find(
    (r) => meaningsOf(r.meaning).some((p) => p.length > 2 && (el.includes(p) || p.includes(el)))
  );
  if (partialRoot)
    return { form: partialRoot.root, hint: `related root "${partialRoot.root}" (${partialRoot.meaning})` };
  const vowels = phon.vowels.map((v) => v.symbol);
  const cons = phon.consonants.map((c) => c.symbol);
  if (vowels.length === 0)
    return { form: "", hint: "" };
  let pick = (arr) => arr[Math.floor(Math.random() * arr.length)];
  if (model && cons.length > 1) {
    const firstLetter = (_a = el[0]) != null ? _a : "";
    const scored = cons.map((c) => ({
      c,
      sim: model.E[c] && model.E[firstLetter] ? model.E[c].reduce((s, v, i) => {
        var _a2;
        return s + v * ((_a2 = model.E[firstLetter][i]) != null ? _a2 : 0);
      }, 0) : 0
    })).sort((a, b) => b.sim - a.sim);
    pick = (arr) => {
      const top = scored.filter((x) => arr.indexOf(x.c) !== -1).slice(0, 3);
      return top.length ? top[Math.floor(Math.random() * top.length)].c : arr[0];
    };
  }
  const sylCount = el.length <= 4 ? 1 : el.length <= 7 ? 2 : 3;
  let generated = "";
  for (let s = 0; s < sylCount; s++) {
    if (cons.length > 0)
      generated += pick(cons);
    generated += vowels[Math.floor(Math.random() * vowels.length)];
    if (s < sylCount - 1 && cons.length > 0)
      generated += pick(cons);
  }
  if (phon.banned.some((b) => b && generated.includes(b))) {
    generated = vowels[Math.floor(Math.random() * vowels.length)];
    for (let s = 0; s < sylCount - 1; s++) {
      if (cons.length > 0)
        generated += pick(cons);
      generated += vowels[Math.floor(Math.random() * vowels.length)];
    }
  }
  return { form: generated, hint: "phonotactic suggestion" };
}
function matchCase(source, target) {
  if (!source || !target)
    return target;
  if (source === source.toUpperCase() && /[A-Z]/.test(source))
    return target.toUpperCase();
  if (/^[A-Z]/.test(source))
    return target[0].toUpperCase() + target.slice(1);
  return target;
}
function phonTokenize(word, phonemes) {
  const syms = phonemes.map((p) => p.symbol).sort((a, b) => b.length - a.length);
  const tokens = [];
  let i = 0;
  while (i < word.length) {
    const match = syms.find((s) => word.startsWith(s, i));
    if (match) {
      tokens.push(match);
      i += match.length;
    } else {
      tokens.push(word[i]);
      i++;
    }
  }
  return tokens;
}
function phonSyllabify(tokens, vowelSet) {
  if (!tokens.length)
    return [];
  const sylls = [];
  let cur = [];
  let hasVowel = false;
  for (let i = 0; i < tokens.length; i++) {
    const isV = vowelSet.has(tokens[i]);
    if (isV && hasVowel) {
      sylls.push(cur);
      cur = [tokens[i]];
      hasVowel = true;
    } else if (!isV && hasVowel) {
      const nextIsV = i + 1 < tokens.length && vowelSet.has(tokens[i + 1]);
      if (nextIsV) {
        sylls.push(cur);
        cur = [tokens[i]];
        hasVowel = false;
      } else {
        cur.push(tokens[i]);
      }
    } else {
      cur.push(tokens[i]);
      if (isV)
        hasVowel = true;
    }
  }
  if (cur.length)
    sylls.push(cur);
  return sylls;
}
function makeSyllables(syllTokens, phon) {
  const vowelSet = new Set(phon.vowels.map((v) => v.symbol));
  return syllTokens.map((phonemes) => {
    const isOpen = phonemes.length > 0 && vowelSet.has(phonemes[phonemes.length - 1]);
    const hasLong = phonemes.some((p) => {
      var _a;
      return (_a = phon.vowels.find((v) => v.symbol === p)) == null ? void 0 : _a.long;
    });
    return { phonemes, isOpen, isHeavy: hasLong || !isOpen };
  });
}
function renderSyllableDisplay(parent, syllTokens, stressIdx) {
  syllTokens.forEach((syll, si) => {
    if (si > 0)
      parent.createSpan({ cls: "rw-phon-dot", text: "-" });
    parent.createSpan({
      cls: "rw-phon-syll-display" + (si === stressIdx ? " is-stressed" : ""),
      text: syll.join("")
    });
  });
}
function phonReconstruct(syllTokens, stressIdx) {
  return syllTokens.map(
    (syll, si) => (si === stressIdx ? "'" : "") + syll.join("")
  ).join("-");
}
function phonPronReading(syllTokens, stressIdx, phon) {
  const allPh = [...phon.vowels, ...phon.consonants];
  return syllTokens.map((syll, si) => {
    const reading = syll.map((p) => {
      var _a, _b;
      return (_b = (_a = allPh.find((x) => x.symbol === p)) == null ? void 0 : _a.pron) != null ? _b : p;
    }).join("");
    return si === stressIdx ? reading.toUpperCase() : reading;
  }).join("-");
}
function nnRand(n, fi, fo) {
  const s = Math.sqrt(2 / (fi + fo));
  return Array.from({ length: n }, () => (Math.random() * 2 - 1) * s);
}
function nnZero(n) {
  return Array.from({ length: n }, () => 0);
}
function matVec(W, x, inD, outD, b) {
  const out = b.slice();
  for (let i = 0; i < inD; i++)
    for (let j = 0; j < outD; j++)
      out[j] += W[i * outD + j] * x[i];
  return out;
}
function matVecBack(delta, x, W, inD, outD) {
  const gW = Array.from({ length: inD * outD }, () => 0);
  const dx = Array.from({ length: inD }, () => 0);
  for (let i = 0; i < inD; i++)
    for (let j = 0; j < outD; j++) {
      gW[i * outD + j] = x[i] * delta[j];
      dx[i] += W[i * outD + j] * delta[j];
    }
  return { gW, gb: delta.slice(), dx };
}
function nnSoftmax(x) {
  const max = Math.max(...x);
  const e = x.map((v) => Math.exp(v - max));
  const s = e.reduce((a, b) => a + b, 0) || 1;
  return e.map((v) => v / s);
}
function reluBack(delta, preAct) {
  return delta.map((d, i) => preAct[i] > 0 ? d : 0);
}
function adamStep(param, grad, m, v, t, lr = 0.01) {
  const b1 = 0.9, b2 = 0.999, eps = 1e-8;
  const bc1 = 1 - Math.pow(b1, t), bc2 = 1 - Math.pow(b2, t);
  for (let i = 0; i < param.length; i++) {
    m[i] = b1 * m[i] + (1 - b1) * grad[i];
    v[i] = b2 * v[i] + (1 - b2) * grad[i] * grad[i];
    param[i] -= lr * (m[i] / bc1) / (Math.sqrt(v[i] / bc2) + eps);
  }
}
function newPhonModel(phonemeSymbols) {
  return {
    E: Object.fromEntries(phonemeSymbols.map((p) => [p, nnRand(E_DIM, 1, E_DIM)])),
    mE: Object.fromEntries(phonemeSymbols.map((p) => [p, nnZero(E_DIM)])),
    vE: Object.fromEntries(phonemeSymbols.map((p) => [p, nnZero(E_DIM)])),
    W1: nnRand(IN * H1, IN, H1),
    b1: nnZero(H1),
    W2: nnRand(H1 * H2, H1, H2),
    b2: nnZero(H2),
    W3: nnRand(H2, H2, 1),
    b3: nnZero(1),
    mW1: nnZero(IN * H1),
    vW1: nnZero(IN * H1),
    mb1: nnZero(H1),
    vb1: nnZero(H1),
    mW2: nnZero(H1 * H2),
    vW2: nnZero(H1 * H2),
    mb2: nnZero(H2),
    vb2: nnZero(H2),
    mW3: nnZero(H2),
    vW3: nnZero(H2),
    mb3: nnZero(1),
    vb3: nnZero(1),
    t: 0,
    version: MODEL_VER
  };
}
function phonGetEmbed(p, m) {
  if (!m.E[p])
    m.E[p] = nnRand(E_DIM, 1, E_DIM);
  if (!m.mE[p])
    m.mE[p] = nnZero(E_DIM);
  if (!m.vE[p])
    m.vE[p] = nnZero(E_DIM);
  return m.E[p];
}
function syllFeats(syll, idx, total, m) {
  const embeds = syll.phonemes.map((p) => phonGetEmbed(p, m));
  const avgEmb = Array.from(
    { length: E_DIM },
    (_, j) => embeds.reduce((s, e) => s + e[j], 0) / (embeds.length || 1)
  );
  const onset = syll.isHeavy ? syll.phonemes.length : 0;
  return [
    ...avgEmb,
    total > 1 ? idx / (total - 1) : 0,
    total > 1 ? (total - 1 - idx) / (total - 1) : 0,
    Math.min(total / 6, 1),
    syll.isOpen ? 1 : 0,
    syll.isHeavy ? 1 : 0,
    Math.min(onset / 3, 1)
  ];
}
function contextFeats(sylls, idx, m) {
  const n = sylls.length;
  const zero = Array.from({ length: SYLL_F }, () => 0);
  const prev = idx > 0 ? syllFeats(sylls[idx - 1], idx - 1, n, m) : zero;
  const curr = syllFeats(sylls[idx], idx, n, m);
  const next = idx < n - 1 ? syllFeats(sylls[idx + 1], idx + 1, n, m) : zero;
  return [...prev, ...curr, ...next];
}
function clipGrad(g, maxNorm = 5) {
  const norm = Math.sqrt(g.reduce((s, x) => s + x * x, 0));
  if (norm > maxNorm) {
    const scale = maxNorm / norm;
    for (let i = 0; i < g.length; i++)
      g[i] *= scale;
  }
}
function nnForward(feat, m) {
  const z1 = matVec(m.W1, feat, IN, H1, m.b1);
  const h1 = z1.map((v) => Math.max(0, v));
  const z2 = matVec(m.W2, h1, H1, H2, m.b2);
  const h2 = z2.map((v) => Math.max(0, v));
  const z3 = matVec(m.W3, h2, H2, 1, m.b3);
  return { z1, h1, z2, h2, score: z3[0] };
}
function predictStress(sylls, m) {
  if (sylls.length === 1)
    return { probs: [1], stressIdx: 0, confidence: 1 };
  const scores = sylls.map((_, i) => nnForward(contextFeats(sylls, i, m), m).score);
  const probs = nnSoftmax(scores);
  const stressIdx = probs.indexOf(Math.max(...probs));
  const H = -probs.reduce((s, p) => s + (p > 1e-9 ? p * Math.log(p) : 0), 0);
  const maxH = Math.log(sylls.length);
  return { probs, stressIdx, confidence: maxH > 0 ? 1 - H / maxH : 1 };
}
function trainOnExample(ex, m, phon, lr = 6e-3) {
  const sylls = makeSyllables(ex.sylls, phon);
  if (sylls.length <= 1)
    return;
  m.t++;
  const feats = sylls.map((_, i) => contextFeats(sylls, i, m));
  const fwds = feats.map((f) => nnForward(f, m));
  const probs = nnSoftmax(fwds.map((f) => f.score));
  const dScores = probs.map((p, i) => p - (i === ex.stress ? 1 : 0));
  const aW1 = nnZero(m.W1.length), ab1 = nnZero(m.b1.length);
  const aW2 = nnZero(m.W2.length), ab2 = nnZero(m.b2.length);
  const aW3 = nnZero(m.W3.length), ab3 = nnZero(m.b3.length);
  const aE = {};
  sylls.forEach((syll, si) => {
    const { z1, h1, z2, h2 } = fwds[si];
    const feat = feats[si];
    const d3 = dScores[si];
    const { gW: gW3, gb: gb3, dx: dh2 } = matVecBack([d3], h2, m.W3, H2, 1);
    const dz2 = reluBack(dh2, z2);
    const { gW: gW2, gb: gb2, dx: dh1 } = matVecBack(dz2, h1, m.W2, H1, H2);
    const dz1 = reluBack(dh1, z1);
    const { gW: gW1, gb: gb1, dx: dFeat } = matVecBack(dz1, feat, m.W1, IN, H1);
    for (let i = 0; i < aW1.length; i++)
      aW1[i] += gW1[i];
    for (let i = 0; i < ab1.length; i++)
      ab1[i] += gb1[i];
    for (let i = 0; i < aW2.length; i++)
      aW2[i] += gW2[i];
    for (let i = 0; i < ab2.length; i++)
      ab2[i] += gb2[i];
    for (let i = 0; i < aW3.length; i++)
      aW3[i] += gW3[i];
    for (let i = 0; i < ab3.length; i++)
      ab3[i] += gb3[i];
    const dEmb = dFeat.slice(SYLL_F, SYLL_F + E_DIM);
    const nP = syll.phonemes.length || 1;
    syll.phonemes.forEach((p) => {
      if (!aE[p])
        aE[p] = nnZero(E_DIM);
      dEmb.forEach((d, j) => {
        aE[p][j] += d / nP;
      });
    });
  });
  const L2 = 1e-4;
  for (let i = 0; i < aW1.length; i++)
    aW1[i] += L2 * m.W1[i];
  for (let i = 0; i < aW2.length; i++)
    aW2[i] += L2 * m.W2[i];
  for (let i = 0; i < aW3.length; i++)
    aW3[i] += L2 * m.W3[i];
  clipGrad(aW1);
  clipGrad(aW2);
  clipGrad(aW3);
  clipGrad(ab1);
  clipGrad(ab2);
  clipGrad(ab3);
  adamStep(m.W1, aW1, m.mW1, m.vW1, m.t, lr);
  adamStep(m.b1, ab1, m.mb1, m.vb1, m.t, lr);
  adamStep(m.W2, aW2, m.mW2, m.vW2, m.t, lr);
  adamStep(m.b2, ab2, m.mb2, m.vb2, m.t, lr);
  adamStep(m.W3, aW3, m.mW3, m.vW3, m.t, lr);
  adamStep(m.b3, ab3, m.mb3, m.vb3, m.t, lr);
  Object.entries(aE).forEach(([p, grad]) => {
    phonGetEmbed(p, m);
    clipGrad(grad);
    adamStep(m.E[p], grad, m.mE[p], m.vE[p], m.t, lr * 0.5);
  });
}
function parseStressNotation(text, syllCount) {
  const parts = text.trim().split(/[-·.\s]+/).map((s) => s.trim()).filter(Boolean);
  if (parts.length !== syllCount)
    return null;
  const idx = parts.findIndex((p) => p.startsWith("'") || p.startsWith("\u02C8"));
  return idx >= 0 ? idx : null;
}
function batchTrain(examples, m, phon, epochs = 40) {
  for (let ep = 0; ep < epochs; ep++)
    for (const ex of examples)
      trainOnExample(ex, m, phon, 8e-3 * (1 - ep / epochs * 0.4));
}
function englishRhymeKey(word) {
  const w = word.toLowerCase().replace(/[^a-z]/g, "");
  const vowels = "aeiouy";
  let i = w.length - 1;
  while (i >= 0 && !vowels.includes(w[i]))
    i--;
  while (i > 0 && vowels.includes(w[i - 1]))
    i--;
  return i >= 0 ? w.slice(i) : w;
}
function detectRhymeScheme(keys) {
  const map = /* @__PURE__ */ new Map();
  let next = 0;
  return keys.map((k) => {
    if (!map.has(k))
      map.set(k, String.fromCharCode(65 + next++));
    return map.get(k);
  });
}
function conlangRhymeKey(word, phon, stressMap) {
  var _a;
  const allPh = [...phon.vowels, ...phon.consonants];
  const vowelSet = new Set(phon.vowels.map((v) => v.symbol));
  if (!allPh.length)
    return null;
  const tokens = phonTokenize(word.toLowerCase(), allPh);
  const syllTokens = phonSyllabify(tokens, vowelSet);
  if (!syllTokens.length)
    return null;
  const stressIdx = (_a = stressMap[word.toLowerCase()]) != null ? _a : 0;
  const stressed = syllTokens[Math.min(stressIdx, syllTokens.length - 1)];
  const nucStart = stressed.findIndex((p) => vowelSet.has(p));
  if (nucStart < 0)
    return null;
  const rhymeToks = [
    ...stressed.slice(nucStart),
    ...syllTokens.slice(stressIdx + 1).flat()
  ];
  return { key: rhymeToks.join(""), tokens: rhymeToks };
}
function rhymeSimilarity(a, b, m) {
  const eA = a.length ? phonGetEmbed(a[0], m) : null;
  const eB = b.length ? phonGetEmbed(b[0], m) : null;
  if (!eA || !eB)
    return 0;
  const dot = eA.reduce((s, v, i) => s + v * eB[i], 0);
  const normA = Math.sqrt(eA.reduce((s, v) => s + v * v, 0));
  const normB = Math.sqrt(eB.reduce((s, v) => s + v * v, 0));
  return normA && normB ? dot / (normA * normB) : 0;
}
function pca2d(vecs) {
  if (vecs.length < 2)
    return vecs.map(() => [0, 0]);
  const n = vecs.length, d = vecs[0].length;
  const mean = Array.from({ length: d }, (_, j) => vecs.reduce((s, v) => s + v[j], 0) / n);
  const X = vecs.map((v) => v.map((x, j) => x - mean[j]));
  const norm = (u) => Math.sqrt(u.reduce((s, x) => s + x * x, 0)) || 1;
  function powerIter(data) {
    let v = Array.from({ length: d }, () => Math.random() - 0.5);
    v = v.map((x) => x / norm(v));
    for (let it = 0; it < 60; it++) {
      const w = data.map((row) => row.reduce((s, x, i) => s + x * v[i], 0));
      const r = Array.from({ length: d }, (_, j) => data.reduce((s, row, i) => s + row[j] * w[i], 0));
      v = r.map((x) => x / norm(r));
    }
    return v;
  }
  const v1 = powerIter(X);
  const s1 = X.map((row) => row.reduce((s, x, i) => s + x * v1[i], 0));
  const X2 = X.map((row, i) => row.map((x, j) => x - s1[i] * v1[j]));
  const v2 = powerIter(X2);
  const s2 = X.map((row) => row.reduce((s, x, i) => s + x * v2[i], 0));
  return s1.map((x, i) => [x, s2[i]]);
}
function inferPhono(words, phon) {
  if (words.length < 3)
    return [];
  const allPh = [...phon.vowels, ...phon.consonants];
  const vowelSet = new Set(phon.vowels.map((v) => v.symbol));
  const conSet = new Set(phon.consonants.map((c) => c.symbol));
  const results = [];
  const tokenized = words.map((w) => phonTokenize(w.word.toLowerCase(), allPh)).filter((t) => t.length > 0 && t.every((p) => vowelSet.has(p) || conSet.has(p)));
  if (tokenized.length < 3)
    return [];
  const n = tokenized.length;
  const endV = tokenized.filter((t) => vowelSet.has(t[t.length - 1])).length;
  const startC = tokenized.filter((t) => t.length > 0 && !vowelSet.has(t[0])).length;
  if (endV === n)
    results.push(`All ${n} words end in a vowel`);
  else if (endV === 0)
    results.push("No words end in a vowel");
  if (startC === n)
    results.push(`All ${n} words start with a consonant`);
  let maxCluster = 0;
  for (const t of tokenized) {
    let run = 0;
    for (const p of t) {
      run = vowelSet.has(p) ? 0 : run + 1;
      maxCluster = Math.max(maxCluster, run);
    }
  }
  if (maxCluster <= 1)
    results.push("No consonant clusters observed");
  else
    results.push(`Largest consonant cluster: ${maxCluster}`);
  const sylls = tokenized.map((t) => phonSyllabify(t, vowelSet).length);
  const maxS = Math.max(...sylls);
  const avgS = (sylls.reduce((a, b) => a + b, 0) / n).toFixed(1);
  results.push(`Syllables per word: max ${maxS}, avg ${avgS}`);
  return results;
}
function forceLayout(nodes, edges, W, H) {
  nodes.forEach((n, i) => {
    const a = 2 * Math.PI * i / nodes.length;
    n.x = W / 2 + Math.cos(a) * Math.min(W, H) * 0.35;
    n.y = H / 2 + Math.sin(a) * Math.min(W, H) * 0.35;
    n.vx = 0;
    n.vy = 0;
  });
  const map = new Map(nodes.map((n) => [n.id, n]));
  for (let t = 0; t < 280; t++) {
    const damp = 0.9 - 0.5 * (t / 280);
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const a = nodes[i], b = nodes[j];
        const dx = b.x - a.x || 0.01;
        const dy = b.y - a.y || 0.01;
        const d2 = Math.max(dx * dx + dy * dy, 1);
        const f = 4e3 / d2;
        a.vx -= dx / Math.sqrt(d2) * f;
        a.vy -= dy / Math.sqrt(d2) * f;
        b.vx += dx / Math.sqrt(d2) * f;
        b.vy += dy / Math.sqrt(d2) * f;
      }
    }
    edges.forEach((e) => {
      const a = map.get(e.src), b = map.get(e.tgt);
      if (!a || !b)
        return;
      const dx = b.x - a.x, dy = b.y - a.y;
      const d = Math.sqrt(dx * dx + dy * dy) || 1;
      const f = (d - 90) * 0.07;
      a.vx += dx / d * f;
      a.vy += dy / d * f;
      b.vx -= dx / d * f;
      b.vy -= dy / d * f;
    });
    nodes.forEach((n) => {
      n.vx += (W / 2 - n.x) * 6e-3;
      n.vy += (H / 2 - n.y) * 6e-3;
      n.x = Math.max(24, Math.min(W - 24, n.x + n.vx * damp));
      n.y = Math.max(24, Math.min(H - 24, n.y + n.vy * damp));
      n.vx *= damp;
      n.vy *= damp;
    });
  }
}
var SVGNS = "http://www.w3.org/2000/svg";
var mksvg = (tag) => activeDocument.createElementNS(SVGNS, tag);
var RootweavePlugin = class extends import_obsidian.Plugin {
  constructor() {
    super(...arguments);
    this.phonModel = null;
    this.phonExamples = [];
    this.wordStress = {};
  }
  async onload() {
    await this.loadSettings();
    this.registerView(VIEW_TYPE, (leaf) => new RootweaveView(leaf, this));
    this.registerView(VIEW_TYPE_GRAPH, (leaf) => new GraphView(leaf, this));
    this.addRibbonIcon("book-open", "Rootweave", () => {
      void this.openPanel();
    });
    this.addCommand({ id: "open", name: "Open panel", callback: () => {
      void this.openPanel();
    } });
    this.addCommand({ id: "open-graph", name: "Open root graph", callback: () => {
      void this.openGraph();
    } });
    this.addSettingTab(new RootweaveSettingTab(this.app, this));
    this.app.workspace.onLayoutReady(() => {
      void this.openPanel();
    });
  }
  async openPanel() {
    const { workspace } = this.app;
    let leaf = workspace.getLeavesOfType(VIEW_TYPE)[0];
    if (!leaf) {
      leaf = workspace.getLeaf("tab");
      await leaf.setViewState({ type: VIEW_TYPE, active: true });
    }
    await workspace.revealLeaf(leaf);
  }
  async openGraph() {
    const { workspace } = this.app;
    let leaf = workspace.getLeavesOfType(VIEW_TYPE_GRAPH)[0];
    if (!leaf) {
      leaf = workspace.getLeaf("tab");
      await leaf.setViewState({ type: VIEW_TYPE_GRAPH, active: true });
    }
    await workspace.revealLeaf(leaf);
  }
  // ── Vault I/O ─────────────────────────────────────────────────────────────
  // We use adapter.read/write directly — vault.create/modify can fail silently
  // when Obsidian's in-memory file cache hasn't caught up with recent changes.
  async readFile(path) {
    try {
      return await this.app.vault.adapter.read((0, import_obsidian.normalizePath)(path));
    } catch (e) {
      return null;
    }
  }
  async writeFile(path, content) {
    const p = (0, import_obsidian.normalizePath)(path);
    const dir = p.split("/").slice(0, -1).join("/");
    if (dir)
      try {
        await this.app.vault.createFolder(dir);
      } catch (e) {
      }
    await this.app.vault.adapter.write(p, content);
  }
  // ── Data I/O ──────────────────────────────────────────────────────────────
  async loadRoots() {
    const c = await this.readFile(FILES.roots);
    return c ? parseRoots(c) : [];
  }
  async saveRoots(r) {
    await this.writeFile(FILES.roots, rootsToMd(r));
  }
  async loadWords() {
    const c = await this.readFile(FILES.words);
    return c ? parseWords(c) : [];
  }
  async saveWords(w) {
    await this.writeFile(FILES.words, wordsToMd(w));
  }
  async loadRules() {
    const c = await this.readFile(FILES.grammar);
    return c ? parseRules(c) : DEFAULT_RULES;
  }
  async saveRules(r) {
    await this.writeFile(FILES.grammar, rulesToMd(r));
  }
  async loadPhonology() {
    const c = await this.readFile(FILES.phonology);
    return c ? parsePhonology(c) : { ...DEFAULT_PHONOLOGY };
  }
  async savePhonology(p) {
    await this.writeFile(FILES.phonology, phonologyToMd(p));
  }
  async reloadView() {
    for (const leaf of this.app.workspace.getLeavesOfType(VIEW_TYPE))
      if (leaf.view instanceof RootweaveView)
        await leaf.view.reload();
  }
  // ── Settings (includes phonModel / phonExamples in pluginData) ────────────
  async loadSettings() {
    var _a, _b, _c, _d;
    const data = (_a = await this.loadData()) != null ? _a : {};
    this.settings = { language: (_b = data["language"]) != null ? _b : DEFAULT_SETTINGS.language };
    this.phonExamples = (_c = data["phonExamples"]) != null ? _c : [];
    const savedWS = data["wordStress"];
    if (savedWS) {
      this.wordStress = savedWS;
    } else {
      this.wordStress = {};
      for (const ex of this.phonExamples)
        this.wordStress[ex.word] = ex.stress;
    }
    const saved = (_d = data["phonModel"]) != null ? _d : null;
    this.phonModel = saved && saved.version === MODEL_VER ? saved : null;
  }
  async saveSettings() {
    await this.saveData({
      language: this.settings.language,
      phonModel: this.phonModel,
      phonExamples: this.phonExamples,
      wordStress: this.wordStress
    });
  }
};
var RootweaveView = class extends import_obsidian.ItemView {
  constructor(leaf, plugin) {
    super(leaf);
    this.tab = "roots";
    this.roots = [];
    this.words = [];
    this.rules = [];
    this.phon = { ...DEFAULT_PHONOLOGY };
    this.plugin = plugin;
  }
  getViewType() {
    return VIEW_TYPE;
  }
  getDisplayText() {
    return "Rootweave";
  }
  getIcon() {
    return "book-open";
  }
  async reload() {
    try {
      [this.roots, this.words, this.rules, this.phon] = await Promise.all([
        this.plugin.loadRoots(),
        this.plugin.loadWords(),
        this.plugin.loadRules(),
        this.plugin.loadPhonology()
      ]);
    } catch (e) {
      console.error("Rootweave reload error", e);
    }
    this.render();
  }
  async onOpen() {
    try {
      [this.roots, this.words, this.rules, this.phon] = await Promise.all([
        this.plugin.loadRoots(),
        this.plugin.loadWords(),
        this.plugin.loadRules(),
        this.plugin.loadPhonology()
      ]);
      const saves = [];
      if (!await this.plugin.readFile(FILES.roots))
        saves.push(this.plugin.saveRoots(this.roots));
      if (!await this.plugin.readFile(FILES.words))
        saves.push(this.plugin.saveWords(this.words));
      if (!await this.plugin.readFile(FILES.grammar))
        saves.push(this.plugin.saveRules(this.rules));
      if (!await this.plugin.readFile(FILES.phonology))
        saves.push(this.plugin.savePhonology(this.phon));
      await Promise.allSettled(saves);
    } catch (e) {
      console.error("Rootweave open error", e);
    }
    this.render();
  }
  async onClose() {
  }
  render() {
    const el = this.contentEl;
    el.empty();
    el.addClass("rootweave-container");
    el.createDiv({ cls: "rw-header" }).createSpan({ cls: "rw-title", text: "Rootweave" });
    const tabBar = el.createDiv({ cls: "rw-tab-bar" });
    const body = el.createDiv({ cls: "rw-content" });
    const TABS = [
      { id: "roots", label: `Roots (${this.roots.length})` },
      { id: "builder", label: "Builder" },
      { id: "words", label: `Words (${this.words.length})` },
      { id: "grammar", label: `Grammar (${this.rules.length})` },
      { id: "translator", label: "Translate" },
      { id: "phonology", label: "Phonology" },
      { id: "export", label: "Export" }
    ];
    TABS.forEach((t) => {
      const btn = tabBar.createEl("button", {
        cls: "rw-tab-btn" + (this.tab === t.id ? " is-active" : ""),
        text: t.label
      });
      btn.addEventListener("click", () => {
        this.tab = t.id;
        this.render();
      });
    });
    switch (this.tab) {
      case "roots":
        this.renderRoots(body);
        break;
      case "builder":
        this.renderBuilder(body);
        break;
      case "words":
        this.renderWords(body);
        break;
      case "grammar":
        this.renderGrammar(body);
        break;
      case "translator":
        this.renderTranslator(body);
        break;
      case "phonology":
        this.renderPhonology(body);
        break;
      case "export":
        this.renderExport(body);
        break;
    }
  }
  // ── Roots tab ─────────────────────────────────────────────────────────────
  renderRoots(el) {
    const ctrl = el.createDiv({ cls: "rw-controls" });
    const search = ctrl.createEl("input", { cls: "rw-input", attr: { type: "text", placeholder: "Search\u2026" } });
    const cats = ["All", ...new Set(this.roots.map((r) => r.category).filter(Boolean))];
    const catSel = ctrl.createEl("select", { cls: "rw-select" });
    cats.forEach((c) => catSel.createEl("option", { value: c, text: c }));
    ctrl.createEl("button", { cls: "rw-btn rw-btn-primary", text: "+ Root" }).addEventListener("click", () => {
      new RootModal(this.app, null, (root) => {
        if (this.roots.some((r) => r.root === root.root)) {
          new import_obsidian.Notice(`Root "${root.root}" already exists.`);
          return;
        }
        this.roots.push(root);
        void this.plugin.saveRoots(this.roots).then(() => this.render());
      }).open();
    });
    const list = el.createDiv({ cls: "rw-list" });
    const draw = () => {
      list.empty();
      const q = search.value.toLowerCase();
      const cat = catSel.value;
      const visible = this.roots.filter(
        (r) => (!q || r.root.toLowerCase().includes(q) || r.meaning.toLowerCase().includes(q) || r.notes.toLowerCase().includes(q)) && (cat === "All" || r.category === cat)
      );
      if (!visible.length) {
        list.createEl("p", { cls: "rw-empty", text: "No roots found." });
        return;
      }
      visible.forEach((root) => {
        const card = list.createDiv({ cls: "rw-card" });
        const info = card.createDiv({ cls: "rw-card-info" });
        info.createSpan({ cls: "rw-root-text", text: root.root });
        if (root.alternates.length)
          info.createSpan({ cls: "rw-root-alts", text: ` / ${root.alternates.join(" / ")}` });
        info.createSpan({ cls: "rw-root-meaning", text: ` \u2014 ${root.meaning}` });
        if (root.category)
          info.createSpan({ cls: "rw-badge", text: root.category });
        if (root.notes)
          card.createDiv({ cls: "rw-root-notes", text: root.notes });
        const acts = card.createDiv({ cls: "rw-card-actions" });
        acts.createEl("button", { cls: "rw-btn rw-btn-sm", text: "Edit" }).addEventListener("click", () => {
          new RootModal(this.app, root, (updated) => {
            const i = this.roots.findIndex((r) => r.root === root.root);
            if (i !== -1)
              this.roots[i] = updated;
            void this.plugin.saveRoots(this.roots).then(() => this.render());
          }).open();
        });
        acts.createEl("button", { cls: "rw-btn rw-btn-sm rw-btn-danger", text: "Delete" }).addEventListener("click", () => {
          this.roots = this.roots.filter((r) => r.root !== root.root);
          void this.plugin.saveRoots(this.roots).then(() => this.render());
        });
      });
    };
    search.addEventListener("input", draw);
    catSel.addEventListener("change", draw);
    draw();
  }
  // ── Builder tab ───────────────────────────────────────────────────────────
  renderBuilder(el) {
    el.createEl("p", { cls: "rw-subtitle", text: "Type a word to see its root components and check grammar." });
    const wordInput = el.createEl("input", { cls: "rw-input rw-input-lg", attr: { type: "text", placeholder: "Type a word\u2026" } });
    const suggestEl = el.createDiv({ cls: "rw-suggestions" });
    const phonEl = el.createDiv({ cls: "rw-phon-breakdown" });
    const formsEl = el.createDiv({ cls: "rw-grammar-forms" });
    const saveArea = el.createDiv({ cls: "rw-add-word-area" });
    const analyze = () => {
      const word = wordInput.value.trim();
      suggestEl.empty();
      phonEl.empty();
      formsEl.empty();
      saveArea.empty();
      if (!word)
        return;
      const matched = this.roots.filter(
        (r) => [r.root, ...r.alternates].some((f) => f.length > 0 && word.toLowerCase().includes(f.toLowerCase()))
      );
      if (matched.length) {
        suggestEl.createEl("p", { cls: "rw-label", text: "Root components:" });
        matched.forEach((root) => {
          const row = suggestEl.createDiv({ cls: "rw-suggestion-row" });
          row.createSpan({ cls: "rw-root-chip", text: root.root });
          const alt = root.alternates.find((f) => f.length > 0 && word.toLowerCase().includes(f.toLowerCase()));
          if (alt)
            row.createSpan({ cls: "rw-alt-chip", text: `via "${alt}"` });
          row.createSpan({ text: ` \u2192 ${root.meaning}` });
          if (root.category)
            row.createSpan({ cls: "rw-badge rw-badge-sm", text: root.category });
        });
        suggestEl.createEl("p", { cls: "rw-meaning-hint", text: `Composed meaning: ${matched.map((r) => r.meaning).join(" + ")}` });
      } else {
        suggestEl.createEl("p", { cls: "rw-empty", text: "No matching roots found." });
      }
      const allPhonemes = [...this.phon.vowels, ...this.phon.consonants];
      if (allPhonemes.length > 0) {
        const vowelSet = new Set(this.phon.vowels.map((v) => v.symbol));
        const tokens = phonTokenize(word.toLowerCase(), allPhonemes);
        const knownSet = new Set(allPhonemes.map((p) => p.symbol));
        const unknown = tokens.filter((p) => !knownSet.has(p));
        const syllTokens = phonSyllabify(tokens, vowelSet);
        const sylls = makeSyllables(syllTokens, this.phon);
        if (tokens.length > 0) {
          phonEl.createEl("p", { cls: "rw-label", text: "Phoneme breakdown:" });
          const breakRow = phonEl.createDiv({ cls: "rw-phon-break" });
          syllTokens.forEach((syll, si) => {
            if (si > 0)
              breakRow.createSpan({ cls: "rw-phon-dot", text: " \xB7 " });
            syll.forEach((p) => {
              const ph = allPhonemes.find((x) => x.symbol === p);
              const sp = breakRow.createSpan({ cls: ph ? "rw-phon-token" : "rw-phon-unknown", text: p });
              if (ph)
                sp.title = ph.pron;
            });
          });
          const model = this.plugin.phonModel;
          if (model && sylls.length > 0 && this.plugin.phonExamples.length >= 2) {
            const { stressIdx, confidence } = predictStress(sylls, model);
            const reading = phonPronReading(syllTokens, stressIdx, this.phon);
            const confPct = Math.round(confidence * 100);
            const confCls = confidence > 0.75 ? "rw-conf-high" : confidence > 0.45 ? "rw-conf-mid" : "rw-conf-low";
            const pronRow = phonEl.createDiv({ cls: "rw-phon-pron-row" });
            renderSyllableDisplay(pronRow, syllTokens, stressIdx);
            pronRow.createSpan({ cls: "rw-phon-reading", text: reading });
            pronRow.createSpan({ cls: `rw-conf ${confCls}`, text: `${confPct}%` });
            if (sylls.length > 1) {
              const stressRow = phonEl.createDiv({ cls: "rw-phon-stress-row" });
              stressRow.createSpan({ cls: "rw-label", text: "Stress: " });
              syllTokens.forEach((syll, si) => {
                const btn = stressRow.createEl("button", {
                  cls: "rw-btn rw-btn-sm rw-phon-syll" + (si === stressIdx ? " is-stressed" : ""),
                  text: syll.join("")
                });
                btn.title = "Click to correct stress";
                btn.addEventListener("click", () => {
                  var _a;
                  const ex = { word: word.toLowerCase(), sylls: syllTokens, stress: si };
                  this.plugin.phonExamples.push(ex);
                  const m = (_a = this.plugin.phonModel) != null ? _a : newPhonModel(allPhonemes.map((p) => p.symbol));
                  this.plugin.phonModel = m;
                  for (let ep = 0; ep < 8; ep++)
                    trainOnExample(ex, m, this.phon);
                  void this.plugin.saveSettings();
                  analyze();
                });
              });
            }
          } else if (sylls.length > 1) {
            const needed = Math.max(0, 2 - this.plugin.phonExamples.length);
            phonEl.createEl("p", { cls: "rw-empty rw-phon-hint", text: needed > 0 ? `Mark stress on ${needed} more word${needed !== 1 ? "s" : ""} in the Phonology tab to enable predictions.` : "Go to Phonology \u2192 Try a word to train stress prediction." });
          }
          if (this.phon.mode === "strict" && unknown.length > 0) {
            phonEl.createEl("p", { cls: "rw-phon-warn", text: `Unknown sounds: ${[...new Set(unknown)].join(", ")} \u2014 add them in the Phonology tab` });
          }
        }
      }
      if (this.rules.length) {
        formsEl.createEl("p", { cls: "rw-label", text: "Grammatical forms:" });
        this.rules.forEach((rule) => {
          const result = applyRule(rule, word);
          const row = formsEl.createDiv({ cls: "rw-form-row" });
          row.createSpan({ cls: `rw-badge rw-badge-${rule.type}`, text: rule.name });
          if (result) {
            row.createSpan({ cls: "rw-form-result", text: result });
            row.createSpan({ cls: "rw-form-meaning", text: `(${rule.meaning})` });
          } else {
            row.createSpan({ cls: "rw-form-result", text: `${rule.form}  ${word}` });
            row.createSpan({ cls: "rw-form-meaning", text: `(${rule.meaning} \u2014 see Grammar tab)` });
          }
        });
      }
      const existing = this.words.find((w) => w.word.toLowerCase() === word.toLowerCase());
      if (existing) {
        const msg = saveArea.createEl("p", { cls: "rw-ok rw-ok-link", text: `\u2713 "${word}" is in the dictionary \u2014 ${existing.meaning}` });
        msg.title = "Click to edit";
        msg.addEventListener("click", () => {
          new WordModal(this.app, existing, (updated) => {
            const i = this.words.findIndex((w) => w.word === existing.word);
            if (i !== -1)
              this.words[i] = updated;
            void this.plugin.saveWords(this.words).then(() => analyze());
          }).open();
        });
      } else {
        saveArea.createEl("p", { cls: "rw-label", text: "Save to dictionary:" });
        const form = saveArea.createDiv({ cls: "rw-add-word-form" });
        const meaningIn = form.createEl("input", { cls: "rw-input", attr: { type: "text", placeholder: "English meaning" } });
        const posIn = form.createEl("input", { cls: "rw-input", attr: { type: "text", placeholder: "Part of speech (noun, verb\u2026)" } });
        form.createEl("button", { cls: "rw-btn rw-btn-primary", text: "Add to Dictionary" }).addEventListener("click", () => {
          const meaning = meaningIn.value.trim();
          if (!meaning) {
            new import_obsidian.Notice("Enter a meaning first.");
            return;
          }
          this.words.push({ word, meaning, pos: posIn.value.trim(), roots: matched.map((r) => r.root) });
          void this.plugin.saveWords(this.words).then(() => {
            new import_obsidian.Notice(`"${word}" added to dictionary!`);
            wordInput.value = "";
            analyze();
          });
        });
      }
    };
    wordInput.addEventListener("input", analyze);
  }
  // ── Words tab ─────────────────────────────────────────────────────────────
  renderWords(el) {
    const ctrl = el.createDiv({ cls: "rw-controls" });
    const search = ctrl.createEl("input", { cls: "rw-input", attr: { type: "text", placeholder: "Search words\u2026" } });
    ctrl.createEl("button", { cls: "rw-btn rw-btn-primary", text: "+ Word" }).addEventListener("click", () => {
      new WordModal(this.app, null, (word) => {
        if (this.words.some((w) => w.word.toLowerCase() === word.word.toLowerCase())) {
          new import_obsidian.Notice(`"${word.word}" is already in the dictionary.`);
          return;
        }
        this.words.push(word);
        void this.plugin.saveWords(this.words).then(() => this.render());
      }).open();
    });
    const list = el.createDiv({ cls: "rw-dict-list" });
    const draw = () => {
      list.empty();
      const q = search.value.toLowerCase();
      const visible = this.words.filter(
        (w) => !q || w.word.toLowerCase().includes(q) || w.meaning.toLowerCase().includes(q) || w.pos.toLowerCase().includes(q)
      );
      if (!visible.length) {
        list.createEl("p", { cls: "rw-empty", text: this.words.length === 0 ? "No words yet. Use the Builder tab or + Word." : "No results." });
        return;
      }
      const table = list.createEl("table", { cls: "rw-table" });
      const hRow = table.createEl("thead").createEl("tr");
      ["Word", "Meaning", "PoS", "Roots", ""].forEach((h) => hRow.createEl("th", { text: h }));
      const tbody = table.createEl("tbody");
      visible.forEach((w) => {
        const row = tbody.createEl("tr");
        row.createEl("td", { cls: "rw-word-cell", text: w.word });
        row.createEl("td", { text: w.meaning });
        row.createEl("td", { text: w.pos });
        row.createEl("td", { text: w.roots.join(", ") });
        const acts = row.createEl("td");
        acts.createEl("button", { cls: "rw-btn rw-btn-sm", text: "Edit" }).addEventListener("click", () => {
          new WordModal(this.app, w, (updated) => {
            const i = this.words.findIndex((w2) => w2.word === w.word);
            if (i !== -1)
              this.words[i] = updated;
            void this.plugin.saveWords(this.words).then(() => draw());
          }).open();
        });
        acts.createEl("button", { cls: "rw-btn rw-btn-sm rw-btn-danger", text: "\xD7" }).addEventListener("click", () => {
          this.words = this.words.filter((w2) => w2.word !== w.word);
          void this.plugin.saveWords(this.words).then(() => draw());
        });
      });
    };
    search.addEventListener("input", draw);
    draw();
  }
  // ── Grammar tab ───────────────────────────────────────────────────────────
  renderGrammar(el) {
    el.createEl("p", { cls: "rw-subtitle", text: "Rules are tested against each word in the Builder." });
    const ctrl = el.createDiv({ cls: "rw-controls" });
    ctrl.createEl("button", { cls: "rw-btn rw-btn-primary", text: "+ Rule" }).addEventListener("click", () => {
      new RuleModal(this.app, null, (rule) => {
        this.rules.push(rule);
        void this.plugin.saveRules(this.rules).then(() => this.render());
      }).open();
    });
    const list = el.createDiv({ cls: "rw-list" });
    if (!this.rules.length) {
      list.createEl("p", { cls: "rw-empty", text: "No grammar rules yet. Add a suffix, prefix, or other construction." });
      return;
    }
    this.rules.forEach((rule, i) => {
      const card = list.createDiv({ cls: "rw-card" });
      const info = card.createDiv({ cls: "rw-card-info" });
      info.createSpan({ cls: "rw-root-text", text: rule.name });
      info.createSpan({ cls: `rw-badge rw-badge-${rule.type}`, text: rule.type });
      info.createSpan({ cls: "rw-root-chip", text: rule.form });
      info.createSpan({ cls: "rw-root-meaning", text: ` \u2014 ${rule.meaning}` });
      if (rule.example)
        card.createDiv({ cls: "rw-root-notes", text: `e.g. ${rule.example}` });
      if (rule.notes)
        card.createDiv({ cls: "rw-root-notes", text: rule.notes });
      const acts = card.createDiv({ cls: "rw-card-actions" });
      acts.createEl("button", { cls: "rw-btn rw-btn-sm", text: "Edit" }).addEventListener("click", () => {
        new RuleModal(this.app, rule, (updated) => {
          this.rules[i] = updated;
          void this.plugin.saveRules(this.rules).then(() => this.render());
        }).open();
      });
      acts.createEl("button", { cls: "rw-btn rw-btn-sm rw-btn-danger", text: "Delete" }).addEventListener("click", () => {
        this.rules.splice(i, 1);
        void this.plugin.saveRules(this.rules).then(() => this.render());
      });
    });
  }
  // ── Translator tab ────────────────────────────────────────────────────────
  renderTranslator(el) {
    el.createEl("p", { cls: "rw-subtitle", text: "Translate using your dictionary and roots." });
    let direction = "forward";
    const dirRow = el.createDiv({ cls: "rw-mode-row" });
    const btnFwd = dirRow.createEl("button", { cls: "rw-mode-btn is-active", text: "English \u2192 Conlang" });
    const btnRev = dirRow.createEl("button", { cls: "rw-mode-btn", text: "Conlang \u2192 English" });
    const setDir = (d) => {
      direction = d;
      btnFwd.toggleClass("is-active", d === "forward");
      btnRev.toggleClass("is-active", d === "reverse");
      inputArea.setAttribute(
        "placeholder",
        d === "forward" ? "Type English text or a poem\u2026" : "Type conlang text\u2026"
      );
    };
    btnFwd.addEventListener("click", () => setDir("forward"));
    btnRev.addEventListener("click", () => setDir("reverse"));
    const inputArea = el.createEl("textarea", { cls: "rw-textarea", attr: { placeholder: "Type English text or a poem\u2026" } });
    const glossLabel = el.createEl("label", { cls: "rw-toggle-label" });
    const glossChk = glossLabel.createEl("input");
    glossChk.type = "checkbox";
    glossLabel.appendText(" Show interlinear gloss");
    const translateBtn = el.createEl("button", { cls: "rw-btn rw-btn-primary", text: "Translate" });
    const outputEl = el.createDiv({ cls: "rw-translator-output" });
    const quickAddEl = el.createDiv({ cls: "rw-quick-add-panel" });
    const showQuickAdd = (englishWord, doTranslate2) => {
      quickAddEl.empty();
      const { form: suggested, hint } = suggestConlangWord(
        englishWord,
        this.roots,
        this.phon,
        this.plugin.phonModel
      );
      const panel = quickAddEl.createDiv({ cls: "rw-qa-inner" });
      panel.createSpan({ cls: "rw-qa-label", text: `Add "${englishWord}" \u2192` });
      const formIn = panel.createEl("input", {
        cls: "rw-input rw-qa-input",
        attr: { type: "text", value: suggested, placeholder: "conlang word" }
      });
      const posSel = panel.createEl("select", { cls: "rw-qa-pos" });
      ["noun", "verb", "adj", "adv", "other"].forEach(
        (p) => posSel.createEl("option", { value: p, text: p })
      );
      if (hint)
        panel.createSpan({ cls: "rw-qa-hint", text: `\u{1F4A1} ${hint}` });
      const saveBtn = panel.createEl("button", { cls: "rw-btn rw-btn-sm rw-btn-primary", text: "Save" });
      const skipBtn = panel.createEl("button", { cls: "rw-btn rw-btn-sm", text: "Skip" });
      skipBtn.addEventListener("click", () => quickAddEl.empty());
      saveBtn.addEventListener("click", () => {
        const wordForm = formIn.value.trim();
        if (!wordForm) {
          new import_obsidian.Notice("Enter a conlang form first.");
          return;
        }
        const newWord = { word: wordForm, meaning: englishWord, pos: posSel.value, roots: [] };
        this.words.push(newWord);
        void this.plugin.saveWords(this.words).then(() => {
          new import_obsidian.Notice(`Saved "${wordForm}" \u2192 ${englishWord}`);
          quickAddEl.empty();
          doTranslate2();
        });
      });
      formIn.focus();
      formIn.select();
    };
    const doTranslate = () => {
      outputEl.empty();
      quickAddEl.empty();
      const fullInput = inputArea.value.trim();
      if (!fullInput)
        return;
      const dict = [
        ...this.words.map((w) => ({ conlang: w.word, meaning: w.meaning })),
        ...this.roots.map((r) => ({ conlang: r.root, meaning: r.meaning }))
      ];
      const splitToken = (token) => {
        const m = token.match(/^([^a-zA-ZÀ-ɏ]*)(.+?)([^a-zA-ZÀ-ɏ]*)$/);
        return m ? { prefix: m[1], word: m[2], suffix: m[3] } : { prefix: "", word: token, suffix: "" };
      };
      const translateToken = (token) => {
        var _a, _b;
        const { prefix, word, suffix } = splitToken(token);
        if (direction === "forward") {
          const wl = word.toLowerCase();
          const entry = dict.find(
            (d) => d.meaning.toLowerCase().split(/[\s,;/]+/).map((p) => p.trim()).some((p) => p === wl)
          );
          return { prefix, word, suffix, meaning: (_a = entry == null ? void 0 : entry.meaning) != null ? _a : "", translated: entry ? matchCase(word, entry.conlang) : null };
        } else {
          const wl = word.toLowerCase();
          const entry = dict.find((d) => d.conlang.toLowerCase() === wl);
          return { prefix, word, suffix, meaning: (_b = entry == null ? void 0 : entry.meaning) != null ? _b : "", translated: entry ? entry.meaning : null };
        }
      };
      const inputLines = fullInput.split(/\r?\n/);
      const lineResults = inputLines.map(
        (line) => line.trim() === "" ? [] : line.split(/\s+/).map(translateToken)
      );
      const allTokens = [].concat(...lineResults);
      const realWords = allTokens.filter((t) => t.word.length > 0);
      const foundWords = realWords.filter((t) => t.translated !== null);
      const pct = realWords.length ? Math.round(foundWords.length / realWords.length * 100) : 100;
      const confCls = pct >= 85 ? "rw-conf-high" : pct >= 60 ? "rw-conf-mid" : "rw-conf-low";
      const confRow = outputEl.createDiv({ cls: "rw-trans-conf-row" });
      confRow.createSpan({ cls: `rw-conf ${confCls}`, text: `${pct}% coverage` });
      confRow.createSpan({ cls: "rw-trans-conf-detail", text: ` \u2014 ${foundWords.length} of ${realWords.length} words found` });
      const linesWrap = outputEl.createDiv({ cls: "rw-trans-lines" });
      lineResults.forEach((results, li) => {
        if (results.length === 0) {
          linesWrap.createDiv({ cls: "rw-trans-blank" });
          return;
        }
        if (glossChk.checked) {
          const gloss = linesWrap.createDiv({ cls: "rw-gloss" });
          const origRow = gloss.createDiv({ cls: "rw-gloss-row rw-gloss-original" });
          const transRow = gloss.createDiv({ cls: "rw-gloss-row rw-gloss-translation" });
          results.forEach(({ prefix, word, suffix, translated }) => {
            const orig = origRow.createSpan({ cls: "rw-gloss-cell", text: prefix + word + suffix });
            const trans = transRow.createSpan({ cls: "rw-gloss-cell" });
            if (translated) {
              trans.setText(translated);
              trans.addClass("rw-gloss-found");
              orig.title = `\u2192 ${translated}`;
            } else {
              trans.setText(direction === "forward" ? "+ add" : "?");
              trans.addClass("rw-gloss-missing");
              orig.addClass("rw-unknown-word");
              orig.title = "Not in dictionary";
              if (direction === "forward")
                trans.addEventListener("click", () => showQuickAdd(word, doTranslate));
            }
          });
        } else {
          const lineEl = linesWrap.createDiv({ cls: "rw-translation-line", attr: { "data-line": String(li) } });
          results.forEach(({ prefix, word, suffix, meaning, translated }, i) => {
            if (i > 0)
              lineEl.appendText(" ");
            if (prefix)
              lineEl.appendText(prefix);
            if (translated) {
              const s = lineEl.createSpan({ cls: "rw-word-found", text: translated });
              s.title = `${word} \u2192 ${meaning}`;
            } else if (direction === "forward") {
              const s = lineEl.createSpan({ cls: "rw-word-missing rw-word-addable", text: word });
              s.title = "Click to add to dictionary";
              s.addEventListener("click", () => showQuickAdd(word, doTranslate));
            } else {
              const s = lineEl.createSpan({ cls: "rw-word-missing", text: word });
              s.title = "Not in dictionary";
            }
            if (suffix)
              lineEl.appendText(suffix);
          });
        }
      });
      const nonEmptyLines = lineResults.filter((l) => l.length > 0);
      if (direction === "forward" && nonEmptyLines.length >= 2) {
        const nonEmptySrcLines = inputLines.filter((l) => l.trim() !== "");
        const srcLastWords = nonEmptyLines.map((_, li) => {
          var _a, _b;
          const toks = ((_a = nonEmptySrcLines[li]) != null ? _a : "").trim().split(/\s+/);
          return ((_b = toks[toks.length - 1]) != null ? _b : "").replace(/[^a-zA-Z]/g, "");
        });
        const srcRhymeKeys = srcLastWords.map((w) => englishRhymeKey(w));
        const srcScheme = detectRhymeScheme(srcRhymeKeys);
        const hasRhyme = new Set(srcScheme).size < srcScheme.length;
        if (hasRhyme) {
          const phon = this.phon;
          const stressMap = this.plugin.wordStress;
          const model = this.plugin.phonModel;
          const hasPhon = phon.vowels.length > 0 || phon.consonants.length > 0;
          const transLastWords = nonEmptyLines.map((results) => {
            for (let i = results.length - 1; i >= 0; i--)
              if (results[i].translated)
                return results[i].translated;
            return null;
          });
          const transRhymeData = transLastWords.map(
            (w) => w && hasPhon ? conlangRhymeKey(w, phon, stressMap) : null
          );
          const transScheme = detectRhymeScheme(
            transRhymeData.map((d) => (d == null ? void 0 : d.key) || `__${Math.random()}`)
          );
          const rhymeSection = outputEl.createDiv({ cls: "rw-rhyme-section" });
          rhymeSection.createDiv({ cls: "rw-label", text: "Rhyme analysis" });
          const schemeRow = rhymeSection.createDiv({ cls: "rw-rhyme-row" });
          schemeRow.createSpan({ cls: "rw-rhyme-label", text: "Source:" });
          schemeRow.createSpan({ cls: "rw-rhyme-scheme", text: srcScheme.join(" ") });
          schemeRow.createSpan({ cls: "rw-rhyme-label", text: "Translation:" });
          if (!hasPhon) {
            schemeRow.createSpan({ cls: "rw-conf rw-conf-low", text: "set up phonology to check" });
          } else {
            const lineMatches = srcScheme.map((srcLetter, i) => {
              if (!transRhymeData[i])
                return null;
              const sibling = srcScheme.findIndex((l, j) => l === srcLetter && j !== i);
              if (sibling < 0)
                return true;
              return transScheme[i] === transScheme[sibling];
            });
            const schemeSpan = schemeRow.createSpan({ cls: "rw-rhyme-scheme" });
            srcScheme.forEach((_l, i) => {
              const match = lineMatches[i];
              const cls = match === false ? "rw-rhyme-letter rw-rhyme-break" : match === true ? "rw-rhyme-letter rw-rhyme-ok" : "rw-rhyme-letter rw-rhyme-unknown";
              schemeSpan.createSpan({ cls, text: transScheme[i] });
              if (i < srcScheme.length - 1)
                schemeSpan.appendText(" ");
            });
            lineMatches.forEach((match, i) => {
              var _a;
              if (match !== false)
                return;
              const srcLetter = srcScheme[i];
              const siblingIdx = lineMatches.findIndex((m, j) => m === true && srcScheme[j] === srcLetter);
              const targetData = siblingIdx >= 0 ? transRhymeData[siblingIdx] : null;
              const engWord = srcLastWords[i];
              const brokenWord = (_a = transLastWords[i]) != null ? _a : "";
              const candidates = dict.filter((d) => d.meaning.toLowerCase().split(/[\s,;/]+/).map((p) => p.trim()).some((p) => p === engWord.toLowerCase())).filter((d) => d.conlang.toLowerCase() !== brokenWord.toLowerCase()).map((d) => {
                const rk = conlangRhymeKey(d.conlang, phon, stressMap);
                const exact = rk && targetData ? rk.key === targetData.key : false;
                const sim = rk && targetData && model ? rhymeSimilarity(rk.tokens, targetData.tokens, model) : 0;
                return { word: d.conlang, exact, sim };
              }).sort((a, b) => (b.exact ? 1 : b.sim) - (a.exact ? 1 : a.sim)).slice(0, 3);
              const fixRow = rhymeSection.createDiv({ cls: "rw-rhyme-fix-row" });
              const endStr = brokenWord ? ` "${brokenWord}"` : "";
              fixRow.createSpan({
                cls: "rw-rhyme-fix-label",
                text: `Line ${i + 1}${endStr} breaks rhyme (${srcLetter})`
              });
              if (candidates.length > 0) {
                fixRow.appendText(" \u2014 try: ");
                candidates.forEach((c, ci) => {
                  if (ci > 0)
                    fixRow.appendText(", ");
                  const badge = c.exact ? "\u2713" : `${Math.round(c.sim * 100)}%`;
                  fixRow.createSpan({
                    cls: "rw-rhyme-alt" + (c.exact ? " rw-rhyme-alt-exact" : ""),
                    text: `${c.word} (${badge})`
                  });
                });
              } else {
                fixRow.appendText(" \u2014 no alternatives in dictionary");
              }
            });
          }
        }
      }
      const btnRow = outputEl.createDiv({ cls: "rw-trans-btn-row" });
      btnRow.createEl("button", { cls: "rw-btn rw-btn-sm", text: "Copy" }).addEventListener("click", () => {
        const text = lineResults.map((r) => r.map(({ prefix, word, suffix, translated }) => prefix + (translated != null ? translated : word) + suffix).join(" ")).join("\n");
        void navigator.clipboard.writeText(text);
        new import_obsidian.Notice("Copied!");
      });
      const transSpeak = () => {
        const allPh = [...this.phon.vowels, ...this.phon.consonants];
        const vowelSet = new Set(this.phon.vowels.map((v) => v.symbol));
        const hasPhon = allPh.length > 0;
        return lineResults.map((results) => results.filter((t) => t.word.length > 0).map(({ word, translated }) => {
          var _a;
          if (!translated)
            return word;
          if (direction === "reverse") {
            return translated.split(/[/|]+/).map((p) => p.trim()).filter(Boolean).join(", ");
          }
          if (!hasPhon)
            return translated;
          const toks = phonTokenize(translated.toLowerCase(), allPh);
          const sylls = phonSyllabify(toks, vowelSet);
          if (!sylls.length)
            return translated;
          const si = (_a = this.plugin.wordStress[translated.toLowerCase()]) != null ? _a : 0;
          const reading = phonPronReading(sylls, si, this.phon);
          return reading || translated;
        }).join(" ")).filter((l) => l.trim()).join(". ");
      };
      const speakBtn = btnRow.createEl("button", { cls: "rw-btn rw-btn-sm rw-tts-btn", text: "\u{1F50A}" });
      speakBtn.addEventListener("click", () => ttsSpeak(transSpeak(), speakBtn));
    };
    translateBtn.addEventListener("click", doTranslate);
  }
  // ── Export tab ────────────────────────────────────────────────────────────
  renderExport(el) {
    el.createEl("p", { cls: "rw-subtitle", text: "Your data already lives in .rootweave/ as Markdown files. Export creates a single consolidated snapshot." });
    const stats = el.createDiv({ cls: "rw-export-stats" });
    stats.createEl("p", { text: `${this.roots.length} root${this.roots.length !== 1 ? "s" : ""}` });
    stats.createEl("p", { text: `${this.words.length} word${this.words.length !== 1 ? "s" : ""}` });
    stats.createEl("p", { text: `${this.rules.length} grammar rule${this.rules.length !== 1 ? "s" : ""}` });
    el.createEl("p", { cls: "rw-label", text: "Source files (open directly):" });
    const links = el.createDiv({ cls: "rw-file-links" });
    Object.values(FILES).forEach((path) => {
      var _a;
      const name = (_a = path.split("/").pop()) != null ? _a : path;
      links.createEl("button", { cls: "rw-btn rw-btn-sm rw-file-link", text: name }).addEventListener("click", () => {
        const file = this.app.vault.getAbstractFileByPath((0, import_obsidian.normalizePath)(path));
        if (file instanceof import_obsidian.TFile)
          void this.app.workspace.getLeaf().openFile(file);
        else
          new import_obsidian.Notice(`${path} hasn't been created yet \u2014 add some data first.`);
      });
    });
    el.createDiv({ cls: "rw-divider" });
    el.createEl("button", { cls: "rw-btn", text: "Open Root Graph" }).addEventListener("click", () => {
      void this.plugin.openGraph();
    });
    el.createEl("button", { cls: "rw-btn rw-btn-primary", text: "Export Snapshot" }).addEventListener("click", () => {
      const lang = this.plugin.settings.language;
      const date = new Date().toISOString().slice(0, 10);
      const content = [`# ${lang} \u2014 ${date}`, "", rootsToMd(this.roots), "", wordsToMd(this.words), "", rulesToMd(this.rules)].join("\n");
      const fname = `${lang.replace(/\s+/g, "-").toLowerCase()}-${date}.md`;
      const np = (0, import_obsidian.normalizePath)(fname);
      const existing = this.app.vault.getAbstractFileByPath(np);
      void (existing instanceof import_obsidian.TFile ? this.app.vault.modify(existing, content) : this.app.vault.create(np, content)).then(() => new import_obsidian.Notice(`Exported to ${fname}`));
    });
  }
  // ── Phonology tab ─────────────────────────────────────────────────────────
  renderPhonology(el) {
    if (!this.plugin.phonModel && this.plugin.phonExamples.length > 0) {
      const allPh = [...this.phon.vowels, ...this.phon.consonants];
      const m = newPhonModel(allPh.map((p) => p.symbol));
      this.plugin.phonModel = m;
      batchTrain(this.plugin.phonExamples, m, this.phon, 60);
      void this.plugin.saveSettings();
    }
    const savePhon = () => {
      void this.plugin.savePhonology(this.phon);
    };
    const renderPhonRow = (parent, ph, isVowel, onChange, onDelete) => {
      const row = parent.createDiv({ cls: "rw-phon-row" });
      const symIn = row.createEl("input", { cls: "rw-input rw-phon-sym", attr: { type: "text", value: ph.symbol, placeholder: "ph" } });
      const pronIn = row.createEl("input", { cls: "rw-input rw-phon-pron", attr: { type: "text", value: ph.pron, placeholder: "sound" } });
      symIn.addEventListener("change", () => {
        ph.symbol = symIn.value.trim();
        onChange();
      });
      pronIn.addEventListener("change", () => {
        ph.pron = pronIn.value.trim();
        onChange();
      });
      if (isVowel) {
        const lbl = row.createEl("label", { cls: "rw-phon-long-label" });
        const chk = lbl.createEl("input");
        chk.type = "checkbox";
        chk.checked = ph.long;
        lbl.appendText(" long");
        chk.addEventListener("change", () => {
          ph.long = chk.checked;
          onChange();
        });
      }
      row.createEl("button", { cls: "rw-btn rw-btn-sm rw-btn-danger", text: "\xD7" }).addEventListener("click", onDelete);
    };
    const vowSection = el.createDiv({ cls: "rw-phon-section" });
    vowSection.createEl("p", { cls: "rw-label", text: "Vowels" });
    vowSection.createEl("p", { cls: "rw-subtitle", text: 'Symbol = how you type it, Sound = how to say it (e.g. "ah", "/a/").' });
    const vowList = vowSection.createDiv({ cls: "rw-phon-list" });
    const redrawVowels = () => {
      vowList.empty();
      this.phon.vowels.forEach(
        (ph, i) => renderPhonRow(
          vowList,
          ph,
          true,
          savePhon,
          () => {
            this.phon.vowels.splice(i, 1);
            savePhon();
            redrawVowels();
          }
        )
      );
    };
    redrawVowels();
    vowSection.createEl("button", { cls: "rw-btn rw-btn-sm", text: "+ Vowel" }).addEventListener("click", () => {
      this.phon.vowels.push({ symbol: "", pron: "", long: false });
      savePhon();
      redrawVowels();
    });
    el.createDiv({ cls: "rw-divider" });
    const conSection = el.createDiv({ cls: "rw-phon-section" });
    conSection.createEl("p", { cls: "rw-label", text: "Consonants" });
    const conList = conSection.createDiv({ cls: "rw-phon-list" });
    const redrawConsonants = () => {
      conList.empty();
      this.phon.consonants.forEach(
        (ph, i) => renderPhonRow(
          conList,
          ph,
          false,
          savePhon,
          () => {
            this.phon.consonants.splice(i, 1);
            savePhon();
            redrawConsonants();
          }
        )
      );
    };
    redrawConsonants();
    conSection.createEl("button", { cls: "rw-btn rw-btn-sm", text: "+ Consonant" }).addEventListener("click", () => {
      this.phon.consonants.push({ symbol: "", pron: "", long: false });
      savePhon();
      redrawConsonants();
    });
    el.createDiv({ cls: "rw-divider" });
    const modeSection = el.createDiv({ cls: "rw-phon-section" });
    modeSection.createEl("p", { cls: "rw-label", text: "Validation mode" });
    const modeRow = modeSection.createDiv({ cls: "rw-mode-row" });
    const makeMode = (id, label, desc) => {
      const btn = modeRow.createEl("button", {
        cls: "rw-mode-btn" + (this.phon.mode === id ? " is-active" : ""),
        text: label
      });
      btn.title = desc;
      btn.addEventListener("click", () => {
        this.phon.mode = id;
        savePhon();
        modeRow.querySelectorAll(".rw-mode-btn").forEach((b) => b.removeClass("is-active"));
        btn.addClass("is-active");
      });
    };
    makeMode("strict", "Strict", "Warn if a word uses sounds not in your inventory.");
    makeMode("permissive", "Permissive", "Allow any characters; inventory is for reference only.");
    const bannedWrap = modeSection.createDiv({ cls: "rw-modal-field" });
    bannedWrap.createEl("label", { text: "Banned clusters (comma-separated):" });
    const bannedIn = bannedWrap.createEl("input", { cls: "rw-input", attr: { type: "text", value: this.phon.banned.join(", "), placeholder: "e.g. kk, str" } });
    bannedIn.addEventListener("change", () => {
      this.phon.banned = bannedIn.value.split(",").map((s) => s.trim()).filter(Boolean);
      savePhon();
    });
    el.createDiv({ cls: "rw-divider" });
    const trySection = el.createDiv({ cls: "rw-phon-section" });
    trySection.createEl("p", { cls: "rw-label", text: "Try a word" });
    trySection.createEl("p", { cls: "rw-subtitle", text: "See how a word breaks into phonemes and syllables. Click a syllable to correct the stress \u2014 the network learns each time." });
    const tryInput = trySection.createEl("input", { cls: "rw-input rw-input-lg", attr: { type: "text", placeholder: "Type a word\u2026" } });
    const tryResult = trySection.createDiv({ cls: "rw-phon-try-result" });
    const tryWord = (forcedStress) => {
      tryResult.empty();
      const w = tryInput.value.trim().toLowerCase();
      if (!w)
        return;
      const allPh = [...this.phon.vowels, ...this.phon.consonants];
      const vowelSet = new Set(this.phon.vowels.map((v) => v.symbol));
      const tokens = phonTokenize(w, allPh);
      const syllTokens = phonSyllabify(tokens, vowelSet);
      const sylls = makeSyllables(syllTokens, this.phon);
      const knownSet = new Set(allPh.map((p) => p.symbol));
      const unknown = tokens.filter((p) => !knownSet.has(p));
      if (!tokens.length)
        return;
      const breakRow = tryResult.createDiv({ cls: "rw-phon-break" });
      syllTokens.forEach((syll, si) => {
        if (si > 0)
          breakRow.createSpan({ cls: "rw-phon-dot", text: " \xB7 " });
        syll.forEach((p) => {
          const ph = allPh.find((x) => x.symbol === p);
          const sp = breakRow.createSpan({ cls: ph ? "rw-phon-token" : "rw-phon-unknown", text: p });
          if (ph)
            sp.title = ph.pron;
        });
      });
      if (sylls.length === 0)
        return;
      if (!this.plugin.phonModel && allPh.length > 0)
        this.plugin.phonModel = newPhonModel(allPh.map((p) => p.symbol));
      const model2 = this.plugin.phonModel;
      const storedStress = this.plugin.wordStress[w];
      const submitCorrection = (stressIdx) => {
        var _a;
        this.plugin.wordStress[w] = stressIdx;
        const ex = { word: w, sylls: syllTokens, stress: stressIdx };
        const prev = this.plugin.phonExamples.findIndex((e) => e.word === w);
        if (prev >= 0)
          this.plugin.phonExamples[prev] = ex;
        else
          this.plugin.phonExamples.push(ex);
        const m = (_a = this.plugin.phonModel) != null ? _a : newPhonModel(allPh.map((p) => p.symbol));
        this.plugin.phonModel = m;
        for (let ep = 0; ep < 20; ep++)
          trainOnExample(ex, m, this.phon, 0.02);
        if (this.plugin.phonExamples.length <= 40)
          batchTrain(this.plugin.phonExamples, m, this.phon, 10);
        void this.plugin.saveSettings();
        new import_obsidian.Notice("Correction saved!");
        tryWord(stressIdx);
      };
      const activeStress = forcedStress !== void 0 ? forcedStress : storedStress !== void 0 ? storedStress : model2 && this.plugin.phonExamples.length >= 2 ? predictStress(sylls, model2).stressIdx : null;
      const isOverride = forcedStress !== void 0 || storedStress !== void 0;
      if (activeStress !== null && sylls.length > 0) {
        const pron = phonReconstruct(syllTokens, activeStress);
        const reading = phonPronReading(syllTokens, activeStress, this.phon);
        const pronRow = tryResult.createDiv({ cls: "rw-phon-pron-row" });
        renderSyllableDisplay(pronRow, syllTokens, activeStress);
        pronRow.createSpan({ cls: "rw-phon-reading", text: reading });
        const ttsBtn = pronRow.createEl("button", { cls: "rw-btn rw-btn-sm rw-tts-btn", text: "\u{1F50A}" });
        ttsBtn.addEventListener("click", () => ttsSpeak(reading, ttsBtn));
        if (isOverride) {
          pronRow.createSpan({ cls: "rw-conf rw-conf-high", text: "\u2713 corrected" });
        } else if (model2) {
          const { confidence } = predictStress(sylls, model2);
          const confPct = Math.round(confidence * 100);
          const confCls = confidence > 0.75 ? "rw-conf-high" : confidence > 0.45 ? "rw-conf-mid" : "rw-conf-low";
          pronRow.createSpan({ cls: `rw-conf ${confCls}`, text: `${confPct}% confident` });
        }
        if (sylls.length > 1) {
          const corrRow = tryResult.createDiv({ cls: "rw-phon-corr-row" });
          corrRow.createSpan({ cls: "rw-label", text: isOverride ? "Change: " : "Correct: " });
          const corrIn = corrRow.createEl("input", {
            cls: "rw-input rw-phon-corr-input",
            attr: { type: "text", value: pron, placeholder: `'syll-syll  (apostrophe = stress)` }
          });
          const applyCorr = () => {
            var _a, _b;
            const si = parseStressNotation(corrIn.value, sylls.length);
            if (si === null) {
              new import_obsidian.Notice(`Put ' before the stressed syllable, e.g. '${syllTokens[0].join("")}-${(_b = (_a = syllTokens[1]) == null ? void 0 : _a.join("")) != null ? _b : ""}`);
              return;
            }
            submitCorrection(si);
          };
          corrIn.addEventListener("keydown", (e) => {
            if (e.key === "Enter")
              applyCorr();
          });
          corrRow.createEl("button", { cls: "rw-btn rw-btn-sm", text: "Submit" }).addEventListener("click", applyCorr);
          const stressRow = tryResult.createDiv({ cls: "rw-phon-stress-row" });
          stressRow.createSpan({ cls: "rw-label", text: "or click: " });
          syllTokens.forEach((syll, si) => {
            stressRow.createEl("button", {
              cls: "rw-btn rw-btn-sm rw-phon-syll" + (si === activeStress ? " is-stressed" : ""),
              text: syll.join("")
            }).addEventListener("click", () => submitCorrection(si));
          });
        } else {
          tryResult.createEl("p", { cls: "rw-phon-hint", text: "Single syllable \u2014 no stress to predict." });
        }
      } else if (sylls.length > 1) {
        const needed = Math.max(0, 2 - this.plugin.phonExamples.length);
        tryResult.createEl("p", { cls: "rw-empty", text: `${needed} more example${needed !== 1 ? "s" : ""} needed to enable predictions.` });
        const corrRow = tryResult.createDiv({ cls: "rw-phon-corr-row" });
        corrRow.createSpan({ cls: "rw-label", text: "Type stress: " });
        const corrIn = corrRow.createEl("input", {
          cls: "rw-input rw-phon-corr-input",
          attr: { type: "text", placeholder: `'syll-syll  (apostrophe = stress)` }
        });
        const applyCorr = () => {
          var _a, _b;
          const si = parseStressNotation(corrIn.value, sylls.length);
          if (si === null) {
            new import_obsidian.Notice(`Put ' before the stressed syllable, e.g. '${syllTokens[0].join("")}-${(_b = (_a = syllTokens[1]) == null ? void 0 : _a.join("")) != null ? _b : ""}`);
            return;
          }
          submitCorrection(si);
        };
        corrIn.addEventListener("keydown", (e) => {
          if (e.key === "Enter")
            applyCorr();
        });
        corrRow.createEl("button", { cls: "rw-btn rw-btn-sm", text: "Submit" }).addEventListener("click", applyCorr);
        const stressRow = tryResult.createDiv({ cls: "rw-phon-stress-row" });
        stressRow.createSpan({ cls: "rw-label", text: "or click: " });
        syllTokens.forEach((syll, si) => {
          stressRow.createEl("button", {
            cls: "rw-btn rw-btn-sm rw-phon-syll",
            text: syll.join("")
          }).addEventListener("click", () => submitCorrection(si));
        });
      }
      if (this.phon.mode === "strict" && unknown.length > 0)
        tryResult.createEl("p", { cls: "rw-phon-warn", text: `Unknown sounds: ${[...new Set(unknown)].join(", ")} \u2014 add them to your inventory above.` });
      const wordStr = tokens.join("");
      const hits = this.phon.banned.filter((b) => b && wordStr.includes(b));
      if (hits.length)
        tryResult.createEl("p", { cls: "rw-phon-warn", text: `Banned cluster${hits.length > 1 ? "s" : ""}: ${hits.join(", ")}` });
    };
    tryInput.addEventListener("input", () => tryWord());
    el.createDiv({ cls: "rw-divider" });
    const mapSection = el.createDiv({ cls: "rw-phon-section" });
    mapSection.createEl("p", { cls: "rw-label", text: "Phoneme map" });
    const model = this.plugin.phonModel;
    if (model && this.plugin.phonExamples.length >= 5) {
      mapSection.createEl("p", { cls: "rw-subtitle", text: "Phonemes that behave similarly in stress patterns cluster together. Circle = vowel, diamond = consonant." });
      const allPh = [...this.phon.vowels, ...this.phon.consonants];
      const vowelSet = new Set(this.phon.vowels.map((v) => v.symbol));
      const withEmb = allPh.filter((ph) => model.E[ph.symbol]);
      if (withEmb.length >= 3) {
        const vecs = withEmb.map((ph) => model.E[ph.symbol]);
        const coords = pca2d(vecs);
        const xs = coords.map((c) => c[0]), ys = coords.map((c) => c[1]);
        const minX = Math.min(...xs), maxX = Math.max(...xs);
        const minY = Math.min(...ys), maxY = Math.max(...ys);
        const rX = maxX - minX || 1, rY = maxY - minY || 1;
        const mapX = (x) => 20 + (x - minX) / rX * 180;
        const mapY = (y) => 20 + (y - minY) / rY * 150;
        const svgEl = activeDocument.createElementNS(SVGNS, "svg");
        svgEl.setAttribute("width", "220");
        svgEl.setAttribute("height", "200");
        svgEl.setAttribute("class", "rw-phon-map");
        withEmb.forEach((ph, i) => {
          const x = mapX(coords[i][0]), y = mapY(coords[i][1]);
          const isV = vowelSet.has(ph.symbol);
          if (isV) {
            const c = activeDocument.createElementNS(SVGNS, "circle");
            c.setAttribute("cx", String(x));
            c.setAttribute("cy", String(y));
            c.setAttribute("r", "6");
            c.setAttribute("class", "rw-node-root");
            svgEl.appendChild(c);
          } else {
            const r = activeDocument.createElementNS(SVGNS, "rect");
            r.setAttribute("x", String(x - 5));
            r.setAttribute("y", String(y - 5));
            r.setAttribute("width", "10");
            r.setAttribute("height", "10");
            r.setAttribute("transform", `rotate(45,${x},${y})`);
            r.setAttribute("class", "rw-node-word");
            svgEl.appendChild(r);
          }
          const t = activeDocument.createElementNS(SVGNS, "text");
          t.setAttribute("x", String(x));
          t.setAttribute("y", String(y - 10));
          t.setAttribute("text-anchor", "middle");
          t.setAttribute("class", "rw-graph-label");
          t.textContent = `${ph.symbol} (${ph.pron})`;
          svgEl.appendChild(t);
        });
        mapSection.appendChild(svgEl);
      } else {
        mapSection.createEl("p", { cls: "rw-empty", text: "Not enough phonemes with trained embeddings yet." });
      }
    } else {
      const needed = Math.max(0, 5 - this.plugin.phonExamples.length);
      mapSection.createEl("p", { cls: "rw-empty", text: `Map appears after ${needed} more stress example${needed !== 1 ? "s" : ""}. Use "Try a word" to add them.` });
    }
    el.createDiv({ cls: "rw-divider" });
    const notesSection = el.createDiv({ cls: "rw-phon-section" });
    notesSection.createEl("p", { cls: "rw-label", text: "Notes" });
    const notesArea = notesSection.createEl("textarea", { cls: "rw-textarea", attr: { placeholder: "Free-form phonology notes\u2026", rows: "3" } });
    notesArea.value = this.phon.notes;
    notesArea.addEventListener("change", () => {
      this.phon.notes = notesArea.value;
      savePhon();
    });
    const obs = inferPhono(this.words, this.phon);
    if (obs.length) {
      el.createDiv({ cls: "rw-divider" });
      const obsSection = el.createDiv({ cls: "rw-phon-section" });
      obsSection.createEl("p", { cls: "rw-label", text: "Phonotactics observations" });
      obsSection.createEl("p", { cls: "rw-subtitle", text: "Automatically inferred from your word list." });
      const obsList = obsSection.createEl("ul", { cls: "rw-obs-list" });
      obs.forEach((o) => obsList.createEl("li", { text: o }));
    }
    if (this.plugin.phonExamples.length > 0) {
      el.createDiv({ cls: "rw-divider" });
      const trainSection = el.createDiv({ cls: "rw-phon-section" });
      trainSection.createEl("p", { cls: "rw-label", text: "Training data" });
      trainSection.createEl("p", { cls: "rw-subtitle", text: `${this.plugin.phonExamples.length} stress example${this.plugin.phonExamples.length !== 1 ? "s" : ""} saved.` });
      const runTrainBtn = trainSection.createEl("button", { cls: "rw-btn rw-btn-sm", text: "Re-train (50 epochs)" });
      runTrainBtn.addEventListener("click", () => {
        var _a;
        if (!this.plugin.phonModel) {
          const allPh = [...this.phon.vowels, ...this.phon.consonants];
          this.plugin.phonModel = newPhonModel(allPh.map((p) => p.symbol));
        }
        const m = (_a = this.plugin.phonModel) != null ? _a : newPhonModel([...this.phon.vowels, ...this.phon.consonants].map((p) => p.symbol));
        this.plugin.phonModel = m;
        batchTrain(this.plugin.phonExamples, m, this.phon, 50);
        void this.plugin.saveSettings();
        new import_obsidian.Notice("Re-training complete!");
      });
      const clearBtn = trainSection.createEl("button", { cls: "rw-btn rw-btn-sm rw-btn-danger rw-btn-ml", text: "Clear training data" });
      clearBtn.addEventListener("click", () => {
        this.plugin.phonExamples = [];
        this.plugin.phonModel = null;
        this.plugin.wordStress = {};
        void this.plugin.saveSettings();
        new import_obsidian.Notice("Training data cleared.");
        this.render();
      });
    }
  }
};
var GraphView = class extends import_obsidian.ItemView {
  constructor(leaf, plugin) {
    super(leaf);
    this.roots = [];
    this.words = [];
    this.plugin = plugin;
  }
  getViewType() {
    return VIEW_TYPE_GRAPH;
  }
  getDisplayText() {
    return "Root Graph";
  }
  getIcon() {
    return "git-fork";
  }
  async onOpen() {
    try {
      [this.roots, this.words] = await Promise.all([
        this.plugin.loadRoots(),
        this.plugin.loadWords()
      ]);
    } catch (e) {
      console.error("Rootweave graph error", e);
    }
    this.render();
  }
  async onClose() {
  }
  render() {
    const el = this.contentEl;
    el.empty();
    el.addClass("rw-graph-view");
    const bar = el.createDiv({ cls: "rw-graph-bar" });
    const legend = bar.createSpan({ cls: "rw-graph-legend" });
    legend.createSpan({ cls: "rw-legend-root", text: "\u25CF" });
    legend.appendText(" Root   ");
    legend.createSpan({ cls: "rw-legend-word", text: "\u25CF" });
    legend.appendText(" Word");
    bar.createEl("button", { cls: "rw-btn rw-btn-sm", text: "Refresh" }).addEventListener("click", () => {
      void this.onOpen();
    });
    if (!this.roots.length && !this.words.length) {
      el.createEl("p", { cls: "rw-empty", text: "No data yet \u2014 add some roots and words first." });
      return;
    }
    const canvas = el.createDiv({ cls: "rw-graph-canvas" });
    window.requestAnimationFrame(() => {
      this.buildGraph(canvas);
    });
  }
  buildGraph(container) {
    const W = container.clientWidth || 500;
    const H = container.clientHeight || 500;
    const nodes = [
      ...this.roots.map((r) => ({ id: `r:${r.root}`, kind: "root", label: r.root, sub: r.meaning, tag: r.category, x: 0, y: 0, vx: 0, vy: 0 })),
      ...this.words.map((w) => ({ id: `w:${w.word}`, kind: "word", label: w.word, sub: w.meaning, tag: w.pos, x: 0, y: 0, vx: 0, vy: 0 }))
    ];
    const edges = this.words.flatMap(
      (w) => w.roots.filter((r) => nodes.some((n) => n.id === `r:${r}`)).map((r) => ({ src: `r:${r}`, tgt: `w:${w.word}` }))
    );
    forceLayout(nodes, edges, W, H);
    const nodeMap = new Map(nodes.map((n) => [n.id, n]));
    const svg = mksvg("svg");
    svg.setAttribute("width", String(W));
    svg.setAttribute("height", String(H));
    container.appendChild(svg);
    let panX = 0, panY = 0, zoom = 1;
    const world = mksvg("g");
    svg.appendChild(world);
    const applyTransform = () => world.setAttribute("transform", `translate(${panX},${panY}) scale(${zoom})`);
    applyTransform();
    const toGraph = (ex, ey) => {
      const r = svg.getBoundingClientRect();
      return { x: (ex - r.left - panX) / zoom, y: (ey - r.top - panY) / zoom };
    };
    const edgeEls = /* @__PURE__ */ new Map();
    edges.forEach((e) => {
      const src = nodeMap.get(e.src), tgt = nodeMap.get(e.tgt);
      if (!src || !tgt)
        return;
      const line = mksvg("line");
      line.setAttribute("class", "rw-graph-edge");
      line.setAttribute("x1", String(src.x));
      line.setAttribute("y1", String(src.y));
      line.setAttribute("x2", String(tgt.x));
      line.setAttribute("y2", String(tgt.y));
      world.appendChild(line);
      edgeEls.set(`${e.src}|${e.tgt}`, line);
    });
    const refreshEdges = () => edges.forEach((e) => {
      const line = edgeEls.get(`${e.src}|${e.tgt}`);
      const src = nodeMap.get(e.src), tgt = nodeMap.get(e.tgt);
      if (!line || !src || !tgt)
        return;
      line.setAttribute("x1", String(src.x));
      line.setAttribute("y1", String(src.y));
      line.setAttribute("x2", String(tgt.x));
      line.setAttribute("y2", String(tgt.y));
    });
    const nodeEls = /* @__PURE__ */ new Map();
    const tip = container.createDiv({ cls: "rw-graph-tip" });
    nodes.forEach((node) => {
      const g = mksvg("g");
      g.setAttribute("class", `rw-graph-node rw-graph-node-${node.kind}`);
      g.setAttribute("transform", `translate(${node.x},${node.y})`);
      const radius = node.kind === "root" ? 13 : 8;
      const circle = mksvg("circle");
      circle.setAttribute("r", String(radius));
      circle.setAttribute("class", `rw-node-${node.kind}`);
      g.appendChild(circle);
      const label = mksvg("text");
      label.setAttribute("y", String(radius + 12));
      label.setAttribute("text-anchor", "middle");
      label.setAttribute("class", "rw-graph-label");
      label.textContent = node.label;
      g.appendChild(label);
      world.appendChild(g);
      nodeEls.set(node.id, g);
      g.addEventListener("mouseenter", () => {
        tip.setText(`${node.label}  \u2014  ${node.sub}${node.tag ? `  [${node.tag}]` : ""}`);
        tip.addClass("is-visible");
      });
      g.addEventListener("mouseleave", () => tip.removeClass("is-visible"));
    });
    let dragNode = null;
    let dragOX = 0, dragOY = 0;
    let panning = false, panSX = 0, panSY = 0;
    nodes.forEach((node) => {
      var _a;
      (_a = nodeEls.get(node.id)) == null ? void 0 : _a.addEventListener("mousedown", (e) => {
        e.stopPropagation();
        const gp = toGraph(e.clientX, e.clientY);
        dragOX = gp.x - node.x;
        dragOY = gp.y - node.y;
        dragNode = node;
      });
    });
    svg.addEventListener("mousedown", (e) => {
      panning = true;
      panSX = e.clientX - panX;
      panSY = e.clientY - panY;
    });
    svg.addEventListener("mousemove", (e) => {
      var _a;
      if (dragNode) {
        const gp = toGraph(e.clientX, e.clientY);
        dragNode.x = gp.x - dragOX;
        dragNode.y = gp.y - dragOY;
        (_a = nodeEls.get(dragNode.id)) == null ? void 0 : _a.setAttribute("transform", `translate(${dragNode.x},${dragNode.y})`);
        refreshEdges();
      } else if (panning) {
        panX = e.clientX - panSX;
        panY = e.clientY - panSY;
        applyTransform();
      }
    });
    const stopAll = () => {
      dragNode = null;
      panning = false;
    };
    svg.addEventListener("mouseup", stopAll);
    svg.addEventListener("mouseleave", stopAll);
    svg.addEventListener("wheel", (e) => {
      e.preventDefault();
      zoom = Math.max(0.15, Math.min(6, zoom * (e.deltaY > 0 ? 0.9 : 1.1)));
      applyTransform();
    }, { passive: false });
  }
};
var RootModal = class extends import_obsidian.Modal {
  constructor(app, existing, onSave) {
    super(app);
    this.existing = existing;
    this.onSave = onSave;
  }
  onOpen() {
    var _a, _b, _c, _d, _e, _f, _g, _h, _i, _j;
    const { contentEl } = this;
    contentEl.createEl("h2", { text: this.existing ? "Edit Root" : "Add Root" });
    const field = (label, value, placeholder) => {
      const wrap = contentEl.createDiv({ cls: "rw-modal-field" });
      wrap.createEl("label", { text: label });
      return wrap.createEl("input", { cls: "rw-input", attr: { type: "text", value, placeholder } });
    };
    const rootIn = field("Root", (_b = (_a = this.existing) == null ? void 0 : _a.root) != null ? _b : "", "e.g. vel");
    const altsIn = field("Alternates", (_d = (_c = this.existing) == null ? void 0 : _c.alternates.join(", ")) != null ? _d : "", "e.g. sight, saw \u2014 comma-separated");
    const meaningIn = field("Meaning", (_f = (_e = this.existing) == null ? void 0 : _e.meaning) != null ? _f : "", "e.g. light, clarity");
    const categoryIn = field("Category", (_h = (_g = this.existing) == null ? void 0 : _g.category) != null ? _h : "", "e.g. element, emotion");
    const notesIn = field("Notes", (_j = (_i = this.existing) == null ? void 0 : _i.notes) != null ? _j : "", "Optional");
    const saveBtn = contentEl.createEl("button", { cls: "rw-btn rw-btn-primary", text: "Save" });
    saveBtn.addEventListener("click", () => {
      const root = rootIn.value.trim();
      if (!root) {
        new import_obsidian.Notice("Root cannot be empty.");
        return;
      }
      this.onSave({
        root,
        alternates: altsIn.value.split(",").map((s) => s.trim()).filter(Boolean),
        meaning: meaningIn.value.trim(),
        category: categoryIn.value.trim(),
        notes: notesIn.value.trim()
      });
      this.close();
    });
    [rootIn, altsIn, meaningIn, categoryIn, notesIn].forEach(
      (inp) => inp.addEventListener("keydown", (e) => {
        if (e.key === "Enter")
          saveBtn.click();
      })
    );
  }
  onClose() {
    this.contentEl.empty();
  }
};
var WordModal = class extends import_obsidian.Modal {
  constructor(app, existing, onSave) {
    super(app);
    this.existing = existing;
    this.onSave = onSave;
  }
  onOpen() {
    var _a, _b, _c, _d, _e, _f, _g, _h;
    const { contentEl } = this;
    contentEl.createEl("h2", { text: this.existing ? "Edit Word" : "Add Word" });
    const field = (label, value, placeholder) => {
      const wrap = contentEl.createDiv({ cls: "rw-modal-field" });
      wrap.createEl("label", { text: label });
      return wrap.createEl("input", { cls: "rw-input", attr: { type: "text", value, placeholder } });
    };
    const wordIn = field("Word", (_b = (_a = this.existing) == null ? void 0 : _a.word) != null ? _b : "", "e.g. veliu");
    const meaningIn = field("Meaning", (_d = (_c = this.existing) == null ? void 0 : _c.meaning) != null ? _d : "", "e.g. lights");
    const posIn = field("Part of speech", (_f = (_e = this.existing) == null ? void 0 : _e.pos) != null ? _f : "", "noun, verb\u2026");
    const rootsIn = field("Roots", (_h = (_g = this.existing) == null ? void 0 : _g.roots.join(", ")) != null ? _h : "", "e.g. vel, iu \u2014 comma-separated");
    const saveBtn = contentEl.createEl("button", { cls: "rw-btn rw-btn-primary", text: "Save" });
    saveBtn.addEventListener("click", () => {
      const word = wordIn.value.trim();
      if (!word) {
        new import_obsidian.Notice("Word cannot be empty.");
        return;
      }
      this.onSave({
        word,
        meaning: meaningIn.value.trim(),
        pos: posIn.value.trim(),
        roots: rootsIn.value.split(",").map((s) => s.trim()).filter(Boolean)
      });
      this.close();
    });
    [wordIn, meaningIn, posIn, rootsIn].forEach(
      (inp) => inp.addEventListener("keydown", (e) => {
        if (e.key === "Enter")
          saveBtn.click();
      })
    );
  }
  onClose() {
    this.contentEl.empty();
  }
};
var RuleModal = class extends import_obsidian.Modal {
  constructor(app, existing, onSave) {
    super(app);
    this.existing = existing;
    this.onSave = onSave;
  }
  onOpen() {
    var _a, _b, _c, _d, _e, _f, _g, _h, _i, _j, _k;
    const { contentEl } = this;
    contentEl.createEl("h2", { text: this.existing ? "Edit Rule" : "Add Rule" });
    const field = (label, value, placeholder) => {
      const wrap = contentEl.createDiv({ cls: "rw-modal-field" });
      wrap.createEl("label", { text: label });
      return wrap.createEl("input", { cls: "rw-input", attr: { type: "text", value, placeholder } });
    };
    const nameIn = field("Name", (_b = (_a = this.existing) == null ? void 0 : _a.name) != null ? _b : "", "e.g. Plural");
    const formIn = field("Form", (_d = (_c = this.existing) == null ? void 0 : _c.form) != null ? _d : "", "e.g. -iu  or  on-");
    const meaningIn = field("Meaning", (_f = (_e = this.existing) == null ? void 0 : _e.meaning) != null ? _f : "", "e.g. plural marker");
    const exampleIn = field("Example", (_h = (_g = this.existing) == null ? void 0 : _g.example) != null ? _h : "", "e.g. vel \u2192 veliu (lights)");
    const notesIn = field("Notes", (_j = (_i = this.existing) == null ? void 0 : _i.notes) != null ? _j : "", "Optional");
    const typeWrap = contentEl.createDiv({ cls: "rw-modal-field" });
    typeWrap.createEl("label", { text: "Type" });
    const typeSel = typeWrap.createEl("select", { cls: "rw-select" });
    typeSel.createEl("option", { value: "prefix", text: "prefix \u2014 added before the word (e.g. on-)" });
    typeSel.createEl("option", { value: "suffix", text: "suffix \u2014 added after the word (e.g. -iu)" });
    typeSel.createEl("option", { value: "infix", text: "infix \u2014 inserted inside the word" });
    typeSel.createEl("option", { value: "other", text: "other \u2014 freeform rule or particle" });
    if ((_k = this.existing) == null ? void 0 : _k.type)
      typeSel.value = this.existing.type;
    const saveBtn = contentEl.createEl("button", { cls: "rw-btn rw-btn-primary", text: "Save" });
    saveBtn.addEventListener("click", () => {
      const name = nameIn.value.trim();
      if (!name) {
        new import_obsidian.Notice("Name cannot be empty.");
        return;
      }
      this.onSave({
        name,
        type: typeSel.value,
        form: formIn.value.trim(),
        meaning: meaningIn.value.trim(),
        example: exampleIn.value.trim(),
        notes: notesIn.value.trim()
      });
      this.close();
    });
    [nameIn, formIn, meaningIn, exampleIn, notesIn].forEach(
      (inp) => inp.addEventListener("keydown", (e) => {
        if (e.key === "Enter")
          saveBtn.click();
      })
    );
  }
  onClose() {
    this.contentEl.empty();
  }
};
var RootweaveSettingTab = class extends import_obsidian.PluginSettingTab {
  constructor(app, plugin) {
    super(app, plugin);
    this.plugin = plugin;
  }
  getSettingDefinitions() {
    return [
      this.languageDef(),
      { type: "group", heading: "Import", items: this.importDefs() },
      { type: "group", heading: "Data tools", items: [this.cleanseDef()] }
    ];
  }
  languageDef() {
    return {
      name: "Language name",
      desc: "Used in export file names and headings.",
      render: (setting) => {
        setting.setName("Language name").setDesc("Used in export file names and headings.").addText(
          (text) => text.setPlaceholder("My Conlang").setValue(this.plugin.settings.language).onChange((value) => {
            this.plugin.settings.language = value;
            void this.plugin.saveSettings();
          })
        );
      }
    };
  }
  importDefs() {
    let importType = "roots";
    const ROOT_TOKENS = "Tokens: [root], [alternates], [meaning], [category], [notes]";
    const WORD_TOKENS = "Tokens: [word], [meaning], [pos]";
    let formatSetting = null;
    let templateEl;
    let dataEl;
    const formatDesc = () => `Arrange tokens to match your data. Each line is parsed against this pattern. ${importType === "roots" ? ROOT_TOKENS : WORD_TOKENS}`;
    return [
      {
        name: "Import type",
        desc: "Whether the pasted data below is parsed as roots or dictionary words.",
        render: (setting) => {
          setting.setName("Type").addDropdown(
            (dd) => dd.addOption("roots", "Roots").addOption("words", "Words").setValue("roots").onChange((val) => {
              importType = val;
              formatSetting == null ? void 0 : formatSetting.setDesc(formatDesc());
            })
          );
        }
      },
      {
        name: "Format template",
        desc: "Arrange tokens to match your data. Each line is parsed against this pattern.",
        render: (setting) => {
          formatSetting = setting;
          setting.setName("Format template").setDesc(formatDesc()).addText((text) => {
            text.setPlaceholder("[root] [meaning]").setValue("[root] [meaning]");
            templateEl = text.inputEl;
          });
        }
      },
      {
        name: "Import data",
        desc: "One entry per line. Lines starting with # are skipped.",
        render: (setting) => {
          setting.setName("Data").setDesc("One entry per line. Lines starting with # are skipped.").addTextArea((ta) => {
            ta.setPlaceholder("vel light\nkar fire");
            ta.inputEl.rows = 10;
            ta.inputEl.addClass("rw-import-textarea");
            dataEl = ta.inputEl;
          });
        }
      },
      {
        name: "Import",
        desc: "Merge the parsed roots or words into your lexicon.",
        render: (setting) => {
          setting.addButton((btn) => btn.setButtonText("Import").setCta().onClick(() => {
            var _a, _b;
            const tmpl = (_a = templateEl == null ? void 0 : templateEl.value.trim()) != null ? _a : "";
            const data = (_b = dataEl == null ? void 0 : dataEl.value.trim()) != null ? _b : "";
            if (!tmpl) {
              new import_obsidian.Notice("Enter a format template first.");
              return;
            }
            if (!data) {
              new import_obsidian.Notice("Paste some data to import.");
              return;
            }
            if (importType === "roots") {
              const parsed = importRoots(tmpl, data);
              if (!parsed.length) {
                new import_obsidian.Notice("No lines matched the template \u2014 check your format.");
                return;
              }
              void this.plugin.loadRoots().then((existing) => {
                const merged = [...existing];
                let added = 0, skipped = 0;
                for (const r of parsed) {
                  if (merged.some((e) => e.root === r.root)) {
                    skipped++;
                    continue;
                  }
                  merged.push(r);
                  added++;
                }
                void this.plugin.saveRoots(merged).then(() => {
                  new import_obsidian.Notice(`Imported ${added} root${added !== 1 ? "s" : ""}${skipped ? `, skipped ${skipped}` : ""}.`);
                  void this.plugin.reloadView();
                }).catch((e) => new import_obsidian.Notice(`Save failed: ${String(e)}`));
              }).catch((e) => new import_obsidian.Notice(`Load failed: ${String(e)}`));
            } else {
              const parsed = importWords(tmpl, data);
              if (!parsed.length) {
                new import_obsidian.Notice("No lines matched the template \u2014 check your format.");
                return;
              }
              void this.plugin.loadWords().then((existing) => {
                const merged = [...existing];
                let added = 0, skipped = 0;
                for (const w of parsed) {
                  if (merged.some((e) => e.word.toLowerCase() === w.word.toLowerCase())) {
                    skipped++;
                    continue;
                  }
                  merged.push(w);
                  added++;
                }
                void this.plugin.saveWords(merged).then(() => {
                  new import_obsidian.Notice(`Imported ${added} word${added !== 1 ? "s" : ""}${skipped ? `, skipped ${skipped}` : ""}.`);
                  void this.plugin.reloadView();
                }).catch((e) => new import_obsidian.Notice(`Save failed: ${String(e)}`));
              }).catch((e) => new import_obsidian.Notice(`Load failed: ${String(e)}`));
            }
          }));
        }
      }
    ];
  }
  cleanseDef() {
    return {
      name: "Cleanse special characters",
      desc: "Replace accented and non-ASCII letters in all roots and words with plain equivalents (e.g. \xD1\u2192N, \xE9\u2192e, \xFC\u2192u, \xE6\u2192ae). Edits your files \u2014 make a backup first.",
      render: (setting) => {
        setting.setName("Cleanse special characters").setDesc("Replace accented and non-ASCII letters in all roots and words with plain equivalents (e.g. \xD1\u2192N, \xE9\u2192e, \xFC\u2192u, \xE6\u2192ae). Edits your files \u2014 make a backup first.").addButton(
          (btn) => btn.setButtonText("Cleanse").setClass("mod-warning").onClick(() => {
            void Promise.all([
              this.plugin.loadRoots(),
              this.plugin.loadWords()
            ]).then(([roots, words]) => {
              const cleanRoots = roots.map((r) => ({
                ...r,
                root: stripDiacritics(r.root),
                alternates: r.alternates.map((a) => stripDiacritics(a))
              }));
              const cleanWords = words.map((w) => ({
                ...w,
                word: stripDiacritics(w.word)
              }));
              void Promise.all([
                this.plugin.saveRoots(cleanRoots),
                this.plugin.saveWords(cleanWords)
              ]).then(() => {
                new import_obsidian.Notice(`Cleansed ${roots.length} roots and ${words.length} words.`);
                void this.plugin.reloadView();
              });
            });
          })
        );
      }
    };
  }
};
