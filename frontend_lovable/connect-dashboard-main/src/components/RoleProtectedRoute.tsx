import { Navigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Loader2 } from 'lucide-react';

interface RoleProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: string[]; // Roles permitidas: 'admin', 'professor', 'aluno', 'gerente'
  requireWrite?: boolean; // Se true, apenas admin pode acessar (gerente não pode)
}

export function RoleProtectedRoute({ 
  children, 
  allowedRoles = [],
  requireWrite = false 
}: RoleProtectedRouteProps) {
  const { isAuthenticated, isLoading, user, isAdmin, isReadonly } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  // Verificar se requer escrita e se é readonly (gerente)
  if (requireWrite && isReadonly()) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-destructive mb-2">Acesso Negado</h1>
          <p className="text-muted-foreground">
            Você não tem permissão para acessar esta página. Gerentes têm apenas permissão de leitura.
          </p>
        </div>
      </div>
    );
  }

  // Se allowedRoles está vazio, qualquer usuário autenticado pode acessar
  if (allowedRoles.length === 0) {
    return <>{children}</>;
  }

  // Verificar se o role do usuário está na lista de roles permitidas
  const userRole = user.role;
  if (!allowedRoles.includes(userRole)) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-destructive mb-2">Acesso Negado</h1>
          <p className="text-muted-foreground">
            Você não tem permissão para acessar esta página.
          </p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}

