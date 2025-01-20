import React, { useState, useEffect } from "react";
import NavBar from "../components/Navbar.jsx";
import MessageFeed from "../components/MessageFeed.jsx";
import { useUser } from '../contexts/UserContext.jsx';
import api from "../api";
import "./styles/Messages.css";
import InboxPreview from "../components/InboxPreview.jsx";

function Messages() {
    const { userData, isLoading } = useUser();
    const [messages, setMessages] = useState([]);
    const [firstMessage, setFirstMessage] = useState(null);
    const [selectedUser, setSelectedUser] = useState(null);
    const [selectedListing, setSelectedListing] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchMessages();
    }, []);

    useEffect(() => {
        if (firstMessage && userData) {
            // Ensure selected user is not the current user
            const userToMessage = userData.id !== firstMessage.sender
                ? firstMessage.sender 
                : firstMessage.receiver;
            setSelectedUser(userToMessage);
            setSelectedListing(firstMessage.related_listing);
        }
    }, [firstMessage, userData]);

    const fetchMessages = async () => {
        setLoading(true);
        try {
            const response = await api.get("/api/messages/");
            const fetchedMessages = response.data || [];
            setMessages(fetchedMessages);

            if (fetchedMessages.length > 0) {
                setFirstMessage(fetchedMessages[0]);
            }
        } catch (err) {
            console.error("Error fetching messages:", err);
        } finally {
            setLoading(false);
        }
    };

    const handleSelectConvo = (user, listing) => {
        setSelectedUser(user);
        setSelectedListing(listing);
    };

    return (
        <>
            <NavBar />
            <div className="messages-container">
                <div className="inbox">
                    {loading ? (
                        <p>Loading...</p>
                    ) : messages.length === 0 ? (
                        <p>No messages found.</p>
                    ) : (
                        messages.map((message) => (
                            <InboxPreview
                                key={message.id}
                                message={message}
                                onSelectConvo={(user) => handleSelectConvo(user, message.related_listing)}
                            />
                        ))
                    )}
                </div>
                <div className="message-feed">
                    {selectedUser ? (
                        <MessageFeed userId={selectedUser} listingId={selectedListing} />
                    ) : (
                        <p>Select a conversation to start chatting.</p>
                    )}
                </div>
            </div>
        </>
    );
}

export default Messages;
