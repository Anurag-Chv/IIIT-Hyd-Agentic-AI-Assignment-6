import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DASHBOARD_JSON = ROOT / "dashboard.json"
DASHBOARD_HTML = ROOT / "dashboard.html"


def _find_conflicts(commitments):
    conflicts = []

    for i, first in enumerate(commitments):
        for second in commitments[i + 1:]:
            if (
                first.get("date") == second.get("date")
                and first.get("time") == second.get("time")
            ):
                conflicts.append({
                    "first": first.get("title", ""),
                    "second": second.get("title", ""),
                    "date": first.get("date", ""),
                    "time": first.get("time", ""),
                })

    return conflicts


def build_dashboard(pending_actions, flagged, commitments):
    dashboard = {
        "pending_actions": pending_actions,
        "flagged": flagged,
        "commitments": commitments,
        "conflicts": _find_conflicts(commitments),
    }

    with DASHBOARD_JSON.open("w", encoding="utf-8") as f:
        json.dump(dashboard, f, indent=2, default=str)

    _write_html(dashboard)
    return dashboard


def _cell(value):
    return html.escape(str(value))


def _write_html(data):
    pending = "".join(
        f"<tr><td>{_cell(x.get('message_id'))}</td>"
        f"<td>{_cell(x.get('action'))}</td>"
        f"<td>{_cell(x.get('reason'))}</td></tr>"
        for x in data["pending_actions"]
    )

    flagged = "".join(
        f"<tr><td>{_cell(x.get('message_id'))}</td>"
        f"<td>{_cell(x.get('attempted'))}</td>"
        f"<td>{_cell(x.get('action_taken'))}</td></tr>"
        for x in data["flagged"]
    )

    commitments = "".join(
        f"<tr><td>{_cell(x.get('date'))}</td>"
        f"<td>{_cell(x.get('time'))}</td>"
        f"<td>{_cell(x.get('title'))}</td>"
        f"<td>{_cell(', '.join(x.get('source_ids', [])))}</td></tr>"
        for x in data["commitments"]
    )

    conflicts = "".join(
        f"<p><strong>CONFLICT:</strong> "
        f"{_cell(x['first'])} and {_cell(x['second'])} "
        f"at {_cell(x['date'])} {_cell(x['time'])}</p>"
        for x in data["conflicts"]
    ) or "<p>No conflicts detected.</p>"

    html_text = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>InboxHero Dashboard</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 30px; }}
.panes {{ display: flex; gap: 20px; }}
.pane {{ flex: 1; border: 1px solid #ccc; padding: 15px; }}
table {{ width: 100%; border-collapse: collapse; }}
th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
th {{ background: #f2f2f2; }}
</style>
</head>
<body>
<h1>InboxHero Dashboard</h1>

<div class="panes">

<div class="pane">
<h2>Pending Actions</h2>
<table>
<tr><th>Message</th><th>Action</th><th>Why</th></tr>
{pending}
</table>
</div>

<div class="pane">
<h2>Flagged</h2>
<table>
<tr><th>Message</th><th>Attempted</th><th>What happened</th></tr>
{flagged}
</table>
</div>

<div class="pane">
<h2>Commitments</h2>
<table>
<tr><th>Date</th><th>Time</th><th>Commitment</th><th>Sources</th></tr>
{commitments}
</table>
<h3>Conflicts</h3>
{conflicts}
</div>

</div>
</body>
</html>
"""

    with DASHBOARD_HTML.open("w", encoding="utf-8") as f:
        f.write(html_text)


if __name__ == "__main__":
    dashboard = build_dashboard(
        pending_actions=[],
        flagged=[],
        commitments=[
            {
                "date": "2026-09-18",
                "time": "10:00",
                "title": "Quarterly board review",
                "source_ids": ["m038"],
            }
        ],
    )

    print(f"Dashboard written to: {DASHBOARD_HTML}")