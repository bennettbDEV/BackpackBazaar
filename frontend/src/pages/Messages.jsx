import NavBar from "../components/Navbar.jsx";
import MessagesFeed from "../components/MessagesFeed.jsx";
import api from "../api";
import React, { useState, useEffect } from "react";
import "./styles/Messages.css";

function Messages() {
    const [loading, setLoading] = useState(false);
    const [messages, setMessages] = useState([]);
    const [isInboxExpanded, setIsInboxExpanded] = useState(true); 

    useEffect(() => {
        fetchMessages();
    }, []);

    const fetchMessages = async () => {
        setLoading(true);
        try {
            const response = await api.get("/api/messages/");
            setMessages(response.data || []);
        } catch (err) {
            console.error("Error fetching messages:", err);
        } finally {
            setLoading(false);
        }
    };

    const toggleInbox = () => {
        setIsInboxExpanded((prev) => !prev);
    };

    return (
        <>
            <NavBar />
            <div className="messages-container">
                <h1>Messages</h1>
                <h2>
                    Inbox:
                    <button 
                        onClick={toggleInbox} 
                        style={{
                            marginLeft: "10px",
                            padding: "5px 10px",
                            cursor: "pointer",
                        }}
                    >
                        {isInboxExpanded ? "Collapse" : "Expand"}
                    </button>
                </h2>

                {isInboxExpanded && (
                    loading ? (
                        <p>Loading...</p>
                    ) : messages.length === 0 ? (
                        <p>Inbox empty. Search the marketplace for a listing you like, and send the owner a message!</p>
                    ) : (
                        <MessagesFeed messages={messages} />
                    )
                )}
            </div>
        </>
    );
}

export default Messages;
