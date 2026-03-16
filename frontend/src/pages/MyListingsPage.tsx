// Assigned to: Harnaindeep Kaur
// Phase: 2 (F2.6)


import React, { useState, useEffect, useContext } from "react"
import { useNavigate } from "react-router-dom"
import { getListings, updateListing } from "../api/listings"
import { Listing } from "../types"
import { AuthContext } from "../context/AuthContext"
import { formatPrice } from "../utils/validators" // Added import

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000"

function statusLabel(status: string) {
  if (status === "active") return "Active"
  if (status === "sold") return "Sold"
  return "Inactive"
}

function statusClass(status: string) {
  if (status === "active") return "status-pill status-pill-active"
  if (status === "sold") return "status-pill status-pill-sold"
  return "status-pill status-pill-inactive"
}

export default function MyListingsPage() {
  const { user } = useContext(AuthContext)
  const navigate = useNavigate()
  const [listings, setListings] = useState<Listing[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Only fetch if user is logged in
    if (!user?.id) return;

    getListings({})
      .then((data) => {
        const all: Listing[] = data.listings || []
        // Filter to only show items belonging to this student
        setListings(all.filter((l) => l.seller_id === user?.id))
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [user])

  const handleDelete = async (id: number) => {
    if (!window.confirm("Are you sure you want to remove this listing?")) return
    try {
      await updateListing(id, { status: "removed" })
      setListings((prev) => prev.filter((l) => l.id !== id))
    } catch {
      alert("Failed to delete listing.")
    }
  }

  return (
    <div className="app-content">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <h1 className="auth-title" style={{ margin: 0, textAlign: 'left' }}>My Listings</h1>
        <button className="btn-red" style={{ width: "auto" }} onClick={() => navigate("/create")}>
          + Create New
        </button>
      </div>

      {loading ? (
        <p style={{ textAlign: "center", paddingTop: 48, color: "#aaa" }}>Loading...</p>
      ) : listings.length === 0 ? (
        <div style={{ textAlign: "center", paddingTop: 48 }}>
          <p style={{ color: "#888", marginBottom: 16 }}>
            You haven't created any listings yet.
          </p>
          <button className="btn-red" style={{ width: "auto", padding: "8px 20px" }} onClick={() => navigate("/create")}>
            Post Your First Item
          </button>
        </div>
      ) : (
        <div className="listings-table-wrap">
          <table className="listings-table">
            <thead>
              <tr>
                <th>Image</th>
                <th>Title</th>
                <th>Price</th>
                <th>Category</th>
                <th>Status</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {listings.map((listing) => {
                const firstImg = [...listing.images].sort(
                  (a, b) => a.position - b.position
                )[0]
                return (
                  <tr key={listing.id}>
                    <td>
                      <div className="listing-thumb">
                        {firstImg ? (
                          <img
                            src={`${API_URL}/${firstImg.file_path}`}
                            alt={listing.title}
                          />
                        ) : (
                          <span style={{ color: "#ccc", fontSize: 12 }}>No Image</span>
                        )}
                      </div>
                    </td>
                    <td
                      style={{ fontWeight: 600, cursor: "pointer", color: "#E31837" }}
                      onClick={() => navigate(`/listings/${listing.id}`)}
                    >
                      {listing.title}
                    </td>
                    {/* Plugged in formatPrice here */}
                    <td style={{ fontWeight: 700 }}>{formatPrice(listing.price)}</td>
                    <td>{listing.category || "Other"}</td>
                    <td>
                      <span className={statusClass(listing.status)}>
                        {statusLabel(listing.status)}
                      </span>
                    </td>
                    <td style={{ textAlign: 'right', whiteSpace: "nowrap" }}>
                      <button
                        className="btn-table-action"
                        style={{ background: '#444' }} // Secondary color for Edit
                        onClick={() => navigate(`/listings/${listing.id}/edit`)}
                      >
                        Edit
                      </button>
                      <button
                        className="btn-table-action"
                        onClick={() => handleDelete(listing.id)}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}