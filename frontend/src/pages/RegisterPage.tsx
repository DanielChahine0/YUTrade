// Assigned to: Mai Komar
// Phase: 1 (F1.5)

import React, { useState } from "react"
import { useNavigate } from "react-router-dom"
import { register } from "../api/auth"
import { isYorkUEmail, isValidPassword } from "../utils/validators"

const EyeIcon = ({ open }: { open: boolean }) =>
  open ? (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  ) : (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94" />
      <path d="M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19" />
      <line x1="1" y1="1" x2="23" y2="23" />
    </svg>
  )

const RegisterPage: React.FC = () => {
  const navigate = useNavigate()
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [showPwd, setShowPwd] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")

    if (!isYorkUEmail(email)) {
      setError("Must use a YorkU email (@my.yorku.ca or @yorku.ca)")
      return
    }

    const pwdCheck = isValidPassword(password)
    if (!pwdCheck.valid) {
      setError(pwdCheck.message)
      return
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match")
      return
    }

    setLoading(true)
    try {
      await register({ name, email, password })
      navigate("/login")
    } catch (err: any) {
      if (err.response?.status === 409) {
        setError("Email already registered")
      } else if (err.response?.status === 400) {
        setError("Must use a YorkU email")
      } else {
        setError("Registration failed")
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-split-page">
      {/* ── Left branded panel ── */}
      <div className="auth-split-left">
        <span className="auth-brand-mark">YUTrade</span>
        <h2 className="auth-brand-headline">Your Campus Marketplace</h2>
        <p className="auth-brand-desc">
          Buy and sell with fellow York University students — safely, easily, and for free.
        </p>
        <div className="auth-brand-pills">
          <div className="auth-brand-pill">
            <span className="auth-brand-pill-icon">✓</span> YU students only
          </div>
          <div className="auth-brand-pill">
            <span className="auth-brand-pill-icon">✓</span> Free to list
          </div>
          <div className="auth-brand-pill">
            <span className="auth-brand-pill-icon">✓</span> Direct messaging
          </div>
        </div>
      </div>

      {/* ── Right form panel ── */}
      <div className="auth-split-right">
        <div className="auth-split-form-box">
          <h1 className="auth-title-lg">Create Account</h1>
          <p className="auth-subtitle-sm">Join the YU community today</p>

          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="auth-field">
              <label className="auth-label">Full Name</label>
              <input
                className="auth-input"
                type="text"
                placeholder="Jane Smith"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>

            <div className="auth-field">
              <label className="auth-label">YorkU Email</label>
              <input
                className="auth-input"
                type="email"
                placeholder="you@my.yorku.ca"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div className="auth-field">
              <label className="auth-label">Password</label>
              <div className="auth-input-wrap">
                <input
                  className="auth-input auth-input-padded-right"
                  type={showPwd ? "text" : "password"}
                  placeholder="Min. 8 characters"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
                <button
                  type="button"
                  className="auth-input-eye"
                  onClick={() => setShowPwd((v) => !v)}
                  tabIndex={-1}
                  aria-label={showPwd ? "Hide password" : "Show password"}
                >
                  <EyeIcon open={showPwd} />
                </button>
              </div>
            </div>

            <div className="auth-field">
              <label className="auth-label">Confirm Password</label>
              <div className="auth-input-wrap">
                <input
                  className="auth-input auth-input-padded-right"
                  type={showConfirm ? "text" : "password"}
                  placeholder="Repeat password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                />
                <button
                  type="button"
                  className="auth-input-eye"
                  onClick={() => setShowConfirm((v) => !v)}
                  tabIndex={-1}
                  aria-label={showConfirm ? "Hide password" : "Show password"}
                >
                  <EyeIcon open={showConfirm} />
                </button>
              </div>
            </div>

            {error && <p className="auth-error">{error}</p>}

            <button className="btn-red" type="submit" disabled={loading}>
              {loading ? "Creating account..." : "Create Account"}
            </button>
          </form>

          <p className="auth-bottom-link">
            Already have an account?{" "}
            <button type="button" onClick={() => navigate("/login")}>
              Login
            </button>
          </p>
        </div>
      </div>
    </div>
  )
}

export default RegisterPage
