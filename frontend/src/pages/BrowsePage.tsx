// Assigned to: Harnaindeep Kaur
// Phase: 2 (F2.3)

import React, { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { getListings } from "../api/listings"
import { Listing } from "../types"
import ListingCard from "../components/ListingCard" // Extracted for F2.2

const CATEGORIES = ["All", "Textbooks", "Electronics", "Furniture", "Clothing", "Other"]

export default function BrowsePage() {
  const navigate = useNavigate()

  const [listings, setListings] = useState<Listing[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [search, setSearch] = useState("")
  const [searchInput, setSearchInput] = useState("")
  const [category, setCategory] = useState("")
  const [minPrice, setMinPrice] = useState("")
  const [maxPrice, setMaxPrice] = useState("")
  const [sort, setSort] = useState<"newest" | "price_low_to_high" | "price_high_to_low">("newest")  
  const [dateListed, setDateListed] = useState<"" | "last_24_hours" | "last_7_days" | "last_30_days">("")
  const limit = 20
  const totalPages = Math.ceil(total / limit)

  useEffect(() => {
    setLoading(true)
    setError("")
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
        setListings(data.listings || [])
        setTotal(data.total || 0)
      })
      .catch(() => setError("Failed to load listings. Please try again later."))
      .finally(() => setLoading(false))
}, [page, search, category, minPrice, maxPrice, sort, dateListed])

const handleFilterSubmit = (e: React.FormEvent) => {
  e.preventDefault()
  setError("")

  if (minPrice && maxPrice && Number(minPrice) > Number(maxPrice)) {
    setError("Minimum price cannot be greater than maximum price.")
    return
  }

  setPage(1)
  setSearch(searchInput.trim())
}

const handleClearFilters = () => {
  setError("")
  setPage(1)
  setSearch("")
  setSearchInput("")
  setCategory("")
  setMinPrice("")
  setMaxPrice("")
  setSort("newest")
  setDateListed("")
}
  const handleCategoryChange = (cat: string) => {
    setPage(1)
    setCategory(cat === "All" ? "" : cat)
  }

  return (
    <div className="app-content">
      {/* Search + filter row */}
    <form
      onSubmit={handleFilterSubmit}
      style={{
        display: "flex",
        flexDirection: "column",
        gap: 16,
        marginBottom: 24,
      }}
    >
      <div style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
        <input
          className="auth-input"
          style={{ flex: "1 1 260px", marginBottom: 0 }}
          type="text"
          placeholder="Search listings..."
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
        />

        <input
          className="auth-input"
          style={{ width: 140, marginBottom: 0 }}
          type="number"
          min="0"
          step="0.01"
          placeholder="Min price"
          value={minPrice}
          onChange={(e) => setMinPrice(e.target.value)}
        />

        <input
          className="auth-input"
          style={{ width: 140, marginBottom: 0 }}
          type="number"
          min="0"
          step="0.01"
          placeholder="Max price"
          value={maxPrice}
          onChange={(e) => setMaxPrice(e.target.value)}
        />
        <select
          className="auth-input listing-select"
          style={{ width: 190, marginBottom: 0 }}
          value={sort}
        onChange={(e) => {
          setPage(1)
          setSort(e.target.value as "newest" | "price_low_to_high" | "price_high_to_low")
        }}
        >
          <option value="newest">Newest</option>
          <option value="price_low_to_high">Price: Low to High</option>
          <option value="price_high_to_low">Price: High to Low</option>
        </select>

        <select
          className="auth-input listing-select"
          style={{ width: 180, marginBottom: 0 }}
          value={dateListed}
        onChange={(e) => {
          setPage(1)
          setDateListed(e.target.value as "" | "last_24_hours" | "last_7_days" | "last_30_days")
        }}
        >
          <option value="">Any time</option>
          <option value="last_24_hours">Last 24 hours</option>
          <option value="last_7_days">Last 7 days</option>
          <option value="last_30_days">Last 30 days</option>
        </select>        

        <button className="btn-red" type="submit" style={{ width: "auto", padding: "10px 24px" }}>
          Apply Filters
        </button>

        <button
          className="btn-outline"
          type="button"
          style={{ width: "auto", padding: "10px 24px" }}
          onClick={handleClearFilters}
        >
          Clear
        </button>
      </div>

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        {CATEGORIES.map((cat) => {
          const active = (cat === "All" && !category) || cat === category
          return (
            <button
              key={cat}
              type="button"
              onClick={() => handleCategoryChange(cat)}
              style={{
                padding: "8px 16px",
                borderRadius: "var(--radius-pill)",
                border: "1.5px solid",
                borderColor: active ? "var(--yu-red)" : "var(--border-color)",
                background: active ? "var(--yu-red)" : "var(--yu-white)",
                color: active ? "var(--yu-white)" : "var(--text-muted)",
                cursor: "pointer",
                fontSize: 14,
                fontWeight: active ? 600 : 400,
                transition: "var(--transition)",
              }}
            >
              {cat}
            </button>
          )
        })}
      </div>
    </form>

      {/* Results */}
      {loading ? (
        <p style={{ textAlign: "center", padding: "48px 0", color: "var(--text-muted)" }}>Loading listings...</p>
      ) : error ? (
        <p style={{ textAlign: "center", padding: "48px 0", color: "var(--error-red)" }}>{error}</p>
      ) : listings.length === 0 ? (
        <p style={{ textAlign: "center", padding: "48px 0", color: "var(--text-muted)" }}>No listings found matching your filters.</p>
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
        <div style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: 16, marginTop: 40 }}>
          <button
            className="btn-outline"
            style={{ width: "auto", padding: "8px 20px" }}
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
          >
            Previous
          </button>
          <span style={{ fontSize: 14, color: "var(--text-main)", fontWeight: 500 }}>
            Page {page} of {totalPages}
          </span>
          <button
            className="btn-outline"
            style={{ width: "auto", padding: "8px 20px" }}
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
          >
            Next
          </button>
        </div>
      )}
    </div>
  )
}