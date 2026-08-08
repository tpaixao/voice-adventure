#!/usr/bin/env python3
"""List all OpenRouter image models with pricing."""
import json
import ssl
import urllib.request

ctx = ssl.create_default_context()
req = urllib.request.Request(
    "https://openrouter.ai/api/v1/models?output_modalities=image",
    headers={"Accept": "application/json"},
)
with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
    data = json.loads(r.read())

for m in data.get("data", []):
    mid = m["id"]
    name = m.get("name", "")
    pricing = m.get("pricing", {})
    img_price = pricing.get("image", "") or pricing.get("image_output", "")
    print(f"{mid:55s} | image={img_price} | {name}")