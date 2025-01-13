import React, { useEffect, useState } from "react";
import api from "../api";
import "./styles/Message.css";

function Message({ message }) {
    const [sender, setSender] = useState(null);

    useEffect(() => {
        const fetchSenderDetails = async () => {
            try {
                const response = await api.get(`/api/users/${message.sender}/`);
                setSender(response.data);
            } catch (error) {
                console.error("Error fetching sender details:", error);
            }
        };

        fetchSenderDetails();
    }, [message.sender]);

    return (
        <div className="message-container">
            <h3>From:</h3>
            <p>{sender ? sender.username : "Loading..."}</p>
            <h3>Content:</h3>
            <p>{message.content}</p>
        </div>
    );
}

export default Message;