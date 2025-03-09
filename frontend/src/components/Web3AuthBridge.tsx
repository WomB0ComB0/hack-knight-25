import { useEffect, useState, createContext, useContext, ReactNode } from 'react';
import { Web3Auth } from '@web3auth/modal';
import { CHAIN_NAMESPACES, IProvider } from '@web3auth/base';
import { EthereumPrivateKeyProvider } from '@web3auth/ethereum-provider';

// Define types
type UserRole = 'patient' | 'healthcare_provider';

interface UserInfo {
  id: string;
  email: string;
  name: string;
  profileImage: string;
  blockchainId: string;
  role: UserRole;
}

interface AuthContextType {
  isLoggedIn: boolean;
  isLoading: boolean;
  userInfo: UserInfo | null;
  provider: IProvider | null;
  login: () => Promise<void>;
  logout: () => Promise<void>;
  getAuthHeader: () => Promise<{ Authorization: string } | null>;
}

// Create context for auth state
const AuthContext = createContext<AuthContextType | null>(null);

// Backend API URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

// Web3Auth configuration
const clientId = 'BPi5PB_UiIZ-cPz1GtV5i1I2iOSOHuimiXBI0e-Oe_u6X3oVAbCiAZOTEBtTXw4tsluTITPqA8zMsfxIKMjiqNQ';
const chainConfig = {
  chainNamespace: CHAIN_NAMESPACES.EIP155,
  chainId: '0xaa36a7',
  rpcTarget: 'https://rpc.ankr.com/eth_sepolia',
  displayName: 'Ethereum Sepolia Testnet',
  blockExplorerUrl: 'https://sepolia.etherscan.io',
  ticker: 'ETH',
  tickerName: 'Ethereum',
};

// Create and configure Web3Auth instance
const privateKeyProvider = new EthereumPrivateKeyProvider({
  config: { chainConfig: chainConfig as any }
});

const web3auth = new Web3Auth({
  clientId,
  web3AuthNetwork: 'sapphire_mainnet',
  privateKeyProvider,
});

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [provider, setProvider] = useState<IProvider | null>(null);

  useEffect(() => {
    const initAuth = async () => {
      try {
        await web3auth.initModal();

        if (web3auth.connected) {
          setProvider(web3auth.provider);
          await getUserInfo();
          setIsLoggedIn(true);
        }
      } catch (error) {
        console.error('Failed to initialize auth:', error);
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  const getUserInfo = async () => {
    if (!web3auth.connected) return;

    try {
      // Get user info from Web3Auth
      const w3aUserInfo = await web3auth.getUserInfo();
      const idToken = await web3auth.authenticateUser();

      // Get or verify user info with our backend
      const response = await fetch(`${API_BASE_URL}/auth/validate`, {
        headers: {
          'Authorization': `Bearer ${idToken.idToken}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setUserInfo({
          id: w3aUserInfo.idToken || '',
          email: w3aUserInfo.email || '',
          name: w3aUserInfo.name || '',
          profileImage: w3aUserInfo.profileImage || '',
          blockchainId: data.user_id,
          role: data.role,
        });
      } else {
        // If user doesn't exist in our system, we need to register them
        console.log('User not found in backend, registration needed');
        setUserInfo(null);
      }
    } catch (error) {
      console.error('Failed to get user info:', error);
      setUserInfo(null);
    }
  };

  const login = async () => {
    try {
      setIsLoading(true);
      const web3authProvider = await web3auth.connect();
      setProvider(web3authProvider);

      await getUserInfo();

      // If no user info was retrieved, user needs to be registered
      if (!userInfo) {
        // Open role selection modal or redirect to registration
        console.log("Redirect to registration");
        // Implementation depends on your UI flow
      }

      setIsLoggedIn(true);
    } catch (error) {
      console.error('Login failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      await web3auth.logout();
      setProvider(null);
      setUserInfo(null);
      setIsLoggedIn(false);
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const getAuthHeader = async () => {
    if (!web3auth.connected) return null;

    try {
      const idToken = await web3auth.authenticateUser();
      return {
        'Authorization': `Bearer ${idToken.idToken}`
      };
    } catch (error) {
      console.error('Failed to get auth header:', error);
      return null;
    }
  };

  return (
    <AuthContext.Provider value={{
      isLoggedIn,
      isLoading,
      userInfo,
      provider,
      login,
      logout,
      getAuthHeader,
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Registration component
export const UserRegistration = () => {
  const { userInfo } = useAuth();
  const [role, setRole] = useState<UserRole>('patient');
  const [isRegistering, setIsRegistering] = useState(false);
  const [error, setError] = useState('');

  const registerUser = async () => {
    try {
      setIsRegistering(true);
      const idToken = await web3auth.authenticateUser();

      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${idToken.idToken}`,
        },
        body: JSON.stringify({ idToken: idToken.idToken, role }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Registration failed');
      }

      // Refresh user info after registration
      window.location.reload();
    } catch (error) {
      setError(error.message || 'Registration failed');
      console.error('Registration error:', error);
    } finally {
      setIsRegistering(false);
    }
  };

  if (userInfo) {
    return null; // Already registered
  }

  return (
    <div className="registration-container">
      <h2>Complete Your Registration</h2>
      <p>Please select your role in the healthcare system:</p>

      <div className="role-selection">
        <label>
          <input
            type="radio"
            name="role"
            value="patient"
            checked={role === 'patient'}
            onChange={() => setRole('patient')}
          />
          Patient
        </label>

        <label>
          <input
            type="radio"
            name="role"
            value="healthcare_provider"
            checked={role === 'healthcare_provider'}
            onChange={() => setRole('healthcare_provider')}
          />
          Healthcare Provider
        </label>
      </div>

      {error && <div className="error">{error}</div>}

      <button
        onClick={registerUser}
        disabled={isRegistering}
      >
        {isRegistering ? 'Registering...' : 'Complete Registration'}
      </button>
    </div>
  );
};
