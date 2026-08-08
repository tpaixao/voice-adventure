#!/usr/bin/env python3
"""Test Seedream 4.5 image generation via OpenRouter Images API."""
import base64
import json
import socket
import ssl
import sys
import urllib.request

API_KEY = open("openrouter_key.txt").read().strip()

# Seedream 4.5 — flat $0.04/image
MODEL = "bytedance-seed/seedream-4.5"

# Test scene: Professor Oak's lab with 3 starter Pokémon
PROMPT = (
    "Bright colorful children's storybook illustration. A cozy research lab "
    "with warm lighting. A friendly professor in a white lab coat stands behind "
    "a table with three Pokéballs. On the table: a small yellow electric mouse "
    "Pokémon (Pikachu), an orange lizard Pokémon with a flame on its tail "
    "(Charmander), and a blue turtle Pokémon with a shell (Squirtle). "
    "A young boy trainer stands in front, eyes wide with excitement. "
    "Cartoon style, vibrant colors, soft outlines, no text."
)

def call_images_api():
    url = "https://openrouter.ai/api/v1/images"
    body = json.dumps({
        "model": MODEL,
        "prompt": PROMPT,
        "aspect_ratio": "16:9",
        "size": "2K",
        "n": 1,
    }).encode()

    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
            data = json.loads(resp.read())
            print(f"Status: {resp.status}")
            print(f"Response keys: {list(data.keys())}")
            if "data" in data and len(data["data"]) > 0:
                item = data["data"][0]
                # Image is base64 in b64_json
                if "b64_json" in item:
                    img_bytes = base64.b64decode(item["b64_json"])
                    out_path = "projects/voice_adventure/test_seedream_lab.png"
                    with open(out_path, "wb") as f:
                        f.write(img_bytes)
                    print(f"Saved image to {out_path} ({len(img_bytes)} bytes)")
                if "media_type" in item:
                    print(f"Media type: {item['media_type']}")
            if "usage" in data:
                print(f"Usage: {json.dumps(data['usage'], indent=2)}")
            return data
            # Print full response for debugging
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode()}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    call_images_api()