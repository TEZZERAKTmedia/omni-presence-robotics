// components/Navbar.jsx
import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Navbar.css';

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();

  const handleLinkClick = () => setIsOpen(false); // close on nav click

  return (
    <>
      <div className="navbar-toggle" onClick={() => setIsOpen(!isOpen)}>
        <div className={`bar ${isOpen ? 'open' : ''}`}></div>
        <div className={`bar ${isOpen ? 'open' : ''}`}></div>
        <div className={`bar ${isOpen ? 'open' : ''}`}></div>
      </div>

      <nav className={`futuristic-navbar ${isOpen ? 'open' : ''}`}>
        <div className="logo">🤖 OmniPresence</div>
        <ul className="nav-links">
          <li className={location.pathname === '/' ? 'active' : ''}>
            <Link to="/" onClick={handleLinkClick}>Home</Link>
          </li>
          <li className={location.pathname === '/editor' ? 'active' : ''}>
            <Link to="/Mapping" onClick={handleLinkClick}>Environment Mapping</Link>
          </li>
          <li className={location.pathname === '/editor' ? 'active' : ''}>
            <Link to="/training" onClick={handleLinkClick}>Training</Link>
          </li>


        </ul>
      </nav>
    </>
  );
}
