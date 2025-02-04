import React, { useEffect, useState, useRef } from "react";
import { Link } from "react-router-dom";
import api from "../api";
import ChatMessage from "./ChatMessage";
import testImg from "../assets/usericon.png";
import { retryWithExponentialBackoff } from "../utils/retryWithExponentialBackoff";
import "./styles/MessageFeed.css";

function MessageFeed({ userId, listingId }) {
	const [messages, setMessages] = useState([]);
	const [newMessage, setNewMessage] = useState("");
	const [userDetails, setUserDetails] = useState({});
	const [listingDetails, setListingDetails] = useState(null);
	const [loading, setLoading] = useState(false);

	// Reference used to scroll to the bottom of messages
	const endOfMessagesRef = useRef(null);

	// userId is the other user
	const userImageUrl = userDetails?.profile?.image
		? `${api.defaults.baseURL}${userDetails.profile.image}`
		: testImg;

	useEffect(() => {
		if (userId) {
			fetchUserDetails();
		}
		if (listingId) {
			fetchListingDetails();
		}
		if (userId && listingId) {
			fetchConversation();
		}
	}, [userId, listingId]);

	// Automatically scroll to bottom whenever messages change
	useEffect(() => {
		if (endOfMessagesRef.current) {
			endOfMessagesRef.current.scrollIntoView({ behavior: "smooth" });
		}
	}, [messages]);

	const fetchConversation = async () => {
		try {
			const response = await api.get(
				`/api/messages/with_user/?user=${userId}&listing=${listingId}`
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
	};

	const fetchListingDetails = async () => {
		try {
			const response = await retryWithExponentialBackoff(() =>
				api.get(`/api/listings/${listingId}/`)
			);
			setListingDetails(response.data);
		} catch (error) {
			console.error("Error fetching listing details:", error);
		} finally {
			setLoading(false);
		}
	};

	const handleSendMessage = async () => {
		// Prevent sending empty messages
		if (!newMessage.trim()) return;
		try {
			await api.post("/api/messages/", {
				receiver: userId,
				related_listing: listingId,
				content: newMessage,
			});
			setNewMessage("");
			fetchConversation();
		} catch (error) {
			console.error("Error sending message:", error);
		}
	};

	const handleKeyDown = (e) => {
		if (e.key === "Enter") {
			// Prevent newline
			e.preventDefault();

			handleSendMessage();
		}
	};

	return (
		<div className="message-feed-view">
			<div className="message-feed-header">
				<div className="header-left">
					{userDetails ? (
						<>
							<img src={userImageUrl} alt="User" width="25" />
							<span>
								<b>{userDetails.username}</b>
							</span>
						</>
					) : (
						<span>Loading user data...</span>
					)}
				</div>

				<div className="header-right">
					{listingDetails ? (
						<Link to={`/listings/${listingId}`} className="listing-detail-link">
							<img src={listingDetails.image} alt="Listing" width="25" />
							<div className="listing-details">
								<span className="listing-title">{listingDetails.title}</span>
								<span className="listing-price">${listingDetails.price}</span>
							</div>
						</Link>
					) : (
						<span>Loading listing...</span>
					)}
				</div>
			</div>

			<div className="message-feed-content">
				{messages.map((message) => (
					<ChatMessage key={message.id} message={message} />
				))}
				{/* Dummy element that can be referenced when we need to scroll down automatically */}
				<div ref={endOfMessagesRef}></div>
			</div>

			<div className="new-message">
				<input
					type="text"
					value={newMessage}
					onChange={(e) => setNewMessage(e.target.value)}
					onKeyDown={handleKeyDown}
					placeholder="Type a message..."
				/>
				<button onClick={handleSendMessage}>Send</button>
			</div>
		</div>
	);
}

export default MessageFeed;
