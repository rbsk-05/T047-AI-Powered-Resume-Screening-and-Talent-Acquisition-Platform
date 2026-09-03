import { createContext, ReactNode, useContext, useEffect, useState } from "react";
import { fetchCurrentUser, login as apiLogin, register as apiRegister, Role, User } from "../api";

const STORAGE_KEY = "talentlens.auth.token";

type AuthContextValue = {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string, role: Role, companyName?: string, companyDescription?: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(STORAGE_KEY));
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!token) {
      setUser(null);
      setIsLoading(false);
      return;
    }
    fetchCurrentUser(token)
      .then(setUser)
      .catch(() => {
        // Token expired or invalid -- clear it so the person is sent back to login.
        localStorage.removeItem(STORAGE_KEY);
        setToken(null);
        setUser(null);
      })
      .finally(() => setIsLoading(false));
  }, [token]);

  async function login(email: string, password: string) {
    const response = await apiLogin(email, password);
    localStorage.setItem(STORAGE_KEY, response.access_token);
    setToken(response.access_token);
    setUser(response.user);
  }

  async function register(email: string, password: string, fullName: string, role: Role, companyName?: string, companyDescription?: string) {
    const response = await apiRegister(email, password, fullName, role, companyName, companyDescription);
    localStorage.setItem(STORAGE_KEY, response.access_token);
    setToken(response.access_token);
    setUser(response.user);
  }

  function logout() {
    localStorage.removeItem(STORAGE_KEY);
    setToken(null);
    setUser(null);
  }

  return <AuthContext.Provider value={{ user, token, isLoading, login, register, logout }}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within an AuthProvider");
  return context;
}
