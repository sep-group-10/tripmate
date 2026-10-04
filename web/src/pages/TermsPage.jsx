import LegalPageLayout from "../components/LegalPageLayout";

function TermsPage() {
  return (
    <LegalPageLayout title="Terms of Service" lastUpdated="October 4, 2026">
      <p className="m-0">
        These Terms of Service ("Terms") govern your use of TripMate, an
        AI-assisted trip-planning application for travel in Sri Lanka built as a
        university project at the University of Moratuwa. By creating an account
        or using TripMate, you agree to these Terms.
      </p>

      <section>
        <h2 className="font-heading mb-2 text-heading-sm font-semibold tracking-tight">
          1. What TripMate is
        </h2>
        <p className="m-0">
          TripMate helps you plan trips by suggesting destinations, attractions,
          accommodations, restaurants, and itineraries, and by letting you
          refine a trip through conversation. It is an academic project, not a
          commercial travel agency or booking service, and does not process
          payments or make reservations on your behalf.
        </p>
      </section>

      <section>
        <h2 className="font-heading mb-2 text-heading-sm font-semibold tracking-tight">
          2. Your account
        </h2>
        <p className="m-0">
          You're responsible for keeping your login credentials secure and for
          all activity under your account. You must provide accurate information
          when registering, and you may sign in either with an email and
          password or with a Google account. You must verify your email address
          before your account becomes fully active.
        </p>
      </section>

      <section>
        <h2 className="font-heading mb-2 text-heading-sm font-semibold tracking-tight">
          3. Acceptable use
        </h2>
        <p className="m-0">
          Use TripMate only for its intended purpose of planning and reviewing
          trips. Don't attempt to disrupt the service, access other users'
          accounts or data, submit abusive or false feedback, or use the
          platform for any unlawful purpose.
        </p>
      </section>

      <section>
        <h2 className="font-heading mb-2 text-heading-sm font-semibold tracking-tight">
          4. AI-generated content
        </h2>
        <p className="m-0">
          Itineraries, recommendations, and chat responses are generated with
          the help of AI models and may be incomplete, outdated, or inaccurate —
          for example, listed opening hours, prices, or availability may not
          reflect reality. Always verify important details (opening hours,
          costs, safety advisories) independently before relying on them,
          especially before travelling.
        </p>
      </section>

      <section>
        <h2 className="font-heading mb-2 text-heading-sm font-semibold tracking-tight">
          5. Feedback
        </h2>
        <p className="m-0">
          If you submit feedback or ratings, you agree that TripMate's admin
          team may read, act on, and record how it was resolved, in order to
          improve the tourism data and the planning experience.
        </p>
      </section>

      <section>
        <h2 className="font-heading mb-2 text-heading-sm font-semibold tracking-tight">
          6. Account deactivation and deletion
        </h2>
        <p className="m-0">
          You may delete your account at any time from your profile. Doing so
          deactivates your account and removes your personal information from
          active use. An administrator may also deactivate an account that
          violates these Terms.
        </p>
      </section>

      <section>
        <h2 className="font-heading mb-2 text-heading-sm font-semibold tracking-tight">
          7. No warranty
        </h2>
        <p className="m-0">
          TripMate is provided "as is," as a student project, without warranties
          of any kind. We don't guarantee the service will be uninterrupted,
          error-free, or fit for any particular purpose.
        </p>
      </section>

      <section>
        <h2 className="font-heading mb-2 text-heading-sm font-semibold tracking-tight">
          8. Changes to these Terms
        </h2>
        <p className="m-0">
          We may update these Terms from time to time. Continuing to use
          TripMate after a change means you accept the updated Terms.
        </p>
      </section>

      <section>
        <h2 className="font-heading mb-2 text-heading-sm font-semibold tracking-tight">
          9. Contact
        </h2>
        <p className="m-0">
          Questions about these Terms can be directed to the TripMate project
          team at the University of Moratuwa.
        </p>
      </section>
    </LegalPageLayout>
  );
}

export default TermsPage;
