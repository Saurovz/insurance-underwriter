// src/pages/Configuration.tsx
import React, { useState, useEffect } from 'react';
import { Upload, CheckCircle, AlertCircle, RefreshCw, Database, FileText } from 'lucide-react';
import toast from 'react-hot-toast';

interface PolicyStatus {
  exists: boolean;
  collection_name?: string;
  db_path?: string;
}

export const Configuration: React.FC = () => {
  const [policyStatus, setPolicyStatus] = useState<PolicyStatus | null>(null);
  const [isChecking, setIsChecking] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadMessage, setUploadMessage] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [forceReload, setForceReload] = useState(false);

  useEffect(() => {
    checkPolicyStatus();
  }, []);

  const checkPolicyStatus = async () => {
    setIsChecking(true);
    try {
      const response = await fetch('http://localhost:8000/api/configuration/check-policy', {
        method: 'POST',
      });
      const data = await response.json();
      
      if (data.success) {
        setPolicyStatus({
          exists: data.exists,
          collection_name: data.collection_name,
          db_path: data.db_path,
        });
      }
    } catch (error) {
      console.error('Error checking policy status:', error);
      toast.error('Failed to check policy status');
    } finally {
      setIsChecking(false);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (!file.name.endsWith('.pdf')) {
        toast.error('Please upload a PDF file only!');
        return;
      }
      
      const fileSizeMB = file.size / (1024 * 1024);
      if (fileSizeMB > 200) {
        toast.error(`File size (${fileSizeMB.toFixed(2)}MB) exceeds 200MB limit!`);
        return;
      }
      
      setSelectedFile(file);
      toast.success(`Selected: ${file.name}`);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      toast.error('Please select a policy PDF file');
      return;
    }

    if (policyStatus?.exists && !forceReload) {
      toast.error('Policy already exists. Enable "Overwrite Existing" to replace it.');
      return;
    }

    setIsUploading(true);
    setUploadProgress(10);
    setUploadMessage('Uploading policy document...');

    const formData = new FormData();
    formData.append('policy_pdf', selectedFile);

    try {
      // CRITICAL FIX: Always set force_reload=true when checkbox is checked
      const url = policyStatus?.exists && forceReload
        ? 'http://localhost:8000/api/configuration/upload-policy?force_reload=true'
        : 'http://localhost:8000/api/configuration/upload-policy';

      console.log('Uploading to:', url);
      console.log('Force reload:', forceReload);

      const response = await fetch(url, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      console.log('Upload response:', data);

      if (data.success) {
        setUploadProgress(100);
        setUploadMessage('Policy knowledge base created successfully!');
        toast.success('Policy uploaded and indexed successfully!');
        
        // Refresh status
        setTimeout(() => {
          checkPolicyStatus();
          setSelectedFile(null);
          setForceReload(false);
        }, 1500);
      } else {
        throw new Error(data.message || data.detail || 'Upload failed');
      }
    } catch (error: any) {
      console.error('Upload error:', error);
      toast.error(error.message || 'Failed to upload policy');
      setUploadMessage('Upload failed');
      setUploadProgress(0);
    } finally {
      setTimeout(() => {
        setIsUploading(false);
      }, 2000);
    }
  };

  if (isChecking) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Checking policy configuration...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-primary-50 rounded-xl p-6 mb-6 border border-primary-100">
          <h1 className="text-3xl font-bold text-primary-700 mb-2">
            ⚙️ Policy Configuration
          </h1>
          <p className="text-gray-600">
            Upload and manage Health Insurance Policy Rules & Regulations for RAG-based risk evaluation
          </p>
        </div>

        {/* Current Status */}
        <div className="card mb-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">📊 Current Status</h2>
          
          <div className="grid md:grid-cols-2 gap-4">
            <div className={`p-4 rounded-lg border-2 ${
              policyStatus?.exists 
                ? 'bg-green-50 border-green-200' 
                : 'bg-yellow-50 border-yellow-200'
            }`}>
              <div className="flex items-center space-x-3">
                {policyStatus?.exists ? (
                  <CheckCircle className="w-6 h-6 text-green-600" />
                ) : (
                  <AlertCircle className="w-6 h-6 text-yellow-600" />
                )}
                <div>
                  <p className="font-semibold text-gray-800">Policy Knowledge Base</p>
                  <p className={`text-sm ${
                    policyStatus?.exists ? 'text-green-700' : 'text-yellow-700'
                  }`}>
                    {policyStatus?.exists ? 'Configured & Ready' : 'Not Configured'}
                  </p>
                </div>
              </div>
            </div>

            <div className="p-4 rounded-lg border-2 bg-blue-50 border-blue-200">
              <div className="flex items-center space-x-3">
                <Database className="w-6 h-6 text-blue-600" />
                <div>
                  <p className="font-semibold text-gray-800">ChromaDB Collection</p>
                  <p className="text-sm text-blue-700">
                    {policyStatus?.collection_name || 'N/A'}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {policyStatus?.db_path && (
            <div className="mt-4 p-3 bg-gray-50 rounded-lg">
              <p className="text-xs text-gray-600">
                <span className="font-semibold">Database Path:</span> {policyStatus.db_path}
              </p>
            </div>
          )}
        </div>

        {/* Upload Section */}
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">📤 Upload Policy Document</h2>

          {policyStatus?.exists && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4 flex items-start space-x-3">
              <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
              <div>
                <p className="font-semibold text-blue-800">Policy Already Exists</p>
                <p className="text-sm text-blue-700 mt-1">
                  A policy knowledge base is already configured. Enable "Overwrite Existing" to replace it with a new policy.
                </p>
              </div>
            </div>
          )}

          {/* File Input */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Policy PDF File <span className="text-red-500">*</span>
            </label>
            <div className="relative">
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileSelect}
                className="hidden"
                id="policy-upload"
                disabled={isUploading}
              />
              <label
                htmlFor="policy-upload"
                className={`flex items-center justify-center w-full px-4 py-8 border-2 border-dashed rounded-lg cursor-pointer transition-colors ${
                  selectedFile
                    ? 'border-green-400 bg-green-50'
                    : 'border-gray-300 bg-gray-50 hover:bg-gray-100'
                } ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <div className="text-center">
                  {selectedFile ? (
                    <>
                      <FileText className="w-12 h-12 text-green-600 mx-auto mb-2" />
                      <p className="font-semibold text-green-800">{selectedFile.name}</p>
                      <p className="text-sm text-green-600 mt-1">
                        {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                      </p>
                    </>
                  ) : (
                    <>
                      <Upload className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                      <p className="text-gray-600 font-medium">Click to upload policy PDF</p>
                      <p className="text-sm text-gray-500 mt-1">PDF files only, max 200MB</p>
                    </>
                  )}
                </div>
              </label>
            </div>
          </div>

          {/* Force Reload Checkbox */}
          {policyStatus?.exists && (
            <div className="mb-4">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={forceReload}
                  onChange={(e) => setForceReload(e.target.checked)}
                  className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                  disabled={isUploading}
                />
                <span className="text-sm font-medium text-gray-700">
                  Overwrite Existing Policy Knowledge Base
                </span>
              </label>
              {forceReload && (
                <p className="text-xs text-orange-600 mt-1 ml-6">
                  ⚠️ This will delete the existing policy and create a new one
                </p>
              )}
            </div>
          )}

          {/* Progress Bar */}
          {isUploading && (
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">{uploadMessage}</span>
                <span className="text-sm font-semibold text-primary-600">{uploadProgress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex space-x-3">
            <button
              onClick={handleUpload}
              disabled={!selectedFile || isUploading || (policyStatus?.exists && !forceReload)}
              className="btn-primary flex items-center space-x-2 flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Upload className="w-4 h-4" />
              <span>{isUploading ? 'Processing...' : 'Upload & Index Policy'}</span>
            </button>

            <button
              onClick={checkPolicyStatus}
              disabled={isUploading}
              className="btn-secondary flex items-center space-x-2"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Refresh Status</span>
            </button>
          </div>
        </div>

        {/* Help Section */}
        <div className="card mt-6 bg-gradient-to-r from-blue-50 to-indigo-50">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">💡 How It Works</h3>
          <ol className="space-y-2 text-sm text-gray-700">
            <li className="flex items-start">
              <span className="font-semibold text-primary-600 mr-2">1.</span>
              Upload your Health Insurance Policy Rules & Regulations PDF
            </li>
            <li className="flex items-start">
              <span className="font-semibold text-primary-600 mr-2">2.</span>
              The system extracts and chunks the policy document
            </li>
            <li className="flex items-start">
              <span className="font-semibold text-primary-600 mr-2">3.</span>
              Creates embeddings using sentence-transformers
            </li>
            <li className="flex items-start">
              <span className="font-semibold text-primary-600 mr-2">4.</span>
              Stores in ChromaDB for RAG-based retrieval during risk evaluation
            </li>
          </ol>
        </div>
      </div>
    </div>
  );
};
