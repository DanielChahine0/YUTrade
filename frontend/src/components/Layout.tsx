// Assigned to: Harnaindeep Kaur
// Phase: 1 (F1.7)

import React, { ReactNode } from "react"
import { Navbar } from "./Navbar"
import { Link } from "react-router-dom"

interface LayoutProps {
    children: ReactNode
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
    return (
        <div className="layout" style={{
            display: "flex",
            flexDirection: "column",
            minHeight: "100vh"
        }}>
            <Navbar />

            <main className="main-content" style={{
                flex: 1,
                maxWidth: "var(--container-width, 1280px)",
                width: "100%",
                margin: "0 auto",
                padding: "0"
            }}>
                {children}
            </main>

            <footer className="footer">
                <div className="footer-inner">
                    <div>
                        <div className="footer-brand">YUTrade</div>
                        <p className="footer-tagline">
                            The trusted marketplace for York University students.
                            Buy and sell safely within your campus community.
                        </p>
                    </div>
                    <div className="footer-links">
                        <Link to="/" className="footer-link">Browse</Link>
                        <Link to="/maps" className="footer-link">Safe Meetup Spots</Link>
                        <Link to="/register" className="footer-link">Join YUTrade</Link>
                    </div>
                </div>
                <div className="footer-bottom">
                    YUTrade &copy; {new Date().getFullYear()} &mdash; York University Campus Marketplace
                </div>
            </footer>
        </div>
    )
}
