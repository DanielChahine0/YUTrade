import { useState, useRef } from "react"
import { useNavigate, useLocation } from "react-router-dom"
import { resetPassword } from "../api/auth"

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
    if (newPassword.length < 8) {
      setError("Password must be at least 8 characters")
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
        <div className="verify-card">
          <span className="yu-logo">YUTrade</span>
          <h1 className="auth-title">Password Reset!</h1>
          <p style={{ textAlign: "center", color: "#2e7d32", fontSize: 14 }}>
            Your password has been updated. Redirecting to login…
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="auth-page">
      <div className="verify-card">
        <span className="yu-logo">YUTrade</span>
        <h1 className="auth-title">Reset Password</h1>
        <p style={{ fontSize: 12, color: "#666", textAlign: "center", marginBottom: 8 }}>
          Enter the 6-digit code sent to your email and choose a new password.
        </p>

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="auth-field">
            <label className="auth-label">Reset Code</label>
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
              minLength={8}
              placeholder="At least 8 characters"
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
              minLength={8}
            />
          </div>

          {error && <p className="auth-error">{error}</p>}

          <button
            className="btn-red"
            type="submit"
            disabled={loading || digits.join("").length < CODE_LENGTH}
          >
            {loading ? "Resetting…" : "Reset Password"}
          </button>
          <button className="btn-outline" type="button" onClick={() => navigate(`/forgot-password?email=${encodeURIComponent(email)}`)}>
            Resend Code
          </button>
        </form>
      </div>
    </div>
  )
}
