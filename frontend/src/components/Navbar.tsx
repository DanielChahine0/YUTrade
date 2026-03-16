// Assigned to: Harnaindeep Kaur
// Phase: 1 (F1.7)

import React from "react"
import { Link, useNavigate } from "react-router-dom"
import { useAuth } from "../hooks/useAuth"

export const Navbar: React.FC = () => {
    const { isAuthenticated, user, logout } = useAuth()
    const navigate = useNavigate()

    const handleLogout = () => {
        logout()
        navigate("/login")
    }

    return (
        <nav className="navbar" style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            // Increased padding from 0.5rem to 1.5rem to make it thicker
            padding: "1.5rem 2rem", 
            backgroundColor: "#E31837",
            color: "white",
            boxShadow: "0 2px 4px rgba(0,0,0,0.1)"
        }}>
            <Link to="/" className="navbar-brand" style={{ 
                color: "white", 
                fontWeight: "bold", 
                fontSize: "1.5rem", 
                textDecoration: "none" 
            }}>
                YU Trade
            </Link>

            <div className="navbar-links" style={{ 
                display: "flex", 
                gap: "1.5rem", 
                alignItems: "center" 
            }}>
                <Link to="/" style={{ color: "white", textDecoration: "none" }}>Browse</Link>

                {isAuthenticated ? (
                    <>
                        <Link to="/create" style={{ color: "white", textDecoration: "none" }}>Sell Item</Link>
                        <Link to="/my-listings" style={{ color: "white", textDecoration: "none" }}>My Listings</Link>
                        <Link to="/messages" style={{ color: "white", textDecoration: "none" }}>Messages</Link>
                        <span style={{ borderLeft: "1px solid rgba(255,255,255,0.3)", paddingLeft: "1rem" }}>
                            Hello, {user?.name}
                        </span>
                        <button onClick={handleLogout} style={{
                            background: "white",
                            color: "#E31837",
                            border: "none",
                            padding: "0.5rem 1rem",
                            borderRadius: "4px",
                            fontWeight: "bold",
                            cursor: "pointer"
                        }}>
                            Logout
                        </button>
                    </>
                ) : (
                    <>
                        <Link to="/login" style={{ color: "white", textDecoration: "none" }}>Login</Link>
                        <Link to="/register" style={{ color: "white", textDecoration: "none" }}>Register</Link>
                    </>
                )}
            </div>
        </nav>
    )
}
