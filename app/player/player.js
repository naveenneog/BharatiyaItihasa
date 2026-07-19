/* Itihāsa motion-comic player: animated scenes + voiced narration + word-synced highlight.
   Loads app/data/<ep>.player.json (produced by tools/voice.py). */
const BASE = "../";
const $ = s => document.querySelector(s);
const qs = new URLSearchParams(location.search);
let EP = qs.get("ep");
let LANG = qs.get("lang") || "en";

const NATIVE = { en: "English", hi: "हिन्दी", kn: "ಕನ್ನಡ", ta: "தமிழ்", te: "తెలుగు", de: "Deutsch" };

let M = null, scene = 0, runId = 0, paused = false, muted = false, musicOn = true;
const audio = new Audio(); audio.preload = "auto";
const bgs = [$("#bgA"), $("#bgB")]; let bgCur = 0, kbN = 0;

async function boot() {
  if (!EP) { document.body.innerHTML = "<p style='color:#eee;padding:24px;font:16px sans-serif'>Add <b>?ep=&lt;episode-id&gt;</b> to the URL.</p>"; return; }
  M = await fetch(`${BASE}data/${EP}.player.json`).then(r => r.json());
  $("#startTitle").textContent = (M.title_i18n && M.title_i18n[LANG]) || M.title;
  $("#startSub").textContent = [M.figure, M.era].filter(Boolean).join(" · ");
  buildLangSel(); buildProgress(); wireControls();
}

function buildLangSel() {
  const sel = $("#langSel"); sel.innerHTML = "";
  (M.langs || ["en"]).forEach(lg => {
    const o = document.createElement("option");
    o.value = lg; o.textContent = NATIVE[lg] || lg; if (lg === LANG) o.selected = true;
    sel.appendChild(o);
  });
  sel.onchange = () => { LANG = sel.value; $("#startTitle").textContent = (M.title_i18n && M.title_i18n[LANG]) || M.title; play(scene); };
}

function buildProgress() {
  const p = $("#progress"); p.innerHTML = "";
  (M.panels || []).forEach(() => { const d = document.createElement("div"); d.className = "dot"; p.appendChild(d); });
}
function updateProgress() {
  [...$("#progress").children].forEach((d, i) => {
    d.className = "dot" + (i < scene ? " done" : i === scene ? " cur" : "");
  });
}

function setToggle() { $("#toggleBtn").textContent = paused ? "▶" : "⏸"; }

function wireControls() {
  $("#startBtn").onclick = () => play(0);
  $("#replayBtn").onclick = () => play(0);
  $("#controls").addEventListener("click", e => {
    const act = e.target.getAttribute && e.target.getAttribute("data-act");
    if (act === "prev") nav(-1);
    else if (act === "next") nav(1);
    else if (act === "toggle") togglePause();
    else if (act === "mute") { muted = !muted; audio.muted = muted; $("#muteBtn").textContent = muted ? "🔇" : "🔊"; }
    else if (act === "music") { musicOn = !musicOn; if (window.Music) Music.setEnabled(musicOn); $("#musicBtn").classList.toggle("off", !musicOn); }
  });
  document.addEventListener("keydown", e => {
    if (e.code === "Space") { e.preventDefault(); togglePause(); }
    else if (e.code === "ArrowRight") nav(1);
    else if (e.code === "ArrowLeft") nav(-1);
  });
}

function togglePause() {
  paused = !paused; setToggle();
  if (paused) audio.pause(); else { const p = audio.play(); if (p) p.catch(() => {}); }
  if (window.Music) Music.setEnabled(!paused && musicOn);
}
function nav(d) { const s = Math.min((M.panels.length - 1), Math.max(0, scene + d)); play(s); }

function show(id, on) { $(id).classList.toggle("hidden", !on); }

async function play(from = 0) {
  show("#startCard", false); show("#endCard", false);
  if (window.Music) { Music.resume(); Music.setEnabled(musicOn); }
  const my = ++runId; paused = false; setToggle();
  for (scene = from; scene < M.panels.length; scene++) {
    updateProgress();
    const ok = await playScene(M.panels[scene], my);
    if (my !== runId) return;
    if (!ok) return;
  }
  showEnd();
}

function showEnd() {
  $("#layer").innerHTML = "";
  $("#endMoral").textContent = M.moral || "";
  show("#endCard", true);
  audio.pause();
}

