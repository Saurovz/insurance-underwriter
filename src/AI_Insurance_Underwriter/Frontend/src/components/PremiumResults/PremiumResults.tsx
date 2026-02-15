// src/components/PremiumResults/PremiumResults.tsx
import React from 'react';
import { CheckCircle, AlertTriangle, XCircle, TrendingUp, Shield, AlertCircle } from 'lucide-react';
import type { ApplicationData } from '../../types/application';

interface PremiumResultsProps {
  data: ApplicationData;
}

export const PremiumResults: React.FC<PremiumResultsProps> = ({ data }) => {
  const getStatusIcon = () => {
    if (data.risk_category === 'DECLINED') {
      return <XCircle className="w-12 h-12 text-red-500" />;
    } else if (data.requires_human_review) {
      return <AlertTriangle className="w-12 h-12 text-yellow-500" />;
    } else {
      return <CheckCircle className="w-12 h-12 text-green-500" />;
    }
  };

  const getStatusColor = () => {
    if (data.risk_category === 'DECLINED') return 'red';
    if (data.requires_human_review) return 'yellow';
    return 'green';
  };

  const statusColor = getStatusColor();

  return (
    <div className="card mt-6 animate-fade-in">
      <h3 className="text-xl font-semibold text-gray-800 mb-6 pb-3 border-b border-gray-200">
        🎯 Decision Making
      </h3>

      {/* Status Banner */}
      <div className={`bg-${statusColor}-50 border-2 border-${statusColor}-200 rounded-xl p-6 mb-6`}>
        <div className="flex items-center justify-center mb-4">
          {getStatusIcon()}
        </div>
        
        <div className="text-center">
          {data.risk_category === 'DECLINED' ? (
            <>
              <h4 className="text-2xl font-bold text-red-700 mb-2">APPLICATION DECLINED</h4>
              <p className="text-red-600">Application exceeds maximum acceptable risk threshold</p>
            </>
          ) : data.requires_human_review ? (
            <>
              <h4 className="text-2xl font-bold text-yellow-700 mb-2">REQUIRES HUMAN REVIEW</h4>
              <p className="text-yellow-600">{data.review_reason}</p>
            </>
          ) : (
            <>
              <h4 className="text-2xl font-bold text-green-700 mb-2">AUTO-APPROVED ✓</h4>
              <p className="text-green-600">Application meets all underwriting criteria</p>
            </>
          )}
        </div>
      </div>

      {/* Risk & Premium Details */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Risk Assessment */}
        <div className="bg-gray-50 rounded-lg p-5">
          <h4 className="font-semibold text-gray-700 mb-4 flex items-center">
            <TrendingUp className="w-5 h-5 mr-2 text-orange-500" />
            Risk Assessment
          </h4>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Risk Score</span>
              <span className="text-lg font-bold text-gray-900">
                {data.risk_score?.toFixed(0)}/100
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Risk Category</span>
              <span className={`badge badge-${getRiskCategoryColor(data.risk_category)}`}>
                {data.risk_category}
              </span>
            </div>
            {data.flagged_conditions && data.flagged_conditions.length > 0 && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <p className="text-sm font-medium text-gray-700 mb-2">Flagged Conditions:</p>
                <ul className="text-sm text-gray-600 space-y-1">
                  {Array.isArray(data.flagged_conditions) 
                    ? data.flagged_conditions.map((condition, idx) => (
                        <li key={idx} className="flex items-start">
                          <AlertCircle className="w-4 h-4 mr-2 mt-0.5 text-orange-500 flex-shrink-0" />
                          {condition}
                        </li>
                      ))
                    : <li>{data.flagged_conditions}</li>
                  }
                </ul>
              </div>
            )}
          </div>
        </div>

        {/* Best Offer */}
        {!data.risk_category?.includes('DECLINED') && (
          <div className="bg-primary-50 rounded-lg p-5">
            <h4 className="font-semibold text-gray-700 mb-4 flex items-center">
              <Shield className="w-5 h-5 mr-2 text-primary-600" />
              Best Offer
            </h4>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Base Premium</span>
                <span className="text-lg font-semibold text-gray-900">
                  ₹{data.base_premium?.toLocaleString()}/year
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Medical Loading</span>
                <span className="text-lg font-semibold text-orange-600">
                  +{data.medical_loading_percentage?.toFixed(0)}%
                </span>
              </div>
              <div className="pt-3 border-t-2 border-primary-200">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-700">Final Premium</span>
                  <span className="text-2xl font-bold text-primary-700">
                    ₹{data.final_premium?.toLocaleString()}
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-1">per year</p>
              </div>
              <div className="flex justify-between items-center pt-3 border-t border-primary-200">
                <span className="text-sm text-gray-600">Recommended Plan</span>
                <span className="text-sm font-semibold text-primary-700">
                  {data.recommended_plan}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* KYC Verification Status */}
      {data.kyc_verification_status && (
        <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h4 className="font-semibold text-gray-700 mb-2 flex items-center">
            <Shield className="w-5 h-5 mr-2 text-blue-600" />
            KYC Verification
          </h4>
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Status:</span>
            <span className={`badge ${
              data.kyc_verification_status === 'VERIFIED' ? 'badge-success' : 
              data.kyc_verification_status === 'NOT_PROVIDED' ? 'badge-warning' : 
              'badge-error'
            }`}>
              {data.kyc_verification_status}
            </span>
          </div>
          {data.kyc_verification_message && (
            <p className="text-sm text-gray-600 mt-2">{data.kyc_verification_message}</p>
          )}
        </div>
      )}

      {/* Exclusions */}
      {data.exclusions && data.exclusions.length > 0 && (
        <div className="mt-6 p-4 bg-amber-50 border border-amber-200 rounded-lg">
          <h4 className="font-semibold text-amber-800 mb-2">⚠️ Policy Exclusions</h4>
          <ul className="text-sm text-amber-700 space-y-1">
            {Array.isArray(data.exclusions)
              ? data.exclusions.map((exclusion, idx) => (
                  <li key={idx}>• {exclusion}</li>
                ))
              : <li>• {data.exclusions}</li>
            }
          </ul>
        </div>
      )}
    </div>
  );
};

const getRiskCategoryColor = (category?: string): string => {
  switch (category) {
    case 'LOW':
      return 'success';
    case 'MODERATE':
      return 'info';
    case 'HIGH':
      return 'warning';
    case 'DECLINED':
      return 'error';
    default:
      return 'info';
  }
};
