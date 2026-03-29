// Assigned to: Harnaindeep Kaur
// Phase: 2 (F2.3)

import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getListings } from "../api/listings";
import { Listing } from "../types";
import ListingCard from "../components/ListingCard";
import SearchBar from "../components/SearchBar";
import { useAuth } from "../hooks/useAuth";

const CATEGORIES = ["All", "Textbooks", "Electronics", "Furniture", "Clothing", "Other"];

export default function BrowsePage() {
  const navigate = useNavigate();
  const { isAuthenticated, user } = useAuth();

  const [listings, setListings] = useState<Listing[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Filters
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [minPrice, setMinPrice] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [sort, setSort] = useState<"newest" | "price_low_to_high" | "price_high_to_low">("newest");
  const [dateListed, setDateListed] = useState<
    "" | "last_24_hours" | "last_7_days" | "last_30_days"
  >("");

  const limit = 20;
  const totalPages = Math.ceil(total / limit);

  // Fetch listings
  useEffect(() => {
    setLoading(true);
    setError("");

    getListings({
      status: "active",
      page,
      limit,
      search: search || undefined,
      category: category || undefined,
      min_price: minPrice ? Number(minPrice) : undefined,
      max_price: maxPrice ? Number(maxPrice) : undefined,
      sort,
      date_listed: dateListed || undefined,
    })
      .then((data) => {
        setListings(data.listings || []);
        setTotal(data.total || 0);
      })
      .catch(() =>
        setError("Failed to load listings. Please try again later.")
      )
      .finally(() => setLoading(false));
  }, [page, search, category, minPrice, maxPrice, sort, dateListed]);

  // Receive filters from SearchBar
  const handleSearch = (params: {
    search?: string;
    category?: string;
    min_price?: number;
    max_price?: number;
    sort?: string;
    date_listed?: string;
  }) => {
    setPage(1);
    setSearch(params.search || "");
    setCategory(params.category || "");
    setMinPrice(params.min_price?.toString() || "");
    setMaxPrice(params.max_price?.toString() || "");
    setSort((params.sort as any) || "newest");
    setDateListed((params.date_listed as any) || "");
  };

  const handleCategoryChange = (cat: string) => {
    setPage(1);
    setCategory(cat === "All" ? "" : cat);
  };

  return (
    <div className="app-content">

      {/* Hero Section */}
      <div className="browse-hero">
        <h1 className="browse-hero-title">
          {isAuthenticated ? `Welcome back, ${user?.name}` : "York's Campus Marketplace"}
        </h1>
        <p className="browse-hero-subtitle">
          {isAuthenticated
            ? "Find great deals from fellow York students or list something to sell."
            : "Buy and sell textbooks, electronics, and more with fellow York University students."}
        </p>
      </div>

      {/* Search Bar */}
      <SearchBar onSearch={handleSearch} />

      {/* Category Pills */}
      <div className="category-pills">
        {CATEGORIES.map((cat) => {
          const active = (cat === "All" && !category) || cat === category;
          return (
            <button
              key={cat}
              onClick={() => handleCategoryChange(cat)}
              className={`category-pill${active ? " active" : ""}`}
            >
              {cat}
            </button>
          );
        })}
      </div>

      {/* Results */}
      {loading ? (
        <div className="loading-state">
          Loading listings...
        </div>
      ) : error ? (
        <div className="loading-state" style={{ color: "var(--error-red)" }}>
          {error}
        </div>
      ) : listings.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">🔍</div>
          <div className="empty-state-title">No listings found</div>
          <p className="empty-state-text">
            Try adjusting your search or filters to find what you're looking for.
          </p>
        </div>
      ) : (
        <div className="listings-grid">
          {listings.map((listing) => (
            <ListingCard
              key={listing.id}
              listing={listing}
              onClick={() => navigate(`/listings/${listing.id}`)}
            />
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="pagination">
          <button
            className="btn-outline"
            style={{ width: "auto", padding: "10px 20px" }}
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
          >
            Previous
          </button>

          <span className="pagination-info">
            Page {page} of {totalPages}
          </span>

          <button
            className="btn-outline"
            style={{ width: "auto", padding: "10px 20px" }}
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
