/* Procedural mood score for the motion-comic (Web Audio, zero files).
   Indian flavour: a tanpura-like drone + tabla/dhol-like percussion + a raga-ish (Bhairavi)
   melody. Moods crossfade: calm / suspense / battle / triumph. Kept low so narration leads. */
const Music = (() => {
  let ctx, master, droneGain, drone = [], mood = null, timer = null, step = 0, enabled = true;
  const A2 = 110; // tonic ~A2
  // Bhairavi-ish intervals (semitones): S r g m P d n
  const RAGA = [0, 1, 4, 5, 7, 8, 11];
  const f = s => A2 * Math.pow(2, s / 12);

  const MOODS = {
    calm:     { vol: 0.16, bpm: 62,  drums: 0,    melody: 0.35, droneMul: [1, 1.5], filt: 700 },
    suspense: { vol: 0.20, bpm: 76,  drums: 0.18, melody: 0.5,  droneMul: [1, 1.498], filt: 520, tense: true },
    battle:   { vol: 0.26, bpm: 132, drums: 0.9,  melody: 0.55, droneMul: [1, 1.5], filt: 900, tense: true },
    triumph:  { vol: 0.24, bpm: 92,  drums: 0.5,  melody: 0.7,  droneMul: [1, 1.5, 2], filt: 1100 },
    spirit:   { vol: 0.19, bpm: 50,  drums: 0,    melody: 0.5,  droneMul: [1, 1.5, 2, 3], filt: 1400 },
  };

  function init() {
    if (ctx) return;
    ctx = new (window.AudioContext || window.webkitAudioContext)();
    master = ctx.createGain(); master.gain.value = 0; master.connect(ctx.destination);
    droneGain = ctx.createGain(); droneGain.gain.value = 0; droneGain.connect(master);
  }
  function resume() { init(); if (ctx.state === "suspended") ctx.resume(); }

  function stopDrone() { drone.forEach(o => { try { o.stop(); } catch (e) {} }); drone = []; }
  function startDrone(muls, filt) {
    stopDrone();
    const lp = ctx.createBiquadFilter(); lp.type = "lowpass"; lp.frequency.value = filt;
    lp.connect(droneGain);
    muls.forEach(m => {
      const o = ctx.createOscillator(); o.type = "sawtooth"; o.frequency.value = A2 * m;
      const g = ctx.createGain(); g.gain.value = 0.10; o.connect(g).connect(lp); o.start(); drone.push(o);
    });
  }

  function pluck(freq, t, dur, g, type = "triangle", dest) {
    const o = ctx.createOscillator(), ga = ctx.createGain();
    o.type = type; o.frequency.value = freq;
    ga.gain.setValueAtTime(0, t); ga.gain.linearRampToValueAtTime(g, t + 0.015);
    ga.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    o.connect(ga).connect(dest || master); o.start(t); o.stop(t + dur + 0.05);
  }
  function tabla(t, g) { // membrane hit + click transient
    const o = ctx.createOscillator(), ga = ctx.createGain();
    o.type = "sine"; o.frequency.setValueAtTime(190, t); o.frequency.exponentialRampToValueAtTime(72, t + 0.12);
    ga.gain.setValueAtTime(g, t); ga.gain.exponentialRampToValueAtTime(0.001, t + 0.2);
    o.connect(ga).connect(master); o.start(t); o.stop(t + 0.22);
    const n = ctx.createBufferSource(), buf = ctx.createBuffer(1, 800, ctx.sampleRate);
    const d = buf.getChannelData(0); for (let i = 0; i < d.length; i++) d[i] = (Math.random() * 2 - 1) * (1 - i / d.length);
    n.buffer = buf; const ng = ctx.createGain(); ng.gain.value = g * 0.5; n.connect(ng).connect(master); n.start(t);
  }

  function tick() {
    if (!mood || !enabled) return;
    const M = MOODS[mood], t = ctx.currentTime + 0.05;
    const beat = step % 8;
    // percussion
    if (M.drums) {
      if (mood === "battle") { tabla(t, M.drums); if (beat % 2 === 1) tabla(t + 0.001, M.drums * 0.5); }
      else if (beat === 0 || beat === 4) tabla(t, M.drums);
    }
    // melody: pick raga notes; tense moods lean on the flat-2nd (r) for unease
    if (Math.random() < M.melody) {
      const deg = M.tense && Math.random() < 0.5 ? [1, 4, 5][Math.floor(Math.random() * 3)]
        : RAGA[Math.floor(Math.random() * RAGA.length)];
      const oct = 12 * (1 + (Math.random() < 0.4 ? 1 : 0));
      pluck(f(deg + oct), t, mood === "battle" ? 0.5 : 1.3, mood === "battle" ? 0.16 : 0.12,
            mood === "triumph" ? "sawtooth" : "triangle");
    }
    if (mood === "triumph" && beat === 0) [0, 4, 7].forEach(d => pluck(f(d + 12), t, 1.6, 0.10, "sawtooth"));
    step++;
  }

  function setMood(m) {
    resume();
    if (!MOODS[m]) m = "calm";
    if (m === mood) return;
    mood = m; step = 0;
    const M = MOODS[m];
    startDrone(M.droneMul, M.filt);
    master.gain.cancelScheduledValues(ctx.currentTime);
    master.gain.linearRampToValueAtTime(enabled ? M.vol : 0, ctx.currentTime + 1.2);
    droneGain.gain.linearRampToValueAtTime(1, ctx.currentTime + 1.2);
    if (timer) clearInterval(timer);
    timer = setInterval(tick, 60000 / M.bpm / 2); // eighth-note grid
  }
  function setEnabled(on) {
    enabled = on; if (!ctx) return;
    master.gain.linearRampToValueAtTime(on && mood ? MOODS[mood].vol : 0, ctx.currentTime + 0.4);
  }
  function stop() { if (timer) clearInterval(timer); timer = null; mood = null; stopDrone(); if (master) master.gain.value = 0; }

  return { resume, setMood, setEnabled, stop };
})();
