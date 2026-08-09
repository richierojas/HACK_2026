export function SoundProfiles() {
  return (
    <section id="sounds" className="sound-section">

      <div className="sound-header">
        <p className="section-tag">SOUND PROFILES</p>

        <h2>Choose Your Cosmic Sound</h2>

        <p>
          The Cosmic SpellSynth can transform its sound using multiple
          instrument profiles and effects.
        </p>
      </div>

      <div className="sound-grid">

        <div className="sound-card">
          <h3>Synth</h3>
          <p>
            A bright electronic sound inspired by retro synthesizers
            and futuristic space music.
          </p>
        </div>

        <div className="sound-card">
          <h3>Guitar</h3>
          <p>
            A powerful electric-style sound designed for heavier
            melodies and energetic performances.
          </p>
        </div>

        <div className="sound-card">
          <h3>Drums</h3>
          <p>
            A powerful percussion profile with hard-hitting beats
            designed to drive the rhythm across the cosmic stage.
          </p>
        </div>

      </div>

      <div className="effects-header">
        <p className="section-tag">EFFECT</p>
        <h2>Alter the Sound</h2>
      </div>

      <div className="effects-grid">

        <div className="effect-card">
          <h3>Vibrato</h3>
          <p>
            Adds a pulsing pitch movement that gives each note
            a more expressive, otherworldly character.
          </p>
        </div>

      </div>

    </section>
  )
}