const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

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

export const USER_INFO_STORAGE = 'userInfo';


/**
 * Wrapper for fetch that includes authorization headers
 * @param url - API endpoint URL
 * @param options - Fetch request options
 * @returns Promise with typed response data
 */
export const fetchWithAuth = async <T>(url: string, options: RequestInit = {}): Promise<T> => {
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

export const auth = {
  register: async <T>(name: string, email: string, role: 'patient' | 'healthcare_provider'): Promise<T> => {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name, email, role }),
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error((data as ApiError).error || `API error: ${response.status}`);
    }

    const data = await response.json();
    return data as T;
  },

  validate: async <T>(apiKey: string): Promise<T> => {
    const response = await fetch(`${API_BASE_URL}/auth/validate`, {
      headers: {
        'Authorization': `ApiKey ${apiKey}`,
      },
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error((data as ApiError).error || `API error: ${response.status}`);
    }

    const data = await response.json();
    return data as T;
  },

  storeUserData: (apiKey: string, userData: any): void => {
    localStorage.setItem(API_KEY_STORAGE, apiKey);
    localStorage.setItem(USER_INFO_STORAGE, JSON.stringify(userData));
  },

  clearUserData: (): void => {
    localStorage.removeItem(API_KEY_STORAGE);
    localStorage.removeItem(USER_INFO_STORAGE);
  },

  getUserData: (): any | null => {
    const userData = localStorage.getItem(USER_INFO_STORAGE);
    return userData ? JSON.parse(userData) : null;
  },
};

export const api = {
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

  manageConsent: async <T>(data: ConsentData): Promise<T> => {
    return fetchWithAuth<T>('/medical/consent', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  getBlockchainInfo: async <T>(): Promise<T> => {
    return fetchWithAuth<T>('/chain');
  },

  getPendingTransactions: async <T>(): Promise<T> => {
    return fetchWithAuth<T>('/transactions/pending');
  },

  mineBlock: async <T>(): Promise<T> => {
    return fetchWithAuth<T>('/mine');
  },
  
  createTransaction: async <T>(sender: string, recipient: string, amount: number, signature: string): Promise<T> => {
    return fetchWithAuth<T>('/transactions/new', {
      method: 'POST',
      body: JSON.stringify({
        sender,
        recipient,
        amount,
        signature,
      }),
    });
  },
  
  registerNodes: async <T>(nodes: string[]): Promise<T> => {
    return fetchWithAuth<T>('/nodes/register', {
      method: 'POST',
      body: JSON.stringify({ nodes }),
    });
  },
  
  getNodes: async <T>(): Promise<T> => {
    return fetchWithAuth<T>('/nodes/get');
  },
  
  resolveNodes: async <T>(): Promise<T> => {
    return fetchWithAuth<T>('/nodes/resolve');
  },
  
  getBlock: async <T>(blockId: number): Promise<T> => {
    return fetchWithAuth<T>(`/block/${blockId}`);
  },
};