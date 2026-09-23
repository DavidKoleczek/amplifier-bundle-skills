---
name: create-demo-video
description: >-
  Produce a narrated demo video that shows something the user made or built,
  cut from recordings they supply or recordings made to their direction. Use
  when showing a product, feature, tool, or project in action. Not for
  slide-style explainers; for a single trim or audio cleanup, use the relevant
  tool directly.
---

# Create a Demo Video

Show the thing working. Build every demo scene from a recording of it, never
from slides or static screenshots standing in for it. Settle the storyboard and
narration before detailed visual timing, then review one canonical export end
to end.

## Harness

Drive this workflow from a harness running a strong reasoning model, such as
the Amplifier CLI with `gpt-6-astra` at high reasoning effort or Claude Opus 5.5.
The workflow depends on sustained judgment across footage, narration timing,
and review.

## Tools

Install the `smart-tools` skill from
[microsoft/amplifier-smart-tools](https://github.com/microsoft/amplifier-smart-tools):

```bash
npx skills add microsoft/amplifier-smart-tools
```

For the Amplifier app CLI, add the Smart Tools behavior instead:

```bash
amplifier bundle add 'git+https://github.com/microsoft/amplifier-smart-tools@main#subdirectory=behaviors/smart-tools.yaml' --app
```

Load it to access the catalog and each tool's installation, prerequisites, and
usage guidance:

- **vid:** edit plans, assembly, rendering, and export verification.
- **aud:** speech cleanup, mastering, and loudness/peak verification.
- **unfold:** silent animations with editable source.
- **showrun:** recorded walkthroughs of a running web app.
- **Stories:** storyboards and speech synthesis. Prefer Gemini 3.1 TTS
  (`gemini-3.1-flash-tts-preview`); audition a short passage to choose the voice.
  Master the resulting speech with aud.

Use FFmpeg/ffprobe for clip preparation and inspection, and small scripts for
repeatable builds. Supply or create music separately from audio mastering.

## Workflow

### 1. Write the storyboard

Inspect existing scripts, recordings, artwork, and credits. Establish the
audience, takeaway, runtime limit, and destination; ask only for missing
decisions. Use 1080p at 30 fps unless the brief calls for another format.

Start with a hook, a tour of visible results, a short synthesis, and a closing
action. Give each demo one spoken point and footage that proves it. Reuse chosen
branding; otherwise compare a few small layout previews and voice/music samples
before applying a direction throughout.

Write `storyboard.md` in the project and share it. The user may edit it or leave
it to the agent; either way it is the source of truth for every later step.
Update it whenever direction changes, and rebuild from it. Each scene lists
what is on screen and its narration. On screen is a recording excerpt, an
Unfold animation such as an opening title or concept diagram, a title card, or
a combination. Text shown on screen, such as titles, animation labels, and
subtitles, is optional and listed separately.

```markdown
# <Title>

Length: 1:00. Format: 1080p, 30 fps.

## <Scene ID>

On-screen: <recording file, in to out; or Unfold animation and reveal order; or title card>
Text (optional): <titles, animation labels, subtitles>
Narration: <spoken line>
```

Use the scene IDs to connect on-screen sources, narration, and review
timestamps. Preserve original assets, animation source, and generation
settings; separate caches from rebuild inputs.

**Success criteria:** Each scene has a purpose, an on-screen source, and a
narration line, and the total fits the runtime budget.

### 2. Get the recordings

Use recordings the user supplies, or make recordings of what the user wants to
show. Long, unedited captures are fine; step 4 cuts them down. Make recordings
with real screen capture of the thing running, for example with Showrun for a
web app. Seed realistic demo data first so screens do not start empty. Only
substitute simulated or animated footage when the user explicitly asks not to
use real screen capture. If a storyboard beat cannot be recorded because the
thing lacks it, tell the user rather than faking it.

**Success criteria:** Every demo scene in the storyboard maps to a recording
that shows it happening.

### 3. Finish narration before timing visuals

Clean supplied speech or generate one clip per scene with consistent voice
settings. Use aud to master it; -16 LUFS and a -1.5 dBTP ceiling are useful
starting points. Inspect verification results and listen to the delivery.
Retain raw and mastered clips; regenerate only changed lines.

Measure speech and set scene durations with breathing room. If the video runs
long, shorten copy and remove redundant beats before speeding up speech or demos.
Keep spoken copy and on-screen claims synchronized. Regenerated speech requires
new timing cues, including any timestamp-based breath or pause edits.

**Success criteria:** Narration sounds consistent, fits each scene without
clipping, and leaves the complete video within its runtime budget.

### 4. Cut demos around the result

Show enough setup to explain the action, meaningful progress, and a readable
result. Remove waiting and repetition; accelerate only where viewers can still
follow. Judge the excerpt at delivery size and speed.

Preserve the full recording and aspect ratio unless a deliberate crop is wanted.
Introduce the name, author, and description beside the recording, then expand it
smoothly to full screen while playback continues. A 2.5-second introduction and
0.9-second expansion are a useful starting point. Hold final outputs long enough
to understand them.

**Success criteria:** Every excerpt supports its spoken point without hiding
content or rushing past the useful result.

### 5. Animate to the measured narration

Give Unfold the meaning, exact labels, palette, canvas size, frame rate, duration,
reveal timestamps, and final hold. Request silent output. For explanations, build
a stable diagram that reveals concepts in spoken order. Check a short prototype
before rendering the full sequence.

Retain editable source and dependencies. Make narrow text, alignment, and timing
changes there instead of regenerating the animation. Recompute cues when speech
changes. Inspect encoded frames at reveals, transitions, and the ending for
collisions, misleading arrows, small text, and blank frames.

**Success criteria:** The animation matches the narration, remains readable,
and holds a complete final composition.

### 6. Assemble and mix

Prepare compatible clips, then generate and save vid's native edit plan. Align
durations to whole frames and account for crossfade overlaps so later narration
does not drift. Extra outgoing footage can compensate for an overlap. Bound audio
padding to the picture's duration without cutting speech.

Mute recording audio only where voiceover replaces it. With continuous narration,
use a steady quiet music bed and a closing fade. Listen to the complete mix,
including the handoff between recorded and synthetic voices.

**Success criteria:** The export has the intended runtime, dimensions, frame
rate, and audio, with aligned transitions and intelligible speech.

### 7. Review and revise the complete video

Generate a contact sheet and scene navigation from the rendered export. Watch
and listen end to end, then inspect transition boundaries and the final seconds
for black flashes, clipped speech, frozen endings, and abrupt cutoffs. Tool
verification cannot establish whether the video looks and sounds right.

Keep one canonical video for feedback, addressed by scene or timestamp. Cache
unchanged scenes and rebuild only affected assets before assembling the full
export. Replace audio without re-encoding video only when visuals and timing
are unchanged and the existing export still matches the project.

Deliver the MP4 as the primary output and present it so the user can watch it
directly, as an inline player or a path to open. Keep review aids, the
storyboard, original assets, animation sources, and rebuild commands with
prerequisites in the project rather than bundling them into an archive. Report
what was actually verified and any viewing or listening checks that still need
the user.

**Success criteria:** The complete video meets the brief and can be revised
without reconstructing the project.
