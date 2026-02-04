// src/pages/Detail.tsx
import React, { useState, useEffect } from 'react';
import { 
  Search, Download, TrendingUp, TrendingDown, Minus, AlertCircle, Loader2, RefreshCw,
  ChevronDown, ChevronUp, User, Activity, DollarSign, FileText, ShieldCheck, X,
  File, ExternalLink
} from 'lucide-react';
import toast from 'react-hot-toast';

interface Application {
  application_id: string;
  id: string;
  filename?: string;
  applicant_name?: string;
  age?: number;
  gender?: string;
  contact_number?: string;
  email?: string;
  address?: string;
  occupation?: string;
  annual_income?: number;
  date_of_birth?: string;
  bmi?: number;
  smoking_status?: string;
  alcohol_consumption?: string;
  risk_score?: number;
  risk_category?: string;
  flagged_conditions?: string;
  exclusions?: string;
  base_premium?: number;
  medical_loading_percentage?: number;
  final_premium?: number;
  recommended_plan?: string;
  requires_human_review?: boolean;
  review_reason?: string;
  kyc_verification_status?: string;
  kyc_document_type?: string;
  kyc_discrepancies?: any[];
  kyc_total_discrepancies?: number;
  kyc_verification_message?: string;
  upload_time?: string;
  processing_timestamp?: string;
  current_step?: string;
  errors?: string;
}