function setBg(art, my) {
  return new Promise(res => {
    const next = bgs[1 - bgCur];
    next.style.backgroundImage = `url("${BASE}${art}")`;
    next.classList.remove("kb1", "kb2", "kb3"); void next.offsetWidth;
    kbN = (kbN % 3) + 1; next.classList.add("kb" + kbN, "show");
    bgs[bgCur].classList.remove("show");
    bgCur = 1 - bgCur;
    setTimeout(() => res(my === runId), 720);
  });
}

function hideChar() {
  const L = $("#actLayer"); L.querySelectorAll("img").forEach(i => i.getAnimations().forEach(a => a.cancel()));
  L.innerHTML = "";
}

function setActionScene(panel, my) {
  return new Promise(res => {
    const m = panel.motion || {};
    const next = bgs[1 - bgCur];
    next.classList.remove("mapfit");
    next.style.backgroundImage = `url("${BASE}${panel.bg}")`;
    next.classList.remove("kb1", "kb2", "kb3"); void next.offsetWidth;
    next.classList.add("show");
    bgs[bgCur].classList.remove("show"); bgCur = 1 - bgCur;
    const live = bgs[bgCur];
    live.getAnimations().forEach(a => a.cancel());
    live.animate([{ transform: "scale(1) translateX(0)" },
                  { transform: `scale(${m.bgZoom || 1.12}) translateX(${m.bgPan || -6}px)` }],
                 { duration: (m.dur || 7000) + 1600, easing: "ease-out", fill: "forwards" });
    const L = $("#actLayer"); L.innerHTML = "";
    const chars = panel.chars || (panel.char ? [{ img: panel.char, motion: panel.motion || {} }] : []);
    chars.forEach(c => {
      const cm = c.motion || {};
      const img = document.createElement("img");
      img.src = BASE + c.img;
      if (c.spirit) img.classList.add("spirit");
      L.appendChild(img);
      if (c.spirit) {
        // a fallen hero returning as a fading spirit: materialise, glow, dissolve slowly upward
        img.animate([
          { transform: `translate(calc(-50% + ${cm.fromX ?? 0}vw),16%) scale(${cm.fromScale ?? 0.9})`, opacity: 0, offset: 0 },
          { opacity: 0.62, offset: 0.34 },
          { opacity: 0.5, offset: 0.72 },
          { transform: `translate(calc(-50% + ${cm.toX ?? 0}vw),-12%) scale(${cm.toScale ?? 1.05})`, opacity: 0.1, offset: 1 }
        ], { duration: cm.dur || m.dur || 8200, easing: "ease-in-out", fill: "forwards", delay: cm.delay || 0 });
      } else {
        img.animate([
          { transform: `translate(calc(-50% + ${cm.fromX ?? -42}vw),6%) scale(${cm.fromScale ?? 0.82}) rotate(${cm.rot || 0}deg)`, opacity: 0.12, offset: 0 },
          { opacity: 1, offset: 0.16 },
          { transform: `translate(calc(-50% + ${cm.toX ?? 4}vw),0) scale(${cm.toScale ?? 1.14}) rotate(0deg)`, opacity: 1, offset: 1 }
        ], { duration: cm.dur || m.dur || 7000, easing: "cubic-bezier(.16,.7,.3,1)", fill: "forwards", delay: cm.delay || 0 });
      }
    });
    setTimeout(() => res(my === runId), 720);
  });
}

