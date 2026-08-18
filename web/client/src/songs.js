// Songs for the rhythm game.
//
// The instrument has 8 buttons, and each one plays a degree of whatever scale
// is selected on the Pico - button 1 is the root, button 8 the octave above.
// So a song here is just a list of scale degrees and how long each lasts. That
// also means every song automatically works in whatever key and octave the
// player has dialled in on the KEY menu.
//
// Each entry is [button, beats]. beats are relative, so changing bpm
// re-times the whole song.

function build(name, bpm, phrases, hint) {
  const secondsPerBeat = 60 / bpm
  const notes = []
  let beat = 0

  for (const [button, beats] of phrases) {
    notes.push({ time: +(beat * secondsPerBeat).toFixed(3), button, beats })
    beat += beats
  }

  return {
    name,
    bpm,
    hint,
    notes,
    duration: +(beat * secondsPerBeat).toFixed(3),
  }
}

// ---------------------------------------------------------------------------
// Repeating figures for the electronic track. House music is built out of a
// short phrase looped with variations, which happens to make an excellent
// rhythm chart - you learn the shape once and then ride it.
// Written here rather than transcribed: real records are copyrighted, and a
// pattern in this style is what makes the genre feel like itself anyway.

// Mostly quarter notes. The first version of this was eighths throughout, which
// at 118bpm meant a note every 0.25s - technically playable, actually not.
// Eighths now appear only as occasional pairs, for accent rather than density.
const HOOK_UP = [[1, 1], [3, 1], [5, 1], [8, 1]]
const HOOK_DOWN = [[8, 1], [5, 1], [3, 1], [1, 1]]
const PULSE = [[1, 1], [1, 1], [5, 1], [5, 1]]
const LIFT = [[6, 1], [8, 1], [5, 1], [3, 1]]
const DROP = [[8, 0.5], [8, 0.5], [6, 1], [5, 1], [3, 1]]

// A vi - IV - I - V turnaround, arpeggiated one chord per bar. This progression
// is everywhere in house and dance music; chord progressions are not
// copyrightable, so building on one is fair game - it is transcribing a
// distinctive melody that would not be.
//   vi = degrees 6 8 3   IV = 4 6 8   I = 1 3 5   V = 5 7 2
const CHORD_VI = [[6, 1], [8, 1], [3, 1], [8, 1]]
const CHORD_IV = [[4, 1], [6, 1], [8, 1], [6, 1]]
const CHORD_I = [[1, 1], [3, 1], [5, 1], [3, 1]]
const CHORD_V = [[5, 1], [7, 1], [2, 1], [7, 1]]

const repeat = (phrase, times) => Array.from({ length: times }, () => phrase).flat()

