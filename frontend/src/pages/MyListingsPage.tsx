// Assigned to: Harnaindeep Kaur
// Phase: 2 (F2.6)

/* Assigned to: Harnaindeep Kaur */
/* Phase: 2 (F2.6) */

import React, { useState, useEffect, useContext } from "react"
import { useNavigate } from "react-router-dom"
import { getListings, deleteListing } from "../api/listings"
import { Listing } from "../types"
import { AuthContext } from "../context/AuthContext"
import { formatPrice } from "../utils/validators"

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000"

function statusLabel(status: string) {
  if (status === "active") return "Active"
  if (status === "pending") return "Pending"
  if (status === "sold") return "Sold"
  return "Inactive"
}

function statusClass(status: string) {
  if (status === "active") return "status-pill status-pill-active"
  if (status === "pending") return "status-pill status-pill-pending"
  if (status === "sold") return "status-pill status-pill-sold"
  return "status-pill status-pill-inactive"
}

export default function MyListingsPage() {
  const { user } = useContext(AuthContext)
  const navigate = useNavigate()
  const [listings, setListings] = useState<Listing[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user?.id) return

    getListings({ status: "all" })
      .then((data) => {
        const all: Listing[] = data.listings || []
        setListings(all.filter((l) => l.seller_id === user?.id && l.status !== "removed"))
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [user])

  const handleDelete = async (id: number) => {
    if (!window.confirm("Are you sure you want to permanently delete this listing? This cannot be undone.")) return

    try {
      await deleteListing(id)
      setListings((prev) => prev.filter((l) => l.id !== id))
    } catch {
      alert("Failed to delete listing.")
    }
  }

  return (
    <div className="app-content">

      {/* Header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 24
        }}
      >
        <h1 className="auth-title" style={{ margin: 0, textAlign: "left" }}>
          My Listings
        </h1>

        {/* ONLY show this button if not loading AND they already have listings */}
        {!loading && listings.length > 0 && (
          <button
            className="btn-red"
            style={{ width: "auto" }}
            onClick={() => navigate("/create")}
          >
            + Create New
          </button>
        )}
      </div>

      {loading ? (
        <p style={{ textAlign: "center", paddingTop: 48, color: "#aaa" }}>
          Loading...
        </p>
      ) : listings.length === 0 ? (

        /* EMPTY STATE - Shown only if listings.length is 0 */
        <div style={{ textAlign: "center", paddingTop: 48 }}>
          <p style={{ color: "#888", marginBottom: 16 }}>
            You haven't created any listings yet.
          </p>

          <button
            className="btn-red"
            style={{ width: "auto", padding: "8px 20px" }}
            onClick={() => navigate("/create")}
          >
            Post Your First Item
          </button>
        </div>

      ) : (

        /* LISTINGS TABLE - Shown only if they have postings */
        <div className="listings-table-wrap">
          <table className="listings-table">
            <thead>
              <tr>
                <th>Image</th>
                <th>Title</th>
                <th>Price</th>
                <th>Category</th>
                <th>Status</th>
                <th style={{ textAlign: "right" }}>Actions</th>
              </tr>
            </thead>

            <tbody>
              {listings.map((listing) => {
                const firstImg = listing.images && listing.images.length > 0
                  ? [...listing.images].sort((a, b) => a.position - b.position)[0]
                  : null

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
                          <span style={{ color: "#ccc", fontSize: 12 }}>
                            No Image
                          </span>
                        )}
                      </div>
                    </td>

                    <td
                      style={{
                        fontWeight: 600,
                        cursor: "pointer",
                        color: "#E31837"
                      }}
                      onClick={() => navigate(`/listings/${listing.id}`)}
                    >
                      {listing.title}
                    </td>

                    <td style={{ fontWeight: 700 }}>
                      {formatPrice(listing.price)}
                    </td>

                    <td>{listing.category || "Other"}</td>

                    <td>
                      <span className={statusClass(listing.status)}>
                        {statusLabel(listing.status)}
                      </span>
                    </td>

                    <td style={{ textAlign: "right", whiteSpace: "nowrap" }}>
                      <button
                        className="btn-table-action"
                        style={{ background: "#444", marginRight: 6 }}
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