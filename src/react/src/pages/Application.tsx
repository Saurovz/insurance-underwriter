// src/pages/Application.tsx
import React, { useState, useEffect } from 'react';
import { FileUploadZone } from '../components/FileUpload/FileUploadZone';
import { ProcessingStatus } from '../components/ProcessingStatus/ProcessingStatus';
import { ExtractedDataDisplay } from '../components/DataDisplay/ExtractedDataDisplay';
import { PremiumResults } from '../components/PremiumResults/PremiumResults';
import { FloatingChatbot } from '../components/Chatbot/FloatingChatbot';
import { uploadFiles, processDocuments, evaluateApplication, getApplication, createWebSocketConnection } from '../services/api';
import type { ApplicationData, ProcessingStatus as ProcessingStatusType } from '../types/application';
import { Loader2, RefreshCw, CheckCircle2 } from 'lucide-react';
import toast, { Toaster } from 'react-hot-toast';

export const Application: React.FC = () => {
  const [applicationForm, setApplicationForm] = useState<File[]>([]);
  const [medicalDocs, setMedicalDocs] = useState<File[]>([]);
  const [kycDocument, setKycDocument] = useState<File[]>([]);
  
  const [applicationId, setApplicationId] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingStatus, setProcessingStatus] = useState<ProcessingStatusType | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  const [extractedData, setExtractedData] = useState<Partial<ApplicationData> | null>(null);
  const [evaluationResults, setEvaluationResults] = useState<ApplicationData | null>(null);
  
  const [currentStep, setCurrentStep] = useState<'upload' | 'extracted' | 'evaluated'>('upload');

  // WebSocket for real-time updates
  useEffect(() => {
    if (!applicationId) return;

    const ws = createWebSocketConnection(applicationId);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setProcessingStatus(data);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    return () => {
      ws.close();
    };
  }, [applicationId]);

  const handleProcessDocuments = async () => {
    if (applicationForm.length === 0 || medicalDocs.length === 0) {
      toast.error('Please upload Application Form and Medical Documents');
      return;
    }

    setIsProcessing(true);
    setError(null);
    setProcessingStatus({ step: 'upload', message: 'Uploading files...', progress: 10 });

    try {
      // Step 1: Upload files
      const uploadResponse = await uploadFiles(
        applicationForm[0],
        medicalDocs,
        kycDocument.length > 0 ? kycDocument[0] : undefined
      );

      if (!uploadResponse.success) {
        throw new Error('File upload failed');
      }

      const appId = uploadResponse.application_id;
      setApplicationId(appId);
      toast.success(`Files uploaded! ID: ${appId.slice(0, 8)}...`);

      // Step 2: Process documents (extract data)
      setProcessingStatus({ step: 'processing', message: 'Extracting data from PDFs...', progress: 30 });
      
      const processResponse = await processDocuments(appId);

      if (!processResponse.success) {
        throw new Error(processResponse.errors?.join(', ') || 'Processing failed');
      }

      setExtractedData(processResponse.data);
      setCurrentStep('extracted');
      toast.success('Data extracted successfully!');
      setProcessingStatus({ step: 'complete', message: 'Data extraction complete!', progress: 100 });

    } catch (err: any) {
      console.error('Processing error:', err);
      setError(err.message || 'An error occurred during processing');
      toast.error(err.message || 'Processing failed');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleEvaluate = async () => {
    if (!applicationId) {
      toast.error('No application ID found');
      return;
    }

    setIsProcessing(true);
    setError(null);
    setProcessingStatus({ step: 'evaluation', message: 'Evaluating risk...', progress: 20 });

    try {
      const evaluationResponse = await evaluateApplication(applicationId);

      if (!evaluationResponse.success) {
        throw new Error('Evaluation failed');
      }

      // Fetch complete application data
      const appDataResponse = await getApplication(applicationId);
      
      if (!appDataResponse.success) {
        throw new Error('Failed to fetch application data');
      }

      setEvaluationResults(appDataResponse.data);
      setCurrentStep('evaluated');
      toast.success('Evaluation complete!');
      setProcessingStatus({ step: 'complete', message: 'Evaluation complete!', progress: 100 });

    } catch (err: any) {
      console.error('Evaluation error:', err);
      setError(err.message || 'An error occurred during evaluation');
      toast.error(err.message || 'Evaluation failed');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleNewApplication = () => {
    setApplicationForm([]);
    setMedicalDocs([]);
    setKycDocument([]);
    setApplicationId(null);
    setExtractedData(null);
    setEvaluationResults(null);
    setProcessingStatus(null);
    setError(null);
    setCurrentStep('upload');
    toast.success('Ready for new application');
  };

  const isUploadComplete = applicationForm.length > 0 && medicalDocs.length > 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 p-6">
      <Toaster position="top-right" />
      
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="bg-primary-50 rounded-xl p-6 mb-6 border border-primary-100">
          <h1 className="text-3xl font-bold text-primary-700 mb-2">
            📝 Customer Underwriting Management
          </h1>
          <p className="text-gray-600">
            Processes Application Form and Lab Reports for underwriter decision-making and offering best premium.
          </p>
        </div>

        {/* File Upload Section */}
        {currentStep === 'upload' && (
          <div className="card animate-fade-in">
            <h2 className="text-2xl font-semibold text-gray-800 mb-6">Document Upload</h2>

            <FileUploadZone
              label="1. Application Form"
              description="Upload the insurance application form (Required)"
              accept="application/pdf"
              multiple={false}
              required={true}
              files={applicationForm}
              onFilesChange={setApplicationForm}
            />

            <FileUploadZone
              label="2. Lab Reports"
              description="Upload one or more medical documents (Required)"
              accept="application/pdf"
              multiple={true}
              required={true}
              files={medicalDocs}
              onFilesChange={setMedicalDocs}
            />

            <FileUploadZone
              label="3. KYC Document (Optional)"
              description="Upload Aadhaar or PAN card for identity verification"
              accept="application/pdf,image/*"
              multiple={false}
              required={false}
              files={kycDocument}
              onFilesChange={setKycDocument}
            />

            {/* Upload Summary */}
            {isUploadComplete && (
              <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-green-800 font-medium flex items-center">
                  <CheckCircle2 className="w-5 h-5 mr-2" />
                  {1 + medicalDocs.length + kycDocument.length} file(s) ready to be processed
                </p>
              </div>
            )}

            {!isUploadComplete && (
              <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-yellow-800 text-sm">
                  ⚠️ Please upload Application Form and at least one Medical Document to continue
                </p>
              </div>
            )}

            {/* Process Button */}
            <button
              onClick={handleProcessDocuments}
              disabled={!isUploadComplete || isProcessing}
              className="btn-primary mt-6 w-full sm:w-auto flex items-center justify-center space-x-2"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Processing...</span>
                </>
              ) : (
                <span>Process Documents</span>
              )}
            </button>
          </div>
        )}

        {/* Processing Status */}
        <ProcessingStatus
          status={processingStatus}
          isProcessing={isProcessing}
          error={error}
        />

        {/* Extracted Data Display */}
        {extractedData && currentStep === 'extracted' && (
          <>
            <ExtractedDataDisplay data={extractedData} />

            <div className="card mt-6">
              <h3 className="text-xl font-semibold text-gray-800 mb-4">
                🔍 Review and Underwriting
              </h3>
              <p className="text-gray-600 mb-4">
                Access risk and decision making
              </p>
              <button
                onClick={handleEvaluate}
                disabled={isProcessing}
                className="btn-primary flex items-center space-x-2"
              >
                {isProcessing ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Evaluating...</span>
                  </>
                ) : (
                  <span>Evaluate Application</span>
                )}
              </button>
            </div>
          </>
        )}

        {/* Premium Results */}
        {evaluationResults && currentStep === 'evaluated' && (
          <>
            <ExtractedDataDisplay data={evaluationResults} />
            <PremiumResults data={evaluationResults} />

            {/* New Application Button */}
            <div className="card mt-6 bg-gradient-to-r from-primary-50 to-indigo-50">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-gray-800">Start New Application</h3>
                  <p className="text-sm text-gray-600">Process another underwriting request</p>
                </div>
                <button
                  onClick={handleNewApplication}
                  className="btn-primary flex items-center space-x-2"
                >
                  <RefreshCw className="w-4 h-4" />
                  <span>New Application</span>
                </button>
              </div>
            </div>
          </>
        )}

        {/* Application ID Display */}
        {applicationId && (
          <div className="mt-6 p-4 bg-gray-50 border border-gray-200 rounded-lg">
            <p className="text-sm text-gray-600">
              Application ID: <span className="font-mono font-semibold text-gray-900">{applicationId}</span>
            </p>
          </div>
        )}
      </div>

      {/* Floating Chatbot */}
      <FloatingChatbot />
    </div>
  );
};
