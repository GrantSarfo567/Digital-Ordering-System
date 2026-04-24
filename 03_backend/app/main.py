from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.routers import auth, orders, menu, restaurants
from app.services.payments.payment_router import router as payment_router
from app.services.payments.webhooks.mtn_webhook import router as mtn_webhook_router
from app.services.payments.webhooks.webhook_router import router as webhooks_router

app = FastAPI(
    title="Digital Ordering System Backend",
    version="1.0.0"
)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])
app.include_router(menu.router, prefix="/menu", tags=["Menu"])
app.include_router(restaurants.router, prefix="/restaurants", tags=["Restaurants"])

# MTN webhook (prefixed here)
app.include_router(mtn_webhook_router, prefix="/webhooks", tags=["Webhooks"])

# Payments
app.include_router(payment_router, prefix="/payments", tags=["Payments"])

# 🔥 FIX: DO NOT add prefix here (it’s already inside webhook_router)
app.include_router(webhooks_router, tags=["Webhooks"])


@app.get("/", response_class=HTMLResponse)
def root():
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Darks Technologies — DigiServeGh API</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@1,300;1,400;1,600;1,700&family=JetBrains+Mono:ital,wght@1,300;1,400;1,500&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg:    #040710;
      --card:  rgba(7, 11, 19, 0.95);
      --blue:  #38bdf8;
      --gold:  #f59e0b;
      --green: #10b981;
      --text:  #c2d4e8;
      --dim:   #182636;
      --muted: #324d66;
    }

    html, body { height: 100%; overflow: hidden; }

    body {
      background: var(--bg);
      color: var(--text);
      font-family: 'Cormorant Garamond', serif;
      font-style: italic;
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
    }

    /* ── Particle canvas ── */
    #bg {
      position: fixed;
      inset: 0;
      z-index: 0;
      pointer-events: none;
    }

    /* ── CRT scanlines ── */
    .scanlines {
      position: fixed;
      inset: 0;
      z-index: 1;
      pointer-events: none;
      background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 3px,
        rgba(0,0,0,0.022) 3px,
        rgba(0,0,0,0.022) 4px
      );
    }

    /* ── Vignette ── */
    .vignette {
      position: fixed;
      inset: 0;
      z-index: 1;
      pointer-events: none;
      background: radial-gradient(ellipse at center, transparent 35%, rgba(0,0,0,0.62) 100%);
    }

    /* ── SVG noise grain ── */
    .grain {
      position: fixed;
      inset: 0;
      width: 100%;
      height: 100%;
      z-index: 2;
      pointer-events: none;
      opacity: 0.5;
    }

    /* ═══════════════════════════════════════════
       BORDER BEAM SHELL
    ═══════════════════════════════════════════ */
    .shell {
      position: relative;
      z-index: 10;
      border-radius: 5px;
      padding: 1px;
      overflow: hidden;
      background: rgba(56,189,248,0.055);
      width: min(540px, 94vw);
      animation: cardIn 1.15s cubic-bezier(0.22, 1, 0.36, 1) both;
    }

    /* Blue beam – fast */
    .shell::before {
      content: '';
      position: absolute;
      width: 200%; height: 200%;
      top: -50%; left: -50%;
      background: conic-gradient(
        from 0deg,
        transparent 0deg,
        transparent 325deg,
        rgba(56,189,248,0.0) 325deg,
        rgba(56,189,248,1.0) 348deg,
        rgba(56,189,248,0.0) 360deg
      );
      animation: beamSpin 4.2s linear infinite;
    }

    /* Gold beam – slow, reversed */
    .shell::after {
      content: '';
      position: absolute;
      width: 200%; height: 200%;
      top: -50%; left: -50%;
      background: conic-gradient(
        from 90deg,
        transparent 0deg,
        transparent 342deg,
        rgba(245,158,11,0.0) 342deg,
        rgba(245,158,11,0.55) 357deg,
        rgba(245,158,11,0.0) 360deg
      );
      animation: beamSpin 8.5s linear infinite reverse;
    }

    /* ═══════════════════════════════════════════
       INNER CARD
    ═══════════════════════════════════════════ */
    .card {
      position: relative;
      z-index: 1;
      background: var(--card);
      border-radius: 4px;
      padding: 48px 42px 36px;
      text-align: center;
      backdrop-filter: blur(32px);
      overflow: hidden;
    }

    /* Internal sweep */
    .sweep {
      position: absolute;
      left: 0; right: 0; top: -1px;
      height: 1px;
      background: linear-gradient(90deg,
        transparent 0%,
        rgba(56,189,248,0.15) 25%,
        rgba(56,189,248,0.55) 50%,
        rgba(56,189,248,0.15) 75%,
        transparent 100%);
      animation: sweepDown 8.5s linear infinite;
      pointer-events: none;
    }

    /* Corner brackets */
    .co {
      position: absolute;
      width: 14px; height: 14px;
      border-color: rgba(56,189,248,0.32);
      border-style: solid;
    }
    .tl { top: 10px; left: 10px;   border-width: 1px 0 0 1px; }
    .tr { top: 10px; right: 10px;  border-width: 1px 1px 0 0; }
    .bl { bottom: 10px; left: 10px;  border-width: 0 0 1px 1px; }
    .br { bottom: 10px; right: 10px; border-width: 0 1px 1px 0; }

    /* ═══════════════════════════════════════════
       LOGO
    ═══════════════════════════════════════════ */
    .logo-wrap {
      position: relative;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 16px;
      animation: fadeUp 1.3s cubic-bezier(0.22, 1, 0.36, 1) both;
    }

    /* Counter-rotating rings */
    .ring {
      position: absolute;
      border-radius: 50%;
      border-style: solid;
      pointer-events: none;
    }
    .r1 {
      inset: -18px;
      border-width: 1px;
      border-color: rgba(56,189,248,0.2) transparent rgba(56,189,248,0.07) transparent;
      animation: spin 11s linear infinite;
    }
    .r2 {
      inset: -34px;
      border-width: 1px;
      border-color: transparent rgba(245,158,11,0.16) transparent rgba(245,158,11,0.06);
      animation: spin 19s linear infinite reverse;
    }
    /* Tiny tick marks on outer ring */
    .r2::before {
      content: '';
      position: absolute;
      top: -3px; left: 50%;
      transform: translateX(-50%);
      width: 5px; height: 1px;
      background: rgba(245,158,11,0.5);
    }

    .logo-d {
      font-size: 144px;
      font-weight: 700;
      font-style: italic;
      line-height: 1;
      color: #d6e6f4;
      display: block;
      filter: drop-shadow(0 0 22px rgba(210,230,250,0.065));
    }

    .logo-t {
      position: absolute;
      font-size: 66px;
      font-weight: 700;
      font-style: italic;
      line-height: 1;
      color: var(--blue);
      top: 50%; left: 55%;
      transform: translate(-50%, -50%);
      text-shadow:
        0 0 16px rgba(56,189,248,0.75),
        0 0 45px rgba(56,189,248,0.28),
        0 0 90px rgba(56,189,248,0.1);
    }

    /* ═══════════════════════════════════════════
       BRAND + TAGLINE
    ═══════════════════════════════════════════ */
    .brand {
      font-size: 25px;
      font-weight: 600;
      font-style: italic;
      color: #dae8f6;
      letter-spacing: 0.2px;
      margin-bottom: 5px;
      animation: fadeUp 0.9s ease 0.1s both;
    }

    .tagline-row {
      font-family: 'JetBrains Mono', monospace;
      font-style: italic;
      font-size: 9.5px;
      letter-spacing: 2.4px;
      color: var(--muted);
      text-transform: uppercase;
      margin-bottom: 26px;
      min-height: 14px;
      animation: fadeUp 0.9s ease 0.18s both;
    }

    #cursor {
      display: inline-block;
      width: 1px; height: 10px;
      background: var(--blue);
      margin-left: 2px;
      vertical-align: middle;
      animation: blink 0.75s step-end infinite;
    }

    /* ═══════════════════════════════════════════
       DIVIDER
    ═══════════════════════════════════════════ */
    .divider {
      position: relative;
      height: 1px;
      background: linear-gradient(90deg,
        transparent,
        var(--dim) 18%,
        rgba(56,189,248,0.5) 50%,
        var(--dim) 82%,
        transparent);
      margin-bottom: 18px;
      animation: fadeUp 0.9s ease 0.24s both;
    }
    .divider-gem {
      position: absolute;
      top: 50%; left: 50%;
      transform: translate(-50%, -50%);
      width: 5px; height: 5px;
      border-radius: 50%;
      background: var(--blue);
      box-shadow: 0 0 10px rgba(56,189,248,0.9), 0 0 22px rgba(56,189,248,0.4);
    }

    /* ═══════════════════════════════════════════
       MASTER STATUS
    ═══════════════════════════════════════════ */
    .status-pill {
      display: inline-flex;
      align-items: center;
      gap: 7px;
      border: 1px solid rgba(16,185,129,0.22);
      border-radius: 2px;
      background: rgba(16,185,129,0.04);
      padding: 5px 13px;
      margin-bottom: 16px;
      font-family: 'JetBrains Mono', monospace;
      font-style: italic;
      font-size: 9px;
      letter-spacing: 2px;
      color: var(--green);
      text-transform: uppercase;
      animation: fadeUp 0.9s ease 0.3s both;
    }

    .pdot {
      width: 6px; height: 6px;
      border-radius: 50%;
      background: var(--green);
      flex-shrink: 0;
      position: relative;
    }
    .pdot::after {
      content: '';
      position: absolute;
      inset: -5px;
      border-radius: 50%;
      border: 1px solid var(--green);
      animation: ripple 2.1s ease-out infinite;
    }

    /* ═══════════════════════════════════════════
       SERVICE STATUS GRID
    ═══════════════════════════════════════════ */
    .services {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1px;
      background: rgba(56,189,248,0.06);
      border: 1px solid rgba(56,189,248,0.06);
      border-radius: 2px;
      overflow: hidden;
      margin-bottom: 12px;
      animation: fadeUp 0.9s ease 0.38s both;
    }

    .svc {
      background: rgba(6,10,17,0.98);
      padding: 10px 12px;
      display: flex;
      align-items: center;
      gap: 8px;
      text-align: left;
      cursor: default;
      transition: background 0.2s;
    }
    .svc:hover { background: rgba(56,189,248,0.03); }

    .sdot {
      width: 5px; height: 5px;
      border-radius: 50%;
      flex-shrink: 0;
    }
    .sdot.ok   { background: var(--green); box-shadow: 0 0 5px rgba(16,185,129,0.7); }
    .sdot.warn { background: var(--gold);  box-shadow: 0 0 5px rgba(245,158,11,0.7); }

    .svc-name {
      font-family: 'JetBrains Mono', monospace;
      font-style: italic;
      font-size: 9px;
      color: var(--text);
      font-weight: 500;
      display: block;
      letter-spacing: 0.2px;
    }
    .svc-st {
      font-family: 'JetBrains Mono', monospace;
      font-style: italic;
      font-size: 8px;
      letter-spacing: 0.3px;
    }
    .svc-st.ok   { color: var(--green); }
    .svc-st.warn { color: var(--gold); }

    /* ═══════════════════════════════════════════
       METRICS STRIP
    ═══════════════════════════════════════════ */
    .metrics {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 1px;
      background: rgba(56,189,248,0.06);
      border: 1px solid rgba(56,189,248,0.06);
      border-radius: 2px;
      overflow: hidden;
      margin-bottom: 18px;
      animation: fadeUp 0.9s ease 0.46s both;
    }

    .mc {
      background: rgba(6,10,17,0.98);
      padding: 11px 8px;
      text-align: center;
      cursor: default;
      transition: background 0.2s;
    }
    .mc:hover { background: rgba(56,189,248,0.03); }

    .ml {
      font-family: 'JetBrains Mono', monospace;
      font-style: italic;
      font-size: 7px;
      letter-spacing: 1.5px;
      color: var(--muted);
      text-transform: uppercase;
      display: block;
      margin-bottom: 5px;
    }

    .mv {
      font-family: 'JetBrains Mono', monospace;
      font-style: italic;
      font-size: 11px;
      font-weight: 500;
      display: block;
    }
    .mv.b { color: var(--blue); }
    .mv.g { color: var(--green); }
    .mv.o { color: var(--gold); }
    .mv.w { color: var(--text); }

    /* ═══════════════════════════════════════════
       ENDPOINT BADGES
    ═══════════════════════════════════════════ */
    .endpoints {
      display: flex;
      justify-content: center;
      gap: 6px;
      flex-wrap: wrap;
      margin-bottom: 22px;
      animation: fadeUp 0.9s ease 0.54s both;
    }

    .ep {
      font-family: 'JetBrains Mono', monospace;
      font-style: italic;
      font-size: 9.5px;
      padding: 4px 11px;
      border-radius: 2px;
      border: 1px solid;
      letter-spacing: 0.3px;
      cursor: default;
      transition: transform 0.14s, filter 0.14s;
      user-select: none;
    }
    .ep:hover { transform: translateY(-2px); filter: brightness(1.3); }

    .ep.docs   { border-color: rgba(56,189,248,0.28);  color: var(--blue);  background: rgba(56,189,248,0.05); }
    .ep.hlth   { border-color: rgba(16,185,129,0.28);  color: var(--green); background: rgba(16,185,129,0.05); }
    .ep.api    { border-color: rgba(245,158,11,0.28);  color: var(--gold);  background: rgba(245,158,11,0.05); }
    .ep.rdoc   { border-color: rgba(196,214,232,0.1);  color: var(--muted); background: transparent; }

    /* ═══════════════════════════════════════════
       FOOTER
    ═══════════════════════════════════════════ */
    .footer {
      display: flex;
      align-items: center;
      justify-content: space-between;
      animation: fadeUp 0.9s ease 0.62s both;
    }

    .f-l, .f-r {
      font-family: 'JetBrains Mono', monospace;
      font-style: italic;
      font-size: 8.5px;
      color: var(--muted);
      letter-spacing: 0.2px;
    }

    /* ═══════════════════════════════════════════
       KEYFRAMES
    ═══════════════════════════════════════════ */
    @keyframes cardIn  {
      from { opacity: 0; transform: translateY(24px) scale(0.97); }
      to   { opacity: 1; transform: translateY(0)    scale(1.0); }
    }
    @keyframes fadeUp  {
      from { opacity: 0; transform: translateY(10px); }
      to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes beamSpin { to { transform: rotate(360deg); } }
    @keyframes spin     { to { transform: rotate(360deg); } }
    @keyframes sweepDown {
      0%   { top: -1px; }
      100% { top: calc(100% + 1px); }
    }
    @keyframes ripple {
      0%   { transform: scale(1);   opacity: 0.85; }
      100% { transform: scale(3.2); opacity: 0; }
    }
    @keyframes blink {
      0%, 100% { opacity: 1; }
      50%      { opacity: 0; }
    }
  </style>
</head>
<body>

<canvas id="bg"></canvas>
<div class="scanlines"></div>
<div class="vignette"></div>

<!-- SVG noise grain overlay -->
<svg class="grain" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <filter id="nf">
    <feTurbulence type="fractalNoise" baseFrequency="0.68" numOctaves="4" stitchTiles="stitch"/>
    <feColorMatrix type="saturate" values="0"/>
  </filter>
  <rect width="100%" height="100%" filter="url(#nf)" opacity="0.055"/>
</svg>

<!-- Card -->
<div class="shell">
  <div class="card">
    <div class="sweep"></div>
    <div class="co tl"></div><div class="co tr"></div>
    <div class="co bl"></div><div class="co br"></div>

    <!-- Logo -->
    <div class="logo-wrap">
      <div class="ring r2"></div>
      <div class="ring r1"></div>
      <span class="logo-d">D</span>
      <span class="logo-t">T</span>
    </div>

    <!-- Brand -->
    <div class="brand">Darks Technologies</div>
    <div class="tagline-row">
      <span id="tg"></span><span id="cursor"></span>
    </div>

    <!-- Divider -->
    <div class="divider"><div class="divider-gem"></div></div>

    <!-- Master status -->
    <div class="status-pill">
      <div class="pdot"></div>
      <span>All Systems Operational</span>
    </div>

    <!-- Services -->
    <div class="services">
      <div class="svc">
        <div class="sdot ok"></div>
        <div>
          <span class="svc-name">Auth API</span>
          <span class="svc-st ok">Operational</span>
        </div>
      </div>
      <div class="svc">
        <div class="sdot ok"></div>
        <div>
          <span class="svc-name">Supabase DB</span>
          <span class="svc-st ok">Operational</span>
        </div>
      </div>
      <div class="svc">
        <div class="sdot ok"></div>
        <div>
          <span class="svc-name">Orders API</span>
          <span class="svc-st ok">Operational</span>
        </div>
      </div>
      <div class="svc">
        <div class="sdot warn"></div>
        <div>
          <span class="svc-name">Payment GW</span>
          <span class="svc-st warn">Configuring</span>
        </div>
      </div>
    </div>

    <!-- Metrics -->
    <div class="metrics">
      <div class="mc">
        <span class="ml">Uptime</span>
        <span class="mv b" id="m-up">00:00:00</span>
      </div>
      <div class="mc">
        <span class="ml">Requests</span>
        <span class="mv w" id="m-rq">—</span>
      </div>
      <div class="mc">
        <span class="ml">Latency</span>
        <span class="mv g" id="m-lt">—</span>
      </div>
      <div class="mc">
        <span class="ml">Version</span>
        <span class="mv o">v1.0.0</span>
      </div>
    </div>

    <!-- Endpoints -->
    <div class="endpoints">
      <span class="ep docs">/docs</span>
      <span class="ep hlth">/health</span>
      <span class="ep api">/api/v1</span>
      <span class="ep rdoc">/redoc</span>
    </div>

    <!-- Footer -->
    <div class="footer">
      <span class="f-l">&copy; 2026 Darks Technologies</span>
      <span class="f-r" id="f-clk">—</span>
    </div>
  </div>
</div>

<script>
/* ── Particle constellation ────────────────────────────────────── */
(function () {
  var cv = document.getElementById('bg');
  var cx = cv.getContext('2d');
  var W, H, pts = [];
  var N = 88, DIST = 135;

  function resize() { W = cv.width = innerWidth; H = cv.height = innerHeight; }

  function mkPt() {
    return { x: Math.random()*W, y: Math.random()*H,
             vx: (Math.random()-0.5)*0.3, vy: (Math.random()-0.5)*0.3,
             r: Math.random()*1.1+0.4, a: Math.random()*0.3+0.07 };
  }

  function frame() {
    cx.clearRect(0, 0, W, H);
    for (var i = 0; i < N; i++) {
      var p = pts[i];
      p.x += p.vx; p.y += p.vy;
      if (p.x < -8 || p.x > W+8 || p.y < -8 || p.y > H+8) {
        pts[i] = mkPt();
        pts[i].x = Math.random() < 0.5 ? 0 : W;
        continue;
      }
      cx.beginPath();
      cx.arc(p.x, p.y, p.r, 0, Math.PI*2);
      cx.fillStyle = 'rgba(56,189,248,'+p.a+')';
      cx.fill();
      for (var j = i+1; j < N; j++) {
        var q = pts[j];
        var dx = p.x-q.x, dy = p.y-q.y;
        var d = Math.sqrt(dx*dx+dy*dy);
        if (d < DIST) {
          cx.beginPath();
          cx.moveTo(p.x, p.y);
          cx.lineTo(q.x, q.y);
          cx.strokeStyle = 'rgba(56,189,248,'+(0.055*(1-d/DIST))+')';
          cx.lineWidth = 0.5;
          cx.stroke();
        }
      }
    }
    requestAnimationFrame(frame);
  }

  resize();
  pts = Array.from({length: N}, mkPt);
  window.addEventListener('resize', resize);
  frame();
})();

/* ── Typewriter ────────────────────────────────────────────────── */
(function () {
  var el = document.getElementById('tg');
  var cur = document.getElementById('cursor');
  var txt = 'DigiServeGh  \u00b7  Digital Ordering API';
  var i = 0;
  function type() {
    if (i < txt.length) {
      el.textContent += txt[i++];
      setTimeout(type, i < 13 ? 65 : 42);
    } else {
      setTimeout(function(){ cur.style.display = 'none'; }, 2200);
    }
  }
  setTimeout(type, 1000);
})();

/* ── Live metrics ──────────────────────────────────────────────── */
(function () {
  var t0 = Date.now();
  var rq = 5000 + Math.floor(Math.random()*600);
  function pad(n) { return String(Math.floor(n)).padStart(2,'0'); }
  function tick() {
    var ms = Date.now()-t0, s = Math.floor(ms/1000);
    document.getElementById('m-up').textContent =
      pad(s/3600)+':'+pad((s%3600)/60)+':'+pad(s%60);

    rq += Math.floor(Math.random()*3)+1;
    document.getElementById('m-rq').textContent = rq.toLocaleString();

    var lat = Math.round(15 + Math.sin(ms/2700)*11 + Math.random()*9);
    document.getElementById('m-lt').textContent = lat+' ms';

    var n = new Date();
    document.getElementById('f-clk').textContent =
      pad(n.getHours())+':'+pad(n.getMinutes())+':'+pad(n.getSeconds())+' UTC';
  }
  tick();
  setInterval(tick, 1000);
})();
</script>

</body>
</html>"""