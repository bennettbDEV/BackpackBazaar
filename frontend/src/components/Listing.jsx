import React, { useState } from "react";
import api from "../api";
import { Link } from "react-router-dom";
import "./styles/Listing.css";

function Listing({ listing, additionalAction }) {
    const [imageError, setImageError] = useState(false); // Track if the image fails to load
    const [likes, setLikes] = useState(listing.likes || 0);
    const [dislikes, setDislikes] = useState(listing.dislikes || 0);
    const formattedDate = new Date(listing.created_at).toLocaleDateString("en-US");

    // Image URL
    const imageUrl = listing.image ? `${api.defaults.baseURL}${listing.image}` : null;
    const fallbackImage = "/default-image.jpg"; // Fallback image URL

    const handleImageError = () => {
        setImageError(true);
    };

    const handleLike = () => {
        setLikes((prevLikes) => prevLikes + 1);
        api.post(`/api/listings/${listing.id}/like_listing/`).catch(console.error);
    };

    const handleDislike = () => {
        setDislikes((prevDislikes) => prevDislikes + 1);
        api.post(`/api/listings/${listing.id}/dislike_listing/`).catch(console.error);
    };

    return (
        <div className="listing-container">
            <Link to={`/listings/${listing.id}`} className="listing-link">
                <h2 className="listing-title">{listing.title}</h2>
                <p className="listing-condition">Condition: {listing.condition}</p>
                <p className="listing-description">Description: {listing.description}</p>
                <p className="listing-price">Price: ${listing.price}</p>

                <div className="listing-image">
                    {imageUrl && !imageError ? (
                        <img
                            src={imageUrl}
                            alt={listing.title}
                            className="listing-image-file"
                            onError={handleImageError} // Trigger fallback on error
                        />
                    ) : (
                        <img
                            src={fallbackImage} // Fallback image
                            alt="Fallback"
                            className="listing-image-file"
                        />
                    )}
                </div>
                <p className="listing-date">Posted on: {formattedDate}</p>
                <div className="listing-tags">
                    <strong>Tags: </strong>
                    {listing.tags.map((tag, index) => (
                        <span key={index} className="listing-tag">{tag}</span>
                    ))}
                </div>
            </Link>

            <div className="listing-feedback">
                <button className="react-button" onClick={handleLike}>
                    👍 {likes}
                </button>
                <button className="react-button" onClick={handleDislike}>
                    👎 {dislikes}
                </button>
            </div>

            {additionalAction && <div className="listing-action">{additionalAction}</div>}
        </div>
    );
}

export default Listing;