export default function CookiePolicy() {
  return (
    <main className="bg-neutral-50 dark:bg-neutral-900 min-h-screen py-16 px-4">
      <article className="max-w-4xl mx-auto bg-white dark:bg-neutral-800 p-8 md:p-12 rounded-3xl shadow-xl prose prose-neutral dark:prose-invert">
        <div className="mb-8">
          <span className="text-primary font-bold tracking-widest text-xs uppercase">Legal Document</span>
          <h1 className="mt-2 text-4xl font-serif tracking-tight">Cookie & Storage Policy</h1>
          <p className="text-neutral-500 dark:text-neutral-400 mt-2">Effective: April 14, 2026</p>
        </div>

        <section>
          <h2>Overview</h2>
          <p>
            This Cookie & Storage Policy explains how OpenResQ uses cookies and similar browser storage technologies on our website and dashboard. We aim to be transparent about the data we store and why.
          </p>
        </section>

        <section>
          <h2>Implicit & Essential Technologies</h2>
          <p>
            OpenResQ primarily uses technologies that are strictly necessary for the service to function. These do not require your prior consent as they are fundamental to the operation of the platform.
          </p>
          <ul>
            <li><strong>Authentication:</strong> We use Firebase Authentication to securely sign you in and protect your account.</li>
            <li><strong>Security and Integrity:</strong> Storage is used to identify your session and prevent fraudulent activities.</li>
            <li><strong>User Preferences:</strong> We use local storage to remember your theme choice (light or dark mode) and UI preferences.</li>
          </ul>
        </section>

        <section>
          <h2>What we do NOT use</h2>
          <p>
            To protect your privacy, OpenResQ adheres to the following principles:
          </p>
          <ul>
            <li><strong>No Tracking Cookies:</strong> We do not use third-party tracking or advertising cookies.</li>
            <li><strong>No Pixel Tags:</strong> We do not use web beacons or tracking pixels to monitor your cross-site behavior.</li>
            <li><strong>Privacy-Friendly Analytics:</strong> If we use analytics, we prioritize cookieless, privacy-focused solutions that do not store personal data.</li>
          </ul>
        </section>

        <section>
          <h2>Your Choices</h2>
          <p>
            You can control how cookies are used in your browser settings. However, disabling all storage may prevent certain features (like sign-in or theme selection) from working correctly.
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
