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
    })
      .then((data) => {
        setListings(data.listings || [])
        setTotal(data.total || 0)
      })
      .catch(() => setError("Failed to load listings. Please try again later."))
      .finally(() => setLoading(false))
  }, [page, search, category])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(1)
    setSearch(searchInput)
  }

  const handleCategoryChange = (cat: string) => {
    setPage(1)
    setCategory(cat === "All" ? "" : cat)
  }

  return (
    <div className="app-content">
      {/* Search + filter row */}
      <div style={{ display: "flex", gap: 12, marginBottom: 24, alignItems: "center", flexWrap: "wrap" }}>
        <form onSubmit={handleSearch} style={{ display: "flex", gap: 8, flex: "1 1 280px" }}>
          <input
            className="auth-input"
            style={{ flex: 1, marginBottom: 0 }}
            type="text"
            placeholder="Search listings..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
          />
          <button className="btn-red" type="submit" style={{ width: "auto", padding: "0 24px" }}>
            Search
          </button>
        </form>

        {/* Category filters */}
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          {CATEGORIES.map((cat) => {
            const active = (cat === "All" && !category) || cat === category
            return (
              <button
                key={cat}
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
      </div>

      {/* Results */}
      {loading ? (
        <p style={{ textAlign: "center", padding: "48px 0", color: "var(--text-muted)" }}>Loading listings...</p>
      ) : error ? (
        <p style={{ textAlign: "center", padding: "48px 0", color: "var(--error-red)" }}>{error}</p>
      ) : listings.length === 0 ? (
        <p style={{ textAlign: "center", padding: "48px 0", color: "var(--text-muted)" }}>No listings found in this category.</p>
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