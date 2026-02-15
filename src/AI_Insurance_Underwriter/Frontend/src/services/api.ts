// src/services/api.ts
import axios from 'axios';
import type {
  UploadResponse,
  ProcessResponse,
  EvaluationResponse,
  ApplicationData,
  ChatMessage,
} from '../types/application';

const API_BASE_URL = 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// File upload endpoint
export const uploadFiles = async (
  applicationForm: File,
  medicalDocs: File[],
  kycDocument?: File
): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('application_form', applicationForm);
  
  medicalDocs.forEach((doc) => {
    formData.append('medical_docs', doc);
  });
  
  if (kycDocument) {
    formData.append('kyc_document', kycDocument);
  }
  
  const response = await api.post<UploadResponse>('/api/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

// Process documents
export const processDocuments = async (applicationId: string): Promise<ProcessResponse> => {
  const response = await api.post<ProcessResponse>(`/api/process-documents/${applicationId}`);
  return response.data;
};

// Evaluate application
export const evaluateApplication = async (applicationId: string): Promise<EvaluationResponse> => {
  const response = await api.post<EvaluationResponse>(`/api/evaluate/${applicationId}`);
  return response.data;
};

// Get application data
export const getApplication = async (applicationId: string): Promise<{ success: boolean; data: ApplicationData }> => {
  const response = await api.get(`/api/application/${applicationId}`);
  return response.data;
};

// Get all applications
export const getAllApplications = async (): Promise<{ success: boolean; count: number; applications: ApplicationData[] }> => {
  const response = await api.get('/api/applications');
  return response.data;
};

// Chatbot query
export const sendChatbotMessage = async (
  message: string,
  history: ChatMessage[]
): Promise<{ success: boolean; response: string }> => {
  const response = await api.post('/api/chatbot', {
    message,
    history,
  });
  return response.data;
};

// WebSocket connection helper
export const createWebSocketConnection = (clientId: string): WebSocket => {
  return new WebSocket(`ws://localhost:8000/ws/${clientId}`);
};
