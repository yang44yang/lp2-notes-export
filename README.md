# lp2-notes-export

Export, proofread, and translate [Light Phone 2](https://www.thelightphone.com/) notes via the unofficial dashboard API.

Most LP2 notes are created via voice input, so they contain speech-to-text artifacts (filler words, broken sentences, missing punctuation). This tool cleans them up and optionally translates them.

## What it does

1. **Exports** all your text notes from the Light Phone dashboard
2. **Proofreads** the rough voice-to-text transcriptions into clean, readable text
3. **Translates** into your target language (Chinese by default)
4. **Saves** each note as an individual markdown file with Original / Proofread / Translation sections

> Audio notes cannot be exported via the API — they are flagged in the output with a link to the dashboard.

## Two ways to use it

### Option A: Claude Skill (recommended)

Use this as a [Claude](https://claude.ai) skill for the full pipeline (export + proofread + translate) powered by AI.

1. Clone this repo into your Claude skills directory:
   ```bash
   git clone https://github.com/yang44yang/lp2-notes-export.git ~/.skills/skills/lp2-notes-export
   ```
2. Open Claude with the Chrome extension connected to a browser tab logged into [dashboard.thelightphone.com](https://dashboard.thelightphone.com)
3. Ask Claude: *"Export my Light Phone notes, proofread them, and translate to Chinese"*

Claude will read your auth token from the dashboard cookie, call the API, download all notes, proofread each one, translate, and save as markdown files.

### Option B: Standalone Python script

For raw export only (no AI proofreading/translation):

```bash
python scripts/export_notes.py \
  --token YOUR_BEARER_TOKEN \
  --device-id YOUR_DEVICE_UUID \
  --output ./my-notes
```

**To get your token and device ID:**
1. Log into [dashboard.thelightphone.com](https://dashboard.thelightphone.com)
2. Open DevTools (F12) → Network tab → click any request
3. Copy the `Authorization` header value (the part after "Bearer ")
4. Copy your device ID from the URL (the UUID after `/devices/`)

## Output format

Each note is saved as a markdown file:

```
01_2026-03-10_your-note-slug.md
02_2026-01-28_another-note.md
...
```

With sections for Original, Proofread, and Translation (when using the Claude skill).

## API details

This project uses the unofficial Light Phone cloud API at `production.lightphonecloud.com`. Key endpoints:

- `GET /api/devices` — list devices and their tool IDs
- `GET /api/notes?device_tool_id={id}` — list all notes
- `GET /api/notes/{id}/generate_presigned_get_url` — get S3 download URL for note content

All requests require `Authorization: Bearer {token}`.

## Credits

API discovery inspired by [Felix Krause's light-phone-2 project](https://github.com/nicklama/light-phone-2).

## License

MIT
