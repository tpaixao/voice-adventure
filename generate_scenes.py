#!/usr/bin/env python3
"""Batch-generate all Pokémon story scene illustrations via Seedream 4.5 on OpenRouter.
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
SCENES_DIR = "projects/voice_adventure/stories/pokemon/scenes"
STYLE = "Bright colorful children's storybook illustration, cartoon style, vibrant colors, soft outlines, no text, kid-friendly."

PROMPTS = {
    "start": "A cozy research lab with warm lighting. A friendly professor in a white lab coat stands behind a table with three Pokeballs. On the table: a small yellow electric mouse Pokemon (Pikachu), an orange lizard Pokemon with a flame on its tail (Charmander), and a blue turtle Pokemon with a shell (Squirtle). A young boy trainer stands in front, eyes wide with excitement.",
    "choose_pikachu": "A young boy trainer hugging a small yellow electric mouse Pokemon (Pikachu) that jumps joyfully into his arms. Both have sparkling happy eyes. Warm sunny outdoor scene with a path ahead. The Pikachu's cheeks glow with tiny electric sparks.",
    "choose_charmander": "A young boy trainer standing with an orange lizard Pokemon with a flame on its tail (Charmander). Both look excited and ready for adventure. Sunny outdoor path leading into the distance. The flame on Charmander's tail burns brightly.",
    "choose_squirtle": "A young boy trainer jumping with joy alongside a blue turtle Pokemon with a hard shell on its back (Squirtle). Water droplets splash from Squirtle's mouth. Sunny outdoor scene with a path ahead. Both are happy and energetic.",
    "forest": "A dark humid forest with enormous tall trees. A small green caterpillar Pokemon (Caterpie) is eating a leaf on a low branch. In the blurry background, a larger mysterious creature moves among the bushes. Dappled light filters through the canopy.",
    "beach": "A hot sandy beach with bright blue sparkling sea. An orange crab Pokemon (Krabby) runs across the sand with big claws raised. In the calm water, a purple clam Pokemon (Shellder) floats gently. Sunny sky, palm trees, waves lapping the shore.",
    "mountain": "A steep rocky mountain path winding upward. At the top, a gray rock Pokemon with arms and eyes (Geodude) sleeps on a warm stone. Below on a ledge, a fighting-type Pokemon (Machop) trains with push-ups. Dramatic mountain vista with clouds.",
    "river": "A crystal clear river flowing over smooth stones in a green meadow. An orange fish Pokemon (Magikarp) jumps high out of the water with a big splash. Near the bank, a small blue tadpole Pokemon with a white spiral on its belly (Poliwag) swims in circles. Sunny, peaceful.",
    "caterpie": "A close friendly encounter in the forest. A young boy trainer and his Pokemon gently approach a small green caterpillar Pokemon (Caterpie) who looks up with big curious eyes. The trainer's Pokemon sniffs it friendlily. Warm forest light, gentle mood.",
    "beedrill": "A dramatic forest scene. A large bee Pokemon with needle-like stingers on its arms (Beedrill) hovers threateningly with wings buzzing. The trainer's Pokemon stands bravely in front of the young boy trainer, protecting him. Tense but not scary, forest background.",
    "krabby": "A funny beach scene. An orange crab Pokemon (Krabby) does a silly dance on the sand, waving its claws side to side. The young boy trainer and his Pokemon laugh together. Bright sunny beach, joyful and comical mood.",
    "shellder": "A magical underwater scene. A purple clam Pokemon (Shellder) opens its shell revealing a glowing shiny pearl inside. The young boy trainer reaches out to touch the pearl, amazed. Sparkling light radiates from the pearl, magical and wondrous.",
    "geodude": "A mountain top scene. A gray rock Pokemon with arms and sleepy eyes (Geodude) wakes up on a warm stone and smiles. The young boy trainer and his Pokemon greet it happily. Sunny mountain summit with blue sky and clouds.",
    "machop": "A sunny mountain scene. A muscular fighting-type Pokemon (Machop) does push-ups on a rocky ledge, counting with a big smile. The young boy trainer and his Pokemon join in exercising together. Bright, energetic, fun mood.",
    "magikarp": "A funny river scene. An orange fish Pokemon (Magikarp) splashes and jumps so high out of the river that it lands in the young boy trainer's hand. Both laugh. Water splashes everywhere. Bright, comical, joyful.",
    "poliwag": "A clear river scene. A small blue tadpole Pokemon with a white spiral on its belly (Poliwag) swims fast in the water. The young boy trainer swims alongside, racing competitively. Splashing water, sunny, energetic and fun.",
    "gym": "Interior of a grand Pokemon Gym arena. A large battle floor with stadium seating. On the far side, a confident Gym Leader stands with a strong Pokemon ready. The young boy trainer enters from the other side with determination. Dramatic arena lighting.",
    "battle_win": "An epic Pokemon battle in a gym arena. The young trainer's Pokemon attacks with powerful glowing energy. The Gym Leader's Pokemon is being knocked back, defeated. Bright explosion of light and energy effects. Triumphant, exciting, dramatic.",
    "battle_smart": "A clever Pokemon battle in a gym arena. The young trainer's Pokemon dodges to the side and attacks from an angle. The Gym Leader looks surprised and caught off guard. Strategic movements shown with motion lines. Exciting, smart, dynamic.",
}


def generate_image(prompt: str, out_path: str) -> bool:
    """Generate one image via OpenRouter Images API. Returns True on success."""
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

    # Move the test image as start.jpg if it exists
    test_img = "projects/voice_adventure/test_seedream_lab.png"
    start_path = os.path.join(SCENES_DIR, "start.jpg")
    if os.path.exists(test_img) and not os.path.exists(start_path):
        import shutil
        shutil.copy(test_img, start_path)
        print(f"Copied test image as start.jpg")

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

        # Small delay to avoid rate limits
        time.sleep(1)

    print(f"\nDone: {done} generated, {skipped} skipped, {len(failed)} failed")
    if failed:
        print(f"Failed: {failed}")
        sys.exit(1)


if __name__ == "__main__":
    main()