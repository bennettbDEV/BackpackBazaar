import React, { useEffect, useState } from "react";
import api from "../api";
import ChatMessage from "./ChatMessage";
import testImg from "../assets/usericon.png";
import { retryWithExponentialBackoff } from "../utils/retryWithExponentialBackoff";
import "./styles/MessageFeed.css";

function MessageFeed({ userId }) {
	const [messages, setMessages] = useState([]);
	const [newMessage, setNewMessage] = useState("");
	const [userDetails, setUserDetails] = useState({});
	const [loading, setLoading] = useState(false);
	const [listingDetails, setListingDetails] = useState(null);

	// userId is the other user
	const imageUrl = userDetails?.profile?.image ? `${api.defaults.baseURL}${userDetails.profile.image}` : testImg;


	useEffect(() => {
		fetchConversation();
		fetchUserDetails();
	}, [userId]);

	const fetchConversation = async () => {
		try {
			const response = await api.get(
				`/api/messages/with_user/?user_id=${userId}`
			);
			setMessages(response.data);
		} catch (error) {
			console.error("Error fetching conversation:", error);
		}
	};

	const fetchUserDetails = async () => {
		try {
			const response = await retryWithExponentialBackoff(() =>
				api.get(`/api/users/${userId}/`)
			);
			setUserDetails(response.data);
		} catch (error) {
			console.error("Error fetching user details:", error);
		}
		finally {
            setLoading(false);
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
			<div className="message-feed-header">
				<div className="header-left">
					{listingDetails && <img src={listingDetails.image_url} alt="Listing" />}
					<div className="listing-title">
						{listingDetails ? listingDetails.title : "No Listing"}
					</div>
				</div>
				<div className="header-right">
					{userDetails ? (
						<>
							<span>{userDetails.username}</span>
							<img src={imageUrl} alt="User" width="25"/>
							
						</>
					) : (
						<span>Loading user data...</span>
					)}
				</div>
			</div>


			<div className="message-feed-content">
				{messages.map((message) => (
					<ChatMessage key={message.id} message={message} />
				))}
			</div>

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
