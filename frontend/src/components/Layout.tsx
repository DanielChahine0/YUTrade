// Assigned to: Harnaindeep Kaur
// Phase: 1 (F1.7)
//
// TODO: Main layout wrapper with Navbar and footer.
//
// Structure:
//   <div className="layout">
//     <Navbar />
//     <main className="main-content">
//       {children}
//     </main>
//     <footer className="footer">
//       <p>YU Trade &copy; 2026 — York University Campus Marketplace</p>
//     </footer>
//   </div>
//
// Props:
//   - children: React.ReactNode
//
// Styling:
//   - Use flexbox column layout so footer stays at bottom
//   - main-content should have max-width (e.g. 1200px) and auto margins for centering
//   - Padding on main content area

import React, { ReactNode } from "react"
import { Navbar } from "./Navbar"

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
                maxWidth: "1200px",
                margin: "0 auto",
                padding: "1rem"
            }}>
                {children}
            </main>

            <footer className="footer" style={{
                textAlign: "center",
                padding: "1rem",
                backgroundColor: "#f2f2f2",
                marginTop: "auto"
            }}>
                <p>YU Trade &copy; 2026 — York University Campus Marketplace</p>
            </footer>
        </div>
    )
}
