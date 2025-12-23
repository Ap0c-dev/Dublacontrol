import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { api } from '@/lib/api';

interface User {
  id: number;
  username: string;
  nome: string;
  role: string;
  is_admin: boolean;
  is_professor: boolean;
  is_aluno: boolean;
  is_gerente: boolean;
  is_readonly: boolean;
  professor_id?: number | null;
  aluno_id?: number | null;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
  // Helpers para verificar roles
  isAdmin: () => boolean;
  isProfessor: () => boolean;
  isAluno: () => boolean;
  isGerente: () => boolean;
  isReadonly: () => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      const storedUser = api.getUser();
      const hasToken = api.isAuthenticated();
      
      console.log('🔍 Verificando autenticação...');
      console.log('👤 Usuário armazenado:', storedUser);
      console.log('🔑 Token presente:', hasToken);
      
      if (storedUser && hasToken) {
        // Verificar se o token ainda é válido fazendo uma requisição
        try {
          const meResponse = await api.getMe();
          if (meResponse.success && meResponse.data) {
            // Usar dados atualizados do servidor
            setUser(meResponse.data);
            console.log('✅ Autenticação válida');
          } else {
            // Se storedUser existe mas getMe falhou, usar storedUser como fallback
            if (storedUser) {
              setUser(storedUser);
              console.log('⚠️ Usando dados armazenados localmente');
            } else {
              console.warn('⚠️ Token inválido, limpando...');
              api.logout();
              setUser(null);
            }
          }
        } catch (error) {
          console.error('❌ Erro ao verificar autenticação:', error);
          // Se storedUser existe, usar como fallback
          if (storedUser) {
            setUser(storedUser);
            console.log('⚠️ Usando dados armazenados localmente após erro');
          } else {
            api.logout();
            setUser(null);
          }
        }
      } else {
        console.warn('⚠️ Nenhuma autenticação encontrada');
        setUser(null);
      }
      setIsLoading(false);
    };
    
    checkAuth();
  }, []);

  const login = async (username: string, password: string) => {
    try {
      const response = await api.login(username, password);
      if (response.success) {
        setUser(response.user);
        return { success: true };
      }
      return { success: false, error: response.message || 'Erro ao fazer login' };
    } catch (error) {
      return { success: false, error: 'Erro de conexão com o servidor' };
    }
  };

  const logout = () => {
    api.logout();
    setUser(null);
  };

  const isAdmin = () => user?.is_admin ?? false;
  const isProfessor = () => user?.is_professor ?? false;
  const isAluno = () => user?.is_aluno ?? false;
  const isGerente = () => user?.is_gerente ?? false;
  const isReadonly = () => user?.is_readonly ?? false;

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
        isAdmin,
        isProfessor,
        isAluno,
        isGerente,
        isReadonly,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
