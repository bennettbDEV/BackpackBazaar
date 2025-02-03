import React, { useState } from "react";
import api from "../api";
import { Link } from "react-router-dom";
import "./styles/Listing.css";


const conditionMapping = {
    "FN": "Factory New",
    "MW": "Minimal Wear",
    "FR": "Fair",
    "WW": "Well Worn",
    "RD": "Refurbished"
};

function Listing({ listing, additionalAction, useFullDesc }) {
    const [imageError, setImageError] = useState(false); // Track if the image fails to load
    const [likes, setLikes] = useState(listing.likes || 0);
    const [dislikes, setDislikes] = useState(listing.dislikes || 0);
    const formattedDate = new Date(listing.created_at).toLocaleDateString("en-US");
    const description_snippet = listing.description.length > 59 ? listing.description.slice(0, 59) + "..." : listing.description;

    // Image URL
    const imageUrl = listing.image ? listing.image : null;
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

    const fullCondition = conditionMapping[listing.condition] || listing.condition;

    return (
        <div className="listing-container">
            <Link to={`/listings/${listing.id}`} className="listing-link">
                <h2 className="listing-title">{listing.title}</h2>
                <p className="listing-condition">Condition: {fullCondition}</p>
                <p className="listing-description">Description: {useFullDesc ? listing.description : description_snippet}</p>
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
                    {listing.tags_out.map((tag, index) => (
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