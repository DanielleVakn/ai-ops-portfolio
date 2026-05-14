"""
Generates a clean, styled HTML report of matched job listings.
"""

import os
from datetime import datetime


def generate_html_report(jobs: list[dict], output_path: str):
    """Write results to a formatted HTML file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    total = len(jobs)

    rows = ""
    for i, job in enumerate(jobs, 1):
        score = job.get("relevance_score", 0)
        title = _esc(job.get("title", "N/A"))
        company = _esc(job.get("company", "N/A"))
        location = _esc(job.get("location", "")) or "—"
        department = _esc(job.get("department", "")) or "—"
        seniority = _esc(job.get("seniority_level", "Unspecified"))
        ats = _esc(job.get("ats", ""))
        url = job.get("url", "#")

        score_class = "score-high" if score >= 40 else ("score-mid" if score >= 20 else "score-low")
        score_bar_width = min(score, 100)

        rows += f"""
        <tr class="job-row">
            <td class="rank">#{i}</td>
            <td class="company">{company}</td>
            <td class="title">
                <a href="{url}" target="_blank" rel="noopener">{title}</a>
            </td>
            <td class="location">{location}</td>
            <td class="department">{department}</td>
            <td class="seniority">
                <span class="badge badge-seniority">{seniority}</span>
            </td>
            <td class="score-cell">
                <div class="score-bar-container">
                    <div class="score-bar {score_class}" style="width: {score_bar_width}%;"></div>
                </div>
                <span class="score-num">{score}</span>
            </td>
            <td class="ats">
                <span class="badge badge-ats">{ats}</span>
            </td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Job Search Results </title>
    <style>
        :root {{
            --bg: #0f1117;
            --surface: #1a1d27;
            --surface2: #22263a;
            --border: #2e3250;
            --accent: #6c63ff;
            --accent2: #00d4aa;
            --text: #e8eaf6;
            --text-muted: #8b8fa8;
            --high: #00d4aa;
            --mid: #ffa94d;
            --low: #6c63ff;
            --badge-bg: #2e3250;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            min-height: 100vh;
        }}
        .header {{
            background: linear-gradient(135deg, #1a1d27 0%, #0f1117 100%);
            border-bottom: 1px solid var(--border);
            padding: 2rem 2.5rem;
        }}
        .header-inner {{
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 1rem;
        }}
        .logo {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}
        .logo-icon {{
            width: 40px; height: 40px;
            background: linear-gradient(135deg, var(--accent), var(--accent2));
            border-radius: 10px;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.2rem;
        }}
        h1 {{
            font-size: 1.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #fff, var(--accent2));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .subtitle {{
            color: var(--text-muted);
            font-size: 0.85rem;
        }}
        .stats {{
            display: flex;
            gap: 1.5rem;
        }}
        .stat {{
            text-align: center;
        }}
        .stat-num {{
            font-size: 1.8rem;
            font-weight: 800;
            color: var(--accent2);
        }}
        .stat-label {{
            font-size: 0.75rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .main {{
            max-width: 1400px;
            margin: 2rem auto;
            padding: 0 2rem;
        }}
        .toolbar {{
            display: flex;
            gap: 0.75rem;
            margin-bottom: 1.5rem;
            align-items: center;
            flex-wrap: wrap;
        }}
        .search-box {{
            flex: 1;
            min-width: 200px;
            padding: 0.6rem 1rem;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text);
            font-size: 0.9rem;
            outline: none;
            transition: border-color 0.2s;
        }}
        .search-box:focus {{ border-color: var(--accent); }}
        .search-box::placeholder {{ color: var(--text-muted); }}
        select {{
            padding: 0.6rem 0.75rem;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text);
            font-size: 0.85rem;
            outline: none;
            cursor: pointer;
        }}
        .table-container {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 24px rgba(0,0,0,0.3);
            overflow-x: auto;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            min-width: 800px;
        }}
        thead {{
            background: var(--surface2);
        }}
        th {{
            padding: 0.9rem 1rem;
            text-align: left;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            color: var(--text-muted);
            border-bottom: 1px solid var(--border);
            cursor: pointer;
            user-select: none;
            white-space: nowrap;
        }}
        th:hover {{ color: var(--text); }}
        .job-row {{
            border-bottom: 1px solid var(--border);
            transition: background 0.15s;
        }}
        .job-row:last-child {{ border-bottom: none; }}
        .job-row:hover {{ background: var(--surface2); }}
        td {{
            padding: 0.85rem 1rem;
            font-size: 0.875rem;
            vertical-align: middle;
        }}
        .rank {{
            color: var(--text-muted);
            font-size: 0.75rem;
            width: 40px;
        }}
        .company {{
            font-weight: 600;
            color: var(--text);
            white-space: nowrap;
        }}
        .title a {{
            color: var(--accent2);
            text-decoration: none;
            font-weight: 500;
            transition: color 0.2s;
        }}
        .title a:hover {{
            color: #fff;
            text-decoration: underline;
        }}
        .location {{ color: var(--text-muted); white-space: nowrap; }}
        .department {{ color: var(--text-muted); }}
        .badge {{
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 20px;
            font-size: 0.7rem;
            font-weight: 600;
            background: var(--badge-bg);
            color: var(--text-muted);
            white-space: nowrap;
        }}
        .badge-seniority {{ background: rgba(108, 99, 255, 0.15); color: var(--accent); }}
        .badge-ats {{ background: rgba(0, 212, 170, 0.1); color: var(--accent2); }}
        .score-cell {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            min-width: 100px;
        }}
        .score-bar-container {{
            flex: 1;
            height: 6px;
            background: var(--border);
            border-radius: 3px;
            overflow: hidden;
        }}
        .score-bar {{ height: 100%; border-radius: 3px; transition: width 0.5s; }}
        .score-high {{ background: linear-gradient(90deg, var(--accent2), #00f5c4); }}
        .score-mid {{ background: linear-gradient(90deg, var(--mid), #ffcc70); }}
        .score-low {{ background: linear-gradient(90deg, var(--accent), #9c91ff); }}
        .score-num {{
            font-size: 0.75rem;
            color: var(--text-muted);
            min-width: 24px;
            text-align: right;
        }}
        .footer {{
            text-align: center;
            padding: 2rem;
            color: var(--text-muted);
            font-size: 0.8rem;
            border-top: 1px solid var(--border);
            margin-top: 3rem;
        }}
        .no-results {{
            text-align: center;
            padding: 4rem 2rem;
            color: var(--text-muted);
        }}
        .no-results .icon {{ font-size: 3rem; margin-bottom: 1rem; }}
        .hidden {{ display: none !important; }}
    </style>
</head>
<body>
    <header class="header">
        <div class="header-inner">
            <div class="logo">
                <div class="logo-icon">🔍</div>
                <div>
                    <h1>Job Match Results</h1>
                    <p class="subtitle"> · Generated {timestamp}</p>
                </div>
            </div>
            <div class="stats">
                <div class="stat">
                    <div class="stat-num" id="visible-count">{total}</div>
                    <div class="stat-label">Matches</div>
                </div>
            </div>
        </div>
    </header>
    <main class="main">
        <div class="toolbar">
            <input class="search-box" type="text" id="search" placeholder="Filter by company, title, or location..." oninput="filterTable()">
            <select id="locationFilter" onchange="filterTable()">
                <option value="">All Locations</option>
                <option value="new york">New York</option>
                <option value="remote">Remote</option>
                <option value="hybrid">Hybrid</option>
            </select>
            <select id="atsFilter" onchange="filterTable()">
                <option value="">All Sources</option>
                <option value="greenhouse">Greenhouse</option>
                <option value="lever">Lever</option>
                <option value="ashby">Ashby</option>
                <option value="generic">Generic</option>
            </select>
        </div>
        <div class="table-container">
            <table id="jobTable">
                <thead>
                    <tr>
                        <th>#</th>
                        <th onclick="sortTable(1)">Company ↕</th>
                        <th onclick="sortTable(2)">Job Title ↕</th>
                        <th onclick="sortTable(3)">Location ↕</th>
                        <th onclick="sortTable(4)">Department ↕</th>
                        <th>Seniority</th>
                        <th onclick="sortTable(6)">Relevance ↕</th>
                        <th>Source</th>
                    </tr>
                </thead>
                <tbody id="jobBody">
                    {rows if rows else '<tr><td colspan="8" class="no-results"><div class="icon">🤷</div><p>No matching jobs found. Try adjusting keywords in config.py.</p></td></tr>'}
                </tbody>
            </table>
        </div>
    </main>
    <footer class="footer">
        <p> NYC Job Matcher · Results are updated each time you run main.py</p>
        <p style="margin-top: 0.5rem">Click any job title to open the listing in a new tab</p>
    </footer>
    <script>
        function filterTable() {{
            const search = document.getElementById('search').value.toLowerCase();
            const locFilter = document.getElementById('locationFilter').value.toLowerCase();
            const atsFilter = document.getElementById('atsFilter').value.toLowerCase();
            const rows = document.querySelectorAll('#jobBody .job-row');
            let visible = 0;
            rows.forEach(row => {{
                const text = row.textContent.toLowerCase();
                const matchSearch = !search || text.includes(search);
                const matchLoc = !locFilter || text.includes(locFilter);
                const matchAts = !atsFilter || text.includes(atsFilter);
                if (matchSearch && matchLoc && matchAts) {{
                    row.classList.remove('hidden');
                    visible++;
                }} else {{
                    row.classList.add('hidden');
                }}
            }});
            document.getElementById('visible-count').textContent = visible;
        }}

        let sortDir = {{}};
        function sortTable(col) {{
            const tbody = document.getElementById('jobBody');
            const rows = Array.from(tbody.querySelectorAll('.job-row'));
            sortDir[col] = !sortDir[col];
            rows.sort((a, b) => {{
                const aText = a.cells[col]?.textContent.trim() || '';
                const bText = b.cells[col]?.textContent.trim() || '';
                const aNum = parseFloat(aText);
                const bNum = parseFloat(bText);
                if (!isNaN(aNum) && !isNaN(bNum)) {{
                    return sortDir[col] ? aNum - bNum : bNum - aNum;
                }}
                return sortDir[col]
                    ? aText.localeCompare(bText)
                    : bText.localeCompare(aText);
            }});
            rows.forEach(r => tbody.appendChild(r));
        }}
    </script>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n✅ Report saved to: {output_path}")
    print(f"   Open in browser: file://{os.path.abspath(output_path)}")


def _esc(text: str) -> str:
    """Escape HTML special characters."""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))
