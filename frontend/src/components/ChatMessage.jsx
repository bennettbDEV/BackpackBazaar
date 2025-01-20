import React, { useEffect, useState } from "react";
import api from "../api";
import "./styles/ChatMessage.css";
import { useUser } from '../contexts/UserContext.jsx';


function ChatMessage({ message }) {
    const { content, sender, edited, created_at } = message;
    const { userData, isLoading } = useUser(); // Access user data from context

    return (
        // selects between self or other to apply css accordingly
         // {new Date(created_at).toLocaleDateString()} to show the date, will use this on hover in a little 
        <>
            <div className={`chat-message ${sender == userData.id ? "self" : "other"}`}>
            <div className="message-content">
                <span className="message-text">{content} </span>
                <span className="timestamp"><i>{new Date(created_at).toLocaleTimeString()}</i></span>
                {edited && <span className="edited"><i> (edited)</i></span>}
            </div>
            </div>
        </>
        
    );
}

export default ChatMessage;
