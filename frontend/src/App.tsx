// Assigned to: Mai Komar
// Phase: 1 (F1.6)

import React from "react"
import { BrowserRouter, Routes, Route } from "react-router-dom"
import { AuthProvider } from "./context/AuthContext"
import RegisterPage from "./pages/RegisterPage"
import VerifyPage from "./pages/VerifyPage"
import LoginPage from "./pages/LoginPage"
import CreateListingPage from "./pages/CreateListingPage"
import ListingDetailPage from "./pages/ListingDetailPage"
import MyListingsPage from "./pages/MyListingsPage"
import SellerProfilePage from "./pages/SellerProfilePage"
import BrowsePage from "./pages/BrowsePage"
import ForgotPasswordPage from "./pages/ForgotPasswordPage"
import ResetPasswordPage from "./pages/ResetPasswordPage"
import EditListingPage from "./pages/EditListingPage"
import ProtectedRoute from "./components/ProtectedRoute"

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<BrowsePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/verify" element={<VerifyPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />
          <Route path="/create" element={<ProtectedRoute><CreateListingPage /></ProtectedRoute>} />
          <Route path="/listings/:id" element={<ListingDetailPage />} />
          <Route path="/listings/:id/edit" element={<ProtectedRoute><EditListingPage /></ProtectedRoute>} />
          <Route path="/my-listings" element={<ProtectedRoute><MyListingsPage /></ProtectedRoute>} />
          <Route path="/seller/:id" element={<SellerProfilePage />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
