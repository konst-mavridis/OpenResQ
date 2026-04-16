import "./globals.css";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import CookieBanner from "@/components/CookieBanner";

export const metadata = {
  title: "OpenResQ",
  description: "Open emergency response platform",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="scroll-smooth bg-white">
      <body className="bg-white text-gray-900">
        <Navbar />
        <CookieBanner />
        {children}
        <Footer />
      </body>
    </html>
  );
}