function setSplitScene(panel, my) {
  return new Promise(res => {
    const L = $("#splitLayer"); L.innerHTML = ""; L.classList.remove("hidden");
    bgs.forEach(b => b.classList.remove("show"));          // montage covers the whole stage
    // three HORIZONTAL diagonal bands (full width) so faces + actions read left-to-right
    const clips = ["polygon(0 0,100% 0,100% 29%,0 41%)",
                   "polygon(0 43%,100% 31%,100% 65%,0 77%)",
                   "polygon(0 79%,100% 67%,100% 100%,0 100%)"];
    const enters = ["translate(-104%,-6%)", "translate(104%,0)", "translate(-104%,6%)"];
    const slots = ["12%", "48%", "82%"];                   // slogan vertical anchor per band
    const slices = panel.slices || [];
    slices.forEach((s, i) => {
      const k = i % 3;
      const d = document.createElement("div"); d.className = "slice";
      d.style.backgroundImage = `url("${BASE}${s.img}")`;
      d.style.backgroundPosition = s.pos || "center 34%";
      if (s.zoom) d.style.backgroundSize = s.zoom;
      d.style.clipPath = clips[k]; d.style.webkitClipPath = clips[k];
      L.appendChild(d);
      const delay = i * 430;
      d.animate([
        { transform: enters[k], opacity: 0, offset: 0 },
        { opacity: 1, offset: 0.4 },
        { transform: "translate(0,0)", opacity: 1, offset: 1 }
      ], { duration: 900, delay, easing: "cubic-bezier(.18,.75,.25,1)", fill: "both" });
      const fl = document.createElement("div"); fl.className = "flash"; d.appendChild(fl);
      fl.animate([{ opacity: 0 }, { opacity: 0.5 }, { opacity: 0 }],
        { duration: 360, delay: delay + 520, easing: "ease-out" });
      const slg = s.slogan && (typeof s.slogan === "string" ? s.slogan : (s.slogan[LANG] || s.slogan.en));
      if (slg) {
        const sl = document.createElement("div"); sl.className = "slogan";
        sl.style.left = "5%"; sl.style.top = slots[k]; sl.textContent = slg; L.appendChild(sl);
        sl.animate([
          { transform: "translateY(-50%) scale(1.5) rotate(-3deg)", opacity: 0, offset: 0 },
          { transform: "translateY(-50%) scale(.94) rotate(-1deg)", opacity: 1, offset: 0.6 },
          { transform: "translateY(-50%) scale(1) rotate(-1deg)", opacity: 1, offset: 1 }
        ], { duration: 640, delay: delay + 380, easing: "cubic-bezier(.2,1.5,.3,1)", fill: "both" });
      }
    });
    setTimeout(() => res(my === runId), slices.length * 430 + 760);
  });
}

function clearScene() {
  hideChar();
  const sl = $("#splitLayer"); sl.classList.add("hidden"); sl.innerHTML = "";
  const hc = $("#heroCard"); hc.classList.add("hidden"); hc.classList.remove("in");
  $("#mapPin").classList.add("hidden"); $("#mapLabel").classList.add("hidden");
  bgs.forEach(b => b.classList.remove("mapfit"));
}

function moodFor(p) {
  return p.mood || (p.type === "action" || p.type === "split" ? "battle" : p.type === "hero" ? "triumph"
    : p.type === "map" ? "suspense" : "calm");
}

function setHeroScene(panel, my) {
  return new Promise(res => {
    const next = bgs[1 - bgCur];
    next.classList.remove("mapfit");
    next.style.backgroundImage = `url("${BASE}${panel.art}")`;
    next.classList.remove("kb1", "kb2", "kb3"); void next.offsetWidth;
    kbN = (kbN % 3) + 1; next.classList.add("kb" + kbN, "show");
    bgs[bgCur].classList.remove("show"); bgCur = 1 - bgCur;
    $("#heroEra").textContent = panel.era || "";
    $("#heroName").textContent = panel.name || "";
    const ep = $("#heroEpithets"); ep.innerHTML = "";
    (panel.epithets || []).forEach(e => { const s = document.createElement("span"); s.textContent = e; ep.appendChild(s); });
    $("#heroLegend").textContent = panel.legend || "";
    const hc = $("#heroCard"); hc.classList.remove("hidden", "in"); void hc.offsetWidth;
    requestAnimationFrame(() => hc.classList.add("in"));
    setTimeout(() => res(my === runId), 950);
  });
}

function mapMarker(x, y) {
  const st = $("#stage"), W = st.clientWidth, H = st.clientHeight, A = 1024 / 1536;
  let dw, dh, ox, oy;
  if (W / H > A) { dh = H; dw = H * A; ox = (W - dw) / 2; oy = 0; }
  else { dw = W; dh = W / A; ox = 0; oy = (H - dh) / 2; }
  return { left: ox + x * dw, top: oy + y * dh };
}

