// src/pages/HomePage.tsx
import React from 'react';
import { Link } from 'react-router-dom';
import { FileText, ClipboardList, Settings, TrendingUp, Users, AlertCircle } from 'lucide-react';

export const HomePage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-800 mb-4">
            🏥 Insurance Underwriting System
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Automate insurance application processing with AI-powered document extraction,
            risk evaluation, and premium calculation.
          </p>
        </div>

        {/* Quick Actions */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <Link
            to="/application"
            className="card hover:shadow-xl transition-shadow cursor-pointer group"
          >
            <div className="flex items-center space-x-4 mb-4">
              <div className="bg-primary-100 p-3 rounded-lg group-hover:bg-primary-200 transition-colors">
                <FileText className="w-8 h-8 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-800">New Application</h3>
            </div>
            <p className="text-gray-600">
              Upload documents and process new insurance applications
            </p>
          </Link>

          <Link
            to="/detail"
            className="card hover:shadow-xl transition-shadow cursor-pointer group"
          >
            <div className="flex items-center space-x-4 mb-4">
              <div className="bg-green-100 p-3 rounded-lg group-hover:bg-green-200 transition-colors">
                <ClipboardList className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-800">View Applications</h3>
            </div>
            <p className="text-gray-600">
              View and manage all submitted applications
            </p>
          </Link>

          <Link
            to="/configuration"
            className="card hover:shadow-xl transition-shadow cursor-pointer group"
          >
            <div className="flex items-center space-x-4 mb-4">
              <div className="bg-purple-100 p-3 rounded-lg group-hover:bg-purple-200 transition-colors">
                <Settings className="w-8 h-8 text-purple-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-800">Configuration</h3>
            </div>
            <p className="text-gray-600">
              Manage policy rules and system settings
            </p>
          </Link>
        </div>

        {/* Features Section */}
        <div className="card">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">Key Features</h2>
          
          <div className="grid md:grid-cols-2 gap-6">
            <div className="flex items-start space-x-3">
              <div className="bg-blue-100 p-2 rounded-lg mt-1">
                <TrendingUp className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-800 mb-1">AI-Powered Extraction</h3>
                <p className="text-sm text-gray-600">
                  Automatically extract applicant data from PDFs using LLM
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <div className="bg-green-100 p-2 rounded-lg mt-1">
                <AlertCircle className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-800 mb-1">RAG-Based Risk Evaluation</h3>
                <p className="text-sm text-gray-600">
                  Evaluate risk using policy knowledge base and retrieval
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <div className="bg-purple-100 p-2 rounded-lg mt-1">
                <Users className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-800 mb-1">Premium Calculation</h3>
                <p className="text-sm text-gray-600">
                  Calculate base and final premium with medical loading
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-3">
              <div className="bg-orange-100 p-2 rounded-lg mt-1">
                <FileText className="w-5 h-5 text-orange-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-800 mb-1">KYC Verification</h3>
                <p className="text-sm text-gray-600">
                  Verify identity using Aadhaar/PAN card OCR
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
