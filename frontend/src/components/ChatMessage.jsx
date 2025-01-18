import React, { useEffect, useState } from "react";
import api from "../api";
import "./styles/ChatMessage.css";
import { useUser } from '../contexts/UserContext.jsx';


function ChatMessage({ message }) {
    const { content, sender, edited, created_at } = message;
    const { userData, isLoading } = useUser(); // Access user data from context
    

    return (
        <div className={`chat-message ${sender == userData.id ? "self" : "other"}`}>
            <div className="message-content">
                <p>{content}</p>
                {edited && <span className="edited">(edited)</span>}
            </div>
            <span className="timestamp">{new Date(created_at).toLocaleTimeString()}</span>
        </div>
    );
}

export default ChatMessage;
