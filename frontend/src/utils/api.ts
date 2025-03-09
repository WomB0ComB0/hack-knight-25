import { useAuth } from '../components/Web3AuthBridge';

// API base URL - should be set in environment variables
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

/**
 * Wrapper for fetch that includes authorization headers
 */
export const fetchWithAuth = async (url: string, options: RequestInit = {}) => {
  // Get the authentication header from localStorage directly
  // This ensures the function works outside of React components
  const apiKey = localStorage.getItem('apiKey');
  
  if (!apiKey) {
    throw new Error('Not authenticated');
  }
  
  const authHeader = { 'Authorization': `ApiKey ${apiKey}` };
  
  const response = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    headers: {
      ...options.headers,
      ...authHeader,
      'Content-Type': 'application/json',
    },
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || `API error: ${response.status}`);
  }
  
  return response.json();
};

/**
 * Healthcare blockchain API client
 */
export const api = {
  // Records
  getMedicalRecords: async (patientId: string, recordType?: string) => {
    const queryParams = recordType ? `?record_type=${recordType}` : '';
    return fetchWithAuth(`/medical/records/${patientId}${queryParams}`);
  },
  
  addMedicalRecord: async (data: {
    patient_id: string;
    record_type: string;
    medical_data: any;
    signature: string;
    access_list?: string[];
  }) => {
    return fetchWithAuth('/medical/record', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
  
  // Consent Management
  manageConsent: async (data: {
    patient_id: string;
    provider_id: string;
    access_type: 'grant' | 'revoke';
    signature: string;
    record_types?: string[];
  }) => {
    return fetchWithAuth('/medical/consent', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
  
  // Blockchain Info
  getBlockchainInfo: async () => {
    return fetchWithAuth('/chain');
  },
  
  getPendingTransactions: async () => {
    return fetchWithAuth('/transactions/pending');
  },
  
  mineBlock: async () => {
    return fetchWithAuth('/mine');
  },
};
