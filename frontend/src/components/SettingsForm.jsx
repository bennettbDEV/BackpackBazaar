// SettingsForm.jsx
import React, { useState } from "react";
import api from "../api";
import { retryWithExponentialBackoff } from "../utils/retryWithExponentialBackoff";
import "./styles/SettingsForm.css";

function SettingsForm({ userData, userId }) {
    const [formData, setFormData] = useState({
        username: userData?.username || "",
        email: userData?.email || "",
        location: userData?.profile.location || "",
        image: null,
        password: "",
        confirmPassword: "",
    });
    const [imagePreview, setImagePreview] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const handleImageUpload = (e) => {
        const file = e.target.files[0];
        if (file) {
            setFormData((prev) => ({ ...prev, image: file }));
            const reader = new FileReader();
            reader.onload = () => {
                setImagePreview(reader.result);
            };
            reader.readAsDataURL(file);
        }
    };

    const isFormEmpty = () => {
        const { username, email, location, image, password, confirmPassword } = formData;
        return (
            !username.trim() &&
            !email.trim() &&
            !location.trim() &&
            !image &&
            !password.trim() &&
            !confirmPassword.trim()
        );
    };

    const handleSaveChanges = async (e) => {
        e.preventDefault();

        if (isFormEmpty()) {
            alert("Please fill out at least one field to update.");
            return;
        }

        if (formData.password && formData.password !== formData.confirmPassword) {
            alert("Passwords do not match!");
            return;
        }

        try {
            setLoading(true);
            const updateData = new FormData();
            if (formData.username.trim()) updateData.append("username", formData.username);
            if (formData.email.trim()) updateData.append("email", formData.email);
            if (formData.location.trim()) updateData.append("location", formData.location);
            if (formData.image) updateData.append("image", formData.image);
            if (formData.password.trim()) updateData.append("password", formData.password);

            const response = await api.patch(`/api/users/${userId}/`, updateData, {
                headers: { "Content-Type": "multipart/form-data" },
            });

            alert("Profile updated successfully!");
            console.log("Response:", response.data);
        } catch (error) {
            console.error("Error updating profile:", error.response || error.message);
            alert("Failed to update profile. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <form className="settings-form" onSubmit={handleSaveChanges}>
            <h4>Edit Profile</h4>
            New Username
            <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                placeholder="Username..."
            />
            New Email
            <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="Email..."
            />
            New Location
            <input
                type="text"
                name="location"
                value={formData.location}
                onChange={handleInputChange}
                placeholder="Location..."
            />
            <label>
                New Profile Image
                <input type="file" accept="image/*" onChange={handleImageUpload} />
            </label>
            {imagePreview && <img src={imagePreview} alt="Image Preview" />}
            New Password
            <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                placeholder="New Password..."
            />
            Confirm New Password
            <input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleInputChange}
                placeholder="Confirm New Password..."
            />
            <button type="submit" disabled={loading}>
                {loading ? "Saving..." : "Save Changes"}
            </button>
        </form>
    );
}

export default SettingsForm;