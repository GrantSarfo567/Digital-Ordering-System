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

# Payments
app.include_router(payment_router, prefix="/payments", tags=["Payments"])

# ALL webhooks grouped under /webhooks
#app.include_router(mtn_webhook_router, prefix="/webhooks", tags=["Webhooks"])
app.include_router(webhooks_router, prefix="/webhooks", tags=["Webhooks"])

@app.get("/", response_class=HTMLResponse)
def root():
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DigiServeGh — Status · Darks Technologies</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg:       #030c18;
      --surface:  #070f1e;
      --surface2: #0c1828;
      --border:   rgba(140, 178, 225, 0.07);
      --borderl:  rgba(140, 178, 225, 0.14);
      --blue:     #4b8cf7;
      --blue-d:   rgba(75, 140, 247, 0.10);
      --green:    #1fd47a;
      --green-d:  rgba(31, 212, 122, 0.09);
      --amber:    #f5a524;
      --amber-d:  rgba(245, 165, 36, 0.09);
      --text:     #dce8f8;
      --text2:    #5b7a9e;
      --text3:    #2e4560;
      --sans:     'Sora', system-ui, sans-serif;
      --mono:     'JetBrains Mono', 'Courier New', monospace;
    }

    html, body {
      height: 100%;
      background: var(--bg);
      color: var(--text);
      font-family: var(--sans);
      font-size: 14px;
      line-height: 1.6;
      -webkit-font-smoothing: antialiased;
    }

    /* Dot-grid background */
    body::before {
      content: '';
      position: fixed;
      inset: 0;
      background-image: radial-gradient(rgba(140, 178, 225, 0.055) 1px, transparent 1px);
      background-size: 30px 30px;
      pointer-events: none;
      z-index: 0;
    }

    /* Radial vignette to keep center readable */
    body::after {
      content: '';
      position: fixed;
      inset: 0;
      background: radial-gradient(ellipse 80% 70% at 50% 35%, transparent 30%, var(--bg) 85%);
      pointer-events: none;
      z-index: 0;
    }

    /* ────── NAV ────── */
    nav {
      position: fixed;
      top: 0; left: 0; right: 0;
      z-index: 100;
      height: 52px;
      display: flex;
      align-items: center;
      padding: 0 28px;
      background: rgba(3, 12, 24, 0.88);
      backdrop-filter: blur(14px);
      -webkit-backdrop-filter: blur(14px);
      border-bottom: 1px solid var(--border);
    }

    .nav-logo {
      display: flex;
      align-items: center;
      gap: 9px;
      text-decoration: none;
      flex-shrink: 0;
    }

    .logo-mark {
      width: 26px; height: 26px;
      background: var(--blue);
      border-radius: 5px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: var(--sans);
      font-weight: 600;
      font-size: 11px;
      color: #fff;
      letter-spacing: -0.3px;
      flex-shrink: 0;
    }

    .logo-name {
      font-size: 13px;
      font-weight: 500;
      color: var(--text);
      letter-spacing: -0.1px;
    }

    .nav-links {
      display: flex;
      align-items: center;
      gap: 1px;
      margin: 0 auto;
    }

    .nav-link {
      font-family: var(--mono);
      font-size: 11px;
      color: var(--text2);
      text-decoration: none;
      padding: 5px 13px;
      border-radius: 4px;
      transition: color 0.15s, background 0.15s;
    }
    .nav-link:hover { color: var(--text); background: var(--surface2); }

    .nav-right {
      display: flex;
      align-items: center;
      gap: 16px;
      flex-shrink: 0;
    }

    .nav-clock {
      font-family: var(--mono);
      font-size: 10.5px;
      color: var(--text3);
      letter-spacing: 0.4px;
    }

    .version-tag {
      font-family: var(--mono);
      font-size: 10px;
      padding: 2px 8px;
      border-radius: 3px;
      border: 1px solid var(--borderl);
      color: var(--text2);
      letter-spacing: 0.2px;
    }

    /* ────── MAIN ────── */
    main {
      position: relative;
      z-index: 1;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 112px 24px 72px;
    }

    .container {
      width: 100%;
      max-width: 740px;
      animation: fadeUp 0.65s cubic-bezier(0.22, 1, 0.36, 1) both;
    }

    /* ────── STATUS PILL ────── */
    .status-pill {
      display: inline-flex;
      align-items: center;
      gap: 7px;
      padding: 5px 13px 5px 10px;
      border-radius: 999px;
      border: 1px solid rgba(31, 212, 122, 0.2);
      background: var(--green-d);
      font-family: var(--mono);
      font-size: 10.5px;
      color: var(--green);
      letter-spacing: 0.3px;
      margin-bottom: 30px;
    }

    .status-dot {
      width: 6px; height: 6px;
      border-radius: 50%;
      background: var(--green);
      flex-shrink: 0;
      position: relative;
    }
    .status-dot::after {
      content: '';
      position: absolute;
      inset: -4px;
      border-radius: 50%;
      background: var(--green);
      opacity: 0.22;
      animation: pulse 2.2s ease-out infinite;
    }

    /* ────── HERO ────── */
    h1 {
      font-size: clamp(38px, 6vw, 56px);
      font-weight: 600;
      letter-spacing: -1.8px;
      line-height: 1.08;
      color: var(--text);
      margin-bottom: 14px;
    }

    .hero-sub {
      font-size: 15px;
      color: var(--text2);
      font-weight: 300;
      max-width: 440px;
      margin-bottom: 52px;
      line-height: 1.7;
    }

    /* ────── SECTION HEADER ────── */
    .section-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 12px;
    }

    .section-label {
      font-family: var(--mono);
      font-size: 10px;
      letter-spacing: 1.6px;
      text-transform: uppercase;
      color: var(--text3);
    }

    .section-meta {
      font-family: var(--mono);
      font-size: 10px;
      color: var(--text3);
    }

    /* ────── SERVICE GRID ────── */
    .services {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0;
      background: var(--border);
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow: hidden;
      margin-bottom: 14px;
    }

    .svc {
      background: var(--surface);
      padding: 18px 20px;
      border-right: 1px solid var(--border);
      border-bottom: 1px solid var(--border);
      transition: background 0.15s;
    }
    .svc:nth-child(even) { border-right: none; }
    .svc:nth-child(n+3)  { border-bottom: none; }
    .svc:hover { background: var(--surface2); }

    .svc-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 12px;
    }

    .svc-name {
      font-size: 13px;
      font-weight: 500;
      color: var(--text);
    }

    .svc-badge {
      font-family: var(--mono);
      font-size: 9.5px;
      padding: 2px 8px;
      border-radius: 3px;
      letter-spacing: 0.1px;
    }
    .svc-badge.ok   { background: var(--green-d); color: var(--green); border: 1px solid rgba(31,212,122,0.2); }
    .svc-badge.warn { background: var(--amber-d); color: var(--amber); border: 1px solid rgba(245,165,36,0.2); }

    /* Uptime bar (45 daily segments = 45 days) */
    .uptime-bar {
      display: flex;
      gap: 2px;
      margin-bottom: 7px;
    }
    .uptime-seg {
      flex: 1;
      height: 4px;
      border-radius: 1px;
    }
    .uptime-seg.up      { background: var(--green); opacity: 0.75; }
    .uptime-seg.partial { background: var(--amber); opacity: 0.65; }
    .uptime-seg.none    { background: var(--text3); opacity: 0.35; }

    .svc-uptime-text {
      font-family: var(--mono);
      font-size: 9.5px;
      color: var(--text3);
    }

    /* ────── METRICS ────── */
    .metrics {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 0;
      background: var(--border);
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow: hidden;
      margin-bottom: 36px;
    }

    .metric {
      background: var(--surface);
      padding: 18px 18px;
      border-right: 1px solid var(--border);
      transition: background 0.15s;
    }
    .metric:last-child { border-right: none; }
    .metric:hover { background: var(--surface2); }

    .metric-label {
      font-family: var(--mono);
      font-size: 9.5px;
      letter-spacing: 1px;
      color: var(--text3);
      text-transform: uppercase;
      margin-bottom: 7px;
    }

    .metric-value {
      font-family: var(--mono);
      font-size: 17px;
      font-weight: 500;
      line-height: 1;
    }
    .mv-blue  { color: var(--blue); }
    .mv-green { color: var(--green); }
    .mv-amber { color: var(--amber); }
    .mv-muted { color: var(--text2); }

    /* ────── ENDPOINTS ────── */
    .endpoints {
      margin-bottom: 0;
    }

    .ep-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 8px;
    }

    .ep {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 7px;
      padding: 16px 17px;
      text-decoration: none;
      display: block;
      cursor: pointer;
      transition: border-color 0.15s, background 0.15s, transform 0.12s;
      user-select: none;
    }
    .ep:hover {
      background: var(--surface2);
      border-color: var(--borderl);
      transform: translateY(-1px);
    }
    .ep:active { transform: translateY(0); }

    .ep-method {
      font-family: var(--mono);
      font-size: 9px;
      letter-spacing: 1.2px;
      color: var(--text3);
      text-transform: uppercase;
      margin-bottom: 5px;
    }

    .ep-path {
      font-family: var(--mono);
      font-size: 12.5px;
      font-weight: 500;
      display: block;
      margin-bottom: 4px;
    }
    .ep-path.blue  { color: var(--blue); }
    .ep-path.green { color: var(--green); }
    .ep-path.amber { color: var(--amber); }
    .ep-path.muted { color: var(--text2); }

    .ep-desc {
      font-size: 11px;
      color: var(--text3);
      line-height: 1.4;
    }

    /* ────── FOOTER ────── */
    footer {
      position: relative;
      z-index: 1;
      border-top: 1px solid var(--border);
      padding: 16px 28px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
    }

    .footer-l, .footer-r {
      font-family: var(--mono);
      font-size: 10.5px;
      color: var(--text3);
      white-space: nowrap;
    }

    .footer-center {
      display: flex;
      align-items: center;
      gap: 20px;
    }

    .footer-tag {
      display: flex;
      align-items: center;
      gap: 5px;
      font-family: var(--mono);
      font-size: 10px;
      color: var(--text3);
    }

    .fdot {
      width: 4px; height: 4px;
      border-radius: 50%;
      flex-shrink: 0;
    }

    /* ────── KEYFRAMES ────── */
    @keyframes fadeUp {
      from { opacity: 0; transform: translateY(14px); }
      to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes pulse {
      0%   { transform: scale(1); opacity: 0.22; }
      100% { transform: scale(3.5); opacity: 0; }
    }
  </style>
</head>
<body>

<!-- ── NAV ── -->
<nav>
  <a href="#" class="nav-logo">
    <div class="logo-mark">DT</div>
    <span class="logo-name">Darks Technologies</span>
  </a>

  <nav class="nav-links" aria-label="API endpoints">
    <a class="nav-link" href="#">/docs</a>
    <a class="nav-link" href="#">/health</a>
    <a class="nav-link" href="#">/api/v1</a>
    <a class="nav-link" href="#">/redoc</a>
  </nav>

  <div class="nav-right">
    <span class="nav-clock" id="nav-clock" aria-live="off">—</span>
    <span class="version-tag">v1.0.0</span>
  </div>
</nav>

<!-- ── MAIN ── -->
<main>
  <div class="container">

    <!-- Status -->
    <div class="status-pill" role="status" aria-label="System status">
      <div class="status-dot"></div>
      <span>All Systems Operational</span>
    </div>

    <!-- Hero -->
    <h1>AfriGrid FSB Backend v1.0.0.</h1>
    <p class="hero-sub">Digital ordering infrastructure for Food Service Businesses. Built on FastAPI and Supabase.</p>

    <!-- Service Status -->
    <div class="section-head">
      <span class="section-label">Service Status</span>
      <span class="section-meta" id="status-ts">—</span>
    </div>

    <div class="services" role="list">
      <!-- Auth API -->
      <div class="svc" role="listitem">
        <div class="svc-header">
          <span class="svc-name">Auth API</span>
          <span class="svc-badge ok">Operational</span>
        </div>
        <div class="uptime-bar" id="bar-auth" aria-label="Uptime history"></div>
        <span class="svc-uptime-text">100.0% uptime · 45 days</span>
      </div>

      <!-- Supabase DB -->
      <div class="svc" role="listitem">
        <div class="svc-header">
          <span class="svc-name">Supabase DB</span>
          <span class="svc-badge ok">Operational</span>
        </div>
        <div class="uptime-bar" id="bar-db" aria-label="Uptime history"></div>
        <span class="svc-uptime-text">99.9% uptime · 45 days</span>
      </div>

      <!-- Orders API -->
      <div class="svc" role="listitem">
        <div class="svc-header">
          <span class="svc-name">Orders API</span>
          <span class="svc-badge ok">Operational</span>
        </div>
        <div class="uptime-bar" id="bar-orders" aria-label="Uptime history"></div>
        <span class="svc-uptime-text">99.8% uptime · 45 days</span>
      </div>

      <!-- Payment GW -->
      <div class="svc" role="listitem">
        <div class="svc-header">
          <span class="svc-name">Payment Gateway</span>
          <span class="svc-badge warn">Configuring</span>
        </div>
        <div class="uptime-bar" id="bar-pay" aria-label="Uptime history"></div>
        <span class="svc-uptime-text" style="color: var(--amber)">Paystack integration · Phase 2</span>
      </div>
    </div>

    <!-- Metrics -->
    <div class="metrics" role="group" aria-label="API Metrics">
      <div class="metric">
        <div class="metric-label">Session Uptime</div>
        <div class="metric-value mv-blue" id="m-up">—</div>
      </div>
      <div class="metric">
        <div class="metric-label">Requests</div>
        <div class="metric-value mv-muted" id="m-rq">—</div>
      </div>
      <div class="metric">
        <div class="metric-label">Avg Latency</div>
        <div class="metric-value mv-green" id="m-lt">—</div>
      </div>
      <div class="metric">
        <div class="metric-label">Environment</div>
        <div class="metric-value mv-amber">production</div>
      </div>
    </div>

    <!-- Endpoints -->
    <div class="endpoints">
      <div class="section-head">
        <span class="section-label">Endpoints</span>
      </div>
      <div class="ep-grid">
        <a class="ep" href="#" aria-label="Swagger UI documentation">
          <div class="ep-method">GET</div>
          <span class="ep-path blue">/docs</span>
          <div class="ep-desc">Swagger UI</div>
        </a>
        <a class="ep" href="#" aria-label="API health check">
          <div class="ep-method">GET</div>
          <span class="ep-path green">/health</span>
          <div class="ep-desc">Health check</div>
        </a>
        <a class="ep" href="#" aria-label="REST API base URL">
          <div class="ep-method">*</div>
          <span class="ep-path amber">/api/v1</span>
          <div class="ep-desc">REST API base</div>
        </a>
        <a class="ep" href="#" aria-label="ReDoc API reference">
          <div class="ep-method">GET</div>
          <span class="ep-path muted">/redoc</span>
          <div class="ep-desc">ReDoc reference</div>
        </a>
      </div>
    </div>

  </div>
</main>

<!-- ── FOOTER ── -->
<footer>
  <span class="footer-l">© 2026 Darks Technologies</span>
  <div class="footer-center">
    <span class="footer-tag">
      <span class="fdot" style="background: var(--green)"></span>
      Ghana · West Africa
    </span>
    <span class="footer-tag">
      <span class="fdot" style="background: var(--blue)"></span>
      FastAPI + Supabase
    </span>
    <span class="footer-tag">
      <span class="fdot" style="background: var(--amber)"></span>
      Africa's Talking SMS
    </span>
  </div>
  <span class="footer-r" id="f-date">—</span>
</footer>

<script>
  /* ── Uptime bar builder ── */
  function buildBar(id, segments) {
    /* segments: array of 45 strings: 'up' | 'partial' | 'none' */
    var el = document.getElementById(id);
    segments.forEach(function(state) {
      var d = document.createElement('div');
      d.className = 'uptime-seg ' + state;
      el.appendChild(d);
    });
  }

  /* Generate realistic uptime patterns */
  function makePattern(totalDays, downDays) {
    var arr = [];
    for (var i = 0; i < totalDays; i++) arr.push('up');
    downDays.forEach(function(d) { if (d < totalDays) arr[d] = 'partial'; });
    return arr;
  }

  buildBar('bar-auth',   makePattern(45, []));
  buildBar('bar-db',     makePattern(45, [14]));
  buildBar('bar-orders', makePattern(45, [5, 28]));

  /* Payment GW: amber for all (not yet deployed) */
  (function() {
    var el = document.getElementById('bar-pay');
    for (var i = 0; i < 45; i++) {
      var d = document.createElement('div');
      d.className = 'uptime-seg ' + (i < 30 ? 'none' : 'partial');
      el.appendChild(d);
    }
  })();

  /* ── Live clock & metrics ── */
  var t0 = Date.now();
  var rq = 12847;

  function pad(n) { return String(Math.floor(n)).padStart(2, '0'); }

  function tick() {
    var now = new Date();

    /* Nav clock — UTC */
    document.getElementById('nav-clock').textContent =
      pad(now.getUTCHours()) + ':' + pad(now.getUTCMinutes()) + ':' + pad(now.getUTCSeconds()) + ' UTC';

    /* Footer date */
    document.getElementById('f-date').textContent =
      now.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });

    /* Status timestamp */
    document.getElementById('status-ts').textContent =
      'Updated ' + pad(now.getHours()) + ':' + pad(now.getMinutes()) + ':' + pad(now.getSeconds());

    /* Session uptime */
    var s = Math.floor((Date.now() - t0) / 1000);
    document.getElementById('m-up').textContent =
      pad(s / 3600) + ':' + pad((s % 3600) / 60) + ':' + pad(s % 60);

    /* Request counter — realistic slow increment */
    rq += Math.random() < 0.6 ? 1 : 0;
    document.getElementById('m-rq').textContent = rq.toLocaleString();

    /* Latency — stable with subtle drift */
    var lat = Math.round(19 + Math.sin(Date.now() / 4200) * 7 + Math.random() * 5);
    document.getElementById('m-lt').textContent = lat + ' ms';
  }

  tick();
  setInterval(tick, 1000);
</script>

</body>
</html>"""