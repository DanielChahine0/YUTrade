import { useState } from "react"
import { useNavigate, useLocation } from "react-router-dom"
import { forgotPassword } from "../api/auth"

export default function ForgotPasswordPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const prefilled = new URLSearchParams(location.search).get("email") || ""

  const [email, setEmail] = useState(prefilled)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [sent, setSent] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setLoading(true)
    try {
      await forgotPassword({ email })
      setSent(true)
      setTimeout(() => navigate(`/reset-password?email=${encodeURIComponent(email)}`), 1500)
    } catch (err: any) {
      if (err?.response?.status === 404) {
        setError("No account found with this email.")
      } else {
        setError("Something went wrong. Please try again.")
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <span className="yu-logo">YUTrade</span>
        <h1 className="auth-title">Forgot Password</h1>
        <p style={{ fontSize: 12, color: "#666", textAlign: "center", marginBottom: 8 }}>
          Enter your YorkU email and we'll send you a 6-digit reset code.
        </p>

        {sent ? (
          <p style={{ textAlign: "center", color: "#2e7d32", fontSize: 14 }}>
            Reset code sent! Redirecting…
          </p>
        ) : (
          <form className="auth-form" onSubmit={handleSubmit}>
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

            {error && <p className="auth-error">{error}</p>}

            <button className="btn-red" type="submit" disabled={loading}>
              {loading ? "Sending…" : "Send Reset Code"}
            </button>
            <button className="btn-outline" type="button" onClick={() => navigate("/login")}>
              Back to Login
            </button>
          </form>
        )}
      </div>
    </div>
  )
}
