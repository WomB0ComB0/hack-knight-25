import { useEffect, useState, createContext, useContext, ReactNode } from 'react';

// Define types
type UserRole = 'patient' | 'healthcare_provider';

interface UserInfo {
  id: string;
  email: string;
  name: string;
  blockchainId: string;
  role: UserRole;
}

interface AuthContextType {
  isLoggedIn: boolean;
  isLoading: boolean;
  userInfo: UserInfo | null;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string, role: UserRole) => Promise<void>;
  logout: () => Promise<void>;
  getAuthHeader: () => { Authorization: string } | null;
}

// Create context for auth state
const AuthContext = createContext<AuthContextType | null>(null);

// Backend API URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const apiKey = localStorage.getItem('apiKey');
        if (!apiKey) {
          setIsLoading(false);
          return;
        }

        const response = await fetch(`${API_BASE_URL}/auth/validate`, {
          headers: {
            'Authorization': `ApiKey ${apiKey}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          if (data.valid) {
            setUserInfo({
              id: data.user_id,
              email: data.user_info.email,
              name: data.user_info.name,
              blockchainId: data.user_id,
              role: data.role,
            });
            setIsLoggedIn(true);
          }
        }
      } catch (error) {
        console.error('Authentication check failed:', error);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      setIsLoading(true);
      
      // In a real application, you would send these credentials to the server
      // For demo purposes, we'll just create a mock API key
      const apiKey = 'demo_' + Math.random().toString(36).substring(2, 15);
      localStorage.setItem('apiKey', apiKey);

      // Fetch user info with the new API key
      const response = await fetch(`${API_BASE_URL}/auth/validate`, {
        headers: {
          'Authorization': `ApiKey ${apiKey}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setUserInfo({
          id: data.user_id,
          email: data.user_info.email,
          name: data.user_info.name,
          blockchainId: data.user_id,
          role: data.role,
        });
        setIsLoggedIn(true);
      } else {
        throw new Error('Login failed');
      }
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (name: string, email: string, password: string, role: UserRole) => {
    try {
      setIsLoading(true);
      
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, email, role }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Registration failed');
      }

      const data = await response.json();
      
      // Save the API key
      localStorage.setItem('apiKey', data.api_key);
      
      // Auto-login after registration
      setUserInfo({
        id: data.user_id,
        email: email,
        name: name,
        blockchainId: data.blockchain_id,
        role: role,
      });
      
      setIsLoggedIn(true);
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      localStorage.removeItem('apiKey');
      setUserInfo(null);
      setIsLoggedIn(false);
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const getAuthHeader = () => {
    const apiKey = localStorage.getItem('apiKey');
    if (!apiKey) return null;
    
    return {
      'Authorization': `ApiKey ${apiKey}`
    };
  };

  return (
    <AuthContext.Provider value={{
      isLoggedIn,
      isLoading,
      userInfo,
      login,
      register,
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
  const { register, userInfo } = useAuth();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState<UserRole>('patient');
  const [isRegistering, setIsRegistering] = useState(false);
  const [error, setError] = useState('');

  const handleRegister = async () => {
    try {
      setIsRegistering(true);
      await register(name, email, password, role);
      // Registration successful and auto-logged in via the register function
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
      
      <div className="form-group">
        <label>Name</label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Your name"
        />
      </div>
      
      <div className="form-group">
        <label>Email</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Your email"
        />
      </div>
      
      <div className="form-group">
        <label>Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Your password"
        />
      </div>

      <div className="role-selection">
        <p>Please select your role in the healthcare system:</p>
        
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
        onClick={handleRegister}
        disabled={isRegistering}
      >
        {isRegistering ? 'Registering...' : 'Complete Registration'}
      </button>
    </div>
  );
};
