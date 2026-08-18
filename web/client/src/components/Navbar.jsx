import { Link } from 'react-router'

export function Navbar() {
  return (
    <nav className="navbar">

      <Link to="/" className="nav-brand">

        <div className="nav-symbol-wrap">
          <img
            src="/images/artemis-logo.png"
            alt=""
            className="nav-logo-image"
          />
        </div>

        <div className="nav-brand-text">
          <span className="artemis-name">ARTEMIS</span>
          <span className="audio-name">AUDIO</span>
        </div>

      </Link>

      <div className="nav-links">
        <Link to="/instrument">Instrument</Link>
        <Link to="/sounds">Sounds</Link>
        <Link to="/band">The Band</Link>
        <Link to="/music">Setlist</Link>
        <Link to="/live">Live</Link>
        <Link to="/play" className="nav-play">Star Runner</Link>
      </div>

    </nav>
  )
}