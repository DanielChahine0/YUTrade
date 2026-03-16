
import { useState, useRef, useEffect } from "react"
import { useNavigate, useLocation } from "react-router-dom"
import { resetPassword } from "../api/auth"
import { isYorkUEmail, isValidPassword } from "../utils/validators" // Added Imports

const CODE_LENGTH = 6

export default function ResetPasswordPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const email = new URLSearchParams(location.search).get("email") || ""

  const [digits, setDigits] = useState<string[]>(Array(CODE_LENGTH).fill(""))
  const [newPassword, setNewPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState(false)
  const inputRefs = useRef<(HTMLInputElement | null)[]>([])

  useEffect(() => {
    if (!email || !isYorkUEmail(email)) {
      navigate("/forgot-password")
    }
  }, [email, navigate])

  const handleChange = (i: number, val: string) => {
    if (!/^\d?$/.test(val)) return
    const next = [...digits]
    next[i] = val
    setDigits(next)
    if (val && i < CODE_LENGTH - 1) inputRefs.current[i + 1]?.focus()
  }

  const handleKeyDown = (i: number, e: React.KeyboardEvent) => {
    if (e.key === "Backspace" && !digits[i] && i > 0)
      inputRefs.current[i - 1]?.focus()
  }

  const handlePaste = (e: React.ClipboardEvent) => {
    const pasted = e.clipboardData.getData("text").replace(/\D/g, "").slice(0, CODE_LENGTH)
    if (!pasted) return
    e.preventDefault()
    const next = [...digits]
    pasted.split("").forEach((ch, i) => { next[i] = ch })
    setDigits(next)
    inputRefs.current[Math.min(pasted.length, CODE_LENGTH - 1)]?.focus()
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const code = digits.join("")
    if (code.length < CODE_LENGTH) return

    const pwdCheck = isValidPassword(newPassword)
    if (!pwdCheck.valid) {
      setError(pwdCheck.message)
      return
    }

    if (newPassword !== confirmPassword) {
      setError("Passwords do not match")
      return
    }
    setError("")
    setLoading(true)
    try {
      await resetPassword({ email, code, new_password: newPassword })
      setSuccess(true)
      setTimeout(() => navigate("/login"), 2000)
    } catch (err: any) {
      if (err?.response?.status === 400) {
        setError(err.response.data?.detail || "Invalid or expired reset code")
      } else {
        setError("Something went wrong. Please try again.")
      }
    } finally {
      setLoading(false)
    }
  }

  if (success) {
    return (
      <div className="auth-page">
        <div className="auth-card">
          <span className="yu-logo">YUTrade</span>
          <h1 className="auth-title">Success!</h1>
          <div style={{ textAlign: "center", padding: "20px 0" }}>
             <p style={{ color: "#2e7d32", fontSize: 16, fontWeight: 600 }}>
               Password updated.
             </p>
             <p style={{ color: "#666", fontSize: 13 }}>Redirecting to login...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <span className="yu-logo">YUTrade</span>
        <h1 className="auth-title">New Password</h1>
        <p style={{ fontSize: 13, color: "#666", textAlign: "center", marginBottom: 20 }}>
          Enter the code sent to <br />
          <strong style={{ color: '#E31837' }}>{email}</strong>
        </p>

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="auth-field">
            <label className="auth-label">6-Digit Reset Code</label>
            <div className="verify-boxes" onPaste={handlePaste}>
              {digits.map((d, i) => (
                <input
                  key={i}
                  ref={(el) => { inputRefs.current[i] = el }}
                  className="verify-box"
                  type="text"
                  inputMode="numeric"
                  maxLength={1}
                  value={d}
                  onChange={(e) => handleChange(i, e.target.value)}
                  onKeyDown={(e) => handleKeyDown(i, e)}
                />
              ))}
            </div>
          </div>

          <div className="auth-field">
            <label className="auth-label">New Password</label>
            <input
              className="auth-input"
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
              placeholder="Min 8 characters"
            />
          </div>

          <div className="auth-field">
            <label className="auth-label">Confirm New Password</label>
            <input
              className="auth-input"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
            />
          </div>

          {error && <p className="auth-error">{error}</p>}

          <button
            className="btn-red"
            type="submit"
            style={{ marginBottom: 12 }}
            disabled={loading || digits.join("").length < CODE_LENGTH}
          >
            {loading ? "Updating..." : "Update Password"}
          </button>
          
          <button className="btn-outline" type="button" onClick={() => navigate(`/forgot-password?email=${encodeURIComponent(email)}`)}>
            Resend Code
          </button>
        </form>
      </div>
    </div>
  )
}
