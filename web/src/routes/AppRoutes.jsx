import { Routes, Route } from "react-router-dom";
import LandingPage from "../pages/LandingPage";
import DevStatusPage from "../pages/DevStatusPage";
import RegisterPage from "../pages/RegisterPage";
import LoginPage from "../pages/LoginPage";
import CheckInboxPage from "../pages/CheckInboxPage";
import VerifyEmailPage from "../pages/VerifyEmailPage";
import ForgotPasswordPage from "../pages/ForgotPasswordPage";
import ResetPasswordPage from "../pages/ResetPasswordPage";
import ProfilePage from "../pages/ProfilePage";
import TripPlanChatPage from "../pages/TripPlanChatPage";
import MyTripsPage from "../pages/MyTripsPage";
import TripItineraryPage from "../pages/TripItineraryPage";
import UserLayout from "../pages/UserLayout";
import AdminLayout from "../pages/admin/AdminLayout";
import AdminDashboard from "../pages/admin/AdminDashboard";
import DestinationsList from "../pages/admin/DestinationsList";
import AttractionsList from "../pages/admin/AttractionsList";
import HotelsList from "../pages/admin/HotelsList";
import RestaurantsList from "../pages/admin/RestaurantsList";
import LocalEventsList from "../pages/admin/LocalEventsList";
import ComingSoon from "../pages/admin/ComingSoon";
import ProtectedRoute from "./ProtectedRoute";
import AdminRoute from "./AdminRoute";
import NotFoundPage from "../pages/NotFoundPage";

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      {import.meta.env.DEV && (
        <Route path="/dev/status" element={<DevStatusPage />} />
      )}
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/check-inbox" element={<CheckInboxPage />} />
      <Route path="/verify-email" element={<VerifyEmailPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/reset-password" element={<ResetPasswordPage />} />
      <Route
        element={
          <ProtectedRoute>
            <UserLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/chat" element={<TripPlanChatPage />} />
        <Route path="/trips" element={<MyTripsPage />} />
        <Route path="/trips/:tripId" element={<TripItineraryPage />} />
      </Route>
      <Route
        path="/admin"
        element={
          <AdminRoute>
            <AdminLayout />
          </AdminRoute>
        }
      >
        <Route index element={<AdminDashboard />} />
        <Route path="destinations" element={<DestinationsList />} />
        <Route path="attractions" element={<AttractionsList />} />
        <Route path="hotels" element={<HotelsList />} />
        <Route path="restaurants" element={<RestaurantsList />} />
        <Route path="admins" element={<ComingSoon title="Admins" />} />
        <Route path="local-events" element={<LocalEventsList />} />
        <Route path="feedback" element={<ComingSoon title="Feedback" />} />
      </Route>
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}

export default AppRoutes;
