//SingleListing.jsx
import React, { useEffect, useState } from "react";
import api from "../api";
import { useParams } from "react-router-dom";
import Listing from "../components/Listing";
import NavBar from "../components/Navbar.jsx";
import "./styles/SingleListing.css";

const SingleListing = () => {
    const { listingId } = useParams(); // Extract listing ID from URL params
    const [listing, setListing] = useState(null);
    const [author, setAuthor] = useState(null);
    const [loading, setLoading] = useState(true);
    const [isBlocked, setIsBlocked] = useState(false); // Local block state
    const [imageError, setImageError] = useState(false); // Track image loading error

    const fallbackImage = "/fallback-author-image.png"; 

    useEffect(() => {
        const fetchListingAndAuthor = async () => {
            try {
                // Fetch the listing data
                const listingResponse = await api.get(`/api/listings/${listingId}/`);
                setListing(listingResponse.data);
    
                // Fetch the author data using the listing's author_id
                const authorResponse = await api.get(`/api/users/${listingResponse.data.author_id}/`);
                setAuthor(authorResponse.data);
    
                // Fetch block status
                const blockStatusResponse = await api.get(
                    `/api/users/${listingResponse.data.author_id}/is_user_blocked/`
                );
                
                // Determine block status from the "detail" field
                const isBlockedStatus = blockStatusResponse.data.detail === "User is blocked.";
                setIsBlocked(isBlockedStatus);
            } catch (error) {
                console.error("Error fetching listing or author data:", error);
            } finally {
                setLoading(false);
            }
        };
    
        fetchListingAndAuthor();
    }, [listingId]);

    //Const: block user logic
    const toggleBlockUser = async () => {
        try {
            if (isBlocked) {
                await api.post(`/api/users/${author.id}/unblock_user/`);
                setIsBlocked(false); // Optimistically update the state
                alert("User unblocked successfully!");
            } else {
                await api.post(`/api/users/${author.id}/block_user/`);
                setIsBlocked(true); // Optimistically update the state
                alert("User blocked successfully!");
            }
        } catch (error) {
            console.error("Error toggling block status:", error);
            alert("An error occurred while trying to block/unblock the user.");
        }
    };

    const handleImageError = () => {
        setImageError(true);
    };

    if (loading) {
        return <p>Loading...</p>;
    }

    if (!listing) {
        return <p>Listing not found!</p>;
    }

    return (
        <div>
            <NavBar />

            <div className="single-listing-page">
                <h1>Listing Details</h1>
                <Listing listing={listing} />

                {author ? (
                    <div className="author-details">
                        <h3>About the Seller</h3>
                        <div className="author-image">
                            <img
                                src={imageError || !author.image ? fallbackImage : `${api.defaults.baseURL}${author.image}`}
                                alt={author.username || "Author"}
                                style={{ width: "150px", height: "auto", borderRadius: "50%" }}
                                onError={handleImageError} // Trigger fallback on error
                            />
                        </div>
                        <p><strong>Name:</strong> {author.username}</p>
                        <p><strong>Location:</strong> {author.location || "Not given"}</p>
                        <button
                            className={`block-button ${isBlocked ? "blocked" : ""}`}
                            onClick={toggleBlockUser}
                        >
                            {isBlocked ? "Unblock User" : "Block User"}
                        </button>
                    </div>
                ) : (
                    <p>Author details not available.</p>
                )}
            </div>
        </div>
    );
};

export default SingleListing;
