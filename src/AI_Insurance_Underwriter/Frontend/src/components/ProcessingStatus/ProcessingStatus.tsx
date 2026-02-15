// src/components/ProcessingStatus/ProcessingStatus.tsx
import React from 'react';
import { Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import type { ProcessingStatus as ProcessingStatusType } from '../../types/application';

interface ProcessingStatusProps {
  status: ProcessingStatusType | null;
  isProcessing: boolean;
  error?: string | null;
}

export const ProcessingStatus: React.FC<ProcessingStatusProps> = ({
  status,
  isProcessing,
  error,
}) => {
  if (!isProcessing && !error && !status) return null;

  return (
    <div className="card mt-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Processing Status</h3>
      
      {error ? (
        <div className="flex items-start space-x-3 p-4 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
          <div>
            <p className="font-medium text-red-800">Error</p>
            <p className="text-sm text-red-600 mt-1">{error}</p>
          </div>
        </div>
      ) : (
        <>
          {/* Progress Bar */}
          <div className="mb-4">
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span>{status?.step || 'Initializing...'}</span>
              <span>{status?.progress || 0}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div
                className="bg-primary-600 h-2.5 rounded-full transition-all duration-500"
                style={{ width: `${status?.progress || 0}%` }}
              />
            </div>
          </div>

          {/* Status Message */}
          <div className="flex items-center space-x-3 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            {status?.progress === 100 ? (
              <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
            ) : (
              <Loader2 className="w-5 h-5 text-primary-600 animate-spin flex-shrink-0" />
            )}
            <div>
              <p className="font-medium text-gray-800">{status?.message}</p>
              {status?.timestamp && (
                <p className="text-xs text-gray-500 mt-1">
                  {new Date(status.timestamp).toLocaleTimeString()}
                </p>
              )}
            </div>
          </div>

          {/* Processing Steps Indicator */}
          <div className="mt-6 flex justify-between items-center text-xs">
            <div className={`flex flex-col items-center ${status?.progress && status.progress >= 20 ? 'text-green-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${status?.progress && status.progress >= 20 ? 'bg-green-100' : 'bg-gray-100'}`}>
                {status?.progress && status.progress >= 20 ? '✓' : '1'}
              </div>
              <span className="mt-1">Upload</span>
            </div>
            
            <div className="flex-1 h-0.5 bg-gray-300 mx-2" />
            
            <div className={`flex flex-col items-center ${status?.progress && status.progress >= 50 ? 'text-green-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${status?.progress && status.progress >= 50 ? 'bg-green-100' : 'bg-gray-100'}`}>
                {status?.progress && status.progress >= 50 ? '✓' : '2'}
              </div>
              <span className="mt-1">Extract</span>
            </div>
            
            <div className="flex-1 h-0.5 bg-gray-300 mx-2" />
            
            <div className={`flex flex-col items-center ${status?.progress && status.progress >= 70 ? 'text-green-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${status?.progress && status.progress >= 70 ? 'bg-green-100' : 'bg-gray-100'}`}>
                {status?.progress && status.progress >= 70 ? '✓' : '3'}
              </div>
              <span className="mt-1">Save</span>
            </div>
            
            <div className="flex-1 h-0.5 bg-gray-300 mx-2" />
            
            <div className={`flex flex-col items-center ${status?.progress === 100 ? 'text-green-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${status?.progress === 100 ? 'bg-green-100' : 'bg-gray-100'}`}>
                {status?.progress === 100 ? '✓' : '4'}
              </div>
              <span className="mt-1">Complete</span>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
