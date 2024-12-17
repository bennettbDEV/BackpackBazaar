import React, { createContext, useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { jwtDecode } from "jwt-decode";
import api from "../api";
import { REFRESH_TOKEN, ACCESS_TOKEN } from "../constants";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [isAuthorized, setIsAuthorized] = useState(false);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    const refreshToken = useCallback(async () => {
        const refresh = localStorage.getItem(REFRESH_TOKEN);
        if (!refresh) {
            logout();
            return;
        }

        try {
            const res = await api.post("/api/token/refresh/", { refresh });
            if (res.status === 200) {
                localStorage.setItem(ACCESS_TOKEN, res.data.access);
                setIsAuthorized(true);
            } else {
                logout();
            }
        } catch (error) {
            console.error("Error refreshing token:", error);
            logout();
        }
    }, []);

    const checkAuth = useCallback(async () => {
        const token = localStorage.getItem(ACCESS_TOKEN);
        if (!token) {
            setIsAuthorized(false);
            setLoading(false);
            return;
        }

        try {
            const decoded = jwtDecode(token);
            const now = Date.now() / 1000;

            if (decoded.exp < now) {
                await refreshToken();
            } else {
                setIsAuthorized(true);
            }
        } catch (error) {
            console.error("Error decoding token:", error);
            logout();
        } finally {
            setLoading(false);
        }
    }, [refreshToken]);

    const logout = useCallback(() => {
        localStorage.removeItem(ACCESS_TOKEN);
        localStorage.removeItem(REFRESH_TOKEN);
        setIsAuthorized(false);
        navigate("/login");
    }, [navigate]);

    useEffect(() => {
        checkAuth();

        const interval = setInterval(() => {
            const token = localStorage.getItem(ACCESS_TOKEN);
            if (token) {
                const decoded = jwtDecode(token);
                const now = Date.now() / 1000;

                // Refresh token proactively before it expires
                if (decoded.exp - now < 60) {
                    refreshToken();
                }
            }
        }, 60000); // Check every 60 seconds

        return () => clearInterval(interval);
    }, [checkAuth, refreshToken]);

    return (
        <AuthContext.Provider value={{ isAuthorized, loading, logout }}>
            {loading ? <div>Loading...</div> : children}
        </AuthContext.Provider>
    );
};
