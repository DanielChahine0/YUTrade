// Phase: 2 (F2.6)
// Edit existing listing page (protected — owner only).

import React, { useState, useEffect } from "react"
import { useNavigate, useParams } from "react-router-dom"
import { getListing, updateListing } from "../api/listings"
import ImageUpload from "../components/ImageUpload"

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000"

interface ExistingImage {
  id: number
  file_path: string
  position: number
}

export default function EditListingPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [price, setPrice] = useState("")
  const [category, setCategory] = useState("")
  const [status, setStatus] = useState("active")
  const [existingImages, setExistingImages] = useState<ExistingImage[]>([])
  const [deleteImageIds, setDeleteImageIds] = useState<number[]>([])
  const [newImages, setNewImages] = useState<File[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState("")

  useEffect(() => {
    if (!id) return
    getListing(parseInt(id))
      .then((listing) => {
        setTitle(listing.title)
        setDescription(listing.description || "")
        setPrice(listing.price.toString())
        setCategory(listing.category || "")
        setStatus(listing.status)
        setExistingImages(listing.images || [])
      })
      .catch(() => setError("Failed to load listing."))
      .finally(() => setLoading(false))
  }, [id])

  const toggleDeleteImage = (imageId: number) => {
    setDeleteImageIds((prev) =>
      prev.includes(imageId) ? prev.filter((i) => i !== imageId) : [...prev, imageId]
    )
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    if (!title.trim()) {
      setError("Title is required")
      return
    }
    const priceNum = parseFloat(price)
    if (isNaN(priceNum) || priceNum < 0.01) {
      setError("Price must be at least $0.01")
      return
    }
    setSaving(true)
    try {
      await updateListing(parseInt(id!), {
        title: title.trim(),
        description: description.trim() || undefined,
        price: priceNum,
        category: category || undefined,
        status,
        newImages: newImages.length > 0 ? newImages : undefined,
        deleteImageIds: deleteImageIds.length > 0 ? deleteImageIds : undefined,
      })
      navigate(`/listings/${id}`)
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to update listing.")
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="auth-page">
        <p style={{ textAlign: "center", color: "#aaa" }}>Loading…</p>
      </div>
    )
  }

  return (
    <div className="auth-page">
      <div className="auth-card" style={{ width: 500 }}>
        <h1 className="auth-title">Edit Listing</h1>

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="auth-field">
            <label className="auth-label">Title *</label>
            <input
              className="auth-input"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              maxLength={200}
              required
            />
          </div>

          <div className="auth-field">
            <label className="auth-label">Description</label>
            <textarea
              className="auth-input listing-textarea"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>

          <div className="auth-field">
            <label className="auth-label">Price ($) *</label>
            <input
              className="auth-input"
              type="number"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              min={0.01}
              step={0.01}
              required
            />
          </div>

          <div className="auth-field">
            <label className="auth-label">Category</label>
            <select
              className="auth-input listing-select"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
            >
              <option value="">-- Select Category --</option>
              <option value="Textbooks">Textbooks</option>
              <option value="Electronics">Electronics</option>
              <option value="Furniture">Furniture</option>
              <option value="Clothing">Clothing</option>
              <option value="Other">Other</option>
            </select>
          </div>

          <div className="auth-field">
            <label className="auth-label">Status</label>
            <select
              className="auth-input listing-select"
              value={status}
              onChange={(e) => setStatus(e.target.value)}
            >
              <option value="active">Active</option>
              <option value="sold">Sold</option>
              <option value="removed">Removed</option>
            </select>
          </div>

          {existingImages.length > 0 && (
            <div className="auth-field">
              <label className="auth-label">Current Photos</label>
              <div className="image-previews">
                {existingImages.map((img) => {
                  const markedForDeletion = deleteImageIds.includes(img.id)
                  return (
                    <div
                      key={img.id}
                      className="image-preview"
                      style={{ opacity: markedForDeletion ? 0.35 : 1 }}
                    >
                      <img
                        src={`${API_URL}/${img.file_path}`}
                        alt={`Photo ${img.position + 1}`}
                      />
                      <button
                        type="button"
                        onClick={() => toggleDeleteImage(img.id)}
                        title={markedForDeletion ? "Undo remove" : "Remove photo"}
                      >
                        {markedForDeletion ? "↩" : "×"}
                      </button>
                    </div>
                  )
                })}
              </div>
              {deleteImageIds.length > 0 && (
                <p style={{ fontSize: 12, color: "#e55", margin: "4px 0 0" }}>
                  {deleteImageIds.length} photo{deleteImageIds.length > 1 ? "s" : ""} will be removed on save.
                </p>
              )}
            </div>
          )}

          <div className="auth-field">
            <label className="auth-label">Add New Photos</label>
            <ImageUpload images={newImages} onChange={setNewImages} />
          </div>

          {error && <p className="auth-error">{error}</p>}

          <button className="btn-red" type="submit" disabled={saving}>
            {saving ? "Saving…" : "Save Changes"}
          </button>

          <button className="btn-outline" type="button" onClick={() => navigate(-1)}>
            Cancel
          </button>
        </form>
      </div>
    </div>
  )
}
