// Assigned to: Mai Komar
// Phase: 1 (F1.5)
//
// TODO: Login page.
//
// Form fields:
//   - Email (email input, required)
//   - Password (password input, required)
//
// Behavior:
//   1. On submit, call api/auth.ts login({ email, password })
//   2. On success:
//      - Call auth context's login(token, user) to store JWT and user
//      - Redirect to / (BrowsePage)
//   3. On 401 error: show "Invalid email or password"
//   4. On 403 error: show "Please verify your email first" with link to /verify
//   5. Show loading spinner while request is in flight
//
// Styling: Use YU branding (red #E31837 for submit button)
// Links:
//   - "Don't have an account? Register" -> /register
//   - "Need to verify your email?" -> /verify

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login as apiLogin } from "../api/auth";
import { useAuth } from "../hooks/useAuth";
import { isYorkUEmail } from "../utils/validators"; // Added Import
import "../styles/global.css"

export default function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (!isYorkUEmail(email)) {
      setError("Please use your YorkU email (@yorku.ca or @my.yorku.ca)");
      return;
    }

    setLoading(true);
    try {
      const { access_token, user } = await apiLogin({ email, password });
      login(access_token, user);
      navigate("/");
    } catch (err: any) {
      if (err?.response?.status === 404) setError("__no_account__");
      else if (err?.response?.status === 401) setError("Invalid password. Please try again.");
      else setError("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <span className="yu-logo">YUTrade</span>
        <h1 className="auth-title">Welcome Back</h1>
        
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

          <div className="auth-field">
            <label className="auth-label">Password</label>
            <input
              className="auth-input"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {/* Error Handling */}
          {error === "__no_account__" ? (
            <div className="auth-error" style={{ textAlign: "center" }}>
              No account found with this email.{" "}
              <span
                style={{ textDecoration: "underline", cursor: "pointer", fontWeight: 'bold' }}
                onClick={() => navigate("/register")}
              >
                Register here?
              </span>
            </div>
          ) : error ? (
            <p className="auth-error">{error}</p>
          ) : null}

          {/* Forgot Password Link */}
          <div style={{ textAlign: "right", marginBottom: 15 }}>
            <span
              style={{ color: "#888", fontSize: 13, cursor: "pointer", textDecoration: 'underline' }}
              onClick={() => navigate(`/forgot-password?email=${encodeURIComponent(email)}`)}
            >
              Forgot password?
            </span>
          </div>

          <button className="btn-red" type="submit" disabled={loading} style={{ marginBottom: 12 }}>
            {loading ? "Logging in..." : "Login"}
          </button>

          <div style={{ textAlign: 'center', marginTop: 10 }}>
            <p className="reg-text" style={{ marginBottom: 8 }}>Don't have an account?</p>
            <button className="btn-outline" type="button" onClick={() => navigate("/register")}>
              Create New Account
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
