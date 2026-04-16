export default function PrivacyPolicy() {
  return (
    <main className="bg-neutral-50 dark:bg-neutral-900 min-h-screen py-16 px-4">
      <article className="max-w-4xl mx-auto bg-white dark:bg-neutral-800 p-8 md:p-12 rounded-3xl shadow-xl prose prose-neutral dark:prose-invert">
        <div className="mb-8">
          <span className="text-primary font-bold tracking-widest text-xs uppercase text-blue-600">Legal Document</span>
          <h1 className="mt-2 text-4xl font-serif tracking-tight">Privacy Policy</h1>
          <p className="text-neutral-500 dark:text-neutral-400 mt-2">Effective: April 14, 2026</p>
        </div>

        <section>
          <h2>Introduction</h2>
          <p>
            This Privacy Policy explains what information OpenResQ processes through our services, why it is used, and the choices available to you. OpenResQ is committed to transparency and the security of your data.
          </p>
        </section>

        <section>
          <h2>Information we process</h2>
          <p>Depending on how you interact with our services, we may process:</p>
          <ul>
            <li><strong>Account details:</strong> Such as your name, email address, and organization membership when you register.</li>
            <li><strong>Operational data:</strong> Such as incidents, responder records, and administrative logs for service delivery.</li>
            <li><strong>Technical data:</strong> IP addresses, browser types, and diagnostic logs to secure and monitor the platform.</li>
            <li><strong>Billing data:</strong> If you subscribe to a paid plan, we process transaction metadata through our payment processor, Stripe.</li>
          </ul>
        </section>

        <section>
          <h2>How we use your information</h2>
          <p>We use your data only for the following purposes:</p>
          <ul>
            <li>To provide and maintain the OpenResQ services.</li>
            <li>To secure the platform and prevent unauthorized access or abuse.</li>
            <li>To process payments and manage subscriptions.</li>
            <li>To communicate with you regarding service updates or support.</li>
            <li>To comply with legal obligations.</li>
          </ul>
        </section>

        <section>
          <h2>Data sharing and retention</h2>
          <p>
            We do not sell your personal data. We share information only with service providers needed for the platform&apos;s operation, including Google (for Firebase and backend infrastructure) and Stripe (for billing).
          </p>
          <p>
            We retain your data for as long as necessary to provide the services, maintain security record, comply with legal requirements, or resolve disputes.
          </p>
        </section>

        <section>
          <h2>Your rights</h2>
          <p>
            You have the right to access, correct, or delete your personal information. If you wish to exercise these rights, or have questions about our data practices, please contact our support team.
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
