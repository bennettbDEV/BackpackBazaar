// User.jsx
import React from "react";
import api from "../api";
import "./styles/User.css";

function User({ user, onUnblock }) {
    const fallbackImage = "/fallback-author-image.png";
    const imageUrl = user.image ? user.image : fallbackImage;
    const location = user.location ? user.location : "No location provided"

    return (
        <div className="user-container">
            <div className="user-avatar">
                <img
                    src={imageUrl}
                    alt={`${user.username}'s avatar`}
                    className="user-avatar-image"
                    style={{ width: "200px", height: "200px" }}
                />
            </div>
            <div className="user-details">
                <h3 className="user-username">{user.username}</h3>
                <p className="user-location">Location: {location}</p>
            </div>
            <button
                className="unblock-button"
                onClick={() => onUnblock(user.id)}
            >
                Unblock
            </button>
        </div>
    );
}

export default User;
