import LegalPageLayout from "../components/LegalPageLayout";

const headingClass =
  "font-heading mb-2 text-heading-sm font-semibold tracking-tight";
const listClass = "m-0 mt-2 list-disc space-y-1 pl-5";

function PrivacyPage() {
  return (
    <LegalPageLayout title="Privacy Policy" lastUpdated="October 4, 2026">
      <p className="m-0">
        This Privacy Policy explains what information TripMate collects, how
        it's used, and the choices you have. TripMate (the AI-Powered Smart
        Tourism Assistant Platform) helps you plan trips in Sri Lanka. It is a
        university project built by Group 10 at the University of Moratuwa, not
        a commercial service, and this policy is written for that context.
      </p>

      <section>
        <h2 className={headingClass}>1. Information we collect</h2>
        <p className="m-0">
          When you register, we collect your full name, email address, and a
          securely hashed password. If you sign in with Google, we receive your
          name and email from Google instead of a password. As you use the app,
          we also store:
        </p>
        <ul className={listClass}>
          <li>
            Your travel preferences (travel style, pace, accommodation type,
            budget range, interests).
          </li>
          <li>
            Your trips and itineraries, including destinations, dates, budget,
            and saved places or favourites.
          </li>
          <li>Your chat messages with the planning assistant.</li>
          <li>Any feedback or ratings you submit.</li>
          <li>Your profile picture, if you upload one.</li>
          <li>
            Security records, such as login sessions, password reset requests,
            and email verification status.
          </li>
        </ul>
      </section>

      <section>
        <h2 className={headingClass}>2. How we use your information</h2>
        <p className="m-0">
          We use your information to run your account, generate and refine trip
          itineraries, remember your preferences, show you your past trips, send
          account emails (such as email verification and password reset), and
          let admins review feedback to improve tourism data. We do not sell
          your information or use it for advertising. TripMate does not take
          payments or make bookings.
        </p>
      </section>

      <section>
        <h2 className={headingClass}>3. AI and other services we use</h2>
        <p className="m-0">
          To plan your trip, we send your trip preferences, trip details (such
          as dates, budget, and destinations), and chat messages to Google's
          Gemini AI service. Only the information needed to plan your trip is
          sent. We do not share your email, password, or login tokens with it.
        </p>
        <p className="m-0 mt-2">
          To work out routes, place details, and weather, we send place names or
          map locations (not your name or account details) to Google Maps
          Platform, Google Places, and OpenWeather. Google also handles Google
          sign-in. These services have their own privacy policies, and we do not
          control how they handle data.
        </p>
        <p className="m-0 mt-2">
          Please do not type sensitive details such as passport numbers or
          payment information into the chat.
        </p>
      </section>

      <section>
        <h2 className={headingClass}>4. Where your data is stored</h2>
        <p className="m-0">
          Your data is stored on Amazon Web Services (AWS) servers in Mumbai,
          India. This includes our database, uploaded images, and the service
          that sends our emails. The website is delivered through Vercel. We use
          Sentry to collect error reports so we can fix bugs. This means your
          information is handled outside Sri Lanka.
        </p>
      </section>

      <section>
        <h2 className={headingClass}>5. Cookies and sessions</h2>
        <p className="m-0">
          On the web, we use essential cookies to keep you signed in: a
          short-lived access token (about 15 minutes) and a refresh token (up to
          7 days). These cookies are required for the app to work and aren't
          used for tracking or advertising. On the Android app, your sign-in
          tokens are kept in your phone's secure storage instead of cookies.
        </p>
      </section>

      <section>
        <h2 className={headingClass}>6. Who can see your information</h2>
        <p className="m-0">
          Your profile and trips are private to your account. Other accounts
          have limited access:
        </p>
        <ul className={listClass}>
          <li>
            <strong>Admin</strong> accounts manage tourism data and can view
            feedback you submit (including your name and rating) in order to
            resolve it.
          </li>
          <li>
            <strong>Super Admin</strong> accounts can also view basic account
            details (name, email, role) to manage users and create Admin
            accounts.
          </li>
          <li>
            Admins do not have access to your trip chat history. Admin actions
            are recorded in an audit log.
          </li>
        </ul>
        <p className="m-0 mt-2">
          The project team can access the database for maintenance and testing,
          and only does so when needed.
        </p>
      </section>

      <section>
        <h2 className={headingClass}>7. Your choices</h2>
        <p className="m-0">
          From your profile, you can update your name and travel preferences,
          change your password, export a copy of your data (profile, trips, and
          feedback) as a file, or delete your account. Your email address and
          role cannot be changed. Logging out signs you out on that device only.
        </p>
        <p className="m-0 mt-2">
          Deleting your account anonymizes your personal details and deactivates
          the account. Our regular database backups may keep older copies for a
          short time before they are replaced.
        </p>
      </section>

      <section>
        <h2 className={headingClass}>8. Data security</h2>
        <p className="m-0">
          Passwords are hashed and never stored in plain text. Session tokens
          are stored in httpOnly cookies, which can't be read by page scripts,
          and data is sent over HTTPS. Password reset links expire after 15
          minutes and can only be used once. No method of storage or
          transmission is perfectly secure, but we take reasonable steps to
          protect your data.
        </p>
      </section>

      <section>
        <h2 className={headingClass}>9. How long we keep your data</h2>
        <p className="m-0">
          We keep your data while your account is active. Because TripMate is a
          university project, the service may be shut down after the project
          ends. If that happens, the stored data will be deleted.
        </p>
      </section>

      <section>
        <h2 className={headingClass}>10. Changes to this policy</h2>
        <p className="m-0">
          We may update this policy as the project evolves. The "last updated"
          date at the top will change when we do. Continuing to use TripMate
          after a change means you accept the updated policy.
        </p>
      </section>
    </LegalPageLayout>
  );
}

export default PrivacyPage;
