import React, { useEffect, useState } from "react";
import api from "../api";
import "./styles/ChatMessage.css";
import { useUser } from '../contexts/UserContext.jsx';


function ChatMessage({ message }) {
    const { content, sender, edited, created_at } = message;
    const { userData, isLoading } = useUser(); // Access user data from context

    return (
        // selects between self or other to apply css accordingly
        <>
            <div className={`chat-message ${sender == userData.id ? "self" : "other"}`}>
            <div className="message-content">
                <span className="message-text">{content} </span>
                {edited && <span className="edited">(edited)</span>}
                <span className="timestamp"><i>{new Date(created_at).toLocaleTimeString()}, {new Date(created_at).toLocaleDateString()}</i></span>
            </div>
            </div>
        </>
        
    );
}

export default ChatMessage;
