import { Navigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { ADMIN_ROLES } from "../constants/roles";
import FullPageLoader from "../components/FullPageLoader";
import Nav from "../components/landing/Nav";
import Hero from "../components/landing/Hero";
import Problem from "../components/landing/Problem";
import HowItWorks from "../components/landing/HowItWorks";
import Destinations from "../components/landing/Destinations";
import Features from "../components/landing/Features";
import Platforms from "../components/landing/Platforms";
import FinalCta from "../components/landing/FinalCta";
import Footer from "../components/landing/Footer";

function LandingPage() {
  const { isAuthenticated, loading, role } = useAuth();

  if (loading) return <FullPageLoader />;
  if (isAuthenticated) {
    return (
      <Navigate to={ADMIN_ROLES.includes(role) ? "/admin" : "/chat"} replace />
    );
  }

  return (
    <div className="relative min-h-screen bg-bg font-body text-ink">
      <Nav />
      <Hero />
      <main className="flex flex-col gap-28 px-5 pt-28">
        <Problem />
        <HowItWorks />
        <Destinations />
        <Features />
        <Platforms />
        <FinalCta />
      </main>
      <Footer />
    </div>
  );
}

export default LandingPage;
