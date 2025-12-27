export default function HowItWorks() {
  const steps = [
    {
      number: "1",
      title: "Report",
      description: "A citizen reports an incident through the platform.",
      icon: "📋",
      highlight: false,
    },
    {
      number: "2",
      title: "Notify",
      description: "Nearby volunteers and authorities are notified instantly through real-time alerts.",
      icon: "⚡",
      highlight: true,
    },
    {
      number: "3",
      title: "Respond",
      description: "Coordinated response based on location and availability.",
      icon: "🚀",
      highlight: false,
    },
  ];

  return (
    <main className="min-h-screen bg-linear-to-b from-slate-50 to-white py-24 px-6">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">How It Works</h1>
          <p className="text-xl text-gray-600">Simple, fast, and effective emergency response</p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {steps.map((step) => (
            <div
              key={step.number}
              className={`p-8 rounded-xl transition-all ${
                step.highlight
                  ? "bg-linear-to-br from-indigo-500 to-blue-600 text-white shadow-lg scale-105"
                  : "bg-white text-gray-900 shadow hover:shadow-lg border border-gray-200"
              }`}
            >
              <div className="text-5xl mb-4">{step.icon}</div>
              <h2 className="text-2xl font-bold mb-3">{step.title}</h2>
              <p className={step.highlight ? "text-indigo-50" : "text-gray-600"}>
                {step.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
