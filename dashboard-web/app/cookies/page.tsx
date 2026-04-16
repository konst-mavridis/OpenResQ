import LegalPageShell from "../components/legal/LegalPageShell";

const EFFECTIVE_DATE = "April 14, 2026";

export default function CookiePolicyPage() {
  return (
    <LegalPageShell
      title="Cookie & Storage Policy"
      summary="This page explains how OpenResQ uses cookies and similar browser storage technologies in the dashboard."
      effectiveDate={EFFECTIVE_DATE}
    >
      <h2>Overview</h2>
      <p>
        OpenResQ uses a limited set of cookies and similar storage technologies
        that are necessary to operate the dashboard securely and reliably. This
        includes browser storage used to remember preferences and maintain
        continuity through authentication and billing workflows.
      </p>

      <h2>What we currently use</h2>
      <ul>
        <li>Essential authentication and security technologies needed to sign users in and protect accounts.</li>
        <li>Preference storage, such as saving a selected theme in the browser.</li>
        <li>Short-lived state used during upgrade, checkout, and session-related flows.</li>
      </ul>

      <h2>What we do not currently use in this dashboard</h2>
      <p>
        Based on the current dashboard implementation, OpenResQ does not load
        optional advertising cookies or standalone analytics cookies on the
        frontend. If optional cookies are introduced in the future, OpenResQ
        will update this policy and, where required, present a consent choice.
      </p>

      <h2>Why these technologies are used</h2>
      <ul>
        <li>To keep users signed in or recognize an authenticated session.</li>
        <li>To maintain account security and fraud prevention controls.</li>
        <li>To remember product settings and improve continuity between visits.</li>
        <li>To support payment and billing workflows initiated by the user.</li>
      </ul>

      <h2>Your choices</h2>
      <p>
        Most browsers let you view, block, or delete cookies and site storage.
        Blocking essential technologies may prevent parts of OpenResQ from
        working correctly, including sign-in, billing, and saved preferences.
      </p>

      <h2>More information</h2>
      <p>
        To learn more about how OpenResQ handles personal information overall,
        please review the Privacy Policy.
      </p>
    </LegalPageShell>
  );
}
