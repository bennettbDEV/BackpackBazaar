import React from "react";
import { useUser } from '../contexts/UserContext.jsx';
import "./styles/InboxPreview.css";

function InboxPreview({ message, onSelectUser }) {
    const { userData, isLoading } = useUser(); // Access user data from context
    const { content, sender, receiver, related_listing, created_at } = message;
    const snippet = content.length > 30 ? content.slice(0, 30) + "..." : content;

    const handleClick = () => {
        const otherUser = sender === userData.id ? receiver : sender;  
        onSelectUser(otherUser);
    };

    return (
        <div className="inbox-preview" onClick={handleClick}>
            <img src={related_listing?.image_url || "default.jpg"} alt="Listing" />
            <div className="details">
                <h4>{receiver.username}</h4>
                {related_listing && <p>{related_listing.title}</p>}
                <p className="snippet">{snippet}</p>
                <span className="timestamp">{new Date(created_at).toLocaleString()}</span>
            </div>
        </div>
    );
}

export default InboxPreview;
