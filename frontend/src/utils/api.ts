// API base URL - should be set in environment variables
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

// Define types for API responses and requests
export interface ApiError {
  error?: string;
}

export interface MedicalRecordData {
  patient_id: string;
  record_type: string;
  medical_data: Record<string, unknown>;
  signature: string;
  access_list?: string[];
}

export interface ConsentData {
  patient_id: string;
  provider_id: string;
  access_type: 'grant' | 'revoke';
  signature: string;
  record_types?: string[];
}

export type ApiResponse<T = unknown> = T | ApiError;

/**
 * Storage key for API key
 */
const API_KEY_STORAGE = 'apiKey';

/**
 * Wrapper for fetch that includes authorization headers
 * @param url - API endpoint URL
 * @param options - Fetch request options
 * @returns Promise with typed response data
 */
export const fetchWithAuth = async <T>(url: string, options: RequestInit = {}): Promise<T> => {
  // Get the authentication header from localStorage directly
  const apiKey = localStorage.getItem(API_KEY_STORAGE);

  if (!apiKey) {
    throw new Error('Not authenticated');
  }

  const headers = new Headers(options.headers);
  headers.set('Authorization', `ApiKey ${apiKey}`);
  headers.set('Content-Type', 'application/json');

  try {
    const response = await fetch(`${API_BASE_URL}${url}`, {
      ...options,
      headers,
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error((data as ApiError).error || `API error: ${response.status}`);
    }

    return data as T;
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Unknown API error occurred');
  }
};

/**
 * Healthcare blockchain API client
 */
export const api = {
  // Records
  getMedicalRecords: async <T>(patientId: string, recordType?: string): Promise<T> => {
    const queryParams = recordType ? `?record_type=${encodeURIComponent(recordType)}` : '';
    return fetchWithAuth<T>(`/medical/records/${encodeURIComponent(patientId)}${queryParams}`);
  },

  addMedicalRecord: async <T>(data: MedicalRecordData): Promise<T> => {
    return fetchWithAuth<T>('/medical/record', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  // Consent Management
  manageConsent: async <T>(data: ConsentData): Promise<T> => {
    return fetchWithAuth<T>('/medical/consent', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  // Blockchain Info
  getBlockchainInfo: async <T>(): Promise<T> => {
    return fetchWithAuth<T>('/chain');
  },

  getPendingTransactions: async <T>(): Promise<T> => {
    return fetchWithAuth<T>('/transactions/pending');
  },

  mineBlock: async <T>(): Promise<T> => {
    return fetchWithAuth<T>('/mine');
  },
};
