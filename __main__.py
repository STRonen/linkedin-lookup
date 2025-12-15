import os
import json
from typing import Any, Dict, Optional

from googleapiclient.discovery import build


def google_search(query: str, api_key: str, cx: str, num: int = 5) -> list[str]:
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=query, cx=cx, num=num).execute()
    items = res.get("items", []) or []
    return [item.get("link") for item in items if item.get("link")]


def pick_linkedin_profile(urls: list[str]) -> Optional[str]:
    for url in urls:
        if isinstance(url, str) and "linkedin.com/in/" in url:
            return url.split("?")[0]
    return None


def main(params: Dict[str, Any]) -> Dict[str, Any]:
    # ---- Validate input ----
    full_name = (params.get("full_name") or "").strip()
    if not full_name:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "full_name is required"})
        }

    # ---- Validate environment ----
    google_api_key = os.getenv("GOOGLE_API_KEY")
    google_cx = os.getenv("GOOGLE_CX")

    if not google_api_key or not google_cx:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": "Missing GOOGLE_API_KEY or GOOGLE_CX environment variables"
            })
        }

    # ---- Perform lookup ----
    query = f'site:linkedin.com/in "{full_name}"'
    urls = google_search(query, google_api_key, google_cx)
    profile_url = pick_linkedin_profile(urls)

    # ---- Always return JSON body (IMPORTANT) ----
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "status": "FOUND" if profile_url else "NOT_FOUND",
            "linkedin_profile_url": profile_url,
            "candidates": urls
        })
    }
