// Assigned to: Mai Komar
// Phase: 1 (F1.6)
// src/App.tsx
import React from "react"
import { Routes, Route } from "react-router-dom"
import ProtectedRoute from "./components/ProtectedRoute"
import { Layout } from "./components/Layout"
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
import MapsPage from './pages/MapsPage'
import MessagesPage from "./pages/MessagesPage"

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<BrowsePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/verify" element={<VerifyPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
        <Route path="/listings/:id" element={<ListingDetailPage />} />
        <Route path="/seller/:id" element={<SellerProfilePage />} />
        <Route path="/maps" element={<MapsPage />} />

        <Route
          path="/create"
          element={
            <ProtectedRoute>
              <CreateListingPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/listings/:id/edit"
          element={
            <ProtectedRoute>
              <EditListingPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/my-listings"
          element={
            <ProtectedRoute>
              <MyListingsPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/messages"
          element={
            <ProtectedRoute>
              <MessagesPage />
            </ProtectedRoute>
          }
        />
      </Routes>
    </Layout>
  )
}

export default App
