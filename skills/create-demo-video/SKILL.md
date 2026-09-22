---
name: create-demo-video
description: >-
  Build or revise a narrated demo showcase with vid, aud, and unfold. Use when
  combining recordings, narration, and animation into a reproducible video.
  For a single trim or audio cleanup, use the relevant tool directly.
---

# Create a Demo Video

Deliver a finished MP4 and an editable project. Settle the story and narration
before detailed visual timing, then review one canonical export end to end.

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
- **Stories:** storyboards and speech synthesis. Prefer Gemini 3.1 TTS
  (`gemini-3.1-flash-tts-preview`); audition a short passage to choose the voice.
  Master the resulting speech with aud.

Use FFmpeg/ffprobe for clip preparation and inspection, and small scripts for
repeatable builds. Supply or create music separately from audio mastering.

## Workflow

### 1. Define the story and delivery

Inspect existing scripts, recordings, artwork, and credits. Establish the
audience, takeaway, runtime limit, output format, and destination; ask only for
missing decisions. Use 1080p at 30 fps unless the brief calls for another format.

Start with a hook, a tour of visible results, a short synthesis, and a closing
action. Give each demo one spoken point and footage that proves it. Reuse chosen
branding; otherwise compare a few small layout previews and voice/music samples
before applying a direction throughout.

Keep copy and timeline settings outside rendering code. Use stable scene IDs to
connect footage, narration, and review timestamps. Preserve original assets,
animation source, and generation settings; separate caches from rebuild inputs.

**Success criteria:** Each scene has a purpose and source, with a runtime budget
and selected visual/audio direction.

### 2. Finish narration before timing visuals

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

### 3. Cut demos around the result

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

### 4. Animate to the measured narration

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

### 5. Assemble and mix

Prepare compatible clips, then generate and save vid's native edit plan. Align
durations to whole frames and account for crossfade overlaps so later narration
does not drift. Extra outgoing footage can compensate for an overlap. Bound audio
padding to the picture's duration without cutting speech.

Mute recording audio only where voiceover replaces it. With continuous narration,
use a steady quiet music bed and a closing fade. Listen to the complete mix,
including the handoff between recorded and synthetic voices.

**Success criteria:** The export has the intended runtime, dimensions, frame
rate, and audio, with aligned transitions and intelligible speech.

### 6. Review and revise the complete video

Generate a contact sheet and scene navigation from the rendered export. Watch
and listen end to end, then inspect transition boundaries and the final seconds
for black flashes, clipped speech, frozen endings, and abrupt cutoffs. Tool
verification cannot establish whether the video looks and sounds right.

Keep one canonical video for feedback, addressed by scene or timestamp. Cache
unchanged scenes and rebuild only affected assets before assembling the full
export. Replace audio without re-encoding video only when visuals and timing
are unchanged and the existing export still matches the project.

Deliver the MP4, review aids, editable copy/timeline, original assets, animation
sources, and rebuild commands with prerequisites. Report what was actually
verified and any viewing or listening checks that still need the user.

**Success criteria:** The complete video meets the brief and can be revised
without reconstructing the project.
