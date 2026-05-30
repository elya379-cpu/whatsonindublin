#!/usr/bin/env python3
"""Fetch upcoming events in Dublin from Ticketmaster and save to data/events.json."""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TICKETMASTER_API_KEY")
if not API_KEY:
    print("Error: TICKETMASTER_API_KEY not set in environment or .env file")
    sys.exit(1)

BASE_URL = "https://app.ticketmaster.com/discovery/v2/events.json"
OUTPUT_PATH = Path(__file__).parent.parent / "data" / "events.json"


def fetch_events(page_size: int = 100, max_pages: int = 5) -> list[dict]:
    events = []
    for page in range(max_pages):
        params = {
            "apikey": API_KEY,
            "city": "Dublin",
            "countryCode": "IE",
            "size": page_size,
            "page": page,
            "sort": "date,asc",
        }
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        page_events = data.get("_embedded", {}).get("events", [])
        if not page_events:
            break

        events.extend(page_events)

        total_pages = data.get("page", {}).get("totalPages", 1)
        if page + 1 >= total_pages:
            break

    return events


def transform_event(raw: dict) -> dict:
    dates = raw.get("dates", {})
    start = dates.get("start", {})
    venue = {}
    venues = raw.get("_embedded", {}).get("venues", [])
    if venues:
        v = venues[0]
        venue = {
            "name": v.get("name"),
            "address": v.get("address", {}).get("line1"),
            "city": v.get("city", {}).get("name"),
            "url": v.get("url"),
        }

    images = raw.get("images", [])
    # prefer 16:9 ratio at ~640px wide, fall back to first available
    hero = next(
        (i["url"] for i in images if i.get("ratio") == "16_9" and i.get("width", 0) >= 640),
        images[0]["url"] if images else None,
    )

    price_ranges = raw.get("priceRanges", [])
    price = None
    if price_ranges:
        pr = price_ranges[0]
        price = {
            "min": pr.get("min"),
            "max": pr.get("max"),
            "currency": pr.get("currency"),
        }

    return {
        "id": raw.get("id"),
        "name": raw.get("name"),
        "url": raw.get("url"),
        "image": hero,
        "date": start.get("localDate"),
        "time": start.get("localTime"),
        "status": dates.get("status", {}).get("code"),
        "venue": venue,
        "price": price,
        "classifications": [
            {
                "segment": c.get("segment", {}).get("name"),
                "genre": c.get("genre", {}).get("name"),
            }
            for c in raw.get("classifications", [])
        ],
    }


def main():
    print("Fetching events from Ticketmaster...")
    raw_events = fetch_events()
    print(f"  Retrieved {len(raw_events)} events")

    transformed = [transform_event(e) for e in raw_events]

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(transformed),
        "events": transformed,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(output, indent=2, ensure_ascii=False))
    print(f"  Saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
