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

Call the smart tool that owns each step: Stories for the storyboard and
narration, Showrun for recordings, aud for mastering, Unfold for animation, and
vid for cutting, assembly, and render verification. Read a tool's help before
its first use. Do not reimplement a tool's work with hand-written FFmpeg
commands or scripts; use FFmpeg/ffprobe directly only for clip preparation and
inspection the tools do not cover, and small scripts only to chain tool calls
into repeatable builds.

## Workflow

### 1. Create the storyboard with Stories

Inspect existing scripts, recordings, artwork, and credits. Establish the
audience, takeaway, runtime limit, and destination; ask only for missing
decisions. Use 1080p at 30 fps unless the brief calls for another format.

Start with a hook, a tour of visible results, a short synthesis, and a closing
action. Give each demo one spoken point and footage that proves it. Reuse chosen
branding; otherwise compare a few small layout previews and voice samples
before applying a direction throughout.

Build the storyboard in Stories. Use `create-storyboard` to import a script the
user already has, or `generate-storyboard` to develop one from the brief. Set
`explore` only when the user asks to compare directions. Each panel is one
scene:

- `id`: stable scene ID.
- `action`: the point the scene makes.
- `visual`: what is on screen: a recording excerpt with file and in/out times,
  an Unfold animation such as an opening title or concept diagram, a title
  card, or a combination.
- `narration`: the spoken line.
- `notes` (optional): on-screen text, such as titles, animation labels, and
  subtitles.
- `production_requirements` (optional): recordings or animations still to make.
- `asset_id` (optional): a still frame from the recording.

A direction holds up to eight panels; for a longer video, make each panel a
section and list its scenes in `visual` and `narration`. Share the storyboard
through the Stories dashboard so the user can comment or edit, or leave it to
the agent. Either way it is the source of truth for every later step. Apply
changes with `revise-storyboard` and rebuild from the latest revision.

Use the scene IDs to connect on-screen sources, narration, and review
timestamps. Preserve original assets, animation source, and generation
settings; separate caches from rebuild inputs.

**Success criteria:** Each scene has a purpose, an on-screen source, and a
narration line, and the total fits the runtime budget.

### 2. Get the recordings

Use recordings the user supplies, or make recordings of what the user wants to
show. Long, unedited captures are fine; step 4 cuts them down. Make recordings
with real screen capture of the thing running, using Showrun for a web app. Seed realistic demo data first so screens do not start empty. Only
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

Cut with vid. Show enough setup to explain the action, meaningful progress, and a readable
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

Mute recording audio only where voiceover replaces it. Listen to the complete
mix, including the handoff between recorded and synthetic voices.

**Success criteria:** The export has the intended runtime, dimensions, frame
rate, and audio, with aligned transitions and intelligible speech.

### 7. Review and revise the complete video

Verify the render with vid, then generate a contact sheet and scene navigation
from the export. Watch
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
