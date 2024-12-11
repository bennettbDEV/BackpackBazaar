import NavBar from "../components/Navbar.jsx";
import ListingFeed from "../components/ListingFeed";
import { jwtDecode } from "jwt-decode";
import { useState, useEffect } from "react";
import api from "../api";
import LinkedButton from "../components/LinkedButton.jsx";
import "./styles/Profile.css";
import { ACCESS_TOKEN } from "../constants";
import testImg from "../assets/usericon.png";
import { retryWithExponentialBackoff } from "../utils/retryWithExponentialBackoff";

function Profile() {
    const [listings, setListings] = useState([]);
    const [nextPage, setNextPage] = useState(null);
    const [previousPage, setPreviousPage] = useState(null);
    const [loading, setLoading] = useState(false);
    const [userId, setUserId] = useState(null);
    const [userData, setUserData] = useState(null);

    const imageUrl = userData?.image ? `${api.defaults.baseURL}${userData.image}` : testImg;

    useEffect(() => {
        const token = localStorage.getItem(ACCESS_TOKEN);
        if (token) {
            try {
                const decodedToken = jwtDecode(token);
                setUserId(decodedToken.user_id);
            } catch (err) {
                console.error("Error decoding JWT:", err);
            }
        }
    }, []);

    useEffect(() => {
        if (userId) {
            fetchUserData(userId);
            getListings(`/api/listings/?author_id=${userId}`);
        }
    }, [userId]);

    const fetchUserData = async (userId) => {
        try {
            const response = await retryWithExponentialBackoff(() =>
                api.get(`/api/users/${userId}/`));
            setUserData(response.data);
        } catch (err) {
            console.error("Error fetching user data:", err);
        } finally {
            setIsLoading(false);
        }
    };

    const getListings = (url) => {
        setLoading(true);
        retryWithExponentialBackoff(() => api.get(url))
            .then((response) => response.data)
            .then((data) => {
                console.log("API Response:", data);
                setListings(data.results);
                setNextPage(data.links?.next || null);
                setPreviousPage(data.links?.previous || null);
            })
            .catch((err) => {
                console.error("Error fetching listings:", err);
            })
            .finally(() => {
                setLoading(false);
            });
    };

    const handleLogout = () => {
        localStorage.clear()
        window.location.reload();
    };

    const handleDeleteListing = async (listingId) => {
        try {
            // Send a DELETE request to the backend
            await api.delete(`/api/listings/${listingId}/`);
            // Update the UI by filtering out the removed listing
            setListings((prevListings) =>
                prevListings.filter((listing) => listing.id !== listingId)
            );
        } catch (err) {
            console.error("Error deleting listing:", err);
        }
    };

    return (
        <div>
            <NavBar />
            <div className="profile-container">
                <h1>Profile Page</h1>
                {userData ? (
                    <>
                        <p>Username: {userData.username}</p>
                        <p>Location: {userData.location || "Not given"}</p>
                        <img src={imageUrl} width="150" alt="Profile" />
                        <br></br>
                        <button onClick={handleLogout}>Logout</button>
                        <br></br>
                    </>
                ) : (
                    <p>Loading user data...</p>
                )}

                <h2>Your Listings:</h2>
                {loading ? (
                    <p>Loading...</p>
                ) : (
                    <>
                        <ListingFeed
                            listings={listings}
                            actionType="remove"
                            onAction={(id) => handleDeleteListing(id)} />

                        <div className="pagination-controls">
                            <LinkedButton
                                url={previousPage}
                                onClick={getListings}
                                label="Previous"
                            />

                            <LinkedButton
                                url={nextPage}
                                onClick={getListings}
                                label="Next"
                            />
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}

export default Profile;
