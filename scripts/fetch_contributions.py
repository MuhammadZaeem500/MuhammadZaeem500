import json
import os

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]


def render_heatmap():
  json_path = "data/contributions.json"
  if not os.path.exists(json_path):
    print("Contributions JSON not found. Run fetch_contributions.py first.")
    return

  with open(json_path, "r") as f:
    days = json.load(f)

  # Calculate total contributions dynamically from counts or levels
  total_contributions = sum(
      int(d.get("count", 0)) if str(d.get("count", 0)).isdigit() else 0
      for d in days
  )
  if total_contributions == 0:
    # Fallback estimation if counts were blank
    total_contributions = sum(
        int(d.get("level", 0)) * 2 for d in days if int(d.get("level", 0)) > 0
    )

  width = 860
  height = 160
  cell_size = 11
  cell_gap = 4
  step = cell_size + cell_gap

  svg_lines = [
      f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}"'
      f' width="{width}" height="{height}" style="background-color: #0d1117;'
      ' border-radius: 6px; font-family: -apple-system, BlinkMacSystemFont,'
      ' \'Segoe UI\', Helvetica, Arial, sans-serif;">',
      "  <style>",
      "    .cell { shape-rendering: geometricPrecision; rx: 3px; ry: 3px;"
      " transition: fill 0.2s ease; }",
      "    .cell:hover { stroke: #8b949e; stroke-width: 1px; }",
      "    .text { fill: #8b949e; font-size: 12px; }",
      "    .title { fill: #c9d1d9; font-size: 13px; font-weight: 600; }",
      "    @keyframes slideDown {",
      "      0% { transform: translateY(-10px); opacity: 0; }",
      "      100% { transform: translateY(0); opacity: 1; }",
      "    }",
      "    .heatmap-grid { animation: slideDown 0.6s ease-out forwards; }",
      "  </style>",
      f'  <rect width="100%" height="100%" fill="#0d1117" rx="6"/>',
      '  <g transform="translate(20, 20)">',
      '    <text x="0" y="2" class="title">GitHub Contributions Heatmap</text>',
      '    <g class="heatmap-grid" transform="translate(0, 18)">',
  ]

  weeks = [days[i : i + 7] for i in range(0, len(days), 7)]

  for w_idx, week in enumerate(weeks):
    for d_idx, day in enumerate(week):
      x = w_idx * step
      y = d_idx * step
      level = min(int(day.get("level", 0)), len(PALETTE) - 1)
      color = PALETTE[level]
      date = day.get("date", "")
      count = day.get("count", 0)

      svg_lines.append(
          f'      <rect x="{x}" y="{y}" width="{cell_size}"'
          f' height="{cell_size}" class="cell" fill="{color}"><title>{count}'
          f" contributions on {date}</title></rect>"
      )

  svg_lines.append("    </g>")

  # Footer text positioned correctly below the grid
  footer_y = 18 + (7 * step) + 20
  svg_lines.extend([
      (
          f'    <text x="0" y="{footer_y}" class="text">{total_contributions}'
          " contributions in the last year</text>"
      ),
      "  </g>",
      "</svg>",
  ])

  output_svg = "contrib-heatmap.svg"
  with open(output_svg, "w") as f:
    f.write("\n".join(svg_lines))

  print(f"Successfully generated {output_svg} with {total_contributions} total.")


if __name__ == "__main__":
  render_heatmap()