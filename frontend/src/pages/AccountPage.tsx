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
      <h1 className="auth-title" style={{ textAlign: "left", marginBottom: 32 }}>Account Settings</h1>

      {/* Profile Section */}
      <div className="account-section">
        <h2 className="account-section-title">Profile</h2>

        <form className="auth-form" onSubmit={handleNameUpdate}>
          <div className="auth-field">
            <label className="auth-label">Email</label>
            <input
              className="auth-input"
              type="text"
              value={user?.email || ""}
              disabled
              style={{ opacity: 0.6 }}
            />
          </div>

          <div className="auth-field">
            <label className="auth-label">Name</label>
            <input
              className="auth-input"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Your display name"
            />
          </div>

          {nameMsg && <p style={{ color: "var(--success-green)", fontSize: 14, fontWeight: 500 }}>{nameMsg}</p>}
          {nameError && <p className="auth-error">{nameError}</p>}

          <button className="btn-red" type="submit">
            Update Name
          </button>
        </form>
      </div>

      {/* Password Section */}
      <div className="account-section">
        <h2 className="account-section-title">Change Password</h2>

        <form className="auth-form" onSubmit={handlePasswordChange}>
          <div className="auth-field">
            <label className="auth-label">Current Password</label>
            <input
              className="auth-input"
              type="password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              placeholder="Enter current password"
            />
          </div>

          <div className="auth-field">
            <label className="auth-label">New Password</label>
            <input
              className="auth-input"
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="Enter new password"
            />
          </div>

          <div className="auth-field">
            <label className="auth-label">Confirm New Password</label>
            <input
              className="auth-input"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Confirm new password"
            />
          </div>

          {pwMsg && <p style={{ color: "var(--success-green)", fontSize: 14, fontWeight: 500 }}>{pwMsg}</p>}
          {pwError && <p className="auth-error">{pwError}</p>}

          <button className="btn-red" type="submit">
            Change Password
          </button>
        </form>
      </div>

      {/* Delete Account Section */}
      <div className="account-section account-danger">
        <h2 className="account-section-title">Delete Account</h2>
        <p style={{ fontSize: 14, color: "var(--text-secondary)", marginBottom: 20, lineHeight: 1.6 }}>
          This will permanently delete your account, all your listings, messages, and ratings. This action cannot be undone.
        </p>

        <form className="auth-form" onSubmit={handleDeleteAccount}>
          <div className="auth-field">
            <label className="auth-label">Confirm Password</label>
            <input
              className="auth-input"
              type="password"
              value={deletePassword}
              onChange={(e) => setDeletePassword(e.target.value)}
              placeholder="Enter your password to confirm"
            />
          </div>

          {deleteError && <p className="auth-error">{deleteError}</p>}

          <button className="btn-red" type="submit">
            Delete My Account
          </button>
        </form>
      </div>
    </div>
  )
}
