
import json
import html
import os
from pathlib import Path


JSON_PATH = Path("data/contributions.json")
OUTPUT_PATH = Path("contrib-heatmap.svg")

CELL_SIZE = 11
CELL_GAP = 4
STEP = CELL_SIZE + CELL_GAP

LEFT_MARGIN = 40
TOP_MARGIN = 32
BOTTOM_MARGIN = 12

WEEKDAY_LABELS = {
    1: "Mon",
    3: "Wed",
    5: "Fri",
}


def render_heatmap():

    if not JSON_PATH.exists():
        raise FileNotFoundError(
            "Contributions JSON not found. "
            "Run fetch_contributions.py first."
        )

    with JSON_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)

    weeks = data.get("weeks", [])
    total = data.get("total_contributions", 0)

    if not weeks:
        raise ValueError("No contribution weeks found.")

    width = (
        LEFT_MARGIN
        + len(weeks) * STEP
        + CELL_GAP
    )

    height = (
        TOP_MARGIN
        + 7 * STEP
        + BOTTOM_MARGIN
    )

    svg = []

    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width} {height}" '
        f'width="100%" height="auto" '
        f'role="img" '
        f'aria-label="GitHub contribution heatmap">'
    )

    svg.append("""
    <style>
        text {
            font-family:
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                Helvetica,
                Arial,
                sans-serif;
        }

        .header {
            fill: #c9d1d9;
            font-size: 13px;
            font-weight: 600;
        }

        .month {
            fill: #8b949e;
            font-size: 10px;
        }

        .weekday {
            fill: #8b949e;
            font-size: 9px;
        }

        .cell {
            rx: 2;
            ry: 2;
        }
    </style>
    """)

    svg.append(
        f'<rect width="{width}" height="{height}" '
        f'rx="6" fill="#0d1117"/>'
    )

    # Header
    svg.append(
        f'<text x="{LEFT_MARGIN}" y="17" '
        f'class="header">'
        f'{total} contributions in the last year'
        f'</text>'
    )

    # Month labels
    for week_index, week in enumerate(weeks):

        month_start = None

        for day in week["days"]:
            if day["date"].endswith("-01"):
                month_start = day
                break

        if month_start:
            month_name = month_start["date"][5:7]

            import calendar

            month_text = calendar.month_abbr[
                int(month_name)
            ]

            x = LEFT_MARGIN + week_index * STEP

            svg.append(
                f'<text x="{x}" y="29" '
                f'class="month">'
                f'{month_text}'
                f'</text>'
            )

    # Weekday labels
    for weekday, label in WEEKDAY_LABELS.items():

        y = TOP_MARGIN + weekday * STEP + 8

        svg.append(
            f'<text x="0" y="{y}" '
            f'class="weekday">'
            f'{label}'
            f'</text>'
        )

    # Contribution squares
    for week_index, week in enumerate(weeks):

        x = LEFT_MARGIN + week_index * STEP

        for day in week["days"]:

            weekday = int(day["weekday"])

            y = TOP_MARGIN + weekday * STEP

            color = day["color"]

            # Basic validation before adding the API color to SVG.
            if not (
                isinstance(color, str)
                and len(color) == 7
                and color.startswith("#")
                and all(
                    char in "0123456789abcdefABCDEF"
                    for char in color[1:]
                )
            ):
                color = "#161b22"

            count = int(day["count"])
            date = html.escape(day["date"])

            tooltip = (
                f"{count} contributions on {date}"
            )

            svg.append(
                f'<rect '
                f'x="{x}" '
                f'y="{y}" '
                f'width="{CELL_SIZE}" '
                f'height="{CELL_SIZE}" '
                f'class="cell" '
                f'fill="{color}">'
                f'<title>{html.escape(tooltip)}</title>'
                f'</rect>'
            )

    svg.append("</svg>")

    OUTPUT_PATH.write_text(
        "\n".join(svg),
        encoding="utf-8",
    )

    print("----------------------------------")
    print("Heatmap generated successfully!")
    print(f"Total contributions: {total}")
    print(f"Total weeks: {len(weeks)}")
    print(f"Output: {OUTPUT_PATH}")
    print("----------------------------------")


if __name__ == "__main__":
    render_heatmap()
