
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests


USERNAME = "MuhammadZaeem500"

GRAPHQL_URL = "https://api.github.com/graphql"

OUTPUT_PATH = Path("data/contributions.json")

GRAPHQL_QUERY = """
query (
  $username: String!
  $from: DateTime!
  $to: DateTime!
) {
  user(login: $username) {
    contributionsCollection(
      from: $from
      to: $to
    ) {
      contributionCalendar {
        totalContributions

        weeks {
          firstDay

          contributionDays {
            date
            contributionCount
            contributionLevel
            color
            weekday
          }
        }
      }
    }
  }
}
"""


def fetch_contributions():
    token = os.getenv("GH_TOKEN")

    if not token:
        raise RuntimeError(
            "GH_TOKEN is missing. Add your GitHub token "
            "to repository secrets."
        )

    print(f"Fetching contributions for {USERNAME}...")

    # GitHub contribution dates use UTC.
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=365)

    variables = {
        "username": USERNAME,
        "from": start_date.isoformat(),
        "to": now.isoformat(),
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/vnd.github+json",
    }

    response = requests.post(
        GRAPHQL_URL,
        json={
            "query": GRAPHQL_QUERY,
            "variables": variables,
        },
        headers=headers,
        timeout=30,
    )

    response.raise_for_status()

    result = response.json()

    if result.get("errors"):
        raise RuntimeError(
            f"GitHub GraphQL error: {result['errors']}"
        )

    user = result.get("data", {}).get("user")

    if not user:
        raise RuntimeError(
            f"GitHub user '{USERNAME}' was not found."
        )

    calendar = (
        user["contributionsCollection"]["contributionCalendar"]
    )

    total_contributions = calendar["totalContributions"]

    weeks = []
    all_days = []

    for week in calendar["weeks"]:
        week_days = []

        for day in week["contributionDays"]:
            contribution = {
                "date": day["date"],
                "count": day["contributionCount"],
                "level": day["contributionLevel"],
                "color": day["color"],
                "weekday": day["weekday"],
            }

            week_days.append(contribution)
            all_days.append(contribution)

        weeks.append({
            "first_day": week["firstDay"],
            "days": week_days,
        })

    calculated_total = sum(
        day["count"] for day in all_days
    )

    if calculated_total != total_contributions:
        print(
            "Warning: Calendar day sum differs from "
            "GitHub's reported total."
        )

        print(
            f"GitHub total: {total_contributions}, "
            f"day sum: {calculated_total}"
        )

    data = {
        "username": USERNAME,
        "generated_at": now.isoformat(),
        "range": {
            "from": start_date.date().isoformat(),
            "to": now.date().isoformat(),
        },
        "total_contributions": total_contributions,
        "weeks": weeks,
        "days": all_days,
    }

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print("----------------------------------")
    print("Contribution data fetched successfully!")
    print(f"Username: {USERNAME}")
    print(f"Total contributions: {total_contributions}")
    print(f"Total days: {len(all_days)}")
    print(f"Total weeks: {len(weeks)}")
    print(f"Saved to: {OUTPUT_PATH}")
    print("----------------------------------")


if __name__ == "__main__":
    try:
        fetch_contributions()
    except Exception as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
