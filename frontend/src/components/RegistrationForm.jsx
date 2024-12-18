import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ACCESS_TOKEN, REFRESH_TOKEN } from "../constants";
import api from "../api";
import "./styles/RegistrationForm.css";

function RegistrationForm({ route }) {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [location, setLocation] = useState("");
    const [image, setImage] = useState(null); // Store the actual file
    const [loading, setLoading] = useState(false);
    const [imagePreview, setImagePreview] = useState(null);
    const navigate = useNavigate();

    const handleImageUpload = (e) => {
        const file = e.target.files[0];
        if (file) {
            setImage(file); // Store the file
            const reader = new FileReader();
            reader.onload = () => {
                setImagePreview(reader.result); // Display preview
            };
            reader.readAsDataURL(file);
        }
    };

    const handleSubmit = async (e) => {
        setLoading(true);
        e.preventDefault();

        try {
            const formData = new FormData();
            formData.append("username", username);
            formData.append("password", password);

            // Conditionally append location and image
            if (location) formData.append("location", location);
            if (image) formData.append("image", image);

            const res = await api.post(route, formData, {
                headers: {
                    "Content-Type": "multipart/form-data", // Ensure the correct headers
                },
            });

            localStorage.setItem(ACCESS_TOKEN, res.data.access);
            localStorage.setItem(REFRESH_TOKEN, res.data.refresh);
            navigate("/");
        } catch (error) {
            alert(error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="registration-form-container">
            <h1>Register</h1>

            <div className="registration-container">
                <div className="form-container">
                    <input
                        className="form-input"
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        placeholder="*Username"
                        name="username"
                        required
                    />
                    <input
                        className="form-input"
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="*Password"
                        name="password"
                        required
                    />
                    <input
                        className="form-input"
                        type="text"
                        value={location}
                        onChange={(e) => setLocation(e.target.value)}
                        placeholder="Location (Optional)"
                        name="location"
                    />

                    <label className="form-input">
                        Upload profile picture:&nbsp;
                        <input
                            type="file"
                            accept="image/*"
                            onChange={handleImageUpload}
                            className="file-input"
                        />
                    </label>

                    {imagePreview && (
                        <div class="form-submit-image-container">
                        <img
                            className="form-submit-image"
                            src={imagePreview}
                            alt="Image Preview"
                        />
                        </div>
                    )}

                    <button className="form-button" type="submit" disabled={loading}>
                        {loading ? "Submitting..." : "Submit"}
                    </button>
                </div>
            </div>
        </form>
    );
}

export default RegistrationForm;