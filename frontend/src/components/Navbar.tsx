// Assigned to: Harnaindeep Kaur
// Phase: 1 (F1.7)
//
// TODO: Navigation bar with YU branding.
//
// Structure:
//   <nav className="navbar">
//     <Link to="/" className="navbar-brand">YU Trade</Link>
//     <div className="navbar-links">
//       {/* Always visible */}
//       <Link to="/">Browse</Link>
//
//       {/* Visible when logged in */}
//       <Link to="/create">Sell Item</Link>
//       <Link to="/my-listings">My Listings</Link>
//       <Link to="/messages">Messages</Link>
//       <span>Hello, {user.name}</span>
//       <button onClick={logout}>Logout</button>
//
//       {/* Visible when NOT logged in */}
//       <Link to="/login">Login</Link>
//       <Link to="/register">Register</Link>
//     </div>
//   </nav>
//
// Behavior:
//   - Use useAuth() hook to check isAuthenticated and get user/logout
//   - Conditionally render links based on auth state
//
// Styling:
//   - Background: YU red (#E31837) or white with red accents
//   - Text/links: white (on red bg) or dark (on white bg)
//   - Horizontal layout, logo left, links right
//   - Responsive: hamburger menu on mobile (optional stretch goal)
import React from "react"
import { Link } from "react-router-dom"
import { useAuth } from "../hooks/useAuth"

export const Navbar: React.FC = () => {
    const { isAuthenticated, user, logout } = useAuth()

    return (
        <nav className="navbar" style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            padding: "0.5rem 1rem",
            backgroundColor: "#E31837",
            color: "white"
        }}>
            <Link to="/" className="navbar-brand" style={{ color: "white", fontWeight: "bold" }}>
                YU Trade
            </Link>

            <div className="navbar-links" style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
                <Link to="/" style={{ color: "white" }}>Browse</Link>

                {isAuthenticated ? (
                    <>
                        <Link to="/create" style={{ color: "white" }}>Sell Item</Link>
                        <Link to="/my-listings" style={{ color: "white" }}>My Listings</Link>
                        <Link to="/messages" style={{ color: "white" }}>Messages</Link>
                        <span>Hello, {user?.name}</span>
                        <button onClick={logout} style={{
                            background: "white",
                            color: "#E31837",
                            border: "none",
                            padding: "0.25rem 0.5rem",
                            cursor: "pointer"
                        }}>Logout</button>
                    </>
                ) : (
                    <>
                        <Link to="/login" style={{ color: "white" }}>Login</Link>
                        <Link to="/register" style={{ color: "white" }}>Register</Link>
                    </>
                )}
            </div>
        </nav>
    )
}