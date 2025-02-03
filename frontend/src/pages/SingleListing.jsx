// SingleListing.jsx
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
    const [isBlocked, setIsBlocked] = useState(null); // Local block state
    const [imageError, setImageError] = useState(false); // Track image loading error
    const [formData, setFormData] = useState({ content: "" });

    const fallbackImage = "/fallback-author-image.png";

    useEffect(() => {
        const fetchListingAndAuthor = async () => {
            try {
                // Fetch the listing data
                const listingResponse = await api.get(`/api/listings/${listingId}/`);
                const listingData = listingResponse.data;
                setListing(listingData);

                // Fetch the author data using the listing's author_id
                const authorResponse = await api.get(`/api/users/${listingData.author_id}/`);
                const authorData = authorResponse.data;
                setAuthor(authorData);

                // Fetch block status
                const blockStatusResponse = await api.get(
                    `/api/users/${listingData.author_id}/is_user_blocked/`
                );

                // Determine block status
                setIsBlocked(blockStatusResponse.data.detail == "User is blocked." || false);
            } catch (error) {
                console.error("Error fetching listing or author data:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchListingAndAuthor();
    }, [listingId]);

    const toggleBlockUser = async () => {
        if (!author) return;

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

    const handleFormChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const handleFormSubmit = async (e) => {
        e.preventDefault();
        if (!author) return;

        try {
            await api.post("/api/messages/", {
                receiver: author.id,
                related_listing: listing.id,
                content: formData.content,
            });
            setFormData({ content: "" });
            alert("Message sent successfully");
        } catch (error) {
            console.error("Error sending message:", error);
            alert("Failed to send message.");
        }
    };

    return (
        <div>
            <NavBar />
            <div className="single-listing-page">
                <h1>Listing Details</h1>
                <div className="content-wrapper">
                    <div className="listing-section">
                    <Listing listing={listing} useFullDesc={true} />
                    </div>

                    {author ? (
                        <div className="author-details">
                            <h3>About the Seller</h3>
                            <div className="author-image">
                                <img
                                    src={
                                        imageError || !author.profile.image
                                            ? fallbackImage
                                            : `${api.defaults.baseURL}${author.profile.image}`
                                    }
                                    alt={author.username || "Author"}
                                    style={{ width: "150px", height: "auto", borderRadius: "50%" }}
                                    onError={handleImageError}
                                />
                            </div>
                            <p>
                                <strong>Name:</strong> {author.username} <br></br>
                                <strong>Location:</strong> {author.profile.location || "Not given"}
                            </p>

                            {/* Message Form */}
                            <div className="message-form">
                                <h2>Send a Message</h2>
                                <form onSubmit={handleFormSubmit}>
                                    <div>
                                        <label
                                            htmlFor="content"
                                            style={{ display: "block", marginBottom: "5px" }}
                                        >
                                            Message Content:
                                        </label>
                                        <textarea className="message-form-textarea"
                                            id="content"
                                            name="content"
                                            value={formData.content}
                                            onChange={handleFormChange}
                                            style={{ width: "95%", padding: "8px" }}
                                            rows="5"
                                            required
                                        ></textarea>
                                    </div>

                                    <button type="submit" classname="message-button">Send Message</button>
                                </form>

                                <div className="button-wrapper">
                                    <button
                                        className={`block-button ${isBlocked ? "blocked" : ""}`}
                                        onClick={toggleBlockUser}
                                    >
                                        {isBlocked ? "Unblock User" : "Block User"}
                                    </button>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <p>Author details not available.</p>
                    )}
                </div>
            </div>
        </div>
    );
};

export default SingleListing;
