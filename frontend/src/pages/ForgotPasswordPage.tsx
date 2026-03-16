
import { useState } from "react"
import { useNavigate, useLocation } from "react-router-dom"
import { forgotPassword } from "../api/auth"
import { isYorkUEmail } from "../utils/validators" // Added Import

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

    if (!isYorkUEmail(email)) {
      setError("Please enter a valid YorkU email (@yorku.ca or @my.yorku.ca)")
      return
    }

    setLoading(true)
    try {
      await forgotPassword({ email })
      setSent(true)
      // Small delay so user can see the success message
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
        <h1 className="auth-title">Reset Password</h1>
        <p style={{ fontSize: 13, color: "#666", textAlign: "center", marginBottom: 20 }}>
          Enter your YorkU email to receive a <br /> 6-digit verification code.
        </p>

        {sent ? (
          <div style={{ textAlign: "center", padding: "20px 0" }}>
            <p style={{ color: "#2e7d32", fontSize: 15, fontWeight: 600 }}>
              Reset code sent!
            </p>
            <p style={{ color: "#666", fontSize: 13 }}>Redirecting to verification...</p>
          </div>
        ) : (
          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="auth-field">
              <label className="auth-label">YorkU Email</label>
              <input
                className="auth-input"
                type="email"
                placeholder="student@my.yorku.ca"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            {error && <p className="auth-error">{error}</p>}

            <button className="btn-red" type="submit" disabled={loading} style={{ marginBottom: 12 }}>
              {loading ? "Sending..." : "Send Reset Code"}
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