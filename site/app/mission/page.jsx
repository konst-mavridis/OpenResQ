export default function Mission() {
  return (
    <main className="py-12 px-4 sm:px-6 lg:px-8 bg-gray-50">
      <div className="max-w-4xl mx-auto">
        <header className="mb-8 text-center sm:text-left">
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold mb-3 bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">
            Our Mission
          </h1>
          <div className="w-20 h-1 bg-blue-600 rounded mx-auto sm:mx-0"></div>
        </header>

        <section className="space-y-6 text-base">
          <div className="bg-blue-50 p-6 sm:p-8 rounded-lg border-l-4 border-blue-600">
            <h2 className="text-xl sm:text-2xl font-semibold mb-3 text-gray-800">
              Transforming Emergency Response
            </h2>
            <p className="text-gray-700 leading-relaxed">
              OpenResQ aims to reduce emergency response times by enabling
              real-time coordination between citizens, volunteers and authorities.
              We empower communities to act quickly when every second counts.
            </p>
          </div>

          <div className="bg-green-50 p-6 sm:p-8 rounded-lg border-l-4 border-green-600">
            <h2 className="text-xl sm:text-2xl font-semibold mb-3 text-gray-800">
              Core Values
            </h2>
            <p className="text-gray-700 leading-relaxed">
              We believe open data, transparency and collaboration can save lives.
              By breaking down barriers between responders and communities, we create
              a network of trust and accountability that strengthens public safety.
            </p>
          </div>

          <div className="bg-purple-50 p-6 sm:p-8 rounded-lg border-l-4 border-purple-600">
            <h2 className="text-xl sm:text-2xl font-semibold mb-3 text-gray-800">
              Our Vision
            </h2>
            <p className="text-gray-700 leading-relaxed">
              The platform is designed to be open, scalable and adaptable
              to local communities and public protection agencies worldwide.
              Together, we&apos;re building the future of emergency response.
            </p>
          </div>
        </section>
      </div>
    </main>
  );
}
