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
	const [loadingMore, setLoadingMore] = useState(false);
	const [currentPage, setCurrentPage] = useState(1);
	const [hasMore, setHasMore] = useState(false);

	// Reference for scrolling
	const endOfMessagesRef = useRef(null);

	// Other users image
	const userImageUrl = userDetails?.profile?.image
		? `${api.defaults.baseURL}${userDetails.profile.image}`
		: testImg;

	// When userId or listingId change, reset pagination and fetch first page of conversation.
	useEffect(() => {
		if (userId && listingId) {
			setCurrentPage(1);
			fetchConversation(1, true);
		}
	}, [userId, listingId]);

	// Automatically scroll to bottom whenever messages change (for new messages)
	useEffect(() => {
		if (endOfMessagesRef.current) {
			endOfMessagesRef.current.scrollIntoView({ behavior: "smooth" });
		}
	}, [messages]);

	const fetchConversation = async (page = 1, reset = false) => {
		if (reset) {
			setMessages([]);
		}
		if (page === 1) {
			setLoading(true);
		} else {
			setLoadingMore(true);
		}
		try {
			const response = await api.get(
				`/api/messages/with_user/?user=${userId}&listing=${listingId}&page=${page}`
			);
			const data = response.data;
			// Reverse array so messages are in ascending order (oldest at top)
			const pageResults = data.results.slice().reverse();

			if (page === 1) {
				setMessages(pageResults);
			} else {
				// Prepend older messages to the current list
				setMessages((prevMessages) => [...pageResults, ...prevMessages]);
			}
			
			// If data.next is not null, then there are more older messages to load
			setHasMore(data.next !== null);
			setCurrentPage(page);
		} catch (error) {
			console.error("Error fetching conversation:", error);
		} finally {
			setLoading(false);
			setLoadingMore(false);
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
		}
	};

	useEffect(() => {
		if (userId) fetchUserDetails();
		if (listingId) fetchListingDetails();
	}, [userId, listingId]);

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
			// Refresh conversation to page 1 so the new message appears at the bottom
			fetchConversation(1, true);
		} catch (error) {
			console.error("Error sending message:", error);
		}
	};

	const handleKeyDown = (e) => {
		if (e.key === "Enter") {
			e.preventDefault();
			handleSendMessage();
		}
	};

	// Handler for "Load More Messages" button
	const handleLoadMore = () => {
		fetchConversation(currentPage + 1);
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
				{hasMore && (
					<div className="load-more-container">
						<button onClick={handleLoadMore} disabled={loadingMore}>
							{loadingMore ? "Loading..." : "Load More Messages"}
						</button>
					</div>
				)}
				{messages.map((message) => (
					<ChatMessage key={message.id} message={message} />
				))}
				{/* Dummy element for auto-scrolling */}
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
