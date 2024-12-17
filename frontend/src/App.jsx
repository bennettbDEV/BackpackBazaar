import React from "react"
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import { AuthProvider } from "./contexts/AuthProvider";
import ThemeProvider from './contexts/ThemeProvider';
import Login from "./pages/Login"
import Register from "./pages/Register"
import Home from "./pages/Home"
import NotFound from "./pages/NotFound"
import Profile from "./pages/Profile"
import Messages from "./pages/Messages"
import SingleListing from "./pages/SingleListing"
import FavoritedListings from "./pages/FavoritedListings"
import ProtectedRoute from "./components/ProtectedRoute"
import CreateListing from "./pages/CreateListing"
import Settings from "./pages/Settings"

function Logout() {
  localStorage.clear()
  return <Navigate to="/login" />
}

function RegisterAndLogout() {
  localStorage.clear()
  return <Register />
}

function App() {
  return (

    <BrowserRouter>
      <ThemeProvider>
        <AuthProvider>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/logout" element={<Logout />} />
            <Route path="/register" element={<RegisterAndLogout />} />
            <Route path="/listings/:listingId" element={<SingleListing />} />

            <Route path="/profile" element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            } />
            <Route
              path="/saved" element={
                <ProtectedRoute>
                  <FavoritedListings />
                </ProtectedRoute>
              }
            />
            <Route path="/createListing" element={
              <ProtectedRoute>
                <CreateListing />
              </ProtectedRoute>
            } />
            <Route path="/settings" element={
              <ProtectedRoute>
                <Settings />
              </ProtectedRoute>
            } />
            <Route path="/messages" element={
              <ProtectedRoute>
                <Messages />
              </ProtectedRoute>
            } />

            <Route path="*" element={<NotFound />}></Route>
          </Routes>
        </AuthProvider>
      </ThemeProvider>
    </BrowserRouter>

  )
}

export default App