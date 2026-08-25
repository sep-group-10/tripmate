import { Routes, Route } from "react-router-dom";
import Home from "../pages/Home";
import RegisterPage from "../pages/RegisterPage";
import LoginPage from "../pages/LoginPage";
import ProfilePage from "../pages/ProfilePage";
import AdminLayout from "../pages/admin/AdminLayout";
import AdminDashboard from "../pages/admin/AdminDashboard";
import DestinationsList from "../pages/admin/DestinationsList";
import AttractionsList from "../pages/admin/AttractionsList";
import HotelsList from "../pages/admin/HotelsList";
import RestaurantsList from "../pages/admin/RestaurantsList";
import ProtectedRoute from "./ProtectedRoute";

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/profile"
        element={
          <ProtectedRoute>
            <ProfilePage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin"
        element={
          <ProtectedRoute>
            <AdminLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<AdminDashboard />} />
        <Route path="destinations" element={<DestinationsList />} />
        <Route path="attractions" element={<AttractionsList />} />
        <Route path="hotels" element={<HotelsList />} />
        <Route path="restaurants" element={<RestaurantsList />} />
      </Route>
    </Routes>
  );
}

export default AppRoutes;
