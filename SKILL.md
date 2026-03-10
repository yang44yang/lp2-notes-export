---
name: lp2-notes-export
description: "Export, proofread, and translate Light Phone 2 notes. Use this skill whenever the user mentions Light Phone, LP2, or wants to export/backup/download notes from their Light Phone dashboard. Also trigger when the user pastes a dashboard.thelightphone.com URL, mentions light phone notes, or wants to batch-process voice memos from their phone."
---

# Light Phone 2 Notes Export

Export all notes from a Light Phone 2 via the unofficial dashboard API, proofread them, optionally translate them, and save each note as a clean markdown file.

## Background

Light Phone 2 (and LP3) stores notes on production.lightphonecloud.com. The dashboard at dashboard.thelightphone.com is an Ember.js app that talks to this API. There is no official export feature, but the API is straightforward once you have the auth token and the correct device tool ID.

Most LP2 notes are created via voice input, so they contain speech-to-text artifacts like filler words, broken sentences, and missing punctuation. The proofreading step cleans these up while preserving the original meaning.

## Prerequisites

The user needs to be logged into dashboard.thelightphone.com in their browser. The skill uses the browser (Claude in Chrome) to extract the auth token from cookies and call the API directly.

## Workflow

### Step 1: Get auth token and device info

Navigate to the Light Phone dashboard. The auth token is in a cookie called "token" on dashboard.thelightphone.com.

Device ID: extract from the dashboard URL (the UUID after /devices/) or call GET /api/devices with the Bearer token.

### Step 2: Find the Notes device_tool_id

1. Call GET /api/devices to get relationships.device_tools.data[]
2. For each device_tool_id, call GET /api/notes?device_tool_id={id}
3. The one returning actual data (response length > 50 bytes) is the Notes tool

All requests require: Authorization: Bearer {token}

### Step 3: Fetch all notes

GET /api/notes?device_tool_id={NOTES_DEVICE_TOOL_ID}

Returns JSON API format with data[] array containing note objects.

### Step 4: Download each note content

GET /api/notes/{note_id}/generate_presigned_get_url

Returns { "presigned_get_url": "https://s3..." } - download content from that URL (no auth needed).

Audio notes cannot be exported via API. Flag them in the output.

### Step 5: Proofread and translate

Clean up voice-to-text artifacts: remove fillers, fix sentence boundaries, restore punctuation, preserve meaning and tone.

Translate the proofread version (not the raw original) if requested.

### Step 6: Export as markdown

File naming: {NN}_{date}_{slug}.md

Each file has: Original, Proofread, and Translation sections.

### Browser JavaScript pattern

All API calls use XMLHttpRequest from the dashboard page. Read the token cookie and use it in the same JS call - never return token values as output (Claude in Chrome blocks cookie values).

## Customization

Ask users about: skip translation, target language, single vs individual files, audio note handling.
