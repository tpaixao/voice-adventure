# Voice Adventure

A fully voiced, icon-based choose-your-own-adventure app for young children. No reading required — all choices are presented as big emoji buttons with Portuguese voice narration that reads the available options aloud before the child taps.

Built for two kids:
- **André** (age 6) — dinosaur and Pokémon adventures
- **Beatriz** (age 2) — gentle unicorn story

## Stories

| Story | Age | Nodes | Audio |
|-------|-----|-------|------|
| 🦕 A Floresta dos Dinossauros | 4-6 | 14 | 34 |
| ⚡ A Aventura Pokémon | 4-6 | 19 | 48 |
| 🦄 O Unicórnio Arco-Íris | 2-4 | 17 | 42 |

## How It Works

Each story is a JSON graph of narrative nodes. Each node has:
- A **narration** string (read aloud by TTS)
- One or more **choices**, each with text, an emoji icon, and a link to the next node

The web UI plays the narration audio, then reveals large circular emoji buttons. The child taps an icon, hears the choice confirmed aloud, and the next scene loads with a new background color and emoji.

No text is displayed — everything is audio-driven, so pre-readers can play independently.

## Tech Stack

- **TTS**: [edge-tts](https://github.com/rany2/edge-tts) with European Portuguese voices
  - Narrator: `pt-PT-RaquelNeural` (female)
  - Choice confirmation: `pt-PT-DuarteNeural` (male)
- **Frontend**: Vanilla HTML/CSS/JS, no build step, no dependencies
- **Server**: Python `http.server` (or any static file server)

## Project Structure

```
voice_adventure/
├── index.html              # Landing page (story picker)
├── generate_audio.py       # TTS generation script
├── stories/
│   ├── dinosaurs/
│   │   ├── story.json       # Story graph
│   │   ├── index.html       # Story player UI
│   │   └── audio/           # Pre-generated MP3s
│   ├── pokemon/
│   │   ├── story.json
│   │   ├── index.html
│   │   └── audio/
│   └── unicorns/
│       ├── story.json
│       ├── index.html
│       └── audio/
└── .venv/                   # Python venv (edge-tts)
```

## Usage

### Serve locally

```bash
cd voice_adventure
python3 -m http.server 8088 --bind 0.0.0.0
```

Then open `http://<your-ip>:8088` on a phone or tablet.

### Regenerate audio

```bash
.venv/bin/python generate_audio.py              # all stories
.venv/bin/python generate_audio.py unicorns      # one story
.venv/bin/python generate_audio.py dinosaurs pokemon  # multiple
```

Note: audio generation uses edge-tts (free, no API key) but can be slow — the script generates sequentially. For large stories, you may need to batch manually (timeout after ~120s of generation).

### Create a new story

1. Create `stories/{name}/` with `story.json`, `index.html`, and `audio/`
2. Write the story graph in JSON (see existing stories for format)
3. Copy an existing `index.html` and update the scene metadata (emoji + background per node)
4. Run `generate_audio.py {name}` to produce MP3s
5. Add a card to the landing `index.html`

## Story JSON Format

```json
{
  "title": "Story Title",
  "start": "start",
  "prompt_text": "O que queres fazer?",
  "nodes": {
    "start": {
      "narration": "Narration text in Portuguese...",
      "choices": [
        {"text": "Choice 1", "icon": "🎈", "next": "node_a"},
        {"text": "Choice 2", "icon": "🌟", "next": "node_b"}
      ]
    },
    "node_a": {
      "narration": "...",
      "choices": [
        {"text": "Replay", "icon": "🔄", "next": "start"}
      ]
    }
  }
}
```

## Language

All narration and choices are in **European Portuguese** (pt-PT).

## License

MIT