#!/usr/bin/env python3
"""Pre-generate all TTS audio for the voice adventure stories.

Usage:
  .venv/bin/python generate_audio.py                  # generate all stories
  .venv/bin/python generate_audio.py dinosaurs         # generate one story
  .venv/bin/python generate_audio.py dinosaurs pokemon # generate multiple
"""
import asyncio
import json
import os
import sys

import edge_tts

BASE_DIR = os.path.join(os.path.dirname(__file__), "stories")
STORIES_DIR = os.path.dirname(__file__)
NARRATOR_VOICE = "pt-PT-RaquelNeural"
CHOICE_VOICE = "pt-PT-DuarteNeural"

# Words that cause TTS mispronunciation due to accent/encoding issues.
# "Pokémon" (with é, U+00E9) causes edge_tts to say "símbolo de copyright"
# because byte 0xA9 (second byte of UTF-8 é) is © in Latin-1.
# Using the unaccented form still pronounces correctly in Portuguese.
TTS_REPLACEMENTS = {
    "Pokémon": "Pokemon",
    "pokémon": "pokemon",
}


def sanitize_for_tts(text: str) -> str:
    for old, new in TTS_REPLACEMENTS.items():
        text = text.replace(old, new)
    return text


async def generate_segment(text: str, voice: str, output_path: str):
    text = sanitize_for_tts(text)
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)


async def generate_story(story_name: str):
    story_dir = os.path.join(BASE_DIR, story_name)
    story_file = os.path.join(story_dir, "story.json")
    audio_dir = os.path.join(story_dir, "audio")

    if not os.path.exists(story_file):
        print(f"  [SKIP] {story_name}: story.json not found at {story_file}")
        return

    os.makedirs(audio_dir, exist_ok=True)

    with open(story_file, "r", encoding="utf-8") as f:
        story = json.load(f)

    prompt_text = story.get("prompt_text", "O que queres fazer?")
    tasks = []

    for node_id, node in story["nodes"].items():
        # Build narration text with options appended
        choices = node["choices"]
        choice_texts = [c["text"] for c in choices]
        if len(choice_texts) == 1:
            options_str = f"{prompt_text} {choice_texts[0]}."
        elif len(choice_texts) == 2:
            options_str = f"{prompt_text} {choice_texts[0]}, ou {choice_texts[1]}."
        else:
            joined = ", ".join(choice_texts[:-1])
            options_str = f"{prompt_text} {joined}, ou {choice_texts[-1]}."
        full_narration = f"{node['narration']} {options_str}"

        narration_path = os.path.join(audio_dir, f"{node_id}.mp3")
        # Always regenerate narration (options text may have changed)
        tasks.append(("narration", node_id, full_narration, NARRATOR_VOICE, narration_path))

        for i, choice in enumerate(choices):
            choice_path = os.path.join(audio_dir, f"{node_id}_choice{i}.mp3")
            tasks.append(("choice", node_id, choice["text"], CHOICE_VOICE, choice_path))

    print(f"\n  Story: {story_name} ({len(tasks)} segments to generate)")
    for kind, node_id, text, voice, path in tasks:
        print(f"    {kind}: {node_id} -> {os.path.basename(path)}")
        await generate_segment(text, voice, path)
    print(f"  Done! {len(tasks)} segments for '{story_name}'")


async def main():
    if len(sys.argv) > 1:
        story_names = sys.argv[1:]
    else:
        story_names = [
            d for d in os.listdir(BASE_DIR)
            if os.path.isdir(os.path.join(BASE_DIR, d))
        ]

    print(f"Generating audio for {len(story_names)} story/stories: {', '.join(story_names)}")
    for name in story_names:
        await generate_story(name)
    print("\nAll audio generation complete!")


if __name__ == "__main__":
    asyncio.run(main())