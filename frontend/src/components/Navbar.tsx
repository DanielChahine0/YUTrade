// Assigned to: Harnaindeep Kaur
// Phase: 1 (F1.7)


import React from "react"
import { Link, useNavigate, useLocation } from "react-router-dom"
import { useAuth } from "../hooks/useAuth"

export const Navbar: React.FC = () => {
    const { isAuthenticated, user, logout } = useAuth()
    const navigate = useNavigate()
    const location = useLocation()  // <-- get current path

    const handleLogout = () => {
        logout()
        navigate("/login")
    }

    // Function to determine if a link is active
    const isActive = (path: string) => location.pathname === path

    const linkStyle = (path: string) => ({
        color: "white",
        textDecoration: "none",
        fontWeight: isActive(path) ? "bold" : "normal",
        borderBottom: isActive(path) ? "2px solid #fff" : "none",
        paddingBottom: "2px",
    })

    return (
        <nav className="navbar" style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
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

            <div className="navbar-links" style={{ display: "flex", gap: "1.5rem", alignItems: "center" }}>
                <Link to="/" style={linkStyle("/")}>Browse</Link>

                {isAuthenticated ? (
                    <>
                        <Link to="/create" style={linkStyle("/create")}>Sell Item</Link>
                        <Link to="/my-listings" style={linkStyle("/my-listings")}>My Listings</Link>
                        <Link to="/messages" style={linkStyle("/messages")}>Messages</Link>
                        <Link to="/maps" style={linkStyle("/maps")}>Maps</Link>
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
                        <Link to="/login" style={linkStyle("/login")}>Login</Link>
                        <Link to="/register" style={linkStyle("/register")}>Register</Link>
                    </>
                )}
            </div>
        </nav>
    )
}