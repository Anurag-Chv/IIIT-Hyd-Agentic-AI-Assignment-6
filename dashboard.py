"""
Create the InboxHero dashboard from a completed run.
"""

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent

DASHBOARD_JSON = PROJECT_ROOT / "dashboard.json"
DASHBOARD_HTML = PROJECT_ROOT / "dashboard.html"


def _find_conflicts(commitments):
    """Find commitments that have the same date and time."""
    conflicts = []

    for i in range(len(commitments)):
        for j in range(i + 1, len(commitments)):
            first = commitments[i]
            second = commitments[j]

            if (
                first.get("date") == second.get("date")
                and first.get("time") == second.get("time")
            ):
                conflicts.append(
                    {
                        "first": first.get("title", ""),
                        "second": second.get("title", ""),
                        "date": first.get("date", ""),
                        "time": first.get("time", ""),
                    }
                )

    return conflicts


def build_dashboard(pending_actions, flagged, commitments):
    """
    Build and save the dashboard data and HTML view.
    """
    conflicts = _find_conflicts(commitments)

    dashboard = {
        "pending_actions": pending_actions,
        "flagged": flagged,
        "commitments": commitments,
        "conflicts": conflicts,
    }

    with DASHBOARD_JSON.open("w", encoding="utf-8") as f:
        json.dump(dashboard, f, indent=2, default=str)

    _write_html(dashboard)

    return dashboard


def _write_html(dashboard):
    """Write a simple three-pane HTML dashboard."""
    pending_rows = ""

    for item in dashboard["pending_actions"]:
        pending_rows += (
            "<tr>"
            f"<td>{item.get('message_id', '')}</td>"
            f"<td>{item.get('action', '')}</td>"
            f"<td>{item.get('reason', '')}</td>"
            "</tr>"
        )

    flagged_rows = ""

    for item in dashboard["flagged"]:
        flagged_rows += (
            "<tr>"
            f"<td>{item.get('message_id', '')}</td>"
            f"<td>{item.get('attempted', '')}</td>"
            f"<td>{item.get('action_taken', '')}</td>"
            "</tr>"
        )

    commitment_rows = ""

    for item in dashboard["commitments"]:
        source_ids = ", ".join(item.get("source_ids", []))

        commitment_rows += (
            "<tr>"
            f"<td>{item.get('date', '')}</td>"
            f"<td>{item.get('time', '')}</td>"
            f"<td>{item.get('title', '')}</td>"
            f"<td>{source_ids}</td>"
            "</tr>"
        )

    conflict_text = ""

    for conflict in dashboard["conflicts"]:
        conflict_text += (
            f"<p><strong>CONFLICT:</strong> "
            f"{conflict['first']} and {conflict['second']} "
            f"at {conflict['date']} {conflict['time']}</p>"
        )

    if not conflict_text:
        conflict_text = "<p>No conflicts detected.</p>"

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>InboxHero Dashboard</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 30px;
        }}

        .panes {{
            display: flex;
            gap: 20px;
        }}

        .pane {{
            flex: 1;
            border: 1px solid #ccc;
            padding: 15px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}

        th {{
            background: #f2f2f2;
        }}
    </style>
</head>

<body>

<h1>InboxHero Dashboard</h1>

<div class="panes">

    <div class="pane">
        <h2>Pending Actions</h2>
        <table>
            <tr>
                <th>Message</th>
                <th>Action</th>
                <th>Why</th>
            </tr>
            {pending_rows}
        </table>
    </div>

    <div class="pane">
        <h2>Flagged</h2>
        <table>
            <tr>
                <th>Message</th>
                <th>Attempted</th>
                <th>What happened</th>
            </tr>
            {flagged_rows}
        </table>
    </div>

    <div class="pane">
        <h2>Commitments</h2>
        <table>
            <tr>
                <th>Date</th>
                <th>Time</th>
                <th>Commitment</th>
                <th>Sources</th>
            </tr>
            {commitment_rows}
        </table>

        <h3>Conflicts</h3>
        {conflict_text}
    </div>

</div>

</body>
</html>
"""

    with DASHBOARD_HTML.open("w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    sample_commitments = [
        {
            "date": "2026-09-18",
            "time": "10:00",
            "title": "Quarterly board review",
            "source_ids": ["m038"],
        }
    ]

    dashboard = build_dashboard(
        pending_actions=[],
        flagged=[],
        commitments=sample_commitments,
    )

    print(f"Dashboard written to: {DASHBOARD_HTML}")
    print(f"Dashboard data written to: {DASHBOARD_JSON}")