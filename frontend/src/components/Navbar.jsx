//Navbar.jsx
import React from 'react';
import './styles/Navbar.css';
import api from "../api";
import { useUser } from '../contexts/UserContext.jsx';
import userIcon from '../assets/usericon.png';
import settingsIcon from '../assets/settingsicon.png';
import homeIcon from '../assets/homeicon.png'; // Import the home icon

const Navbar = () => {
  const { userData, isLoading } = useUser(); // Access user data from context
  const userImage = userData?.profile.image
    ? `${api.defaults.baseURL}${userData.profile.image}`
    : userIcon; // Set fallback image if user image is not available

  return (
    <nav className="navbar">
      <div className="navbar-left">
        <a href="/" className="logo">
          <img src={homeIcon}
            //alt="Home" 
            className="home-icon" /> {/* Home Icon */}
          Backpack Bazaar
        </a>
      </div>
      <div className="navbar-center">
        <ul className="nav-links">
          <li>
            <a href="/createlisting">Create Listing</a>
          </li>
          <li>
            <a href="/saved">Saved</a>
          </li>
          <li>
            <a href="/messages">Messages</a>
          </li>
        </ul>
      </div>
      <div className="navbar-right">
        <div className="navbar-end-align">
          <a href="/profile" className="profile-icon">
            <img
              src={userImage}
              //alt="Profile"
              onError={(e) => {
                e.target.src = userIcon;
              }}
            />
          </a>
          <a href="/settings" className="settings">
            <img src={settingsIcon} alt="Settings" />
          </a>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
