from __future__ import annotations

import html
from pathlib import Path

import yaml


def dashboard_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Observability Dashboard</title>
  <style>
    :root { color-scheme: dark; font-family: Inter, system-ui, sans-serif; }
    body { margin: 0; background: #07111f; color: #e5eefb; }
    main { max-width: 1180px; margin: auto; padding: 28px; }
    header { display: flex; justify-content: space-between; align-items: end; }
    h1 { margin: 0; font-size: 28px; }
    .meta { color: #8ea5c4; font-size: 14px; }
    .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 24px; }
    .card { background: #101e32; border: 1px solid #243b58; border-radius: 14px; padding: 20px; min-height: 150px; }
    .card h2 { color: #9fb7d5; font-size: 14px; margin: 0 0 18px; text-transform: uppercase; letter-spacing: .08em; }
    .value { font-size: 35px; font-weight: 750; }
    .row { display: flex; justify-content: space-between; margin: 9px 0; }
    .ok { color: #48d597; } .warn { color: #ffba5c; } .bad { color: #ff6b77; }
    .threshold { margin-top: 16px; padding-top: 12px; border-top: 1px dashed #3d5575; color: #8ea5c4; font-size: 13px; }
    @media (max-width: 850px) { .grid { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
<main>
  <header>
    <div><h1>Day 13 Observability Dashboard</h1><div class="meta">Main layer: 6 panels</div></div>
    <div class="meta">Range: Last 1 hour | Auto refresh: 15 seconds<br><span id="updated">Loading...</span></div>
  </header>
  <section class="grid">
    <article class="card"><h2>1. Latency</h2><div class="row"><span>P50</span><b id="p50">0 ms</b></div><div class="row"><span>P95</span><b id="p95">0 ms</b></div><div class="row"><span>P99</span><b id="p99">0 ms</b></div><div class="threshold">SLO line: P95 &lt; 3000 ms</div></article>
    <article class="card"><h2>2. Traffic</h2><div class="value" id="traffic">0</div><div class="meta">successful requests / current run</div><div class="threshold">Total attempts: <span id="attempts">0</span></div></article>
    <article class="card"><h2>3. Errors</h2><div class="value" id="errors">0%</div><div class="meta" id="breakdown">No errors</div><div class="threshold">SLO line: error rate &lt; 2%</div></article>
    <article class="card"><h2>4. Cost</h2><div class="value" id="cost">$0.000000</div><div class="meta">total estimated cost (USD)</div><div class="threshold">Budget line: &lt; $2.50/day</div></article>
    <article class="card"><h2>5. Tokens</h2><div class="row"><span>Input</span><b id="tokens-in">0</b></div><div class="row"><span>Output</span><b id="tokens-out">0</b></div><div class="threshold">Unit: tokens</div></article>
    <article class="card"><h2>6. Quality</h2><div class="value" id="quality">0.00</div><div class="meta">average heuristic score</div><div class="threshold">Objective line: &gt;= 0.75</div></article>
  </section>
</main>
<script>
function statusClass(ok) { return ok ? "ok" : "bad"; }
async function refresh() {
  const m = await fetch("/metrics").then(r => r.json());
  p50.textContent = `${m.latency_p50_ms.toFixed(0)} ms`;
  p95.textContent = `${m.latency_p95_ms.toFixed(0)} ms`;
  p99.textContent = `${m.latency_p99_ms.toFixed(0)} ms`;
  p95.className = statusClass(m.latency_p95_ms < 3000);
  traffic.textContent = m.traffic;
  attempts.textContent = m.total_requests;
  errors.textContent = `${m.error_rate_pct.toFixed(2)}%`;
  errors.className = `value ${statusClass(m.error_rate_pct < 2)}`;
  breakdown.textContent = Object.keys(m.error_breakdown).length ? JSON.stringify(m.error_breakdown) : "No errors";
  cost.textContent = `$${m.total_cost_usd.toFixed(6)}`;
  tokensIn.textContent = m.tokens_in_total.toLocaleString();
  tokensOut.textContent = m.tokens_out_total.toLocaleString();
  quality.textContent = m.quality_avg.toFixed(2);
  quality.className = `value ${statusClass(m.quality_avg >= .75)}`;
  updated.textContent = `Updated ${new Date().toLocaleTimeString()}`;
}
const p50 = document.getElementById("p50"), p95 = document.getElementById("p95"), p99 = document.getElementById("p99");
const traffic = document.getElementById("traffic"), attempts = document.getElementById("attempts");
const errors = document.getElementById("errors"), breakdown = document.getElementById("breakdown");
const cost = document.getElementById("cost"), tokensIn = document.getElementById("tokens-in"), tokensOut = document.getElementById("tokens-out");
const quality = document.getElementById("quality"), updated = document.getElementById("updated");
refresh(); setInterval(refresh, 15000);
</script>
</body>
</html>"""


def alerts_html() -> str:
    config = yaml.safe_load(Path("config/alert_rules.yaml").read_text(encoding="utf-8"))
    cards = []
    for alert in config["alerts"]:
        cards.append(
            f"""
            <article>
              <div class="severity">{html.escape(alert['severity'])}</div>
              <h2>{html.escape(alert['name'])}</h2>
              <p><b>Condition:</b> {html.escape(alert['condition'])}</p>
              <p><b>Owner:</b> {html.escape(alert['owner'])}</p>
              <p><b>Type:</b> {html.escape(alert['type'])}</p>
              <p><b>Runbook:</b> <code>{html.escape(alert['runbook'])}</code></p>
            </article>
            """
        )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Alert Rules</title>
<style>
body {{ background:#07111f;color:#e5eefb;font-family:Inter,system-ui;margin:0;padding:32px }}
main {{ max-width:1100px;margin:auto }} section {{ display:grid;grid-template-columns:repeat(3,1fr);gap:18px }}
article {{ background:#101e32;border:1px solid #294563;border-radius:14px;padding:22px }}
h1 {{ font-size:30px }} h2 {{ color:#8fc7ff }} p {{ line-height:1.45 }} code {{ color:#48d597 }}
.severity {{ float:right;background:#d95363;padding:5px 10px;border-radius:20px;font-weight:bold }}
</style></head><body><main><h1>Validated Alert Rules and Runbooks</h1>
<p>Three symptom-based rules aligned with the lab SLOs.</p><section>{''.join(cards)}</section>
</main></body></html>"""
