// Assigned to: Harnaindeep Kaur
// Phase: 2 (F2.3)

import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getListings } from "../api/listings";
import { Listing } from "../types";
import ListingCard from "../components/ListingCard";
import SearchBar from "../components/SearchBar";

const CATEGORIES = ["All", "Textbooks", "Electronics", "Furniture", "Clothing", "Other"];

export default function BrowsePage() {
  const navigate = useNavigate();

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
      
      {/* Search Bar */}
      <SearchBar onSearch={handleSearch} />

      {/* Category Pills */}
      <div
        style={{
          display: "flex",
          gap: 8,
          flexWrap: "wrap",
          marginBottom: 20,
        }}
      >
        {CATEGORIES.map((cat) => {
          const active = (cat === "All" && !category) || cat === category;

          return (
            <button
              key={cat}
              onClick={() => handleCategoryChange(cat)}
              style={{
                padding: "8px 16px",
                borderRadius: "20px",
                border: "1.5px solid",
                borderColor: active ? "#E31837" : "#ddd",
                background: active ? "#E31837" : "#fff",
                color: active ? "#fff" : "#555",
                cursor: "pointer",
                fontSize: 14,
                fontWeight: active ? 600 : 400,
              }}
            >
              {cat}
            </button>
          );
        })}
      </div>

      {/* Results */}
      {loading ? (
        <p style={{ textAlign: "center", padding: "48px 0" }}>
          Loading listings...
        </p>
      ) : error ? (
        <p style={{ textAlign: "center", padding: "48px 0", color: "red" }}>
          {error}
        </p>
      ) : listings.length === 0 ? (
        <p style={{ textAlign: "center", padding: "48px 0" }}>
          No listings found.
        </p>
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
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            gap: 16,
            marginTop: 40,
          }}
        >
          <button
            className="btn-outline"
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
          >
            Previous
          </button>

          <span style={{ fontSize: 14 }}>
            Page {page} of {totalPages}
          </span>

          <button
            className="btn-outline"
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