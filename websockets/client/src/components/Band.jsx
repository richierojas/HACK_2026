import { useState } from 'react'

const members = [
  {
    id: 'ryland',
    name: 'Ryland',
    photo: '/images/ryland.jpg',
    subtitle: 'CSE Major · Bay Area, California',
    description:
      'Ryland is the lead performer of the Cosmic SpellSynth and is responsible for bringing the instrument to life on stage. He also handled much of the project’s backend development, helping connect the instrument’s hardware, software, and musical controls.',
  },
  {
    id: 'shea',
    name: 'Shea',
    photo: '/images/shea.jpg',
    subtitle: 'Electrical Engineering Major · Sherman Oaks, California',
    description:
      'Shea focused on the hardware side of the Cosmic SpellSynth, designing and assembling the circuits that power the instrument. She also contributed to the CAD design and fabrication of the instrument’s physical enclosure.',
  },
  {
    id: 'richie',
    name: 'Richie',
    photo: '/images/richie.jpg',
    subtitle: 'Computer Science Major · Bellflower, California',
    description:
      'Richie handled the frontend development for the Cosmic SpellSynth website and created the live performance visualizer that reacts to the instrument. He also contributed to the CAD design and helped integrate the instrument with the website through USB and WebSocket communication.',
  },
]

export function Band() {
  const [selectedMember, setSelectedMember] = useState(null)

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

        {members.map((member) => (
          <div
            key={member.id}
            className="member-card"
            onClick={() => setSelectedMember(member)}
          >
            <img
              src={member.photo}
              alt={member.name}
              className="member-photo"
            />

            <h3>{member.name}</h3>

            <h4>{member.subtitle}</h4>

            <p>{member.description}</p>
          </div>
        ))}

      </div>

      <div className="group-photo-section">
        <h3 className="group-photo-title">
          Artemis Audio
        </h3>

        <img
          src="/images/group-photo.jpg"
          alt="Artemis Audio group photo"
          className="group-photo"
        />
      </div>

      {selectedMember && (
        <div
          className="profile-overlay"
          onClick={() => setSelectedMember(null)}
        >
          <div
            className="profile-modal"
            onClick={(event) => event.stopPropagation()}
          >

            <button
              className="profile-close"
              onClick={() => setSelectedMember(null)}
            >
              ×
            </button>

            <img
              src={selectedMember.photo}
              alt={selectedMember.name}
              className="profile-modal-photo"
            />

            <h2>{selectedMember.name}</h2>

            <h4>{selectedMember.subtitle}</h4>

            <p>{selectedMember.description}</p>

          </div>
        </div>
      )}

    </section>
  )
}