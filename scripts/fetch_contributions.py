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
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/115.0.0.0 Safari/537.36"
      )
  }
  response = requests.get(URL, headers=headers)
  if response.status_code != 200:
    raise Exception(
        f"Failed to fetch contributions. Status code: {response.status_code}"
    )

  soup = BeautifulSoup(response.text, "html.parser")

  # Find all contribution days
  days = []
  svg_days = soup.find_all("td", class_="ContributionCalendar-day")

  for day in svg_days:
    date = day.get("data-date")
    count_text = day.get("data-count")
    level = day.get("data-level", "0")

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