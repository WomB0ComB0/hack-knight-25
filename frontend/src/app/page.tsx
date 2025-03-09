"use client";

import type React from "react";
import { useRef } from "react";
import { useRouter } from "next/navigation";
import {
  Shield,
  Users,
  Lock,
  KeyRound,
  ArrowRight,
  Activity,
  UserCircle2,
  Stethoscope,
  Mail,
  Phone,
  MapPin,
  ChevronDown,
  CheckCircle2,
} from "lucide-react";

export default function Home() {
  const aboutRef = useRef<HTMLDivElement>(null);
  const featuresRef = useRef<HTMLDivElement>(null);
  const contactRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  const scrollToSection = (ref: React.RefObject<HTMLDivElement>) => {
    if (ref.current) {
      ref.current.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }
  };

  const scrollDown = () => {
    window.scrollTo({
      top: window.innerHeight,
      behavior: "smooth",
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Navigation */}
      <nav className="fixed left-0 right-0 top-0 z-50 bg-white shadow-sm">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Activity className="h-8 w-8 text-blue-600" />
              <span className="ml-2 text-xl font-bold text-gray-900">
                MedChain
              </span>
            </div>
            <div className="flex space-x-4">
              <button
                type="button"
                onClick={() => scrollToSection(aboutRef)}
                className="px-4 py-2 text-gray-600 transition-colors hover:text-gray-900"
              >
                About
              </button>
              <button
                type="button"
                onClick={() => scrollToSection(featuresRef)}
                className="px-4 py-2 text-gray-600 transition-colors hover:text-gray-900"
              >
                Features
              </button>
              <button
                type="button"
                onClick={() => scrollToSection(contactRef)}
                className="px-4 py-2 text-gray-600 transition-colors hover:text-gray-900"
              >
                Contact
              </button>
              <a
                href="/signin"
                className="rounded-lg bg-blue-600 px-4 py-2 text-white transition-colors hover:bg-blue-700"
              >
                Sign In
              </a>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="relative overflow-hidden pb-20 pt-32">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="relative z-10 text-center">
            <h1 className="mb-8 text-4xl font-extrabold text-gray-900 sm:text-5xl md:text-6xl">
              Your Health Data,
              <span className="text-blue-600"> Your Control</span>
            </h1>
            <p className="mx-auto mb-10 max-w-2xl text-xl text-gray-600">
              MedChain empowers patients with complete control over their health
              records while enabling secure data sharing with healthcare
              providers.
            </p>
            <div className="flex justify-center space-x-4">
              <button
                type="button"
                onClick={scrollDown}
                className="flex items-center rounded-lg bg-blue-600 px-8 py-4 text-white transition-colors hover:bg-blue-700"
              >
                Get Started
                <ArrowRight className="ml-2 h-5 w-5" />
              </button>
              <button
                type="button"
                onClick={() => router.push("/dashboard")}
                className="group rounded-lg border-2 border-blue-600 px-8 py-4 text-blue-600 transition-colors hover:bg-blue-50"
              >
                Learn More
                <ChevronDown className="ml-2 inline-block h-5 w-5 transition-transform group-hover:translate-y-1" />
              </button>
            </div>
          </div>
        </div>
        <div className="bg-grid-pattern absolute inset-0 opacity-5" />
      </div>

      {/* About Section */}
      <div ref={aboutRef} className="bg-white py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mb-16 text-center">
            <h2 className="text-3xl font-bold text-gray-900">About MedChain</h2>
            <p className="mt-4 text-xl text-gray-600">
              Revolutionizing healthcare data management through blockchain
              technology
            </p>
          </div>
          <div className="grid grid-cols-1 items-center gap-12 md:grid-cols-2">
            <div className="space-y-6">
              <div className="flex items-start space-x-4">
                <CheckCircle2 className="mt-1 h-6 w-6 text-green-500" />
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">
                    Blockchain Security
                  </h3>
                  <p className="text-gray-600">
                    Your medical records are encrypted and stored on a secure
                    blockchain network.
                  </p>
                </div>
              </div>
              <div className="flex items-start space-x-4">
                <CheckCircle2 className="mt-1 h-6 w-6 text-green-500" />
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">
                    Smart Contracts
                  </h3>
                  <p className="text-gray-600">
                    Automated access control through blockchain smart contracts.
                  </p>
                </div>
              </div>
              <div className="flex items-start space-x-4">
                <CheckCircle2 className="mt-1 h-6 w-6 text-green-500" />
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">
                    HIPAA Compliant
                  </h3>
                  <p className="text-gray-600">
                    Fully compliant with healthcare privacy regulations and
                    standards.
                  </p>
                </div>
              </div>
            </div>
            <div className="relative">
              <img
                src="https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=800&q=80"
                alt="Medical technology"
                className="rounded-lg shadow-xl"
              />
              <div className="absolute inset-0 rounded-lg bg-blue-600 opacity-10" />
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div
        ref={featuresRef}
        className="bg-gradient-to-b from-gray-50 to-white py-20"
      >
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mb-16 text-center">
            <h2 className="text-3xl font-bold text-gray-900">
              Why Choose MedChain?
            </h2>
            <p className="mt-4 text-xl text-gray-600">
              Comprehensive features designed for patients and healthcare
              providers
            </p>
          </div>
          <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
            <div className="rounded-xl bg-white p-6 shadow-lg transition-shadow hover:shadow-xl">
              <Shield className="mb-4 h-12 w-12 text-blue-600" />
              <h3 className="mb-2 text-xl font-semibold">Complete Control</h3>
              <p className="mb-4 text-gray-600">
                You decide who can access your medical records and for how long.
              </p>
              <ul className="space-y-2 text-sm text-gray-500">
                <li className="flex items-center">
                  <CheckCircle2 className="mr-2 h-4 w-4 text-green-500" />
                  Granular access control
                </li>
                <li className="flex items-center">
                  <CheckCircle2 className="mr-2 h-4 w-4 text-green-500" />
                  Time-based permissions
                </li>
                <li className="flex items-center">
                  <CheckCircle2 className="mr-2 h-4 w-4 text-green-500" />
                  Revoke access anytime
                </li>
              </ul>
            </div>
            <div className="rounded-xl bg-white p-6 shadow-lg transition-shadow hover:shadow-xl">
              <Lock className="mb-4 h-12 w-12 text-blue-600" />
              <h3 className="mb-2 text-xl font-semibold">Secure Sharing</h3>
              <p className="mb-4 text-gray-600">
                Blockchain-powered security ensures your data remains private
                and encrypted.
              </p>
              <ul className="space-y-2 text-sm text-gray-500">
                <li className="flex items-center">
                  <CheckCircle2 className="mr-2 h-4 w-4 text-green-500" />
                  End-to-end encryption
                </li>
                <li className="flex items-center">
                  <CheckCircle2 className="mr-2 h-4 w-4 text-green-500" />
                  Immutable audit trail
                </li>
                <li className="flex items-center">
                  <CheckCircle2 className="mr-2 h-4 w-4 text-green-500" />
                  Zero-knowledge proofs
                </li>
              </ul>
            </div>
            <div className="rounded-xl bg-white p-6 shadow-lg transition-shadow hover:shadow-xl">
              <Users className="mb-4 h-12 w-12 text-blue-600" />
              <h3 className="mb-2 text-xl font-semibold">Easy Collaboration</h3>
              <p className="mb-4 text-gray-600">
                Seamlessly share records with healthcare providers when needed.
              </p>
              <ul className="space-y-2 text-sm text-gray-500">
                <li className="flex items-center">
                  <CheckCircle2 className="mr-2 h-4 w-4 text-green-500" />
                  Quick provider access
                </li>
                <li className="flex items-center">
                  <CheckCircle2 className="mr-2 h-4 w-4 text-green-500" />
                  Real-time updates
                </li>
                <li className="flex items-center">
                  <CheckCircle2 className="mr-2 h-4 w-4 text-green-500" />
                  Integrated messaging
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* How It Works Section */}
      <div className="bg-white py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mb-16 text-center">
            <h2 className="text-3xl font-bold text-gray-900">How It Works</h2>
            <p className="mt-4 text-xl text-gray-600">
              Simple and secure process for managing your health data
            </p>
          </div>
          <div className="grid grid-cols-1 items-center gap-12 md:grid-cols-2">
            <div className="space-y-8">
              <div className="relative flex items-center">
                <div className="mr-4 flex h-12 w-12 items-center justify-center rounded-full bg-blue-100">
                  <UserCircle2 className="h-6 w-6 text-blue-600" />
                </div>
                <div>
                  <h3 className="mb-2 text-xl font-semibold">Patient Portal</h3>
                  <p className="text-gray-600">
                    Access and manage your complete medical history in one
                    secure location.
                  </p>
                </div>
              </div>
              <div className="relative flex items-center">
                <div className="mr-4 flex h-12 w-12 items-center justify-center rounded-full bg-blue-100">
                  <KeyRound className="h-6 w-6 text-blue-600" />
                </div>
                <div>
                  <h3 className="mb-2 text-xl font-semibold">Grant Access</h3>
                  <p className="text-gray-600">
                    Easily provide temporary access to healthcare providers when
                    needed.
                  </p>
                </div>
              </div>
              <div className="relative flex items-center">
                <div className="mr-4 flex h-12 w-12 items-center justify-center rounded-full bg-blue-100">
                  <Stethoscope className="h-6 w-6 text-blue-600" />
                </div>
                <div>
                  <h3 className="mb-2 text-xl font-semibold">Provider View</h3>
                  <p className="text-gray-600">
                    Doctors can securely access relevant patient data with
                    permission.
                  </p>
                </div>
              </div>
            </div>
            <div className="relative">
              <img
                src="https://images.unsplash.com/photo-1576091160550-2173dba999ef?auto=format&fit=crop&w=800&q=80"
                alt="Medical professional using tablet"
                className="rounded-lg shadow-xl"
              />
              <div className="absolute inset-0 rounded-lg bg-blue-600 opacity-10" />
            </div>
          </div>
        </div>
      </div>

      {/* Contact Section */}
      <div ref={contactRef} className="bg-gray-50 py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="mb-16 text-center">
            <h2 className="text-3xl font-bold text-gray-900">Contact Us</h2>
            <p className="mt-4 text-xl text-gray-600">
              Get in touch with our team for support or inquiries
            </p>
          </div>
          <div className="grid grid-cols-1 gap-12 md:grid-cols-2">
            <div className="space-y-8">
              <div className="flex items-center space-x-4">
                <div className="flex-shrink-0">
                  <Mail className="h-6 w-6 text-blue-600" />
                </div>
                <div>
                  <h3 className="text-lg font-medium text-gray-900">Email</h3>
                  <p className="mt-1 text-gray-600">
                    support@medchain.example.com
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="flex-shrink-0">
                  <Phone className="h-6 w-6 text-blue-600" />
                </div>
                <div>
                  <h3 className="text-lg font-medium text-gray-900">Phone</h3>
                  <p className="mt-1 text-gray-600">+1 (555) 123-4567</p>
                </div>
              </div>
              <div className="flex items-center space-x-4">
                <div className="flex-shrink-0">
                  <MapPin className="h-6 w-6 text-blue-600" />
                </div>
                <div>
                  <h3 className="text-lg font-medium text-gray-900">
                    Location
                  </h3>
                  <p className="mt-1 text-gray-600">
                    123 Health Street, Medical District
                    <br />
                    San Francisco, CA 94105
                  </p>
                </div>
              </div>
            </div>
            <form className="space-y-6">
              <div>
                <label
                  htmlFor="name"
                  className="block text-sm font-medium text-gray-700"
                >
                  Name
                </label>
                <input
                  type="text"
                  id="name"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
              </div>
              <div>
                <label
                  htmlFor="email"
                  className="block text-sm font-medium text-gray-700"
                >
                  Email
                </label>
                <input
                  type="email"
                  id="email"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
              </div>
              <div>
                <label
                  htmlFor="message"
                  className="block text-sm font-medium text-gray-700"
                >
                  Message
                </label>
                <textarea
                  id="message"
                  rows={4}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
              </div>
              <button
                type="submit"
                className="w-full rounded-lg bg-blue-600 px-4 py-2 text-white transition-colors hover:bg-blue-700"
              >
                Send Message
              </button>
            </form>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 py-12 text-white">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 gap-8 md:grid-cols-4">
            <div>
              <div className="flex items-center">
                <Activity className="h-6 w-6 text-blue-400" />
                <span className="ml-2 text-lg font-semibold">MedChain</span>
              </div>
              <p className="mt-4 text-gray-400">
                Secure, transparent, and patient-controlled healthcare data
                management.
              </p>
            </div>
            <div>
              <h3 className="text-sm font-semibold uppercase tracking-wider">
                Product
              </h3>
              <ul className="mt-4 space-y-2">
                <li>
                  <a
                    href="."
                    className="text-gray-400 transition-colors hover:text-white"
                  >
                    Features
                  </a>
                </li>
                <li>
                  <a
                    href="."
                    className="text-gray-400 transition-colors hover:text-white"
                  >
                    Security
                  </a>
                </li>
                <li>
                  <a
                    href="."
                    className="text-gray-400 transition-colors hover:text-white"
                  >
                    For Patients
                  </a>
                </li>
                <li>
                  <a
                    href="."
                    className="text-gray-400 transition-colors hover:text-white"
                  >
                    For Providers
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="text-sm font-semibold uppercase tracking-wider">
                Company
              </h3>
              <ul className="mt-4 space-y-2">
                <li>
                  <a
                    href="."
                    className="text-gray-400 transition-colors hover:text-white"
                  >
                    About
                  </a>
                </li>
                <li>
                  <a
                    href="."
                    className="text-gray-400 transition-colors hover:text-white"
                  >
                    Blog
                  </a>
                </li>
                <li>
                  <a
                    href="."
                    className="text-gray-400 transition-colors hover:text-white"
                  >
                    Careers
                  </a>
                </li>
                <li>
                  <a
                    href="."
                    className="text-gray-400 transition-colors hover:text-white"
                  >
                    Contact
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="text-sm font-semibold uppercase tracking-wider">
                Legal
              </h3>
              <ul className="mt-4 space-y-2">
                <li>
                  <a
                    href="."
                    className="text-gray-400 transition-colors hover:text-white"
                  >
                    Privacy
                  </a>
                </li>
                <li>
                  <a
                    href="."
                    className="text-gray-400 transition-colors hover:text-white"
                  >
                    Terms
                  </a>
                </li>
                <li>
                  <a
                    href="."
                    className="text-gray-400 transition-colors hover:text-white"
                  >
                    HIPAA
                  </a>
                </li>
                <li>
                  <a
                    href="."
                    className="text-gray-400 transition-colors hover:text-white"
                  >
                    Security
                  </a>
                </li>
              </ul>
            </div>
          </div>
          <div className="mt-12 border-t border-gray-800 pt-8">
            <p className="text-center text-gray-400">
              © 2025 MedChain. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
