import json
import os
from bs4 import BeautifulSoup
import requests

USERNAME = "MuhammadZaeem500"
URL = f"https://github.com/users/{USERNAME}/contributions"


def fetch_contributions():
  print(f"Fetching contribution data for {USERNAME}...")
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
          " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
      )
  }
  response = requests.get(URL, headers=headers)
  if response.status_code != 200:
    raise Exception(
        f"Failed to fetch contributions. Status code: {response.status_code}"
    )

  soup = BeautifulSoup(response.text, "html.parser")

  days = []
  # GitHub uses tooltips or data cells inside the contribution graph table
  # Let's target both standard table cells and tooltips/rects
  cells = soup.find_all("td", class_="ContributionCalendar-day")

  if not cells:
    # Fallback to finding any elements with data-date attributes if class names change
    cells = soup.find_all(attrs={"data-date": True})

  for cell in cells:
    date = cell.get("data-date")
    count_text = cell.get("data-count")
    level = cell.get("data-level", "0")

    if date:
      count = int(count_text) if count_text and count_text.isdigit() else 0
      days.append({"date": date, "count": count, "level": int(level)})

  os.makedirs("data", exist_ok=True)
  output_path = "data/contributions.json"

  with open(output_path, "w") as f:
    json.dump(days, f, indent=2)

  print(f"Successfully saved {len(days)} days of contributions to {output_path}")


if __name__ == "__main__":
  fetch_contributions()