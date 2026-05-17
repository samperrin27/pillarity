"""
Pillarity — app.py
==================
Flask web app serving the Pillarity medicine comparison tool.
Uses medicines.db (SQLite) which should be in the same directory.
 
To run locally:
    pip install flask
    python app.py
 
For Render deployment:
    Set start command to: gunicorn app:app
"""
 
import sqlite3
import os
from flask import Flask, request, jsonify, render_template_string
 
app = Flask(__name__)
 
# ── Database connection ────────────────────────────────────────────────────
 
def get_db():
    """Get a database connection."""
    db_path = os.path.join(os.path.dirname(__file__), 'medicines.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn
 
 
# ── HTML Template ──────────────────────────────────────────────────────────
 
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pillarity — Find identical medicines for less</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: Arial, sans-serif; color: #333; background: #f5f7fa; }
 
        .nav { background: #1a3a5c; padding: 16px 40px; display: flex; justify-content: space-between; align-items: center; }
        .nav .logo { color: white; font-size: 22px; font-weight: 700; }
        .nav .logo span { color: #5bc8f5; }
        .nav a { color: rgba(255,255,255,0.8); text-decoration: none; font-size: 14px; margin-left: 24px; }
 
        .hero { background: linear-gradient(135deg, #1a3a5c 0%, #2a6496 100%); color: white; padding: 60px 40px; text-align: center; }
        .hero h1 { font-size: 38px; font-weight: 700; margin-bottom: 12px; line-height: 1.2; }
        .hero h1 span { color: #5bc8f5; }
        .hero p { font-size: 17px; opacity: 0.9; max-width: 580px; margin: 0 auto; line-height: 1.6; }
 
        .search-bar { background: white; padding: 20px 40px; border-bottom: 1px solid #e0e0e0; display: flex; gap: 10px; max-width: 800px; margin: 0 auto; }
        .search-wrap { background: white; padding: 20px 0; border-bottom: 1px solid #e0e0e0; }
        .search-inner { display: flex; gap: 10px; max-width: 800px; margin: 0 auto; padding: 0 40px; }
        .search-inner input { flex: 1; padding: 12px 18px; border: 1px solid #ccc; border-radius: 6px; font-size: 15px; outline: none; }
        .search-inner input:focus { border-color: #1a3a5c; }
        .search-inner button { padding: 12px 28px; background: #1a3a5c; color: white; border: none; border-radius: 6px; font-size: 15px; cursor: pointer; }
        .search-inner button:hover { background: #2a5a8c; }
 
        .stats { background: white; padding: 24px 40px; display: flex; justify-content: center; gap: 60px; border-bottom: 1px solid #e0e0e0; }
        .stat { text-align: center; }
        .stat .number { font-size: 28px; font-weight: 700; color: #1a3a5c; }
        .stat .label { font-size: 12px; color: #888; margin-top: 4px; }
 
        .container { max-width: 900px; margin: 28px auto; padding: 0 24px; }
 
        .section-title { font-size: 16px; font-weight: 600; color: #1a3a5c; margin-bottom: 12px; }
 
        .match-card { background: white; border-radius: 8px; padding: 18px 22px; margin-bottom: 14px; border: 1px solid #e0e0e0; border-left: 4px solid #28a745; }
        .match-card.amber { border-left-color: #ffc107; }
        .badge { display: inline-block; font-size: 11px; font-weight: 600; padding: 3px 10px; border-radius: 12px; margin-bottom: 12px; background: #d4edda; color: #155724; }
        .badge.amber { background: #fff3cd; color: #856404; }
        .vs-row { display: grid; grid-template-columns: 1fr 44px 1fr; gap: 12px; align-items: center; margin-bottom: 10px; }
        .vs-product { background: #f8f9fa; border-radius: 6px; padding: 10px 14px; }
        .vs-product .pname { font-size: 14px; font-weight: 600; }
        .vs-product .pmfr { font-size: 12px; color: #666; margin-top: 2px; }
        .vs-product .ppl { font-size: 11px; color: #999; margin-top: 3px; }
        .vs-circle { width: 36px; height: 36px; background: #1a3a5c; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 600; margin: 0 auto; }
        .evidence { font-size: 12px; color: #666; background: #f8f9fa; padding: 6px 10px; border-radius: 4px; }
 
        .product-card { background: white; border: 1px solid #e0e0e0; border-radius: 8px; padding: 14px 18px; margin-bottom: 10px; }
        .product-card .pname { font-size: 15px; font-weight: 600; margin-bottom: 6px; }
        .product-card .detail { font-size: 12px; color: #666; line-height: 1.7; }
        .tag { display: inline-block; font-size: 11px; padding: 2px 8px; border-radius: 4px; margin-right: 6px; margin-bottom: 6px; background: #e8f4fd; color: #1a6aad; }
 
        .welcome { background: white; border: 1px solid #e0e0e0; border-radius: 8px; padding: 40px; text-align: center; color: #666; }
        .welcome h2 { color: #1a3a5c; margin-bottom: 12px; font-size: 20px; }
        .welcome p { line-height: 1.6; font-size: 14px; }
        .tip { background: #e8f4fd; border-radius: 6px; padding: 10px 16px; font-size: 13px; color: #1a3a5c; margin-top: 16px; display: inline-block; }
 
        .no-results { text-align: center; padding: 40px; color: #999; background: white; border-radius: 8px; border: 1px solid #e0e0e0; }
 
        .footer { background: #111; color: rgba(255,255,255,0.5); text-align: center; padding: 20px 40px; font-size: 12px; margin-top: 40px; }
        .footer a { color: rgba(255,255,255,0.5); text-decoration: underline; }
 
        @media (max-width: 650px) {
            .stats { gap: 20px; flex-wrap: wrap; }
            .hero h1 { font-size: 26px; }
            .vs-row { grid-template-columns: 1fr; }
            .vs-circle { display: none; }
            .nav a { display: none; }
        }
    </style>
</head>
<body>
 
<nav class="nav">
    <div class="logo">pill<span>arity</span></div>
    <div>
        <a href="https://samperrin27.github.io/pillarity#how">How it works</a>
        <a href="https://samperrin27.github.io/pillarity#findings">Findings</a>
        <a href="https://samperrin27.github.io/pillarity#about">About</a>
    </div>
</nav>
 
<div class="hero">
    <h1>Stop overpaying for<br><span>identical medicines</span></h1>
    <p>Search any medicine to see its formulation and find identical products that may cost less.</p>
</div>
 
<div class="search-wrap">
    <div class="search-inner">
        <input type="text" id="searchInput"
               placeholder="Search e.g. paracetamol, Nurofen, Zirtek, omeprazole..."
               onkeypress="if(event.key==='Enter') search()">
        <button onclick="search()">Search</button>
    </div>
</div>
 
<div class="stats">
    <div class="stat">
        <div class="number" id="statProducts">—</div>
        <div class="label">Products analysed</div>
    </div>
    <div class="stat">
        <div class="number" id="statMatches">—</div>
        <div class="label">Identical pairs found</div>
    </div>
    <div class="stat">
        <div class="number">5</div>
        <div class="label">Medicines covered</div>
    </div>
    <div class="stat">
        <div class="number">EMC</div>
        <div class="label">Official data source</div>
    </div>
</div>
 
<div class="container">
    <div id="results">
        <div class="welcome">
            <h2>Search for any medicine</h2>
            <p>Find out if a branded product is identical to a cheaper alternative using official UK regulatory data.</p>
            <p style="margin-top:8px">Try: <strong>paracetamol</strong> &nbsp;·&nbsp; <strong>Nurofen</strong> &nbsp;·&nbsp; <strong>Zirtek</strong> &nbsp;·&nbsp; <strong>omeprazole</strong> &nbsp;·&nbsp; <strong>Benylin</strong></p>
            <div class="tip">💡 Two products with the same PL code are 100% identical — same factory, same formula.</div>
        </div>
    </div>
</div>
 
<div class="footer">
    <p>© 2026 Pillarity. Data sourced from the <a href="https://www.medicines.org.uk" target="_blank">Electronic Medicines Compendium (EMC)</a>. For informational purposes only — not medical advice.</p>
</div>
 
<script>
async function loadStats() {
    const r = await fetch('/api/stats');
    const d = await r.json();
    document.getElementById('statProducts').textContent = d.products;
    document.getElementById('statMatches').textContent = d.matches;
}
 
async function search() {
    const q = document.getElementById('searchInput').value.trim();
    if (!q) return;
    document.getElementById('results').innerHTML = '<p style="text-align:center;padding:40px;color:#888">Searching...</p>';
    const r = await fetch('/api/search?q=' + encodeURIComponent(q));
    const d = await r.json();
    renderResults(d, q);
}
 
function renderResults(data, q) {
    let html = '';
 
    if (data.products.length === 0) {
        html = '<div class="no-results">No products found for "' + q + '"<br><small style="margin-top:8px;display:block">Try a different search term</small></div>';
        document.getElementById('results').innerHTML = html;
        return;
    }
 
    if (data.matches.length > 0) {
        html += '<div class="section-title" style="margin-bottom:14px">⚠️ Identical or near-identical products (' + data.matches.length + ')</div>';
        data.matches.forEach(m => {
            const identical = m.tier === 1;
            html += '<div class="match-card' + (identical ? '' : ' amber') + '">';
            html += '<span class="badge' + (identical ? '' : ' amber') + '">' + (identical ? '✅ 100% Identical — same PL code' : '⚠️ Very likely identical — ' + m.confidence + '% confidence') + '</span>';
            html += '<div class="vs-row">';
            html += '<div class="vs-product"><div class="pname">' + m.product_a + '</div><div class="pmfr">' + (m.holder_a || '') + '</div>' + (m.pl_a ? '<div class="ppl">' + m.pl_a + '</div>' : '') + '</div>';
            html += '<div><div class="vs-circle">VS</div></div>';
            html += '<div class="vs-product"><div class="pname">' + m.product_b + '</div><div class="pmfr">' + (m.holder_b || '') + '</div>' + (m.pl_b ? '<div class="ppl">' + m.pl_b + '</div>' : '') + '</div>';
            html += '</div>';
            html += '<div class="evidence">' + m.evidence + '</div>';
            html += '</div>';
        });
        html += '<br>';
    }
 
    html += '<div class="section-title">Products (' + data.products.length + ' found)</div>';
    data.products.forEach(p => {
        html += '<div class="product-card">';
        html += '<div class="pname">' + p.name + '</div>';
        html += '<div>';
        if (p.form) html += '<span class="tag">' + p.form + '</span>';
        if (p.pl_code && p.pl_code !== 'None') html += '<span class="tag">' + p.pl_code + '</span>';
        html += '</div>';
        html += '<div class="detail">';
        if (p.licence_holder && p.licence_holder !== 'None') html += '<strong>Licence holder:</strong> ' + p.licence_holder + '<br>';
        if (p.excipients && p.excipients !== 'None' && p.excipients.length > 5) {
            const exc = p.excipients.length > 200 ? p.excipients.substring(0, 200) + '...' : p.excipients;
            html += '<strong>Excipients:</strong> ' + exc;
        }
        html += '</div></div>';
    });
 
    document.getElementById('results').innerHTML = html;
}
 
loadStats();
</script>
</body>
</html>
"""
 
 
# ── Routes ─────────────────────────────────────────────────────────────────
 
@app.route('/')
def index():
    return HTML
 
 
@app.route('/api/stats')
def stats():
    conn = get_db()
    products = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    matches  = conn.execute("SELECT COUNT(*) FROM matches WHERE [Match Tier] = 1").fetchone()[0]
    conn.close()
    return jsonify({"products": products, "matches": matches})
 
 
@app.route('/api/search')
def search():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify({"products": [], "matches": []})
 
    conn = get_db()
 
    rows = conn.execute("""
        SELECT [Product Name], [Licence Holder], [PL Code],
               [Pharmaceutical Form], [Excipients Display]
        FROM products
        WHERE [Product Name] LIKE ?
           OR [Excipients Display] LIKE ?
           OR [Licence Holder] LIKE ?
        GROUP BY [Product Name]
        ORDER BY [Product Name]
        LIMIT 40
    """, (f'%{q}%', f'%{q}%', f'%{q}%')).fetchall()
 
    products = [{
        "name":           r["Product Name"] or '',
        "licence_holder": r["Licence Holder"] or '',
        "pl_code":        r["PL Code"] or '',
        "form":           r["Pharmaceutical Form"] or '',
        "excipients":     r["Excipients Display"] or '',
    } for r in rows]
 
    product_names = [p["name"] for p in products]
    matches = []
    if product_names:
        placeholders = ','.join(['?' for _ in product_names])
        match_rows = conn.execute(f"""
            SELECT DISTINCT [Product A], [Licence Holder A], [PL Code A],
                   [Product B], [Licence Holder B], [PL Code B],
                   [Match Tier], [Confidence %], [Evidence]
            FROM matches
            WHERE ([Product A] IN ({placeholders}) OR [Product B] IN ({placeholders}))
              AND [Match Tier] <= 3
            ORDER BY [Match Tier], [Confidence %] DESC
            LIMIT 15
        """, product_names + product_names).fetchall()
 
        matches = [{
            "product_a":  r["Product A"] or '',
            "holder_a":   r["Licence Holder A"] or '',
            "pl_a":       r["PL Code A"] or '',
            "product_b":  r["Product B"] or '',
            "holder_b":   r["Licence Holder B"] or '',
            "pl_b":       r["PL Code B"] or '',
            "tier":       r["Match Tier"] or 0,
            "confidence": r["Confidence %"] or 0,
            "evidence":   r["Evidence"] or '',
        } for r in match_rows]
 
    conn.close()
    return jsonify({"products": products, "matches": matches})
 
 
# ── Run ────────────────────────────────────────────────────────────────────
 
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
