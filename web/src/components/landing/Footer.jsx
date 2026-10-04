import { Link } from "react-router-dom";
import { MapPin, GitFork } from "lucide-react";

function Footer() {
  return (
    <footer className="px-5 pt-28 pb-10">
      <div className="mx-auto flex max-w-[1120px] flex-col gap-8">
        <div className="flex flex-wrap justify-between gap-8">
          <div className="flex flex-col gap-2.5">
            <span className="flex items-center gap-2.5">
              <span className="flex h-logo w-logo items-center justify-center rounded-lg bg-accent text-white">
                <MapPin size={15} aria-hidden="true" />
              </span>
              <span className="font-heading text-lg font-semibold">
                TripMate
              </span>
            </span>
            <span className="text-sm text-muted-600">
              AI trip planning for Sri Lanka
            </span>
          </div>
          <div className="flex flex-wrap gap-6 text-sm">
            <a href="#how" className="text-muted-700">
              How it works
            </a>
            <a href="#features" className="text-muted-700">
              Features
            </a>
            <Link to="/login" className="text-muted-700">
              Login
            </Link>
            <Link to="/register" className="text-muted-700">
              Sign up
            </Link>
            <a
              href="https://github.com/sep-group-10/tripmate"
              className="flex items-center gap-1.5 text-muted-700"
            >
              <GitFork size={16} aria-hidden="true" />
              GitHub
            </a>
          </div>
        </div>
        <div className="flex flex-wrap items-center justify-between gap-4 border-t border-divider pt-5 text-sm text-muted-600">
          <span>
            © <span className="num">2026</span> TripMate. All rights reserved.
          </span>
          <div className="flex flex-wrap items-center gap-6">
            <Link to="/terms" className="text-muted-600">
              Terms of Service
            </Link>
            <Link to="/privacy" className="text-muted-600">
              Privacy Policy
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
