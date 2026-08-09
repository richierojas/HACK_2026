export function Band() {
  return (
    <section className="band-section">
      <div className="band-header">
        <p className="section-tag">THE BAND</p>
        <h2>Meet Artemis Audio</h2>
        <p>
          The team behind Cosmic SpellSynth, combining software,
          circuits, fabrication, and live performance.
        </p>
      </div>

      <div className="band-grid">
        <div className="member-card">
          <img
            src="/images/ryland.jpg"
            alt="Ryland"
            className="member-photo"
          />
          <h3>Ryland</h3>
          <h4>CSE Major · Bay Area, California</h4>
          <p>
            Ryland is the lead performer of the Cosmic SpellSynth and is
            responsible for bringing the instrument to life on stage. He also
            handled much of the project’s backend development, helping connect
            the instrument’s hardware, software, and musical controls.
          </p>
        </div>

        <div className="member-card">
          <img
            src="/images/shea.jpg"
            alt="Shea"
            className="member-photo"
          />
          <h3>Shea</h3>
          <h4>Electrical Engineering Major · Sherman Oaks, California</h4>
          <p>
            Shea focused on the hardware side of the Cosmic SpellSynth,
            designing and assembling the circuits that power the instrument.
            She also contributed to the CAD design and fabrication of the
            instrument’s physical enclosure.
          </p>
        </div>

        <div className="member-card">
          <img
            src="/images/richie.jpg"
            alt="Richie"
            className="member-photo"
          />
          <h3>Richie</h3>
          <h4>Computer Science Major · Bellflower, California</h4>
          <p>
            Richie handled the frontend development for the Cosmic SpellSynth
            website and created the live performance visualizer that reacts to
            the instrument. He also contributed to the CAD design and helped
            integrate the instrument with the website through USB and WebSocket
            communication.
          </p>
        </div>
      </div>

      <div className="group-photo-section">
        <h3 className="group-photo-title">Artemis Audio</h3>
        <img
          src="/images/group-photo.jpg"
          alt="Artemis Audio group photo"
          className="group-photo"
        />
      </div>
    </section>
  )
}