// Assigned to: Mai Komar
// Phase: 1 (F1.5)

import { useState, useEffect, useRef } from "react"
import { useNavigate, useLocation } from "react-router-dom"
import { verify, resendVerification } from "../api/auth"
import { isYorkUEmail } from "../utils/validators"

const CODE_LENGTH = 6
const RESEND_SECONDS = 60

export default function VerifyPage() {
  const navigate = useNavigate()
  const location = useLocation()

  const email = new URLSearchParams(location.search).get("email") || ""

  const [digits, setDigits] = useState<string[]>(Array(CODE_LENGTH).fill(""))
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [countdown, setCountdown] = useState(RESEND_SECONDS)
  const inputRefs = useRef<(HTMLInputElement | null)[]>([])

  useEffect(() => {
    if (!email || !isYorkUEmail(email)) {
      navigate("/register")
    }
  }, [email, navigate])

  useEffect(() => {
    if (countdown <= 0) return
    const t = setTimeout(() => setCountdown((c) => c - 1), 1000)
    return () => clearTimeout(t)
  }, [countdown])

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

    setError("")
    setLoading(true)
    try {
      await verify({ email, code })
      navigate("/login")
    } catch {
      setError("Invalid or expired verification code")
    } finally {
      setLoading(false)
    }
  }

  const handleResend = async () => {
    setError("")
    try {
      await resendVerification(email)
      setCountdown(RESEND_SECONDS)
      setDigits(Array(CODE_LENGTH).fill(""))
      inputRefs.current[0]?.focus()
    } catch {
      setError("Failed to resend code. Please try again.")
    }
  }

  const fmt = (s: number) =>
    `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`

  return (
    <div className="auth-split-page">
      {/* ── Left branded panel ── */}
      <div className="auth-split-left">
        <span className="auth-brand-mark">YUTrade</span>
        <h2 className="auth-brand-headline">Almost there!</h2>
        <p className="auth-brand-desc">
          We sent a 6-digit code to your YorkU email. Enter it to activate your account.
        </p>
        <div className="auth-brand-pills">
          <div className="auth-brand-pill">
            <span className="auth-brand-pill-icon">✉</span> Check your inbox
          </div>
          <div className="auth-brand-pill">
            <span className="auth-brand-pill-icon">⏱</span> Code expires in 15 min
          </div>
          <div className="auth-brand-pill">
            <span className="auth-brand-pill-icon">↩</span> Can resend if needed
          </div>
        </div>
      </div>

      {/* ── Right form panel ── */}
      <div className="auth-split-right">
        <div className="auth-split-form-box">
          <h1 className="auth-title-lg">Verify Your Email</h1>
          <p className="auth-subtitle-sm">
            Code sent to <strong style={{ color: "#E31837" }}>{email}</strong>
          </p>

          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="auth-field">
              <label className="auth-label">6-Digit Code</label>
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

            {error && <p className="auth-error">{error}</p>}

            <p className="verify-countdown" style={{ textAlign: "center", fontSize: 13, margin: "4px 0 2px" }}>
              {countdown > 0
                ? `Resend available in ${fmt(countdown)}`
                : "You can now resend the code"}
            </p>

            <button
              type="submit"
              className="btn-red"
              disabled={loading || digits.join("").length < CODE_LENGTH}
            >
              {loading ? "Verifying..." : "Verify Account"}
            </button>

            <button
              type="button"
              className="btn-outline"
              onClick={handleResend}
              disabled={countdown > 0}
            >
              Resend Code
            </button>
          </form>

          <p className="auth-bottom-link">
            Wrong email?{" "}
            <button type="button" onClick={() => navigate("/register")}>
              Go back
            </button>
          </p>
        </div>
      </div>
    </div>
  )
}
