import React, { createContext, useState, useEffect, useContext } from "react";
import api from "../api";
import { jwtDecode } from "jwt-decode";
import { retryWithExponentialBackoff } from "../utils/retryWithExponentialBackoff";
import { ACCESS_TOKEN } from "../constants";

const UserContext = createContext();

export const UserProvider = ({ children }) => {
    const [userData, setUserData] = useState(null); // Holds user data
    const [isLoading, setIsLoading] = useState(true); // Loading state for user fetch

    useEffect(() => {
        const token = localStorage.getItem(ACCESS_TOKEN);
        if (token) {
            try {
                const decodedToken = jwtDecode(token);
                fetchUserData(decodedToken.user_id);
            } catch (err) {
                console.error("Error decoding token:", err);
                setIsLoading(false);
            }
        } else {
            setIsLoading(false);
        }
    }, []);

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

    const loginUser = (token) => {
        localStorage.setItem(ACCESS_TOKEN, token);
        const decodedToken = jwtDecode(token);
        fetchUserData(decodedToken.user_id);
    };

    const logoutUser = () => {
        localStorage.removeItem(ACCESS_TOKEN);
        localStorage.removeItem(REFRESH_TOKEN);
        setUserData(null);
    };

    return (
        <UserContext.Provider value={{ userData, isLoading, loginUser, logoutUser }}>
            {children}
        </UserContext.Provider>
    );
};

export const useUser = () => {
    return useContext(UserContext);
};