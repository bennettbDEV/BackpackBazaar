import { useState } from "react";
import { useNavigate } from "react-router-dom";
import NavBar from "../components/Navbar.jsx";
import api from "../api";
import "./styles/CreateListing.css";

function CreateListing() {
    const navigate = useNavigate();
    const [title, setTitle] = useState("");
    const [price, setPrice] = useState("");
    const [condition, setCondition] = useState("FN");
    const [description, setDescription] = useState("");
    const [tags, setTags] = useState([]);
    const [currentTag, setCurrentTag] = useState("");
    const [image, setImage] = useState(null);
    const [imagePreview, setImagePreview] = useState(null);
    const [loading, setLoading] = useState(false);

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

    const handleTagChange = (e) => {
        setCurrentTag(e.target.value);
    };

    const addTag = () => {
        if (currentTag.trim() !== "") {
            setTags((prevTags) => [...prevTags, currentTag.trim()]);
            setCurrentTag(""); // Clear the input field
        }
    };

    const removeTag = (index) => {
        setTags(tags.filter((_, i) => i !== index));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            const formData = new FormData();
            formData.append("title", title);
            formData.append("price", price);
            formData.append("condition", condition);
            formData.append("description", description);
            tags.forEach((tag) => formData.append("tags", tag));
            formData.append("image", image);

            const res = await api.post("/api/listings/", formData, {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
            });

            alert("Listing created successfully!");
            navigate("/profile"); // Redirect to home or another page
        } catch (error) {
            alert("Error creating listing: " + error.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <>
            <NavBar />
            <div className="centered-container">
                <div className="createlisting-container">
                    <h1>Create Listing</h1>

                    <form className="create-listing-form" onSubmit={handleSubmit}>

                        <label htmlFor="title"><red>*</red> Item Title</label>
                        <input
                            id="title"
                            className="form-input"
                            type="text"
                            value={title}
                            onChange={(e) => setTitle(e.target.value)}
                            placeholder="Enter item name"
                            required
                        />

                        <label htmlFor="price"><red>*</red> Price</label>
                        <input
                            id="price"
                            className="form-input"
                            type="number"
                            value={price}
                            onChange={(e) => setPrice(e.target.value)}
                            placeholder="Enter price in USD"
                            step="0.01"
                            min="0"
                            required
                        />

                        <label htmlFor="condition"><red>*</red> Condition</label>
                        <select
                            id="condition"
                            className="form-input"
                            value={condition}
                            onChange={(e) => setCondition(e.target.value)}
                            required
                        >
                            <option value="FN">Factory New</option>
                            <option value="MW">Minimal Wear</option>
                            <option value="FR">Fair</option>
                            <option value="WW">Well Worn</option>
                            <option value="RD">Refurbished</option>
                        </select>

                        <label htmlFor="description"><red>*</red> Description</label>
                        <textarea
                            id="description"
                            className="form-input"
                            placeholder="Enter description"
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            rows="5"
                            cols="50"
                            required
                        ></textarea>

                        <label><red>*</red> Tags</label>
                        <div className="tags-input-container">
                            <input
                                className="form-input"
                                type="text"
                                placeholder="Enter a tag"
                                value={currentTag}
                                onChange={handleTagChange}
                            />
                            <button type="button" className="add-tag-button" onClick={addTag}>
                                Add Tag
                            </button>
                        </div>
                        <div className="tags-container">
                            {tags.map((tag, index) => (
                                <div key={index} className="tag">
                                    {tag}
                                    <span className="remove-tag" onClick={() => removeTag(index)}>
                                        &times;
                                    </span>
                                </div>
                            ))}
                        </div>

                        <label htmlFor="image"><red>*</red> Upload Item Image</label>
                        <input
                            id="image"
                            className="form-input file-input"
                            type="file"
                            accept="image/*"
                            onChange={handleImageUpload}
                            required
                        />
                        {imagePreview && (
                            <div class="form-submit-image-container">
                                <img
                                    className="form-submit-image"
                                    src={imagePreview}
                                    alt="Item Preview"
                                />
                                </div>
                        )}
                        <button className="form-button" type="submit" disabled={loading}>
                            {loading ? "Submitting..." : "Create Listing"}
                        </button>
                    </form>
                </div>
            </div>
        </>
    );
}

export default CreateListing;