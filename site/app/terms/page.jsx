export default function TermsOfService() {
  return (
    <main className="bg-neutral-50 dark:bg-neutral-900 min-h-screen py-16 px-4">
      <article className="max-w-4xl mx-auto bg-white dark:bg-neutral-800 p-8 md:p-12 rounded-3xl shadow-xl prose prose-neutral dark:prose-invert">
        <div className="mb-8">
          <span className="text-primary font-bold tracking-widest text-xs uppercase text-blue-600">Legal Document</span>
          <h1 className="mt-2 text-4xl font-serif tracking-tight">Terms of Service</h1>
          <p className="text-neutral-500 dark:text-neutral-400 mt-2">Effective: April 14, 2026</p>
        </div>

        <section>
          <h2>Agreement to Terms</h2>
          <p>
            By accessing or using OpenResQ, you agree to these Terms of Service. If you represent an organization, you state that you have the authority to bind that organization to these Terms. If you do not agree, you may not use the service.
          </p>
        </section>

        <section>
          <h2>Service Overview</h2>
          <p>
            OpenResQ provides a platform for organizational response coordination, administrative management, reporting, and related workflows. Features may evolve over time and may rely on third-party services like Firebase, Google, and Stripe.
          </p>
          <p>
            <strong>Critical Limitation:</strong> OpenResQ is a software tool and is not a substitute for official emergency dispatch, professional medical judgment, or legal compliance. Customers remain responsible for their operational decisions and emergency protocols.
          </p>
        </section>

        <section>
          <h2>Accounts and Security</h2>
          <p>
            You are responsible for maintaining the confidentiality of your account credentials and for all activities that occur under your account. You must notify us immediately of any unauthorized use or security breach.
          </p>
        </section>

        <section>
          <h2>Acceptable Use</h2>
          <p>
            You may not use OpenResQ to:
          </p>
          <ul>
            <li>Break any laws or infringe upon the rights of others.</li>
            <li>Disrupt, scan, or compromise the integrity of the platform.</li>
            <li>Transmit malicious code, unlawful, or harmful content.</li>
            <li>Access data belonging to another customer without authorization.</li>
          </ul>
        </section>

        <section>
          <h2>Billing and Subscriptions</h2>
          <p>
            Pricing, usage limits, and billing intervals are as described in the platform or order forms. OpenResQ reserves the right to suspend access for overdue payments or suspected fraud. Fees are generally non-refundable unless required by law.
          </p>
        </section>

        <section>
          <h2>Termination</h2>
          <p>
            We may suspend or terminate your access if you violate these Terms, if required by law, or if your usage creates security risks. You may stop using the service at any time, subject to any existing subscription obligations.
          </p>
        </section>

        <section>
          <h2>Disclaimers and Liability</h2>
          <p>
            To the maximum extent permitted by law, the service is provided "as is" without any warranties. OpenResQ is not liable for indirect, incidental, or consequential damages arising from your use of the service.
          </p>
        </section>

        <div className="mt-12 pt-8 border-t border-neutral-100 dark:border-neutral-700">
          <p className="text-sm font-medium">Questions?</p>
          <p className="text-sm text-neutral-500">Contact us at <a href="mailto:openresq.info@gmail.com" className="text-primary">openresq.info@gmail.com</a></p>
        </div>
      </article>
    </main>
  );
}
