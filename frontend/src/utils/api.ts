// Add these functions to your api.ts file

// Storage key for user info
export const USER_INFO_STORAGE = 'userInfo';

// Authentication functions
export const auth = {
  // Register a new user
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

  // Validate API key
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

  // Store user auth data
  storeUserData: (apiKey: string, userData: any): void => {
    localStorage.setItem(API_KEY_STORAGE, apiKey);
    localStorage.setItem(USER_INFO_STORAGE, JSON.stringify(userData));
  },

  // Clear user auth data
  clearUserData: (): void => {
    localStorage.removeItem(API_KEY_STORAGE);
    localStorage.removeItem(USER_INFO_STORAGE);
  },

  // Get stored user data
  getUserData: (): any | null => {
    const userData = localStorage.getItem(USER_INFO_STORAGE);
    return userData ? JSON.parse(userData) : null;
  },
};

// Add transaction functions to the api object
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
  
  // Generic Blockchain Transactions
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
  
  // Nodes management
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
  
  // Block retrieval
  getBlock: async <T>(blockId: number): Promise<T> => {
    return fetchWithAuth<T>(`/block/${blockId}`);
  },
};