export const SONGS = [
  build('TWINKLE TWINKLE', 100, [
    [1, 1], [1, 1], [5, 1], [5, 1], [6, 1], [6, 1], [5, 2],
    [4, 1], [4, 1], [3, 1], [3, 1], [2, 1], [2, 1], [1, 2],
    [5, 1], [5, 1], [4, 1], [4, 1], [3, 1], [3, 1], [2, 2],
    [5, 1], [5, 1], [4, 1], [4, 1], [3, 1], [3, 1], [2, 2],
    [1, 1], [1, 1], [5, 1], [5, 1], [6, 1], [6, 1], [5, 2],
    [4, 1], [4, 1], [3, 1], [3, 1], [2, 1], [2, 1], [1, 2],
  ], 'the easy one - lots of repeated pairs'),

  build('ODE TO JOY', 112, [
    [3, 1], [3, 1], [4, 1], [5, 1],
    [5, 1], [4, 1], [3, 1], [2, 1],
    [1, 1], [1, 1], [2, 1], [3, 1],
    [3, 1.5], [2, 0.5], [2, 2],
    [3, 1], [3, 1], [4, 1], [5, 1],
    [5, 1], [4, 1], [3, 1], [2, 1],
    [1, 1], [1, 1], [2, 1], [3, 1],
    [2, 1.5], [1, 0.5], [1, 2],
  ], 'steps up and down the scale - good for finding your place'),

  build('NEON CIRCUIT', 104, [
    // intro - just the pulse, so you can find the beat
    ...repeat(PULSE, 2),
    // the hook, stated twice
    ...repeat(HOOK_UP, 2),
    // answer phrase
    ...HOOK_DOWN, ...HOOK_UP,
    // lift into the brighter part of the scale
    ...repeat(LIFT, 2),
    // drop - the busiest bars
    ...repeat(DROP, 2),
    // hook returns
    ...repeat(HOOK_UP, 2),
    ...HOOK_DOWN,
    // outro - back to the pulse and rest on the root
    ...PULSE,
    [1, 4],
  ], 'electronic - one repeating hook, learn it once and ride it'),

  // Daft Punk - Get Lucky. The signature riff follows the four-chord loop
  // Bm - D - F#m - E, which in scale degrees is chords built on 1, 3, 5 and 4.
  // Set the Pico to KEY B / QUALITY MINOR and it sits in the record's own key.
  //
  // One approximation: the real E chord is major (it borrows a G#), and your
  // buttons only play the notes of the selected scale - so that bar comes out
  // minor. Everything else is exact.
  build('GET LUCKY', 116, [
    // main riff - the four-chord loop, arpeggiated
    [1, 1], [3, 1], [5, 1], [3, 1],
    [3, 1], [5, 1], [7, 1], [5, 1],
    [5, 1], [7, 1], [2, 1], [7, 1],
    [4, 1], [6, 1], [8, 1], [6, 1],
    // round again, with the little climb that lifts each bar
    [1, 1], [3, 1], [5, 0.5], [7, 0.5], [5, 1],
    [3, 1], [5, 1], [7, 0.5], [2, 0.5], [7, 1],
    [5, 1], [7, 1], [2, 0.5], [3, 0.5], [2, 1],
    [4, 1], [6, 1], [8, 0.5], [6, 0.5], [4, 1],
    // last time through, landing on the root
    [1, 1], [3, 1], [5, 1], [3, 1],
    [3, 1], [5, 1], [7, 1], [5, 1],
    [5, 1], [7, 1], [2, 1], [7, 1],
    [4, 1], [6, 1], [8, 1], [6, 1],
    [1, 4],
  ], 'daft punk - set the Pico to KEY B / MINOR for the real key'),

  build('MIDNIGHT DRIVE', 100, [
    // vi - IV - I - V, twice through as an intro
    ...CHORD_VI, ...CHORD_IV, ...CHORD_I, ...CHORD_V,
    ...CHORD_VI, ...CHORD_IV, ...CHORD_I, ...CHORD_V,
    // same progression, busier top line
    [6, 0.5], [8, 0.5], [3, 1], [8, 1], [6, 1],
    [4, 0.5], [6, 0.5], [8, 1], [6, 1], [4, 1],
    [1, 0.5], [3, 0.5], [5, 1], [3, 1], [1, 1],
    [5, 0.5], [7, 0.5], [2, 1], [7, 1], [5, 1],
    // land back on the turnaround and rest
    ...CHORD_VI, ...CHORD_IV, ...CHORD_I,
    [1, 4],
  ], 'a classic house turnaround - four chords, round and round'),

  build('MARY HAD A LITTLE LAMB', 108, [
    [3, 1], [2, 1], [1, 1], [2, 1],
    [3, 1], [3, 1], [3, 2],
    [2, 1], [2, 1], [2, 2],
    [3, 1], [5, 1], [5, 2],
    [3, 1], [2, 1], [1, 1], [2, 1],
    [3, 1], [3, 1], [3, 1], [3, 1],
    [2, 1], [2, 1], [3, 1], [2, 1],
    [1, 4],
  ], 'shortest song - a good first try'),
]

// How close a press has to be, in seconds, to count.
// Timing windows, in seconds.
//
// Generous on purpose: presses travel Pico -> bridge -> websocket -> browser,
// adding latency before the game even sees them, and this is meant to be fun
// rather than a reflex test.
//
// early and late are deliberately different. Notes in the busiest song sit
// 0.25s apart in the same lane, so a symmetric 0.26s window would let a late
// press land inside the NEXT note's window too - you would clear the note you
// already missed and then miss the one you actually aimed at. Keeping the late
// window under half that gap means a note is out of reach by the time the next
// one is due, and presses always resolve to what you were aiming at.
export const WINDOWS = {
  perfect: 0.13,   // either side, counts as PERFECT
  early: 0.26,     // how far ahead of the note you may press
  late: 0.15,      // how far behind - must stay under half the closest gap
}

// How long a note takes to travel from the horizon to the hit line.
export const APPROACH_SECONDS = 2.2

// Silence before the first note, so you can see what is coming.
export const LEAD_IN_SECONDS = 3
