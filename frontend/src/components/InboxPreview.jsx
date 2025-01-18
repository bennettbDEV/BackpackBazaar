import React, { useState, useEffect } from "react";
import api from "../api";
import { useUser } from '../contexts/UserContext.jsx';
import { retryWithExponentialBackoff } from "../utils/retryWithExponentialBackoff";
import "./styles/InboxPreview.css";

function InboxPreview({ message, onSelectConvo }) {
    const { userData, isLoading } = useUser(); // Access user data from context
    const { content, sender, receiver, related_listing, created_at } = message;
    const [listingDetails, setListingDetails] = useState(null);
    const [loading, setLoading] = useState(false);
    const snippet = content.length > 30 ? content.slice(0, 30) + "..." : content;

    useEffect(() => {
        fetchListingDetails();
    }, []);


    const handleClick = () => {
        const otherUser = sender === userData.id ? receiver : sender;
        onSelectConvo(otherUser);
    };

    const fetchListingDetails = async () => {
        try {
            const response = await retryWithExponentialBackoff(() => api.get(`/api/listings/${related_listing}/`));
            setListingDetails(response.data);
        } catch (error) {
            console.error("Error fetching listing details:", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="inbox-preview" onClick={handleClick}>

            <div className="details">
                {listingDetails ? (
                    <>
                        <img src={listingDetails.image} alt="Listing" width="25" />
                        <h4>{listingDetails.title}</h4>
                        <p className="snippet">{snippet}</p>
                        <span className="timestamp">{new Date(created_at).toLocaleString()}</span>
                    </>
                ) : (
                    <span>Loading listing...</span>
                )}
            </div>
        </div>
    );
}

export default InboxPreview;
