export function Band() {
  return (
    <section id="band" className="band-section">

      <div className="band-header">
        <p className="section-tag">The Cosmic Coven</p>

        <h2>Artemis Audio</h2>

        <p>
          Cosmic SpellSynth was created by a team combining software,
          electronics, fabrication, and live performance.
        </p>
      </div>

      <div className="band-photo">
        <div className="band-photo-placeholder">
          Band Photo Coming Soon
        </div>
      </div>

      <div className="member-grid">

        <div className="member-card">
          <h3>Ryland</h3>

          <p className="member-role">
            CSE Major • Bay Area, California
          </p>

          <p>
            Ryland is the lead performer of the Cosmic SpellSynth and is
            responsible for bringing the instrument to life on stage. He also
            handled much of the project's backend development, helping connect
            the instrument's hardware, software, and musical controls.
          </p>
        </div>

        <div className="member-card">
          <h3>Shea</h3>

          <p className="member-role">
            Electrical Engineering Major • Sherman Oaks, California
          </p>

          <p>
            Shea focused on the hardware side of the Cosmic SpellSynth,
            designing and assembling the circuits that power the instrument.
            She also contributed to the CAD design and fabrication of the
            instrument's physical enclosure.
          </p>
        </div>

        <div className="member-card">
          <h3>Richie</h3>

          <p className="member-role">
            Computer Science Major • Bellflower, California
          </p>

          <p>
            Richie handled the frontend development for the Cosmic SpellSynth
            website and created the live performance visualizer that reacts to
            the instrument. He also contributed to the CAD design and helped
            integrate the instrument with the website through USB and WebSocket
            communication.
          </p>
        </div>

      </div>

    </section>
  )
}