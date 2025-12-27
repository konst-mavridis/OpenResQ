export default function Join() {
  return (
    <main className=" mx-auto py-20 px-6 bg-white">
      <section className="text-center mb-12">
        <h1 className="text-4xl md:text-5xl font-extrabold mb-4 bg-clip-text text-transparent bg-linear-to-r from-blue-600 to-indigo-600">
          Get Involved
        </h1>

        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          OpenResQ is open to everyone who wants to contribute — volunteers, organizations, developers, sponsors, and citizens. Pick the role that fits you and join our community.
        </p>
      </section>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="rounded-lg p-6 bg-linear-to-br from-blue-50 to-indigo-50 border border-blue-200 shadow-sm hover:shadow-lg transition transform hover:-translate-y-2 duration-300">
          <h2 className="text-xl font-semibold mb-2 text-blue-900">Volunteers</h2>
          <p className="text-gray-700">Respond to incidents in your local area and help neighbors when it matters most.</p>
        </div>

        <div className="rounded-lg p-6 bg-linear-to-br from-blue-50 to-indigo-50 border border-blue-200 shadow-sm hover:shadow-lg transition transform hover:-translate-y-2 duration-300">
          <h2 className="text-xl font-semibold mb-2 text-blue-900">Organizations</h2>
          <p className="text-gray-700">Partner with us to improve emergency response at scale and coordinate resources effectively.</p>
        </div>

        <div className="rounded-lg p-6 bg-linear-to-br from-blue-50 to-indigo-50 border border-blue-200 shadow-sm hover:shadow-lg transition transform hover:-translate-y-2 duration-300">
          <h2 className="text-xl font-semibold mb-2 text-blue-900">Developers</h2>
          <p className="text-gray-700">Contribute to our open-source tools and help build resilient, reliable systems.</p>
        </div>

        <div className="rounded-lg p-6 bg-linear-to-br from-blue-50 to-indigo-50 border border-blue-200 shadow-sm hover:shadow-lg transition transform hover:-translate-y-2 duration-300">
          <h2 className="text-xl font-semibold mb-2 text-blue-900">Sponsors</h2>
          <p className="text-gray-700">Support our mission to enhance emergency response and expand our impact.</p>
        </div>

        <div className="rounded-lg p-6 bg-linear-to-br from-blue-50 to-indigo-50 border border-blue-200 shadow-sm hover:shadow-lg transition transform hover:-translate-y-2 duration-300">
          <h2 className="text-xl font-semibold mb-2 text-blue-900">Citizens</h2>
          <p className="text-gray-700">Get involved locally and help make your community safer through preparedness and awareness.</p>
        </div>

        <div className="rounded-lg p-6 bg-linear-to-br from-blue-50 to-indigo-50 border border-blue-200 shadow-sm hover:shadow-lg transition transform hover:-translate-y-2 duration-300">
          <h2 className="text-xl font-semibold mb-2 text-blue-900">Not sure where to start?</h2>
          <p className="text-gray-700 mb-4">Start with a quick survey to help us recommend the best way for you to contribute.</p>
          <a href="/contact" className="inline-block bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold px-5 py-2 rounded-md shadow hover:opacity-95 transition-opacity duration-200">Get recommendations</a>
        </div>
      </div>
    </main>
  );
}
