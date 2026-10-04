import LegalPageLayout from "../components/LegalPageLayout";

function PrivacyPage() {
  return (
    <LegalPageLayout title="Privacy Policy" lastUpdated="October 4, 2026">
      <p className="m-0">
        This Privacy Policy explains what information TripMate collects, how
        it's used, and the choices you have. TripMate is a university project
        built at the University of Moratuwa, not a commercial service, and this
        policy is written for that context.
      </p>

      <section>
        <h2 className="font-heading mb-2 text-heading-sm font-semibold tracking-tight">
          1. Information we collect
        </h2>
        <p className="m-0">
          When you register, we collect your full name, email address, and a
          securely hashed password (or, if you sign in with Google, basic
          profile details Google shares with us). As you use the app, we store
          the trip preferences you set (travel style, pace, accommodation type,
          budget range, interests), the trips and itineraries you create, your
          chat messages with the planning assistant, and any feedback or ratings
          you submit.
        </p>
      </section>

      <section>
        <h2 className="font-heading mb-2 text-heading-sm font-semibold tracking-tight">
          2. How we use your information
        </h2>
        <p className="m-0">
          We use your information to run your account, generate and refine trip
          itineraries, remember your preferences, show you your past trips, and
          let admins review feedback to improve tourism data. We do not sell
          your information or use it for advertising.
        </p>
      </section>

      <section>
        <h2 className="font-heading mb-2 text-heading-sm font-semibold tracking-tight">
          3. AI processing
        </h2>
        <p className="m-0">
          Your trip preferences and chat messages are sent to a third-party AI
          provider to generate itineraries and conversational responses. Only
          the information needed to plan your trip is sent — we don't share your
          email, password, or account credentials with the AI provider.
        </p>
      </section>

      <section>
        <h2 className="font-heading mb-2 text-heading-sm font-semibold tracking-tight">
          4. Cookies and sessions
        </h2>
        <p className="m-0">
          We use essential cookies to keep you signed in (an access token and a
          refresh token). These cookies are required for the app to work and
          aren't used for tracking or advertising.
        </p>
      </section>

      <section>
        <h2 className="font-heading mb-2 text-heading-sm font-semibold tracking-tight">
          5. Who can see your information
        </h2>
        <p className="m-0">
          Your profile and trips are private to your account. Admin and Super
          Admin accounts can view feedback you submit (including your name and
          rating) in order to resolve it, and Super Admin accounts can view
          basic account details for managing users. Admins do not have access to
          your trip chat history.
        </p>
      </section>

      <section>
        <h2 className="font-heading mb-2 text-heading-sm font-semibold tracking-tight">
          6. Your choices
        </h2>
        <p className="m-0">
          From your profile, you can update your name and travel preferences,
          export a copy of your data (profile, trips, and feedback) as a file,
          or delete your account. Deleting your account anonymizes your personal
          details and deactivates the account.
        </p>
      </section>

      <section>
        <h2 className="font-heading mb-2 text-heading-sm font-semibold tracking-tight">
          7. Data security
        </h2>
        <p className="m-0">
          Passwords are hashed and never stored in plain text. Session tokens
          are stored in httpOnly cookies, which can't be read by page scripts.
          No method of storage or transmission is perfectly secure, but we take
          reasonable steps to protect your data.
        </p>
      </section>

      <section>
        <h2 className="font-heading mb-2 text-heading-sm font-semibold tracking-tight">
          8. Changes to this policy
        </h2>
        <p className="m-0">
          We may update this policy as the project evolves. Continuing to use
          TripMate after a change means you accept the updated policy.
        </p>
      </section>

      <section>
        <h2 className="font-heading mb-2 text-heading-sm font-semibold tracking-tight">
          9. Contact
        </h2>
        <p className="m-0">
          Questions about this policy or your data can be directed to the
          TripMate project team at the University of Moratuwa.
        </p>
      </section>
    </LegalPageLayout>
  );
}

export default PrivacyPage;
