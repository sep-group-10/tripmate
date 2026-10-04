import LegalPageLayout from "../components/LegalPageLayout";

const headingClass =
  "font-heading mb-2 text-heading-sm font-semibold tracking-tight";
const listClass = "m-0 mt-2 list-disc space-y-1 pl-5";

function TermsPage() {
  return (
    <LegalPageLayout title="Terms of Service" lastUpdated="October 4, 2026">
      <p className="m-0">
        These Terms of Service ("Terms") explain the rules for using TripMate,
        an AI-assisted trip-planning application for travel in Sri Lanka. It is
        a university project built by Group 10 at the University of Moratuwa. By
        creating an account or using TripMate, you agree to these Terms. If you
        do not agree, please do not use TripMate.
      </p>

      <section>
        <h2 className={headingClass}>1. What TripMate is</h2>
        <p className="m-0">
          TripMate helps you plan trips by suggesting destinations, attractions,
          hotels, restaurants, events, and itineraries, and by letting you
          refine a trip through conversation. It is an academic project, not a
          commercial travel agency or booking service. It does not process
          payments or make reservations for you.
        </p>
      </section>

      <section>
        <h2 className={headingClass}>2. Your account</h2>
        <p className="m-0">
          You are responsible for keeping your login details safe and for all
          activity under your account. Please give accurate information when you
          register. You can sign in with an email and password, or with a Google
          account. You must verify your email address before your account
          becomes fully active.
        </p>
        <p className="m-0 mt-2">
          All new sign-ups are created as regular Tourist accounts. Admin and
          Super Admin accounts are created only by the project team, and you
          cannot register for them.
        </p>
      </section>

      <section>
        <h2 className={headingClass}>3. Acceptable use</h2>
        <p className="m-0">
          Use TripMate only to plan and review trips. Please do not:
        </p>
        <ul className={listClass}>
          <li>Disrupt, overload, or try to break the service.</li>
          <li>Try to access other users' accounts or data.</li>
          <li>Try to misuse the AI assistant or get around its limits.</li>
          <li>Submit abusive or false feedback.</li>
          <li>Use TripMate for anything unlawful.</li>
        </ul>
        <p className="m-0 mt-2">
          To keep the service fair and control costs, we may limit how many
          trips you can plan in a day.
        </p>
      </section>

      <section>
        <h2 className={headingClass}>4. AI-generated content</h2>
        <p className="m-0">
          Itineraries, recommendations, and chat replies are made with the help
          of AI and may be incomplete, outdated, or wrong. Opening hours,
          prices, travel times, and weather may not match reality. Cost and
          transport figures are estimates, shown as ranges. Always check
          important details (opening hours, costs, safety advice) yourself
          before you travel.
        </p>
      </section>

      <section>
        <h2 className={headingClass}>
          5. Tourism data and third-party services
        </h2>
        <p className="m-0">
          Place information is managed by our admin team and may also come from
          services such as Google Maps, Google Places, and OpenWeather. We try
          to keep it correct, but we cannot promise it is always complete or up
          to date. These services can change or stop working, and parts of
          TripMate may be unavailable when they do. Names, logos, and photos of
          places belong to their owners.
        </p>
      </section>

      <section>
        <h2 className={headingClass}>6. Your content and feedback</h2>
        <p className="m-0">
          You keep ownership of what you write, such as chat messages and
          feedback. You allow TripMate to use it only to run the service: to
          build your trips, show your data to you, and improve tourism data.
          When you submit feedback or ratings, our admin team may read it, act
          on it, and record how it was resolved. Our Privacy Policy explains how
          your information is handled.
        </p>
      </section>

      <section>
        <h2 className={headingClass}>7. Account deactivation and deletion</h2>
        <p className="m-0">
          You can delete your account at any time from your profile. This
          anonymizes your personal details and deactivates the account. An
          administrator may also deactivate an account that breaks these Terms.
        </p>
      </section>

      <section>
        <h2 className={headingClass}>8. No warranty</h2>
        <p className="m-0">
          TripMate is provided "as is," as a student project, without warranties
          of any kind. We do not promise that the service will be uninterrupted,
          error-free, or right for any particular purpose. Because it is a
          university project, it may change or be shut down after the project
          ends.
        </p>
      </section>

      <section>
        <h2 className={headingClass}>9. Limit of liability</h2>
        <p className="m-0">
          To the extent the law allows, the TripMate team and the University of
          Moratuwa are not responsible for any loss or harm that comes from
          using TripMate or relying on its suggestions, including travel
          decisions, missed bookings, or extra costs. You are responsible for
          your own travel plans and safety.
        </p>
      </section>

      <section>
        <h2 className={headingClass}>10. Governing law</h2>
        <p className="m-0">
          These Terms are governed by the laws of Sri Lanka.
        </p>
      </section>

      <section>
        <h2 className={headingClass}>11. Changes to these Terms</h2>
        <p className="m-0">
          We may update these Terms from time to time. The "last updated" date
          at the top will change when we do. Continuing to use TripMate after a
          change means you accept the updated Terms.
        </p>
      </section>
    </LegalPageLayout>
  );
}

export default TermsPage;
