//Home.jsx
import { useState, useEffect } from "react";
import api from "../api";
import ListingFeed from "../components/ListingFeed";
import NavBar from "../components/Navbar.jsx";
import Filters from "../components/Filters.jsx";
import SearchBar from "../components/SearchBar.jsx";
import LinkedButton from "../components/LinkedButton.jsx";
import { retryWithExponentialBackoff } from "../utils/retryWithExponentialBackoff";
import "./styles/Home.css";

function Home() {
  const [listings, setListings] = useState([]);
  const [nextPage, setNextPage] = useState(null);
  const [previousPage, setPreviousPage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    searchTerm: "",
    minPrice: "",
    maxPrice: "",
    condition: "",
    sortOption: "",
  });

  useEffect(() => {
    getListings("/api/listings/");
  }, [filters]);

  const buildFilterQuery = () => {
    const queryParams = new URLSearchParams();

    if (filters.searchTerm) queryParams.append("search", filters.searchTerm);
    if (filters.minPrice) queryParams.append("min_price", filters.minPrice);
    if (filters.maxPrice) queryParams.append("max_price", filters.maxPrice);
    if (filters.condition) queryParams.append("condition", filters.condition);
    if (filters.sortOption) queryParams.append("ordering", filters.sortOption);

    return queryParams.toString();
  };

  const getListings = (url) => {
    setLoading(true);

    const [baseUrl, existingQuery] = url.split("?");
    const filterQuery = buildFilterQuery();

    // Merge filter query with existing query parameters
    const mergedQuery = new URLSearchParams(existingQuery || "");

    if (filterQuery) {
      const newFilters = new URLSearchParams(filterQuery);
      newFilters.forEach((value, key) => {
        mergedQuery.set(key, value); // Avoid duplicate entries
      });
    }

    // Construct the full URL
    const fullUrl = `${baseUrl}?${mergedQuery.toString()}`;
    retryWithExponentialBackoff(() => api.get(fullUrl))
      .then((response) => response.data)
      .then((data) => {
        setListings(data.results);
        setNextPage(data.next);
        setPreviousPage(data.previous);
      })
      .catch((err) => console.error("Error fetching listings:", err))
      .finally(() => setLoading(false));
  };

  const handleFilterChange = (updatedFilters) => {
    setFilters((prevFilters) => ({ ...prevFilters, ...updatedFilters }));
  };

  //Const: saves a listings
  const handleSaveListing = async (listingId) => {
    try {
      await api.post(`/api/listings/${listingId}/save_listing/`);
      alert("Listing saved to favorites!");
    } catch (err) {
      if (err.response) {
        // Check the status code of the error response
        if (err.response.status === 401) {
          alert("Error: You need to be logged in to save a listing!");
        } else if (err.response.status === 409) {
          alert("Alert: This listing is already in your favorites!");
        } else {
          alert(`Error: Something went wrong! Status code: ${err.response.status}`);
        }
      } else {
        // Generic error if no response exists
        alert("Error: Unable to save the listing. Please try again later.");
      }
      console.error("Error saving listing:", err);
    }
  };

  return (
    <div>
      <NavBar />
      <div className="home-container">
        <div className="filters-section">
          <Filters onFilterChange={handleFilterChange} />
        </div>

        <div className="listings-section">
          <h1>Listings</h1>

          <SearchBar onSearch={handleFilterChange} />

          {loading ? (
            <p>Loading...</p>
          ) : listings.length === 0 ? (
            <div className="empty-listings-message">
                <p>No Listings found.</p>
            </div>
        ) : (
            <>
              <ListingFeed
                listings={listings}
                actionType="save"
                onAction={(id) => handleSaveListing(id)}
              />
              <div className="pagination-controls">
                <LinkedButton
                  url={previousPage}
                  onClick={getListings}
                  label="Previous"
                />
                <LinkedButton
                  url={nextPage}
                  onClick={getListings}
                  label="Next"
                />
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default Home;