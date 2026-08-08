#!/usr/bin/env python3
"""Batch-generate all Unicorn story scene illustrations via Seedream 4.5 on OpenRouter.
Resumable: skips images that already exist in scenes/."""
import base64
import json
import os
import ssl
import sys
import time
import urllib.request

API_KEY = open("openrouter_key.txt").read().strip()
MODEL = "bytedance-seed/seedream-4.5"
SCENES_DIR = "projects/voice_adventure/stories/unicorns/scenes"
STYLE = "Soft gentle children's storybook illustration, cute and dreamy, pastel colors, soft outlines, no text, toddler-friendly, warm and cozy."

PROMPTS = {
    "start": "A cute white unicorn with a sparkling magical horn on its head and a flowing soft mane, standing in a sunny green meadow with colorful wildflowers. The unicorn looks friendly and happy, smiling at the viewer. Rainbows in the sky.",
    "hug": "A little girl giving a big warm hug to a soft fluffy unicorn in a meadow. Both are happy and cozy, surrounded by flowers. The unicorn's mane is silky and flowing. Warm, loving, gentle mood.",
    "choose_color": "A cute unicorn standing in a meadow looking curious and excited, with a magical glowing horn. Around the unicorn float three sparkling circles of light: one pink, one blue, one yellow. The unicorn seems to be choosing a color. Magical, playful.",
    "pink": "A beautiful unicorn transformed to a soft pink color, with a flowing mane full of tiny pink flowers. The unicorn jumps joyfully in a meadow. Cherry blossom petals float in the air. Bright, cheerful, lovely.",
    "blue": "A beautiful unicorn transformed to a gentle sky-blue color, with a mane that shimmers like the ocean. The unicorn does a graceful leap. Blue sky and fluffy white clouds behind. Serene, magical, pretty.",
    "yellow": "A beautiful unicorn transformed to a warm golden-yellow color, with a mane that glows like sunshine. The unicorn looks like a star, sparkling brightly. Sunny meadow, warm light, radiant and happy.",
    "play": "A colorful meadow full of red, yellow, and blue flowers. Butterflies fly in the air, small birds sing on branches. A cute unicorn and a little girl run happily together through the flowers. Bright, joyful, sunny day.",
    "flowers": "A little girl making a flower crown and placing it on a cute unicorn's head. The unicorn looks elegant and happy, wearing a crown of red, yellow, and blue flowers. Surrounded by a colorful meadow. Sweet, tender moment.",
    "run": "A little girl and a cute unicorn running fast together through a flower meadow. The unicorn waits for the girl. Wind blows their hair and mane. Both are laughing. Bright, energetic, joyful, fun.",
    "butterflies": "A little girl watching beautiful colorful butterflies in a meadow. One butterfly has landed on her nose, making her giggle. A cute unicorn watches and laughs too. Soft, gentle, magical, happy.",
    "friends": "A cute unicorn introducing its friends to a little girl: a small fluffy white bunny, a twinkling little star, and a soft round white cloud. They are all in a meadow at golden hour. Friendly, warm, adorable.",
    "bunny": "A tiny fluffy white bunny with big ears that move up and down, giving a little kiss to a girl's nose in a meadow. The cute unicorn watches and laughs. Soft, adorable, gentle, sweet.",
    "star": "A bright twinkling star dancing in the sky, leaving a trail of sparkling light. A little girl and a cute unicorn look up at it with wonder and happiness. Night sky with soft glowing stars. Magical, dreamy.",
    "cloud": "A soft fluffy white cloud like cotton, floating gently in the sky. A little girl sits on top of the cloud, comfortable and relaxed. A cute unicorn floats nearby. Peaceful, dreamy, cozy, soft.",
    "sleep": "A beautiful sunset with orange and pink sky. A cute unicorn looks tired and sleepy in a meadow. The sun is setting on the horizon. Calm, peaceful, warm evening light, gentle.",
    "ending_sleep": "A little girl and a cute unicorn sleeping together under a starry night sky. The unicorn rests its soft head on the girl's lap. The sky is filled with twinkling stars. Peaceful, tender, cozy, dreamy.",
    "ending_song": "A little girl singing a gentle lullaby to a cute unicorn who has closed its eyes and smiles. Stars in the sky twinkle extra bright, as if the song makes them shine. Night sky, peaceful, magical, sweet.",
}


def generate_image(prompt: str, out_path: str) -> bool:
    body = json.dumps({
        "model": MODEL,
        "prompt": f"{STYLE} {prompt}",
        "aspect_ratio": "16:9",
        "size": "2K",
        "n": 1,
    }).encode()

    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/images",
        data=body,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=180, context=ctx) as resp:
            data = json.loads(resp.read())
            if "data" in data and len(data["data"]) > 0:
                item = data["data"][0]
                if "b64_json" in item:
                    img_bytes = base64.b64decode(item["b64_json"])
                    with open(out_path, "wb") as f:
                        f.write(img_bytes)
                    cost = data.get("usage", {}).get("cost", "?")
                    print(f"  Saved {out_path} ({len(img_bytes)} bytes, ${cost})")
                    return True
            print(f"  ERROR: unexpected response: {json.dumps(data)[:200]}")
            return False
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


def main():
    os.makedirs(SCENES_DIR, exist_ok=True)

    total = len(PROMPTS)
    done = 0
    skipped = 0
    failed = []

    for key, prompt in PROMPTS.items():
        out_path = os.path.join(SCENES_DIR, f"{key}.jpg")
        if os.path.exists(out_path):
            print(f"[{done+skipped+1}/{total}] {key}: already exists, skipping")
            skipped += 1
            continue

        print(f"[{done+skipped+1}/{total}] {key}: generating...")
        if generate_image(prompt, out_path):
            done += 1
        else:
            failed.append(key)

        time.sleep(1)

    print(f"\nDone: {done} generated, {skipped} skipped, {len(failed)} failed")
    if failed:
        print(f"Failed: {failed}")
        sys.exit(1)


if __name__ == "__main__":
    main()