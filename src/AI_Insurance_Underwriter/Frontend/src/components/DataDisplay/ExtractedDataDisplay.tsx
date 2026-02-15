// src/components/DataDisplay/ExtractedDataDisplay.tsx
import React from 'react';
import { User, Heart, Briefcase, Mail, Phone, MapPin, DollarSign } from 'lucide-react';
import type { ApplicationData } from '../../types/application';

interface ExtractedDataDisplayProps {
  data: Partial<ApplicationData>;
}

export const ExtractedDataDisplay: React.FC<ExtractedDataDisplayProps> = ({ data }) => {
  return (
    <div className="card mt-6 animate-fade-in">
      <h3 className="text-xl font-semibold text-gray-800 mb-6 pb-3 border-b border-gray-200">
        📄 Application Data Extract
      </h3>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Applicant Information */}
        <div>
          <h4 className="font-semibold text-gray-700 mb-4 flex items-center">
            <User className="w-5 h-5 mr-2 text-primary-600" />
            Applicant Information
          </h4>
          <div className="space-y-3 bg-gray-50 rounded-lg p-4">
            <DataRow label="Name" value={data.applicant_name} icon={<User className="w-4 h-4" />} />
            <DataRow label="Age" value={data.age?.toString()} icon={<User className="w-4 h-4" />} />
            <DataRow label="Gender" value={data.gender} icon={<User className="w-4 h-4" />} />
            <DataRow label="Contact Number" value={data.contact_number} icon={<Phone className="w-4 h-4" />} />
            <DataRow label="Email" value={data.email} icon={<Mail className="w-4 h-4" />} />
            <DataRow label="Address" value={data.address} icon={<MapPin className="w-4 h-4" />} />
            <DataRow label="Occupation" value={data.occupation} icon={<Briefcase className="w-4 h-4" />} />
            <DataRow 
              label="Annual Income" 
              value={data.annual_income ? `₹${data.annual_income.toLocaleString()}` : undefined}
              icon={<DollarSign className="w-4 h-4" />}
            />
          </div>
        </div>

        {/* Health Information */}
        <div>
          <h4 className="font-semibold text-gray-700 mb-4 flex items-center">
            <Heart className="w-5 h-5 mr-2 text-red-500" />
            Health Information
          </h4>
          <div className="space-y-3 bg-gray-50 rounded-lg p-4">
            <DataRow 
              label="BMI" 
              value={data.bmi ? data.bmi.toFixed(1) : undefined}
              icon={<Heart className="w-4 h-4" />}
            />
            <DataRow 
              label="Smoking Status" 
              value={data.smoking_status}
              icon={<Heart className="w-4 h-4" />}
              highlight={data.smoking_status ? data.smoking_status !== 'Non-Smoker' : false}
            />
            <DataRow 
              label="Alcohol Consumption" 
              value={data.alcohol_consumption}
              icon={<Heart className="w-4 h-4" />}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

interface DataRowProps {
  label: string;
  value?: string;
  icon?: React.ReactNode;
  highlight?: boolean;
}

const DataRow: React.FC<DataRowProps> = ({ label, value, icon, highlight }) => (
  <div className="flex justify-between items-center">
    <span className="text-sm text-gray-600 flex items-center">
      {icon && <span className="mr-2 text-gray-400">{icon}</span>}
      {label}
    </span>
    <span className={`text-sm font-medium ${highlight ? 'text-orange-600' : 'text-gray-900'}`}>
      {value || 'Not extracted'}
    </span>
  </div>
);
