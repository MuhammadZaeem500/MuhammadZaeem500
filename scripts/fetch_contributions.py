import json
import os
import re
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

  for day in soup.find_all("td", class_="ContributionCalendar-day"):
    date = day.get("data-date")
    if not date:
      continue

    count = 0
    level = int(day.get("data-level", "0"))

    # Check text content or tooltips inside the cell
    text_content = day.get_text(strip=True)
    aria_label = day.get("aria-label", "")

    # Combine text inspection for safety
    combined_info = f"{text_content} {aria_label}"
    match = re.search(r"(\d+)\s+contribution", combined_info, re.IGNORECASE)
    if match:
      count = int(match.group(1))
    elif "no contribution" in combined_info.lower():
      count = 0
    else:
      # If level is active but text is hidden, map a basic estimate or check data-count
      data_count = day.get("data-count")
      if data_count and data_count.isdigit():
        count = int(data_count)
      elif level > 0:
        count = level * 2  # fallback scale based on intensity level

    days.append({"date": date, "count": count, "level": level})

  days = sorted(days, key=lambda k: k["date"])

  os.makedirs("data", exist_ok=True)
  output_path = "data/contributions.json"
  with open(output_path, "w") as f:
    json.dump(days, f, indent=2)

  total = sum(d["count"] for d in days)
  print(
      f"Successfully saved {len(days)} structured days of contributions to"
      f" {output_path}. Total: {total}"
  )


if __name__ == "__main__":
  fetch_contributions()