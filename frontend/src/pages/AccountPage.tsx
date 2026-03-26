import React, { useState, useContext } from "react"
import { useNavigate } from "react-router-dom"
import { AuthContext } from "../context/AuthContext"
import { updateProfile, changePassword, deleteAccount } from "../api/auth"

export default function AccountPage() {
  const { user, login, token, logout } = useContext(AuthContext)
  const navigate = useNavigate()

  const [name, setName] = useState(user?.name || "")
  const [nameMsg, setNameMsg] = useState("")
  const [nameError, setNameError] = useState("")

  const [currentPassword, setCurrentPassword] = useState("")
  const [newPassword, setNewPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [pwMsg, setPwMsg] = useState("")
  const [pwError, setPwError] = useState("")

  const [deletePassword, setDeletePassword] = useState("")
  const [deleteError, setDeleteError] = useState("")

  const handleNameUpdate = async (e: React.FormEvent) => {
    e.preventDefault()
    setNameMsg("")
    setNameError("")

    if (!name.trim()) {
      setNameError("Name cannot be empty.")
      return
    }

    try {
      const updatedUser = await updateProfile({ name: name.trim() })
      // Update AuthContext so the navbar reflects the new name
      if (token) {
        login(token, updatedUser)
      }
      setNameMsg("Name updated successfully.")
    } catch (err: any) {
      setNameError(err.response?.data?.detail || "Failed to update name.")
    }
  }

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault()
    setPwMsg("")
    setPwError("")

    if (!currentPassword || !newPassword) {
      setPwError("Please fill in all password fields.")
      return
    }
    if (newPassword.length < 6) {
      setPwError("New password must be at least 6 characters.")
      return
    }
    if (newPassword !== confirmPassword) {
      setPwError("New passwords do not match.")
      return
    }

    try {
      await changePassword({ current_password: currentPassword, new_password: newPassword })
      setPwMsg("Password changed successfully.")
      setCurrentPassword("")
      setNewPassword("")
      setConfirmPassword("")
    } catch (err: any) {
      setPwError(err.response?.data?.detail || "Failed to change password.")
    }
  }

  const handleDeleteAccount = async (e: React.FormEvent) => {
    e.preventDefault()
    setDeleteError("")

    if (!deletePassword) {
      setDeleteError("Please enter your password to confirm.")
      return
    }

    if (!window.confirm("Are you sure you want to permanently delete your account? All your listings, messages, and ratings will be removed. This cannot be undone.")) {
      return
    }

    try {
      await deleteAccount({ password: deletePassword })
      logout()
      navigate("/login")
    } catch (err: any) {
      setDeleteError(err.response?.data?.detail || "Failed to delete account.")
    }
  }

  return (
    <div className="app-content">
      <h1 className="auth-title" style={{ textAlign: "left" }}>Account Settings</h1>

      {/* Profile Section */}
      <div className="auth-card" style={{ maxWidth: 500, marginBottom: 32 }}>
        <h2 style={{ fontSize: 18, marginBottom: 16 }}>Profile</h2>

        <form onSubmit={handleNameUpdate}>
          <label className="auth-label">Email</label>
          <input
            className="auth-input"
            type="text"
            value={user?.email || ""}
            disabled
            style={{ backgroundColor: "#f5f5f5", color: "#888" }}
          />

          <label className="auth-label">Name</label>
          <input
            className="auth-input"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Your display name"
          />

          {nameMsg && <p style={{ color: "green", fontSize: 14 }}>{nameMsg}</p>}
          {nameError && <p style={{ color: "red", fontSize: 14 }}>{nameError}</p>}

          <button className="btn-red" type="submit" style={{ marginTop: 8 }}>
            Update Name
          </button>
        </form>
      </div>

      {/* Password Section */}
      <div className="auth-card" style={{ maxWidth: 500, marginBottom: 32 }}>
        <h2 style={{ fontSize: 18, marginBottom: 16 }}>Change Password</h2>

        <form onSubmit={handlePasswordChange}>
          <label className="auth-label">Current Password</label>
          <input
            className="auth-input"
            type="password"
            value={currentPassword}
            onChange={(e) => setCurrentPassword(e.target.value)}
            placeholder="Enter current password"
          />

          <label className="auth-label">New Password</label>
          <input
            className="auth-input"
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            placeholder="Enter new password"
          />

          <label className="auth-label">Confirm New Password</label>
          <input
            className="auth-input"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="Confirm new password"
          />

          {pwMsg && <p style={{ color: "green", fontSize: 14 }}>{pwMsg}</p>}
          {pwError && <p style={{ color: "red", fontSize: 14 }}>{pwError}</p>}

          <button className="btn-red" type="submit" style={{ marginTop: 8 }}>
            Change Password
          </button>
        </form>
      </div>

      {/* Delete Account Section */}
      <div className="auth-card" style={{ maxWidth: 500, border: "1px solid #E31837" }}>
        <h2 style={{ fontSize: 18, marginBottom: 8, color: "#E31837" }}>Delete Account</h2>
        <p style={{ fontSize: 14, color: "#666", marginBottom: 16 }}>
          This will permanently delete your account, all your listings, messages, and ratings. This action cannot be undone.
        </p>

        <form onSubmit={handleDeleteAccount}>
          <label className="auth-label">Confirm Password</label>
          <input
            className="auth-input"
            type="password"
            value={deletePassword}
            onChange={(e) => setDeletePassword(e.target.value)}
            placeholder="Enter your password to confirm"
          />

          {deleteError && <p style={{ color: "red", fontSize: 14 }}>{deleteError}</p>}

          <button
            type="submit"
            style={{
              marginTop: 8,
              width: "100%",
              padding: "10px",
              backgroundColor: "#E31837",
              color: "white",
              border: "none",
              borderRadius: "4px",
              fontWeight: "bold",
              cursor: "pointer",
            }}
          >
            Delete My Account
          </button>
        </form>
      </div>
    </div>
  )
}
