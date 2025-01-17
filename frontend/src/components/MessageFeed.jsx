import React, { useEffect, useState } from "react";
import api from "../api";
import ChatMessage from "./ChatMessage";
import "./styles/MessageFeed.css";

function MessageFeed({ userId }) {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState("");
  
  console.log(userId)

  useEffect(() => {
    fetchConversation();
  }, [userId]);

  const fetchConversation = async () => {
    try {
      const response = await api.get(`/api/messages/with_user/?user_id=${userId}`);
      setMessages(response.data);
    } catch (error) {
      console.error("Error fetching conversation:", error);
    }
  };

  const handleSendMessage = async () => {
    try {
      await api.post("/api/messages/", {
        receiver: userId,
        content: newMessage,
      });
      setNewMessage("");
      fetchConversation();
    } catch (error) {
      console.error("Error sending message:", error);
    }
  };

  return (
    <div className="message-feed-view">
      {messages.map((message) => (
        <ChatMessage key={message.id} message={message} />
      ))}
      <div className="new-message">
        <input
          type="text"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          placeholder="Type a message..."
        />
        <button onClick={handleSendMessage}>Send</button>
      </div>
    </div>
  );
}

export default MessageFeed;
