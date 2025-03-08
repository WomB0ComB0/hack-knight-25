// import { LoginSelection } from "@/components/login-selection"
"use client";
import type React from 'react';  
import { useRef } from 'react';
import { Shield, Users, Lock, KeyRound, ArrowRight, Activity, UserCircle2, Stethoscope, Mail, Phone, MapPin, ChevronDown, CheckCircle2 } from 'lucide-react';


export default function Home() {
const aboutRef = useRef<HTMLDivElement>(null);
const featuresRef = useRef<HTMLDivElement>(null);
const contactRef = useRef<HTMLDivElement>(null);

const scrollToSection = (ref: React.RefObject<HTMLDivElement>) => {
  ref.current?.scrollIntoView({ behavior: 'smooth' });
};

return (
  <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
    {/* Navigation */}
    <nav className="fixed top-0 left-0 right-0 bg-white shadow-sm z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center">
            <Activity className="h-8 w-8 text-blue-600" />
            <span className="ml-2 text-xl font-bold text-gray-900">MedChain</span>
          </div>
          <div className="flex space-x-4">
            <button 
              onClick={() => scrollToSection(aboutRef)}
              className="px-4 py-2 text-gray-600 hover:text-gray-900 transition-colors"
            >
              About
            </button>
            <button 
              onClick={() => scrollToSection(featuresRef)}
              className="px-4 py-2 text-gray-600 hover:text-gray-900 transition-colors"
            >
              Features
            </button>
            <button 
              onClick={() => scrollToSection(contactRef)}
              className="px-4 py-2 text-gray-600 hover:text-gray-900 transition-colors"
            >
              Contact
            </button>
            <a 
              href="/signin" 
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Sign In
            </a>
          </div>
        </div>
      </div>
    </nav>

    {/* Hero Section */}
    <div className="pt-32 pb-20 relative overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center relative z-10">
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold text-gray-900 mb-8">
            Your Health Data,
            <span className="text-blue-600"> Your Control</span>
          </h1>
          <p className="text-xl text-gray-600 mb-10 max-w-2xl mx-auto">
            MedChain empowers patients with complete control over their health records while enabling secure data sharing with healthcare providers.
          </p>
          <div className="flex justify-center space-x-4">
            <button className="px-8 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center transition-colors">
              Get Started
              <ArrowRight className="ml-2 h-5 w-5" />
            </button>
            <button 
              onClick={() => scrollToSection(aboutRef)}
              className="px-8 py-4 border-2 border-blue-600 text-blue-600 rounded-lg hover:bg-blue-50 transition-colors group"
            >
              Learn More
              <ChevronDown className="ml-2 h-5 w-5 inline-block group-hover:translate-y-1 transition-transform" />
            </button>
          </div>
        </div>
      </div>
      <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
    </div>

    {/* About Section */}
    <div ref={aboutRef} className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-gray-900">About MedChain</h2>
          <p className="mt-4 text-xl text-gray-600">Revolutionizing healthcare data management through blockchain technology</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
          <div className="space-y-6">
            <div className="flex items-start space-x-4">
              <CheckCircle2 className="h-6 w-6 text-green-500 mt-1" />
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Blockchain Security</h3>
                <p className="text-gray-600">Your medical records are encrypted and stored on a secure blockchain network.</p>
              </div>
            </div>
            <div className="flex items-start space-x-4">
              <CheckCircle2 className="h-6 w-6 text-green-500 mt-1" />
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Smart Contracts</h3>
                <p className="text-gray-600">Automated access control through blockchain smart contracts.</p>
              </div>
            </div>
            <div className="flex items-start space-x-4">
              <CheckCircle2 className="h-6 w-6 text-green-500 mt-1" />
              <div>
                <h3 className="text-lg font-semibold text-gray-900">HIPAA Compliant</h3>
                <p className="text-gray-600">Fully compliant with healthcare privacy regulations and standards.</p>
              </div>
            </div>
          </div>
          <div className="relative">
            <img
              src="https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=800&q=80"
              alt="Medical technology"
              className="rounded-lg shadow-xl"
            />
            <div className="absolute inset-0 bg-blue-600 opacity-10 rounded-lg"></div>
          </div>
        </div>
      </div>
    </div>

    {/* Features Section */}
    <div ref={featuresRef} className="py-20 bg-gradient-to-b from-gray-50 to-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-gray-900">Why Choose MedChain?</h2>
          <p className="mt-4 text-xl text-gray-600">Comprehensive features designed for patients and healthcare providers</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="p-6 bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow">
            <Shield className="h-12 w-12 text-blue-600 mb-4" />
            <h3 className="text-xl font-semibold mb-2">Complete Control</h3>
            <p className="text-gray-600 mb-4">You decide who can access your medical records and for how long.</p>
            <ul className="text-sm text-gray-500 space-y-2">
              <li className="flex items-center">
                <CheckCircle2 className="h-4 w-4 text-green-500 mr-2" />
                Granular access control
              </li>
              <li className="flex items-center">
                <CheckCircle2 className="h-4 w-4 text-green-500 mr-2" />
                Time-based permissions
              </li>
              <li className="flex items-center">
                <CheckCircle2 className="h-4 w-4 text-green-500 mr-2" />
                Revoke access anytime
              </li>
            </ul>
          </div>
          <div className="p-6 bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow">
            <Lock className="h-12 w-12 text-blue-600 mb-4" />
            <h3 className="text-xl font-semibold mb-2">Secure Sharing</h3>
            <p className="text-gray-600 mb-4">Blockchain-powered security ensures your data remains private and encrypted.</p>
            <ul className="text-sm text-gray-500 space-y-2">
              <li className="flex items-center">
                <CheckCircle2 className="h-4 w-4 text-green-500 mr-2" />
                End-to-end encryption
              </li>
              <li className="flex items-center">
                <CheckCircle2 className="h-4 w-4 text-green-500 mr-2" />
                Immutable audit trail
              </li>
              <li className="flex items-center">
                <CheckCircle2 className="h-4 w-4 text-green-500 mr-2" />
                Zero-knowledge proofs
              </li>
            </ul>
          </div>
          <div className="p-6 bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow">
            <Users className="h-12 w-12 text-blue-600 mb-4" />
            <h3 className="text-xl font-semibold mb-2">Easy Collaboration</h3>
            <p className="text-gray-600 mb-4">Seamlessly share records with healthcare providers when needed.</p>
            <ul className="text-sm text-gray-500 space-y-2">
              <li className="flex items-center">
                <CheckCircle2 className="h-4 w-4 text-green-500 mr-2" />
                Quick provider access
              </li>
              <li className="flex items-center">
                <CheckCircle2 className="h-4 w-4 text-green-500 mr-2" />
                Real-time updates
              </li>
              <li className="flex items-center">
                <CheckCircle2 className="h-4 w-4 text-green-500 mr-2" />
                Integrated messaging
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    {/* How It Works Section */}
    <div className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-gray-900">How It Works</h2>
          <p className="mt-4 text-xl text-gray-600">Simple and secure process for managing your health data</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
          <div className="space-y-8">
            <div className="flex items-center relative">
              <div className="flex items-center justify-center w-12 h-12 bg-blue-100 rounded-full mr-4">
                <UserCircle2 className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <h3 className="text-xl font-semibold mb-2">Patient Portal</h3>
                <p className="text-gray-600">Access and manage your complete medical history in one secure location.</p>
              </div>
            </div>
            <div className="flex items-center relative">
              <div className="flex items-center justify-center w-12 h-12 bg-blue-100 rounded-full mr-4">
                <KeyRound className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <h3 className="text-xl font-semibold mb-2">Grant Access</h3>
                <p className="text-gray-600">Easily provide temporary access to healthcare providers when needed.</p>
              </div>
            </div>
            <div className="flex items-center relative">
              <div className="flex items-center justify-center w-12 h-12 bg-blue-100 rounded-full mr-4">
                <Stethoscope className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <h3 className="text-xl font-semibold mb-2">Provider View</h3>
                <p className="text-gray-600">Doctors can securely access relevant patient data with permission.</p>
              </div>
            </div>
          </div>
          <div className="relative">
            <img
              src="https://images.unsplash.com/photo-1576091160550-2173dba999ef?auto=format&fit=crop&w=800&q=80"
              alt="Medical professional using tablet"
              className="rounded-lg shadow-xl"
            />
            <div className="absolute inset-0 bg-blue-600 opacity-10 rounded-lg"></div>
          </div>
        </div>
      </div>
    </div>

    {/* Contact Section */}
    <div ref={contactRef} className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold text-gray-900">Contact Us</h2>
          <p className="mt-4 text-xl text-gray-600">Get in touch with our team for support or inquiries</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
          <div className="space-y-8">
            <div className="flex items-center space-x-4">
              <div className="flex-shrink-0">
                <Mail className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <h3 className="text-lg font-medium text-gray-900">Email</h3>
                <p className="mt-1 text-gray-600">support@medchain.example.com</p>
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
                <h3 className="text-lg font-medium text-gray-900">Location</h3>
                <p className="mt-1 text-gray-600">123 Health Street, Medical District<br />San Francisco, CA 94105</p>
              </div>
            </div>
          </div>
          <form className="space-y-6">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700">Name</label>
              <input
                type="text"
                id="name"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
            </div>
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">Email</label>
              <input
                type="email"
                id="email"
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
            </div>
            <div>
              <label htmlFor="message" className="block text-sm font-medium text-gray-700">Message</label>
              <textarea
                id="message"
                rows={4}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              ></textarea>
            </div>
            <button
              type="submit"
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Send Message
            </button>
          </form>
        </div>
      </div>
    </div>

    {/* Footer */}
    <footer className="bg-gray-900 text-white py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <div className="flex items-center">
              <Activity className="h-6 w-6 text-blue-400" />
              <span className="ml-2 text-lg font-semibold">MedChain</span>
            </div>
            <p className="mt-4 text-gray-400">Secure, transparent, and patient-controlled healthcare data management.</p>
          </div>
          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wider">Product</h3>
            <ul className="mt-4 space-y-2">
              <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Features</a></li>
              <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Security</a></li>
              <li><a href="#" className="text-gray-400 hover:text-white transition-colors">For Patients</a></li>
              <li><a href="#" className="text-gray-400 hover:text-white transition-colors">For Providers</a></li>
            </ul>
          </div>
          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wider">Company</h3>
            <ul className="mt-4 space-y-2">
              <li><a href="#" className="text-gray-400 hover:text-white transition-colors">About</a></li>
              <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Blog</a></li>
              <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Careers</a></li>
              <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Contact</a></li>
            </ul>
          </div>
          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wider">Legal</h3>
            <ul className="mt-4 space-y-2">
              <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Privacy</a></li>
              <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Terms</a></li>
              <li><a href="#" className="text-gray-400 hover:text-white transition-colors">HIPAA</a></li>
              <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Security</a></li>
            </ul>
          </div>
        </div>
        <div className="mt-12 border-t border-gray-800 pt-8">
          <p className="text-gray-400 text-center">© 2025 MedChain. All rights reserved.</p>
        </div>
      </div>
    </footer>
  </div>
);
}

