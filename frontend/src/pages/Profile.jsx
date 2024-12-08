import testImage from '../assets/test.jpg';
import NavBar from "../components/Navbar.jsx";
import ListingFeed from "../components/ListingFeed";
import { useState, useEffect } from "react";
import api from "../api";
import Filters from "../components/Filters.jsx";
import LinkedButton from "../components/LinkedButton.jsx";
import "./styles/Home.css";


function Profile() {

    const [listings, setListings] = useState([]);
  const [nextPage, setNextPage] = useState(null);
  const [previousPage, setPreviousPage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    searchTerm: "",
    minPrice: "",
    maxPrice: "",
    condition: "",
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

    return queryParams.toString();
  };

  const getListings = (url) => {
    setLoading(true);
    const filterQuery = buildFilterQuery();
    const fullUrl = filterQuery ? `${url}?${filterQuery}` : url;
    api
      .get(fullUrl)
      .then((response) => response.data)
      .then((data) => {
        console.log("API Response:", data);
        setListings(data.results);
        setNextPage(data.links.next);
        setPreviousPage(data.links.previous);
      })
      .catch((err) => {
        console.error("Error fetching listings:", err);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const handleFilterChange = (updatedFilters) => {
    setFilters(updatedFilters);
    getListings("/api/listings/");
  };


    return <div>
        <NavBar />
        <h1>Profile page</h1>
        <p>You are logged in</p>

        <h2>Your listings:</h2>
        {loading ? (
            <p>Loading...</p>
          ) : (
            <>
              <ListingFeed listings={listings} />

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
}

export default Profile