"use client";

import { useState, useEffect } from "react";
import { Clock, Database, GitBranchPlus, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { api } from "@/utils/api";
import { toast } from "@/components/ui/use-toast";

interface BlockchainInfo {
  length: number;
  chain: Array<{
    index: number;
    timestamp: number;
    transactions: Array<any>;
    previous_hash: string;
  }>;
}

interface PendingTransactions {
  count: number;
 */ending_transactions: Array<any>;
const API_KEY_STORAGE = 'apiKey';

/**ort function BlockchainInfoCard() {
 * Wrapper for fetch that includes authorization headerslockchainInfo | null>(null);
 * @param url - API endpoint URLtPendingTransactions] = useState<PendingTransactions | null>(null);
 * @param options - Fetch request optionsfalse);
 * @returns Promise with typed response datauseState(false);
 */
export const fetchWithAuth = async <T>(url: string, options: RequestInit = {}): Promise<T> => {
  // Get the authentication header from localStorage directly
  const apiKey = localStorage.getItem(API_KEY_STORAGE);
      const chainData = await api.getBlockchainInfo<BlockchainInfo>();
  if (!apiKey) {ainInfo(chainData);
    throw new Error('Not authenticated');
  }   const pendingTxData = await api.getPendingTransactions<PendingTransactions>();
      setPendingTransactions(pendingTxData);
  const headers = new Headers(options.headers);
  headers.set('Authorization', `ApiKey ${apiKey}`);:", error);
  headers.set('Content-Type', 'application/json');
        title: "Error",
  try { description: "Failed to fetch blockchain data",
    const response = await fetch(`${API_BASE_URL}${url}`, {
      ...options,
      headers,{
    });etLoading(false);
    }
    const data = await response.json();

    if (!response.ok) { = async () => {
      throw new Error((data as ApiError).error || `API error: ${response.status}`);
    } setMiningLoading(true);
      await api.mineBlock();
    return data as T;
  } catch (error) {cess",
    if (error instanceof Error) {ined successfully!",
      throw error;
    } // Refresh data after mining
    throw new Error('Unknown API error occurred');
  } } catch (error) {
};    console.error("Error mining block:", error);
      toast({
// Storage key for user info     title: "Error",
export const USER_INFO_STORAGE = 'userInfo';e block",
     variant: "destructive",
// Authentication functions
export const auth = {y {
  // Register a new user
  register: async <T>(name: string, email: string, role: 'patient' | 'healthcare_provider'): Promise<T> => {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: {  useEffect(() => {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name, email, role }),
    });number) => {
urn new Date(timestamp * 1000).toLocaleString();
    if (!response.ok) {
      const data = await response.json();
      throw new Error((data as ApiError).error || `API error: ${response.status}`);
    }

    const data = await response.json();assName="flex items-center gap-2">
    return data as T;5 w-5 text-blue-600" />
  },   Blockchain Status
    </CardTitle>
  // Validate API key        <CardDescription>
  validate: async <T>(apiKey: string): Promise<T> => {ate of the healthcare blockchain
    const response = await fetch(`${API_BASE_URL}/auth/validate`, {
      headers: {
        'Authorization': `ApiKey ${apiKey}`,  <CardContent>
      },        {loading ? (
    });fy-center">
text-blue-600" />
    if (!response.ok) {      </div>
      const data = await response.json();        ) : (
      throw new Error((data as ApiError).error || `API error: ${response.status}`);
    }g border p-3">
          <div className="flex items-center justify-between">
    const data = await response.json();              <div className="flex items-center gap-2">
    return data as T;                  <GitBranchPlus className="h-5 w-5 text-blue-600" />






























































































};  },    return fetchWithAuth<T>(`/block/${blockId}`);  getBlock: async <T>(blockId: number): Promise<T> => {  // Block retrieval    },    return fetchWithAuth<T>('/nodes/resolve');  resolveNodes: async <T>(): Promise<T> => {    },    return fetchWithAuth<T>('/nodes/get');  getNodes: async <T>(): Promise<T> => {    },    });      body: JSON.stringify({ nodes }),      method: 'POST',    return fetchWithAuth<T>('/nodes/register', {  registerNodes: async <T>(nodes: string[]): Promise<T> => {  // Nodes management    },    });      }),        signature,        amount,        recipient,        sender,      body: JSON.stringify({      method: 'POST',    return fetchWithAuth<T>('/transactions/new', {  createTransaction: async <T>(sender: string, recipient: string, amount: number, signature: string): Promise<T> => {  // Generic Blockchain Transactions    },    return fetchWithAuth<T>('/mine');  mineBlock: async <T>(): Promise<T> => {  },    return fetchWithAuth<T>('/transactions/pending');  getPendingTransactions: async <T>(): Promise<T> => {  },    return fetchWithAuth<T>('/chain');  getBlockchainInfo: async <T>(): Promise<T> => {  // Blockchain Info  },    });      body: JSON.stringify(data),      method: 'POST',    return fetchWithAuth<T>('/medical/consent', {  manageConsent: async <T>(data: ConsentData): Promise<T> => {  // Consent Management  },    });      body: JSON.stringify(data),      method: 'POST',    return fetchWithAuth<T>('/medical/record', {  addMedicalRecord: async <T>(data: MedicalRecordData): Promise<T> => {  },    return fetchWithAuth<T>(`/medical/records/${encodeURIComponent(patientId)}${queryParams}`);    const queryParams = recordType ? `?record_type=${encodeURIComponent(recordType)}` : '';  getMedicalRecords: async <T>(patientId: string, recordType?: string): Promise<T> => {  // Recordsexport const api = { */ * Healthcare blockchain API client/**};  },    return userData ? JSON.parse(userData) : null;    const userData = localStorage.getItem(USER_INFO_STORAGE);  getUserData: (): any | null => {  // Get stored user data  },    localStorage.removeItem(USER_INFO_STORAGE);    localStorage.removeItem(API_KEY_STORAGE);  clearUserData: (): void => {  // Clear user auth data  },    localStorage.setItem(USER_INFO_STORAGE, JSON.stringify(userData));    localStorage.setItem(API_KEY_STORAGE, apiKey);  storeUserData: (apiKey: string, userData: any): void => {  // Store user auth data  },                  <span className="font-medium">Chain Length</span>
                </div>
                <span className="text-xl font-bold">
                  {blockchainInfo?.length || 0} blocks
                </span>
              </div>
            </div>

            <div className="rounded-lg border p-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Clock className="h-5 w-5 text-blue-600" />
                  <span className="font-medium">Last Updated</span>
                </div>
                <span className="text-sm">
                  {blockchainInfo?.chain[0]
                    ? formatDate(blockchainInfo.chain[0].timestamp)
                    : "N/A"}
                </span>
              </div>
            </div>

            <div className="rounded-lg border p-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Database className="h-5 w-5 text-blue-600" />
                  <span className="font-medium">Pending Transactions</span>
                </div>
                <span className="text-xl font-bold">
                  {pendingTransactions?.count || 0}
                </span>
              </div>
            </div>
          </div>
        )}
      </CardContent>
      <CardFooter>
        <Button 
          onClick={handleMineBlock} 
          className="w-full"
          disabled={miningLoading}
        >
          {miningLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          Mine New Block
        </Button>
      </CardFooter>
    </Card>
  );
}// API base URL - should be set in environment variables
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