export const Detail: React.FC = () => {
  const [applications, setApplications] = useState<Application[]>([]);
  const [filteredApps, setFilteredApps] = useState<Application[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterRisk, setFilterRisk] = useState('All');
  const [filterReview, setFilterReview] = useState('All');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedAppId, setSelectedAppId] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'personal' | 'health' | 'premium' | 'metadata' | 'kyc'>('personal');
  const [expandedDocs, setExpandedDocs] = useState<Set<string>>(new Set());

  useEffect(() => {
    fetchApplications();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [applications, searchTerm, filterRisk, filterReview]);

  const fetchApplications = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/api/applications');
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      let apps: Application[] = [];
      
      if (data.success === true && Array.isArray(data.applications)) {
        apps = data.applications;
      } else if (Array.isArray(data)) {
        apps = data;
      }
      
      setApplications(apps);
      setFilteredApps(apps);
      
    } catch (err: any) {
      console.error('Fetch error:', err);
      setError(err.message || 'Failed to load applications');
      toast.error('Failed to load applications');
      setApplications([]);
      setFilteredApps([]);
    } finally {
      setIsLoading(false);
    }
  };

  const applyFilters = () => {
    if (!Array.isArray(applications)) {
      setFilteredApps([]);
      return;
    }

    let filtered = [...applications];

    if (searchTerm && searchTerm.trim()) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(app => 
        (app.applicant_name?.toLowerCase() || '').includes(term) ||
        (app.application_id?.toLowerCase() || '').includes(term) ||
        (app.id?.toLowerCase() || '').includes(term)
      );
    }

    if (filterRisk !== 'All') {
      filtered = filtered.filter(app => {
        const category = app.risk_category?.toUpperCase();
        return category === filterRisk.toUpperCase();
      });
    }

    if (filterReview === 'Review Required') {
      filtered = filtered.filter(app => app.requires_human_review === true);
    } else if (filterReview === 'Auto Approved') {
      filtered = filtered.filter(app => app.requires_human_review === false);
    }

    setFilteredApps(filtered);
  };

  const getRiskBadge = (category?: string) => {
    if (!category) {
      return <span className="text-gray-400 text-sm">N/A</span>;
    }

    const normalizedCategory = category.toUpperCase();
    
    const badges: Record<string, { bg: string; text: string; icon: any }> = {
      LOW: { bg: 'bg-green-100 text-green-800', text: 'Low Risk', icon: TrendingDown },
      MEDIUM: { bg: 'bg-yellow-100 text-yellow-800', text: 'Medium Risk', icon: Minus },
      HIGH: { bg: 'bg-red-100 text-red-800', text: 'High Risk', icon: TrendingUp },
    };

    const badge = badges[normalizedCategory] || badges.MEDIUM;
    const Icon = badge.icon;

    return (
      <span className={`inline-flex items-center space-x-1 px-3 py-1 rounded-full text-sm font-medium whitespace-nowrap ${badge.bg}`}>
        <Icon className="w-4 h-4" />
        <span>{badge.text}</span>
      </span>
    );
  };

  const getReviewBadge = (requiresReview?: boolean) => {
    if (requiresReview === undefined || requiresReview === null) {
      return <span className="text-gray-400 text-sm">N/A</span>;
    }
    
    return requiresReview ? (
      <span className="bg-orange-100 text-orange-800 px-3 py-1 rounded-full text-sm font-medium whitespace-nowrap">
        Review Required
      </span>
    ) : (
      <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium whitespace-nowrap">
        Auto Approved
      </span>
    );
  };

  const getPlanBadge = (plan?: string) => {
    if (!plan) return <span className="text-gray-400 text-sm">N/A</span>;

    const planColors: Record<string, string> = {
      'GOLD_PLAN': 'bg-yellow-100 text-yellow-800 border-yellow-300',
      'SILVER_PLAN': 'bg-gray-100 text-gray-800 border-gray-300',
      'BRONZE_PLAN': 'bg-orange-100 text-orange-800 border-orange-300',
      'STANDARD_PLAN': 'bg-blue-100 text-blue-800 border-blue-300',
      'BRONZE_PLAN_WITH_EXCLUSIONS': 'bg-red-100 text-red-800 border-red-300',
    };

    const colorClass = planColors[plan] || 'bg-gray-100 text-gray-800 border-gray-300';
    
    // Format plan name for display
    let displayName = plan.replace(/_/g, ' ');
    
    // Special handling for long names
    if (plan === 'BRONZE_PLAN_WITH_EXCLUSIONS') {
      displayName = 'Bronze + Exclusions';
    }

    return (
      <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium border whitespace-nowrap ${colorClass}`}>
        {displayName}
      </span>
    );
  };

  const toggleRow = (appId: string) => {
    if (selectedAppId === appId) {
      setSelectedAppId(null);
      setExpandedDocs(new Set());
    } else {
      setSelectedAppId(appId);
      setActiveTab('personal');
      setExpandedDocs(new Set());
    }
  };

  const toggleDocument = (docName: string) => {
    const newExpanded = new Set(expandedDocs);
    if (newExpanded.has(docName)) {
      newExpanded.delete(docName);
    } else {
      newExpanded.add(docName);
    }
    setExpandedDocs(newExpanded);
  };

  const getDocumentUrl = (appId: string, filename: string) => {
    // Construct URL to backend document endpoint
    return `http://localhost:8000/api/documents/${appId}/${encodeURIComponent(filename)}`;
  };

  const exportToCSV = () => {
    if (!filteredApps || filteredApps.length === 0) {
      toast.error('No applications to export');
      return;
    }

    try {
      const headers = [
        'Application ID', 'Name', 'Age', 'Gender', 'BMI', 'Smoking',
        'Risk Score', 'Risk Category', 'Base Premium', 'Final Premium',
        'Plan', 'Review Required', 'KYC Status',
      ];

      const rows = filteredApps.map(app => [
        app.application_id || app.id || '',
        app.applicant_name || 'N/A',
        app.age?.toString() || 'N/A',
        app.gender || 'N/A',
        app.bmi?.toFixed(1) || 'N/A',
        app.smoking_status || 'N/A',
        app.risk_score?.toString() || 'N/A',
        app.risk_category || 'N/A',
        app.base_premium?.toString() || 'N/A',
        app.final_premium?.toString() || 'N/A',
        app.recommended_plan || 'N/A',
        app.requires_human_review ? 'Yes' : 'No',
        app.kyc_verification_status || 'N/A',
      ]);

      const csvContent = [headers, ...rows]
        .map(row => row.map(cell => `"${cell}"`).join(','))
        .join('\n');

      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `applications_${new Date().toISOString().split('T')[0]}.csv`;
      a.click();
      window.URL.revokeObjectURL(url);
      
      toast.success(`Exported ${filteredApps.length} applications to CSV`);
    } catch (err) {
      console.error('Export error:', err);
      toast.error('Failed to export CSV');
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-primary-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600 font-medium">Loading applications...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center p-6">
        <div className="card max-w-md">
          <div className="text-center">
            <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h2 className="text-2xl font-semibold text-gray-800 mb-2">Error Loading Data</h2>
            <p className="text-gray-600 mb-6">{error}</p>
            <button 
              onClick={fetchApplications} 
              className="btn-primary flex items-center space-x-2 mx-auto"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Try Again</span>
            </button>
          </div>
        </div>
      </div>
    );
  }

  const lowRiskCount = applications.filter(a => a.risk_category?.toUpperCase() === 'LOW').length;
  const mediumRiskCount = applications.filter(a => a.risk_category?.toUpperCase() === 'MEDIUM').length;
  const highRiskCount = applications.filter(a => a.risk_category?.toUpperCase() === 'HIGH').length;

  const selectedApp = applications.find(app => 
    (app.application_id || app.id) === selectedAppId
  );

  // Parse documents from filename field
  const getDocuments = (filename?: string): string[] => {
    if (!filename) return [];
    return filename.split(',').map(f => f.trim()).filter(f => f.length > 0);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-primary-50 rounded-xl p-6 mb-6 border border-primary-100">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-primary-700 mb-2">
                📋 All Applications
              </h1>
              <p className="text-gray-600">
                View and manage all submitted insurance applications
              </p>
            </div>
            <button
              onClick={fetchApplications}
              className="btn-secondary flex items-center space-x-2"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Refresh</span>
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg p-4 shadow-md border-l-4 border-primary-500">
            <p className="text-sm text-gray-600 mb-1">Total Applications</p>
            <p className="text-3xl font-bold text-gray-800">{applications.length}</p>
          </div>
          <div className="bg-white rounded-lg p-4 shadow-md border-l-4 border-green-500">
            <p className="text-sm text-gray-600 mb-1">Low Risk</p>
            <p className="text-3xl font-bold text-green-600">{lowRiskCount}</p>
          </div>
          <div className="bg-white rounded-lg p-4 shadow-md border-l-4 border-yellow-500">
            <p className="text-sm text-gray-600 mb-1">Medium Risk</p>
            <p className="text-3xl font-bold text-yellow-600">{mediumRiskCount}</p>
          </div>
          <div className="bg-white rounded-lg p-4 shadow-md border-l-4 border-red-500">
            <p className="text-sm text-gray-600 mb-1">High Risk</p>
            <p className="text-3xl font-bold text-red-600">{highRiskCount}</p>
          </div>
        </div>

        {/* Filters */}
        <div className="card mb-6">
          <div className="flex flex-wrap items-center gap-4 mb-4">
            <div className="flex-1 min-w-[250px]">
              <div className="relative">
                <Search className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search by name or ID..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
                />
              </div>
            </div>

            <select
              value={filterRisk}
              onChange={(e) => setFilterRisk(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none bg-white"
            >
              <option value="All">All Risk Levels</option>
              <option value="Low">Low Risk</option>
              <option value="Medium">Medium Risk</option>
              <option value="High">High Risk</option>
            </select>

            <select
              value={filterReview}
              onChange={(e) => setFilterReview(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none bg-white"
            >
              <option value="All">All Status</option>
              <option value="Auto Approved">Auto Approved</option>
              <option value="Review Required">Review Required</option>
            </select>

            <button
              onClick={exportToCSV}
              disabled={!filteredApps || filteredApps.length === 0}
              className="btn-primary flex items-center space-x-2"
            >
              <Download className="w-4 h-4" />
              <span>Export CSV</span>
            </button>
          </div>

          <div className="text-sm text-gray-600">
            Showing <span className="font-semibold text-primary-600">{filteredApps.length}</span> of <span className="font-semibold">{applications.length}</span> applications
          </div>
        </div>

        {/* Applications Table */}
        <div className="card overflow-hidden">
          {filteredApps.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b-2 border-gray-200">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">App ID</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Name</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Age/Gender</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">BMI</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Smoking</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Risk</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Plan</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Premium</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Status</th>
                    <th className="px-4 py-3 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 bg-white">
                  {filteredApps.map((app, index) => {
                    const appUniqueId = app.application_id || app.id;
                    const isExpanded = selectedAppId === appUniqueId;
                    
                    return (
                      <React.Fragment key={appUniqueId || `app-${index}`}>
                        <tr 
                          className={`hover:bg-gray-50 transition-colors cursor-pointer ${
                            isExpanded ? 'bg-blue-50' : ''
                          }`}
                          onClick={() => toggleRow(appUniqueId)}
                        >
                          <td className="px-4 py-4">
                            <p className="text-xs text-gray-500 font-mono">
                              {appUniqueId ? appUniqueId.slice(0, 8) + '...' : 'N/A'}
                            </p>
                          </td>
                          <td className="px-4 py-4">
                            <p className="font-medium text-gray-800">{app.applicant_name || 'N/A'}</p>
                          </td>
                          <td className="px-4 py-4 text-sm text-gray-700">
                            {app.age || 'N/A'} / {app.gender || 'N/A'}
                          </td>
                          <td className="px-4 py-4 text-sm text-gray-700">
                            {app.bmi ? app.bmi.toFixed(1) : 'N/A'}
                          </td>
                          <td className="px-4 py-4 text-sm text-gray-700">
                            {app.smoking_status || 'N/A'}
                          </td>
                          <td className="px-4 py-4">
                            {getRiskBadge(app.risk_category)}
                          </td>
                          <td className="px-4 py-4">
                            {getPlanBadge(app.recommended_plan)}
                          </td>
                          <td className="px-4 py-4">
                            <p className="text-sm font-semibold text-gray-800">
                              ₹{app.final_premium ? app.final_premium.toLocaleString('en-IN') : 'N/A'}
                            </p>
                          </td>
                          <td className="px-4 py-4">
                            {getReviewBadge(app.requires_human_review)}
                          </td>
                          <td className="px-4 py-4 text-center">
                            {isExpanded ? (
                              <ChevronUp className="w-5 h-5 text-primary-600 mx-auto" />
                            ) : (
                              <ChevronDown className="w-5 h-5 text-gray-400 mx-auto" />
                            )}
                          </td>
                        </tr>

                        {/* Expanded Detail View - ONLY for selected app */}
                        {isExpanded && selectedApp && (
                          <tr>
                            <td colSpan={10} className="px-0 py-0">
                              <div className="bg-gradient-to-br from-gray-50 to-gray-100 border-t-2 border-primary-200">
                                {/* Tab Headers */}
                                <div className="flex border-b border-gray-300 bg-white">
                                  <button
                                    onClick={(e) => { e.stopPropagation(); setActiveTab('personal'); }}
                                    className={`flex items-center space-x-2 px-6 py-3 font-medium transition-colors ${
                                      activeTab === 'personal'
                                        ? 'text-primary-600 border-b-2 border-primary-600 bg-blue-50'
                                        : 'text-gray-600 hover:text-primary-600 hover:bg-gray-50'
                                    }`}
                                  >
                                    <User className="w-4 h-4" />
                                    <span>Personal Info</span>
                                  </button>
                                  <button
                                    onClick={(e) => { e.stopPropagation(); setActiveTab('health'); }}
                                    className={`flex items-center space-x-2 px-6 py-3 font-medium transition-colors ${
                                      activeTab === 'health'
                                        ? 'text-primary-600 border-b-2 border-primary-600 bg-blue-50'
                                        : 'text-gray-600 hover:text-primary-600 hover:bg-gray-50'
                                    }`}
                                  >
                                    <Activity className="w-4 h-4" />
                                    <span>Health & Risk</span>
                                  </button>
                                  <button
                                    onClick={(e) => { e.stopPropagation(); setActiveTab('premium'); }}
                                    className={`flex items-center space-x-2 px-6 py-3 font-medium transition-colors ${
                                      activeTab === 'premium'
                                        ? 'text-primary-600 border-b-2 border-primary-600 bg-blue-50'
                                        : 'text-gray-600 hover:text-primary-600 hover:bg-gray-50'
                                    }`}
                                  >
                                    <DollarSign className="w-4 h-4" />
                                    <span>Premium Details</span>
                                  </button>
                                  <button
                                    onClick={(e) => { e.stopPropagation(); setActiveTab('metadata'); }}
                                    className={`flex items-center space-x-2 px-6 py-3 font-medium transition-colors ${
                                      activeTab === 'metadata'
                                        ? 'text-primary-600 border-b-2 border-primary-600 bg-blue-50'
                                        : 'text-gray-600 hover:text-primary-600 hover:bg-gray-50'
                                    }`}
                                  >
                                    <FileText className="w-4 h-4" />
                                    <span>Metadata</span>
                                  </button>
                                  <button
                                    onClick={(e) => { e.stopPropagation(); setActiveTab('kyc'); }}
                                    className={`flex items-center space-x-2 px-6 py-3 font-medium transition-colors ${
                                      activeTab === 'kyc'
                                        ? 'text-primary-600 border-b-2 border-primary-600 bg-blue-50'
                                        : 'text-gray-600 hover:text-primary-600 hover:bg-gray-50'
                                    }`}
                                  >
                                    <ShieldCheck className="w-4 h-4" />
                                    <span>KYC Verification</span>
                                  </button>

                                  {/* Close Button */}
                                  <div className="ml-auto flex items-center px-4">
                                    <button
                                      onClick={(e) => { e.stopPropagation(); setSelectedAppId(null); }}
                                      className="text-gray-400 hover:text-gray-600 transition-colors"
                                    >
                                      <X className="w-5 h-5" />
                                    </button>
                                  </div>
                                </div>

                                {/* Tab Content */}
                                <div className="p-6" onClick={(e) => e.stopPropagation()}>
                                  {/* Personal Info Tab */}
                                  {activeTab === 'personal' && (
                                    <div className="grid md:grid-cols-2 gap-6">
                                      <div className="space-y-4">
                                        <div>
                                          <p className="text-xs text-gray-500 mb-1">Full Name</p>
                                          <p className="text-gray-800 font-medium">{selectedApp.applicant_name || 'N/A'}</p>
                                        </div>
                                        <div>
                                          <p className="text-xs text-gray-500 mb-1">Age</p>
                                          <p className="text-gray-800 font-medium">{selectedApp.age || 'N/A'}</p>
                                        </div>
                                        <div>
                                          <p className="text-xs text-gray-500 mb-1">Gender</p>
                                          <p className="text-gray-800 font-medium">{selectedApp.gender || 'N/A'}</p>
                                        </div>
                                        <div>
                                          <p className="text-xs text-gray-500 mb-1">Date of Birth</p>
                                          <p className="text-gray-800 font-medium">{selectedApp.date_of_birth || 'N/A'}</p>
                                        </div>
                                        <div>
                                          <p className="text-xs text-gray-500 mb-1">Contact Number</p>
                                          <p className="text-gray-800 font-medium">{selectedApp.contact_number || 'N/A'}</p>
                                        </div>
                                      </div>
                                      <div className="space-y-4">
                                        <div>
                                          <p className="text-xs text-gray-500 mb-1">Email</p>
                                          <p className="text-gray-800 font-medium break-words">{selectedApp.email || 'N/A'}</p>
                                        </div>
                                        <div>
                                          <p className="text-xs text-gray-500 mb-1">Occupation</p>
                                          <p className="text-gray-800 font-medium">{selectedApp.occupation || 'N/A'}</p>
                                        </div>
                                        <div>
                                          <p className="text-xs text-gray-500 mb-1">Annual Income</p>
                                          <p className="text-gray-800 font-medium">
                                            ₹{selectedApp.annual_income ? selectedApp.annual_income.toLocaleString('en-IN') : 'N/A'}
                                          </p>
                                        </div>
                                        <div>
                                          <p className="text-xs text-gray-500 mb-1">Address</p>
                                          <p className="text-gray-800 font-medium">{selectedApp.address || 'N/A'}</p>
                                        </div>
                                      </div>
                                    </div>
                                  )}

                                  {/* Health & Risk Tab */}
                                  {activeTab === 'health' && (
                                    <div>
                                      <div className="grid md:grid-cols-2 gap-6 mb-6">
                                        <div className="space-y-4">
                                          <h3 className="text-lg font-semibold text-gray-800 mb-4">Health Metrics</h3>
                                          <div>
                                            <p className="text-xs text-gray-500 mb-1">BMI</p>
                                            <p className="text-gray-800 font-medium">{selectedApp.bmi ? selectedApp.bmi.toFixed(1) : 'N/A'}</p>
                                          </div>
                                          <div>
                                            <p className="text-xs text-gray-500 mb-1">Smoking Status</p>
                                            <p className="text-gray-800 font-medium">{selectedApp.smoking_status || 'N/A'}</p>
                                          </div>
                                          <div>
                                            <p className="text-xs text-gray-500 mb-1">Alcohol Consumption</p>
                                            <p className="text-gray-800 font-medium">{selectedApp.alcohol_consumption || 'N/A'}</p>
                                          </div>
                                        </div>
                                        <div className="space-y-4">
                                          <h3 className="text-lg font-semibold text-gray-800 mb-4">Risk Assessment</h3>
                                          <div>
                                            <p className="text-xs text-gray-500 mb-1">Risk Score</p>
                                            <p className="text-gray-800 font-medium text-2xl">{selectedApp.risk_score || 0}/100</p>
                                          </div>
                                          <div>
                                            <p className="text-xs text-gray-500 mb-1">Risk Category</p>
                                            <div className="mt-2">{getRiskBadge(selectedApp.risk_category)}</div>
                                          </div>
                                        </div>
                                      </div>

                                      {/* Flagged Conditions */}
                                      {selectedApp.flagged_conditions && selectedApp.flagged_conditions.trim() && (
                                        <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                                          <p className="text-sm font-semibold text-yellow-800 mb-2">⚠️ Flagged Conditions</p>
                                          <p className="text-sm text-yellow-700">{selectedApp.flagged_conditions}</p>
                                        </div>
                                      )}

                                      {(!selectedApp.flagged_conditions || !selectedApp.flagged_conditions.trim()) && (
                                        <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                                          <p className="text-sm font-semibold text-green-800">✅ No flagged conditions</p>
                                        </div>
                                      )}
                                    </div>
                                  )}

                                  {/* Premium Details Tab */}
                                  {activeTab === 'premium' && (
                                    <div className="grid md:grid-cols-2 gap-6">
                                      <div className="space-y-6">
                                        <h3 className="text-lg font-semibold text-gray-800">Premium Calculation Breakdown</h3>
                                        <div>
                                          <p className="text-xs text-gray-500 mb-1">Base Premium</p>
                                          <p className="text-3xl font-bold text-gray-800">
                                            ₹{selectedApp.base_premium ? selectedApp.base_premium.toLocaleString('en-IN') : 'N/A'}
                                          </p>
                                        </div>
                                        <div>
                                          <p className="text-xs text-gray-500 mb-1">Medical Loading</p>
                                          <p className="text-xl font-semibold text-gray-800">
                                            {selectedApp.medical_loading_percentage !== undefined 
                                              ? `${selectedApp.medical_loading_percentage}%` 
                                              : 'N/A'}
                                          </p>
                                        </div>
                                      </div>
                                      <div className="space-y-6">
                                        <h3 className="text-lg font-semibold text-gray-800">Best Offer</h3>
                                        <div>
                                          <p className="text-xs text-gray-500 mb-1">Final Annual Premium</p>
                                          <p className="text-3xl font-bold text-primary-600">
                                            ₹{selectedApp.final_premium ? selectedApp.final_premium.toLocaleString('en-IN') : 'N/A'}
                                          </p>
                                          <p className="text-xs text-gray-500 mt-1">per year</p>
                                        </div>
                                        <div>
                                          <p className="text-xs text-gray-500 mb-2">Recommended Plan</p>
                                          {getPlanBadge(selectedApp.recommended_plan)}
                                        </div>
                                      </div>
                                    </div>
                                  )}

                                  {/* Metadata Tab with PDF Viewer */}
                                  {activeTab === 'metadata' && (
                                    <div className="space-y-6">
                                      <div className="grid md:grid-cols-2 gap-6">
                                        <div className="space-y-4">
                                          <div>
                                            <p className="text-xs text-gray-500 mb-1">Application ID</p>
                                            <p className="text-gray-800 font-mono text-sm break-all bg-gray-100 p-2 rounded">
                                              {selectedApp.application_id || selectedApp.id || 'N/A'}
                                            </p>
                                          </div>
                                          <div>
                                            <p className="text-xs text-gray-500 mb-1">Upload Time</p>
                                            <p className="text-gray-800 font-medium">
                                              {selectedApp.upload_time 
                                                ? new Date(selectedApp.upload_time).toLocaleString('en-IN')
                                                : 'N/A'}
                                            </p>
                                          </div>
                                        </div>
                                        <div className="space-y-4">
                                          <div>
                                            <p className="text-xs text-gray-500 mb-1">Processing Time</p>
                                            <p className="text-gray-800 font-medium">
                                              {selectedApp.processing_timestamp || 'N/A'}
                                            </p>
                                          </div>
                                          <div>
                                            <p className="text-xs text-gray-500 mb-1">Current Step</p>
                                            <p className="text-gray-800 font-medium">
                                              {selectedApp.current_step || 'completed'}
                                            </p>
                                          </div>
                                        </div>
                                      </div>

                                      {/* Application Documents - Expandable PDF Viewers */}
                                      <div className="mt-6">
                                        <h3 className="text-lg font-semibold text-gray-800 mb-4">Application Documents</h3>
                                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                                          <p className="text-sm text-blue-800 mb-3">
                                            📄 Found {getDocuments(selectedApp.filename).length} document(s)
                                          </p>
                                          
                                          <div className="space-y-2">
                                            {getDocuments(selectedApp.filename).map((docName, idx) => {
                                              const isDocExpanded = expandedDocs.has(docName);
                                              
                                              return (
                                                <div key={idx} className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                                                  <button
                                                    onClick={() => toggleDocument(docName)}
                                                    className="w-full flex items-center justify-between px-4 py-3 hover:bg-gray-50 transition-colors"
                                                  >
                                                    <div className="flex items-center space-x-3">
                                                      <File className="w-5 h-5 text-blue-600" />
                                                      <span className="text-sm font-medium text-gray-800">{docName}</span>
                                                    </div>
                                                    {isDocExpanded ? (
                                                      <ChevronUp className="w-5 h-5 text-gray-400" />
                                                    ) : (
                                                      <ChevronDown className="w-5 h-5 text-gray-400" />
                                                    )}
                                                  </button>
                                                  
                                                  {isDocExpanded && (
                                                    <div className="border-t border-gray-200 p-4 bg-gray-50">
                                                      <iframe
                                                        src={getDocumentUrl(selectedApp.application_id || selectedApp.id, docName)}
                                                        className="w-full h-96 border border-gray-300 rounded"
                                                        title={docName}
                                                      />
                                                      <a
                                                        href={getDocumentUrl(selectedApp.application_id || selectedApp.id, docName)}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        className="mt-2 inline-flex items-center space-x-2 text-sm text-primary-600 hover:text-primary-700"
                                                      >
                                                        <ExternalLink className="w-4 h-4" />
                                                        <span>Open in new tab</span>
                                                      </a>
                                                    </div>
                                                  )}
                                                </div>
                                              );
                                            })}
                                          </div>
                                        </div>
                                      </div>

                                      {selectedApp.errors && selectedApp.errors.trim() && (
                                        <div className="p-3 bg-red-50 border border-red-200 rounded">
                                          <p className="text-xs text-red-600 font-semibold mb-1">Errors:</p>
                                          <p className="text-sm text-red-700">{selectedApp.errors}</p>
                                        </div>
                                      )}
                                    </div>
                                  )}

                                  {/* KYC Verification Tab */}
                                  {activeTab === 'kyc' && (
                                    <div className="space-y-6">
                                      <h3 className="text-lg font-semibold text-gray-800 mb-4">KYC Verification</h3>
                                      <div className="grid md:grid-cols-2 gap-6">
                                        <div className="space-y-4">
                                          <div>
                                            <p className="text-xs text-gray-500 mb-1">Verification Status</p>
                                            <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
                                              selectedApp.kyc_verification_status === 'Verified'
                                                ? 'bg-green-100 text-green-800'
                                                : selectedApp.kyc_verification_status === 'Failed'
                                                ? 'bg-red-100 text-red-800'
                                                : 'bg-gray-100 text-gray-800'
                                            }`}>
                                              {selectedApp.kyc_verification_status || 'NOT_PROVIDED'}
                                            </span>
                                          </div>
                                          <div>
                                            <p className="text-xs text-gray-500 mb-1">Document Type</p>
                                            <p className="text-gray-800 font-medium">{selectedApp.kyc_document_type || 'None'}</p>
                                          </div>
                                          <div>
                                            <p className="text-xs text-gray-500 mb-1">Total Discrepancies</p>
                                            <p className="text-2xl font-bold text-gray-800">
                                              {selectedApp.kyc_total_discrepancies || 0}
                                            </p>
                                          </div>
                                        </div>
                                        <div>
                                          {selectedApp.kyc_verification_message && (
                                            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                                              <p className="text-xs text-blue-600 font-semibold mb-2">Verification Message:</p>
                                              <p className="text-sm text-blue-800">{selectedApp.kyc_verification_message}</p>
                                            </div>
                                          )}

                                          {selectedApp.kyc_discrepancies && selectedApp.kyc_discrepancies.length > 0 && (
                                            <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                                              <p className="text-xs text-yellow-700 font-semibold mb-2">Discrepancies Found:</p>
                                              <ul className="list-disc list-inside space-y-1">
                                                {selectedApp.kyc_discrepancies.map((disc: any, idx: number) => (
                                                  <li key={idx} className="text-sm text-yellow-800">
                                                    {typeof disc === 'string' ? disc : JSON.stringify(disc)}
                                                  </li>
                                                ))}
                                              </ul>
                                            </div>
                                          )}
                                        </div>
                                      </div>
                                    </div>
                                  )}
                                </div>
                              </div>
                            </td>
                          </tr>
                        )}
                      </React.Fragment>
                    );
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-16">
              <AlertCircle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500 text-lg font-medium">No applications found</p>
              <p className="text-gray-400 text-sm mt-2">
                {applications.length === 0 
                  ? 'Process some applications to see them here'
                  : 'Try adjusting your search or filters'}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
