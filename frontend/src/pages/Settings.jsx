import React, { useState, useEffect, useContext } from "react";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "../constants";
import { useNavigate } from "react-router-dom";
import { useUser } from '../contexts/UserContext.jsx';
import NavBar from "../components/Navbar.jsx";
import UserFeed from "../components/UserFeed";
import SettingsForm from "../components/SettingsForm";
import api from "../api";
import { retryWithExponentialBackoff } from "../utils/retryWithExponentialBackoff";
import { ThemeContext } from '../contexts/ThemeProvider';
import "./styles/Settings.css";

function Settings() {
    const { theme, toggleTheme } = useContext(ThemeContext);
    const { userData, isLoading } = useUser();
    const [newUserData, setNewUserData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [blockedUsers, setBlocked] = useState([]);
    

    const navigate = useNavigate();
    const userId = userData ? userData.id : -1;

    useEffect(() => {
        fetchBlockedUsers();
    }, []);

    const handleLogout = () => {
        localStorage.removeItem(ACCESS_TOKEN);
        localStorage.removeItem(REFRESH_TOKEN);
        navigate("/login", { replace: true });
    };

    // Function: Fetch all blocked users
    const fetchBlockedUsers = async () => {
        setLoading(true);
        try {
            const response = await retryWithExponentialBackoff(() =>
                api.get("/api/users/list_blocked_users/"));
            setBlocked(response.data.blocked || []);
        } catch (err) {
            console.error("Error fetching blocked users:", err);
        } finally {
            setLoading(false);
        }
    };

    // Function: Remove a user from blockedUsers
    const handleUnblock = async (userId) => {
        try {
            // Send a DELETE request to the backend
            await api.post(`/api/users/${userId}/unblock_user/`);
            // Update the UI by filtering out the unblocked user
            setBlocked((prevBlocked) =>
                prevBlocked.filter((user) => user.id !== userId)
            );
        } catch (err) {
            console.error("Error unblocking user:", err);
        }
    };

    const handleDeleteAccount = async () => {
        const confirmDelete = window.confirm(
            "Are you sure you want to delete your account? This action cannot be undone."
        );
        if (confirmDelete) {
            try {
                await api.delete(`/api/users/${userId}/`);
                localStorage.clear();
                navigate("/login", { replace: true });
            } catch (err) {
                console.error("Error deleting account:", err);
                alert("An error occurred while trying to delete your account. Please try again.");
            }
        }
    };

    return (
        <>
            <NavBar />
            <div className="settings-page">
                <h2>Settings</h2>
                <button className={`theme-button ${theme === 'dark' ? 'dark-mode' : 'light-mode'}`}
                    onClick={toggleTheme}>
                    {theme === 'light' ? 'Enable Dark Mode' : 'Enable Light Mode'}
                </button>

                <button className="logout-button" onClick={handleLogout}>Logout</button>
                
                <br></br>
                <h3>Blocked users:</h3>
                <UserFeed users={blockedUsers} onUnblock={handleUnblock} />
                <h3>Edit & Delete:</h3>
                <div className="editing-form-container">
                    {userData ? (
                        <SettingsForm userData={userData} userId={userId} />
                    ) : (
                        <p>Error loading user data.</p>
                    )}
                </div>
                <br></br>
                <button className="delete-account-button"
                    onClick={handleDeleteAccount}>Delete Account</button>
            </div>

        </>
    );
}

export default Settings;