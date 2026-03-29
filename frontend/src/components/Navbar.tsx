// Assigned to: Harnaindeep Kaur
// Phase: 1 (F1.7)

import React, { useState } from "react"
import { Link, useNavigate, useLocation } from "react-router-dom"
import { useAuth } from "../hooks/useAuth"

export const Navbar: React.FC = () => {
    const { isAuthenticated, user, logout } = useAuth()
    const navigate = useNavigate()
    const location = useLocation()
    const [mobileOpen, setMobileOpen] = useState(false)

    const handleLogout = () => {
        logout()
        navigate("/login")
        setMobileOpen(false)
    }

    const isActive = (path: string) => location.pathname === path

    const closeMobile = () => setMobileOpen(false)

    return (
        <>
            <nav className="navbar">
                <Link to="/" className="navbar-brand">
                    YU<span className="navbar-brand-accent">Trade</span>
                </Link>

                <div className="navbar-links">
                    <Link to="/" className={`navbar-link${isActive("/") ? " active" : ""}`}>
                        Browse
                    </Link>

                    {isAuthenticated ? (
                        <>
                            <Link to="/create" className={`navbar-link${isActive("/create") ? " active" : ""}`}>
                                Sell Item
                            </Link>
                            <Link to="/my-listings" className={`navbar-link${isActive("/my-listings") ? " active" : ""}`}>
                                My Listings
                            </Link>
                            <Link to="/messages" className={`navbar-link${isActive("/messages") ? " active" : ""}`}>
                                Messages
                            </Link>
                            <Link to="/maps" className={`navbar-link${isActive("/maps") ? " active" : ""}`}>
                                Maps
                            </Link>

                            <div className="navbar-divider" />

                            <span className="navbar-user">
                                {user?.name}
                            </span>
                            <Link to="/account" className={`navbar-link${isActive("/account") ? " active" : ""}`}>
                                Account
                            </Link>
                            <button onClick={handleLogout} className="navbar-logout">
                                Logout
                            </button>
                        </>
                    ) : (
                        <>
                            <Link to="/login" className={`navbar-link${isActive("/login") ? " active" : ""}`}>
                                Login
                            </Link>
                            <Link to="/register" className={`navbar-link${isActive("/register") ? " active" : ""}`}>
                                Register
                            </Link>
                        </>
                    )}
                </div>

                <button
                    className="navbar-hamburger"
                    onClick={() => setMobileOpen(!mobileOpen)}
                    aria-label="Toggle menu"
                >
                    {mobileOpen ? (
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                            <line x1="18" y1="6" x2="6" y2="18" />
                            <line x1="6" y1="6" x2="18" y2="18" />
                        </svg>
                    ) : (
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                            <line x1="3" y1="6" x2="21" y2="6" />
                            <line x1="3" y1="12" x2="21" y2="12" />
                            <line x1="3" y1="18" x2="21" y2="18" />
                        </svg>
                    )}
                </button>
            </nav>

            <div className={`navbar-mobile-menu${mobileOpen ? " open" : ""}`}>
                <Link to="/" className={`navbar-mobile-link${isActive("/") ? " active" : ""}`} onClick={closeMobile}>
                    Browse
                </Link>

                {isAuthenticated ? (
                    <>
                        <Link to="/create" className={`navbar-mobile-link${isActive("/create") ? " active" : ""}`} onClick={closeMobile}>
                            Sell Item
                        </Link>
                        <Link to="/my-listings" className={`navbar-mobile-link${isActive("/my-listings") ? " active" : ""}`} onClick={closeMobile}>
                            My Listings
                        </Link>
                        <Link to="/messages" className={`navbar-mobile-link${isActive("/messages") ? " active" : ""}`} onClick={closeMobile}>
                            Messages
                        </Link>
                        <Link to="/maps" className={`navbar-mobile-link${isActive("/maps") ? " active" : ""}`} onClick={closeMobile}>
                            Maps
                        </Link>
                        <Link to="/account" className={`navbar-mobile-link${isActive("/account") ? " active" : ""}`} onClick={closeMobile}>
                            Account ({user?.name})
                        </Link>
                        <button
                            className="navbar-mobile-link"
                            onClick={handleLogout}
                            style={{ background: "none", border: "none", textAlign: "left", cursor: "pointer", color: "rgba(255,255,255,0.9)", font: "inherit" }}
                        >
                            Logout
                        </button>
                    </>
                ) : (
                    <>
                        <Link to="/login" className={`navbar-mobile-link${isActive("/login") ? " active" : ""}`} onClick={closeMobile}>
                            Login
                        </Link>
                        <Link to="/register" className={`navbar-mobile-link${isActive("/register") ? " active" : ""}`} onClick={closeMobile}>
                            Register
                        </Link>
                    </>
                )}
            </div>
        </>
    )
}
