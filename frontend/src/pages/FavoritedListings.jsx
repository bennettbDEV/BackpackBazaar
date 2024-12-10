import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom"; // Import Link for navigation
import NavBar from "../components/Navbar";
import ListingFeed from "../components/ListingFeed";
import api from "../api";
import "./styles/FavoriteListings.css";

function FavoritedListings() {
    const [listings, setListings] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchFavoriteListings();
    }, []);

    // Function: Fetch all favorite listings
    const fetchFavoriteListings = async () => {
        setLoading(true);
        try {
            const response = await api.get("/api/listings/list_favorite_listings/");
            setListings(response.data.favorites || []);
        } catch (err) {
            console.error("Error fetching favorite listings:", err);
        } finally {
            setLoading(false);
        }
    };

    // Function: Remove a listing from favorites
    const handleRemoveFavorite = async (listingId) => {
        try {
            // Send a DELETE request to the backend
            await api.delete(`/api/listings/${listingId}/remove_favorite_listing/`);
            // Update the UI by filtering out the removed listing
            setListings((prevListings) =>
                prevListings.filter((listing) => listing.id !== listingId)
            );
        } catch (err) {
            console.error("Error removing favorite listing:", err);
        }
    };

    return (
        <>
            <NavBar />
            <div className="saved-listings-container">
                <h1>Your Saved Listings</h1>
                {loading ? (
                    <p>Loading...</p>
                ) : listings.length === 0 ? (
                    <div className="empty-listings-message">
                        <p>You don't have any saved listings yet.</p>
                        <p>Browse the marketplace to save your favorite items!</p>
                    </div>
                ) : (
                    <ListingFeed
                        listings={listings}
                        actionType="remove"
                        onAction={(id) => handleRemoveFavorite(id)}
                    />
                )}
            </div>
        </>
    );
}

export default FavoritedListings;