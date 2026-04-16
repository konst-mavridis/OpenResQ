import LegalPageShell from "../components/legal/LegalPageShell";

const EFFECTIVE_DATE = "April 14, 2026";

export default function PrivacyPage() {
  return (
    <LegalPageShell
      title="Privacy Policy"
      summary="This policy explains what information OpenResQ processes through the dashboard, why it is used, and the choices available to administrators and responders."
      effectiveDate={EFFECTIVE_DATE}
    >
      <h2>Who this policy applies to</h2>
      <p>
        This Privacy Policy applies to the OpenResQ dashboard and related
        account, billing, and support workflows made available through
        `dashboard.openresq.org` and connected OpenResQ services.
      </p>

      <h2>Information we collect</h2>
      <p>Depending on how you use the service, OpenResQ may process:</p>
      <ul>
        <li>Account details such as name, email address, role, and organization membership.</li>
        <li>Authentication data needed to sign in securely, including Firebase authentication identifiers.</li>
        <li>Operational data such as incidents, responder assignments, team records, device-related dashboard activity, and administrative settings.</li>
        <li>Billing and subscription information, including plan details, payment status, customer identifiers, and Stripe checkout session metadata.</li>
        <li>Location data when you choose to grant browser geolocation access for setup, team, or billing features.</li>
        <li>Technical data such as IP address, browser type, device information, timestamps, and diagnostic logs used to secure and maintain the service.</li>
        <li>Support and communications data you send to OpenResQ.</li>
      </ul>

      <h2>How we use information</h2>
      <ul>
        <li>Provide, secure, and maintain the dashboard and associated services.</li>
        <li>Authenticate users, manage organization access, and prevent unauthorized use.</li>
        <li>Process subscriptions, upgrades, invoicing, and related billing support.</li>
        <li>Support incident response, team coordination, mapping, and service administration features.</li>
        <li>Remember product preferences, such as theme selection and basic session continuity.</li>
        <li>Investigate bugs, abuse, fraud, and service reliability issues.</li>
        <li>Comply with legal obligations and enforce contractual rights.</li>
      </ul>

      <h2>Legal bases</h2>
      <p>
        Where applicable data protection laws require a legal basis, OpenResQ
        generally relies on contract performance, legitimate interests, legal
        obligations, and consent when a feature specifically asks for it, such
        as optional geolocation permission granted through your browser.
      </p>

      <h2>How information is shared</h2>
      <p>OpenResQ may share information with service providers that help operate the platform, including:</p>
      <ul>
        <li>Firebase and Google services for authentication, hosting-related functions, and database support.</li>
        <li>Stripe for subscription billing and payment processing.</li>
        <li>Infrastructure, security, communications, and support vendors acting on OpenResQ&apos;s behalf.</li>
        <li>Authorities or counterparties when required by law, court order, or to protect rights, safety, and the integrity of the service.</li>
      </ul>
      <p>
        OpenResQ does not sell personal information or share dashboard data for
        cross-context behavioral advertising through this product.
      </p>

      <h2>Retention</h2>
      <p>
        Information is retained for as long as reasonably necessary to provide
        the services, maintain security and audit records, comply with legal
        obligations, resolve disputes, and enforce agreements. Retention periods
        may differ by data category and customer configuration.
      </p>

      <h2>Your choices and rights</h2>
      <p>
        Depending on your location, you may have rights to access, correct,
        delete, restrict, or export certain personal information, and to object
        to particular processing. Organization administrators may also be able
        to update some account information directly within the dashboard.
      </p>
      <p>
        To request privacy assistance, please contact OpenResQ through your
        organization&apos;s account contact or support channel and include enough
        information for verification and response handling.
      </p>

      <h2>Children</h2>
      <p>
        OpenResQ is intended for business, municipal, and organizational use and
        is not directed to children under 13.
      </p>

      <h2>International transfers</h2>
      <p>
        OpenResQ and its service providers may process information in countries
        other than the country where it was collected. When that happens,
        OpenResQ aims to use appropriate safeguards required by applicable law.
      </p>

      <h2>Changes to this policy</h2>
      <p>
        OpenResQ may update this Privacy Policy from time to time. Material
        updates will be posted here with a revised effective date.
      </p>
    </LegalPageShell>
  );
}
