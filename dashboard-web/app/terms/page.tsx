import LegalPageShell from "../components/legal/LegalPageShell";

const EFFECTIVE_DATE = "April 14, 2026";

export default function TermsPage() {
  return (
    <LegalPageShell
      title="Terms of Service"
      summary="These Terms govern access to and use of the OpenResQ dashboard and related hosted services by customer organizations and their authorized users."
      effectiveDate={EFFECTIVE_DATE}
    >
      <h2>Agreement to these Terms</h2>
      <p>
        By accessing or using OpenResQ, you agree to these Terms of Service on
        behalf of yourself and, if applicable, the organization you represent.
        If you do not have authority to bind your organization, do not use the
        service.
      </p>

      <h2>Service overview</h2>
      <p>
        OpenResQ provides a dashboard for organizational response coordination,
        administration, reporting, billing, and related workflows. Features may
        change over time, and some functionality may rely on third-party
        services such as Firebase, Google, and Stripe.
      </p>

      <h2>Important service limitation</h2>
      <p>
        OpenResQ is a software tool and not a substitute for emergency dispatch,
        public safety judgment, professional medical care, or legal compliance
        obligations that apply to your organization. You remain responsible for
        your operational decisions, responder workflows, and emergency
        procedures.
      </p>

      <h2>Accounts and access</h2>
      <ul>
        <li>You must provide accurate registration and billing information.</li>
        <li>You are responsible for maintaining the confidentiality of account credentials and for activity under your accounts.</li>
        <li>You must promptly notify OpenResQ if you suspect unauthorized access or a security incident affecting your account.</li>
        <li>Administrators are responsible for managing authorized users within their organizations.</li>
      </ul>

      <h2>Acceptable use</h2>
      <p>You may not use OpenResQ to:</p>
      <ul>
        <li>Break the law, infringe rights, or interfere with the safety or privacy of others.</li>
        <li>Probe, scan, disable, reverse engineer, or disrupt the service beyond what applicable law permits.</li>
        <li>Upload malicious code, interfere with network integrity, or bypass access restrictions.</li>
        <li>Use the service to transmit unlawful, abusive, deceptive, or harmful content.</li>
        <li>Access data belonging to another customer without authorization.</li>
      </ul>

      <h2>Customer data</h2>
      <p>
        As between the parties, customers retain their rights in the data they
        submit to OpenResQ. Customers are responsible for ensuring they have the
        rights and notices needed to collect and use that data in connection
        with the service.
      </p>

      <h2>Billing and subscriptions</h2>
      <ul>
        <li>Paid plans, pricing, usage limits, and billing intervals are described in the dashboard, order form, or checkout flow.</li>
        <li>Fees are generally non-refundable except where required by law or expressly agreed in writing.</li>
        <li>OpenResQ may suspend or limit paid features for overdue amounts, failed payments, or suspected fraud.</li>
        <li>Enterprise or custom arrangements may be governed by separate written terms.</li>
      </ul>

      <h2>Availability and changes</h2>
      <p>
        OpenResQ aims to keep the service available and secure but does not
        guarantee uninterrupted or error-free operation. Maintenance, upgrades,
        outages, security responses, and third-party dependencies may affect
        availability.
      </p>

      <h2>Termination</h2>
      <p>
        OpenResQ may suspend or terminate access if these Terms are violated, if
        required by law, or if use of the service creates security or operational
        risk. Customers may stop using the service at any time, subject to any
        subscription commitments already in effect.
      </p>

      <h2>Disclaimers</h2>
      <p>
        To the maximum extent permitted by law, the service is provided on an
        &quot;as is&quot; and &quot;as available&quot; basis without warranties of any
        kind, whether express, implied, or statutory.
      </p>

      <h2>Limitation of liability</h2>
      <p>
        To the maximum extent permitted by law, OpenResQ will not be liable for
        indirect, incidental, special, consequential, exemplary, or punitive
        damages, or for loss of profits, revenues, goodwill, or data. Where a
        liability cap is permitted, OpenResQ&apos;s aggregate liability arising out
        of or relating to the service will not exceed the amounts paid by the
        customer for the service during the 12 months preceding the event giving
        rise to the claim.
      </p>

      <h2>Changes to these Terms</h2>
      <p>
        OpenResQ may update these Terms from time to time. Continued use of the
        service after the revised Terms become effective constitutes acceptance
        of the updated Terms.
      </p>
    </LegalPageShell>
  );
}
