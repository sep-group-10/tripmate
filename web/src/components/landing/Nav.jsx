import { useState } from "react";
import { Link } from "react-router-dom";
import { Menu, X } from "lucide-react";
import Logo from "../Logo";

const NAV_LINKS = [
  { label: "How it works", href: "#how" },
  { label: "Features", href: "#features" },
];

function Nav() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <div className="sticky top-0 z-30 px-5 pt-3.5">
      <nav className="mx-auto flex max-w-[1120px] items-center justify-between gap-4 rounded-pill bg-surface p-2 pl-4 shadow-raised">
        <a
          href="#top"
          className="flex items-center gap-2.5 text-ink no-underline"
        >
          <Logo />
        </a>

        <div className="hidden items-center gap-0.5 md:flex">
          {NAV_LINKS.map((l) => (
            <a
              key={l.href}
              href={l.href}
              className="rounded-full px-3 py-2.5 text-sm text-muted-700 no-underline hover:bg-muted-300 hover:text-ink"
            >
              {l.label}
            </a>
          ))}
        </div>
        <div className="hidden items-center gap-2 md:flex">
          <Link
            to="/login"
            className="rounded-full border border-border bg-surface px-5 py-2.5 text-sm font-medium text-ink shadow-control no-underline"
          >
            Login
          </Link>
          <Link
            to="/register"
            className="rounded-full bg-accent px-5 py-2.5 text-sm font-medium text-white shadow-control no-underline hover:bg-accent-600"
          >
            Sign up
          </Link>
        </div>

        <div className="flex items-center gap-1.5 md:hidden">
          <Link
            to="/register"
            className="rounded-full bg-accent px-4 py-2.5 text-sm font-medium text-white no-underline"
          >
            Sign up
          </Link>
          <button
            type="button"
            onClick={() => setMenuOpen((v) => !v)}
            aria-label="Menu"
            className="flex h-10 w-10 items-center justify-center rounded-full bg-inset text-muted-800"
          >
            {menuOpen ? (
              <X size={20} aria-hidden="true" />
            ) : (
              <Menu size={20} aria-hidden="true" />
            )}
          </button>
        </div>
      </nav>

      {menuOpen && (
        <div className="mx-auto mt-2 flex max-w-[1120px] flex-col gap-0.5 rounded-card bg-surface p-2 shadow-card md:hidden">
          {NAV_LINKS.map((l) => (
            <a
              key={l.href}
              href={l.href}
              onClick={() => setMenuOpen(false)}
              className="rounded-lg px-3.5 py-3 font-medium text-ink no-underline"
            >
              {l.label}
            </a>
          ))}
          <Link
            to="/login"
            className="mt-1.5 rounded-full border border-border bg-surface px-5 py-2.5 text-center text-sm font-medium text-ink shadow-control no-underline"
          >
            Login
          </Link>
        </div>
      )}
    </div>
  );
}

export default Nav;