function setMapScene(panel, my) {
  return new Promise(res => {
    const next = bgs[1 - bgCur];
    next.style.backgroundImage = `url("${BASE}${panel.map}")`;
    next.classList.remove("kb1", "kb2", "kb3", "show"); next.classList.add("mapfit"); void next.offsetWidth;
    next.classList.add("show");
    bgs[bgCur].classList.remove("show"); bgCur = 1 - bgCur;
    const m = mapMarker(panel.x ?? 0.45, panel.y ?? 0.35);
    const pin = $("#mapPin"), lab = $("#mapLabel");
    pin.style.left = m.left + "px"; pin.style.top = m.top + "px"; pin.classList.remove("hidden");
    lab.style.left = m.left + "px"; lab.style.top = m.top + "px"; lab.textContent = panel.label || "";
    lab.classList.remove("hidden");
    setTimeout(() => res(my === runId), 800);
  });
}

async function playScene(panel, my) {
  clearScene();
  if (window.Music) Music.setMood(moodFor(panel));
  let ok;
  if (panel.type === "action") ok = await setActionScene(panel, my);
  else if (panel.type === "split") ok = await setSplitScene(panel, my);
  else if (panel.type === "hero") ok = await setHeroScene(panel, my);
  else if (panel.type === "map") ok = await setMapScene(panel, my);
  else ok = await setBg(panel.art, my);
  if (my !== runId || !ok) return false;
  for (const line of (panel.lines || [])) {
    const r = await playLine(line, my);
    if (my !== runId || !r) return false;
    await sleep(380, my);
  }
  await sleep(480, my);
  return true;
}

function sleep(ms, my) {
  return new Promise(res => {
    let el = 0; const step = 80;
    const t = setInterval(() => {
      if (my !== runId) { clearInterval(t); return res(); }
      if (!paused) el += step;
      if (el >= ms) { clearInterval(t); res(); }
    }, step);
  });
}

function playLine(line, my) {
  return new Promise(resolve => {
    const layer = $("#layer"); layer.innerHTML = "";
    const text = (line.text && (line.text[LANG] || line.text.en)) || "";
    if (!text.trim()) return resolve(true);
    const words = (line.words && (line.words[LANG] || [])) || [];

    const el = document.createElement("div"); el.className = "line " + (line.type || "speech");
    if (line.type !== "narration" && line.speaker) {
      const who = document.createElement("div"); who.className = "who"; who.textContent = line.speaker; el.appendChild(who);
    }
    const box = document.createElement("div"); box.className = "box";
    const toks = text.split(/\s+/).filter(Boolean);
    const spans = toks.map(w => { const s = document.createElement("span"); s.className = "w"; s.textContent = w; return s; });
    spans.forEach((s, i) => { box.appendChild(s); if (i < spans.length - 1) box.appendChild(document.createTextNode(" ")); });
    el.appendChild(box); layer.appendChild(el);
    requestAnimationFrame(() => el.classList.add("in"));

    let done = false;
    const finish = ok => { if (done) return; done = true; el.classList.add("out"); setTimeout(() => resolve(ok), 240); };
    const times = dur => spans.map((_, k) => (words[k] != null ? words[k].t : (k / Math.max(1, spans.length)) * dur));

    const src = line.audio && line.audio[LANG];
    if (src) {
      audio.onended = null; audio.onerror = null;
      audio.src = BASE + src; audio.muted = muted;
      const p = audio.play(); if (p) p.catch(() => {});
      const tick = () => {
        if (done) return;
        if (my !== runId) { audio.pause(); return finish(false); }
        if (!paused) {
          const dur = (audio.duration || 3) * 1000, ms = audio.currentTime * 1000, T = times(dur);
          let cur = -1;
          spans.forEach((s, k) => { if (ms >= T[k] - 40) { s.classList.add("on"); cur = k; } });
          spans.forEach((s, k) => s.classList.toggle("active", k === cur));
        }
        requestAnimationFrame(tick);
      };
      audio.onended = () => { if (my === runId) { spans.forEach(s => { s.classList.add("on"); s.classList.remove("active"); }); setTimeout(() => finish(true), 320); } };
      audio.onerror = () => revealTimed();
      requestAnimationFrame(tick);
    } else { revealTimed(); }

    function revealTimed() {
      const total = Math.max(1600, text.length * 58);
      spans.forEach((s, k) => setTimeout(() => {
        if (my === runId && !paused) { s.classList.add("on"); spans.forEach((x, j) => x.classList.toggle("active", j === k)); }
      }, (k / Math.max(1, spans.length)) * total));
      setTimeout(() => { spans.forEach(s => s.classList.remove("active")); finish(true); }, total + 320);
    }
  });
}

boot();
