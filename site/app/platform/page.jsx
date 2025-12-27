export default function Platform() {
  return (
    <main className="min-h-screen bg-linear-to-br from-slate-50 to-slate-100">
      <div className="max-w-5xl mx-auto py-24 px-6">
        <div className="mb-16 text-center">
          <h1 className="text-5xl font-bold mb-4 bg-linear-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">
            The Platform
          </h1>
          <p className="text-lg text-gray-700 max-w-2xl mx-auto">
            A comprehensive emergency response system designed to connect citizens, responders, and authorities seamlessly.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          <div className="bg-white border border-gray-200 p-8 rounded-xl hover:shadow-xl transition-all duration-300 hover:border-blue-300">
            <div className="text-4xl mb-4">🚨</div>
            <h2 className="text-xl font-bold mb-3 text-gray-900">
              Incident Reporting
            </h2>
            <p className="text-gray-600 leading-relaxed">
              Citizens can report incidents in real-time using intuitive map-based tools. Submit photos, location details, and incident descriptions instantly.
            </p>
          </div>

          <div className="bg-white border border-gray-200 p-8 rounded-xl hover:shadow-xl transition-all duration-300 hover:border-blue-300">
            <div className="text-4xl mb-4">🔐</div>
            <h2 className="text-xl font-bold mb-3 text-gray-900">
              Role-based Access
            </h2>
            <p className="text-gray-600 leading-relaxed">
              Customized interfaces for citizens, emergency responders, and authorities. Each role has tailored features and permissions for optimal efficiency.
            </p>
          </div>

          <div className="bg-white border border-gray-200 p-8 rounded-xl hover:shadow-xl transition-all duration-300 hover:border-blue-300">
            <div className="text-4xl mb-4">✓</div>
            <h2 className="text-xl font-bold mb-3 text-gray-900">
              Secure & Transparent
            </h2>
            <p className="text-gray-600 leading-relaxed">
              Data integrity, full traceability, and GDPR-compliant design. Trust and transparency at every step.
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
