import { Link } from 'react-router'

export function Navbar() {
  return (
    <nav className="navbar">

      <Link to="/" className="nav-logo">
        COSMIC SPELLSYNTH
      </Link>

      <div className="nav-links">
        <Link to="/instrument">Instrument</Link>
        <Link to="/sounds">Sounds</Link>
        <Link to="/band">Meet the Band</Link>
        <Link to="/music">Setlist</Link>
      </div>

    </nav>
  )
}