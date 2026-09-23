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

  # Target individual contribution calendar days
  for day in soup.find_all("td", class_="ContributionCalendar-day"):
    date = day.get("data-date")
    if not date:
      continue

    # Extract commit count text or level attribute safely
    data_count = day.get("data-count", "0")
    count = int(data_count) if data_count.isdigit() else 0

    # Determine activity level (0 to 4)
    data_level = day.get("data-level", "0")
    level = int(data_level) if data_level.isdigit() else 0

    days.append({"date": date, "count": count, "level": level})

  # Ensure chronological ordering
  days = sorted(days, key=lambda k: k["date"])

  os.makedirs("data", exist_ok=True)
  output_path = "data/contributions.json"
  with open(output_path, "w") as f:
    json.dumps(days, f)
    json.dump(days, f, indent=2)

  print(
      f"Successfully saved {len(days)} structured days of contributions to"
      f" {output_path}"
  )


if __name__ == "__main__":
  fetch_contributions()