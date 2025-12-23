import { Link, useLocation } from 'react-router-dom';
import { cn } from '@/lib/utils';
import { useAuth } from '@/contexts/AuthContext';
import { useSidebar } from '@/contexts/SidebarContext';
import { useTheme } from 'next-themes';
import { Button } from '@/components/ui/button';
import {
  LayoutDashboard,
  Users,
  GraduationCap,
  CreditCard,
  BookOpen,
  LogOut,
  Menu,
  X,
  ChevronLeft,
  ChevronRight,
  Sun,
  Moon,
} from 'lucide-react';
import { useState, useEffect } from 'react';

const navItems = [
  { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard', roles: ['admin', 'professor', 'aluno', 'gerente'] },
  { icon: Users, label: 'Alunos', path: '/alunos', roles: ['admin', 'professor', 'gerente'] },
  { icon: GraduationCap, label: 'Professores', path: '/professores', roles: ['admin', 'gerente'] },
  { icon: CreditCard, label: 'Pagamentos', path: '/pagamentos', roles: ['admin', 'professor', 'gerente'] },
  { icon: BookOpen, label: 'Notas', path: '/notas', roles: ['admin', 'professor', 'aluno', 'gerente'] },
];

export function Sidebar() {
  const location = useLocation();
  const { user, logout } = useAuth();
  const { isCollapsed, toggleSidebar } = useSidebar();
  const { theme, setTheme } = useTheme();
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <>
      {/* Mobile menu button */}
      <button
        onClick={() => setIsMobileOpen(!isMobileOpen)}
        className="fixed top-4 left-4 z-20 p-2 rounded-lg bg-card shadow-card lg:hidden"
        type="button"
        aria-label="Toggle menu"
      >
        {isMobileOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      {/* Overlay - apenas em mobile quando menu está aberto */}
      {isMobileOpen && (
        <div
          className="fixed inset-0 bg-foreground/20 backdrop-blur-sm z-[5] lg:hidden"
          onClick={() => setIsMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed left-0 top-0 z-50 h-screen bg-sidebar border-r border-sidebar-border transition-all duration-300 ease-in-out',
          isMobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
          isCollapsed ? 'w-16' : 'w-64'
        )}
        style={{ pointerEvents: 'auto' }}
      >
        <div className="flex flex-col h-full">
          {/* Logo e Controles */}
          <div className={cn(
            "flex items-center border-b border-sidebar-border transition-all duration-300 relative",
            isCollapsed ? "px-3 py-6 justify-center" : "px-6 py-6 gap-3"
          )}>
            <div className="w-10 h-10 rounded-xl gradient-primary flex items-center justify-center shadow-glow animate-pulse-glow flex-shrink-0">
              <GraduationCap className="w-6 h-6 text-primary-foreground" />
            </div>
            {!isCollapsed && (
              <>
                <div className="flex-1 min-w-0">
                  <h1 className="font-bold text-sidebar-foreground text-lg text-gradient">
                    Voxen
                  </h1>
                  <p className="text-xs text-muted-foreground font-mono">Gestão Escolar</p>
                </div>
                {/* Botão para colapsar (apenas desktop) */}
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={toggleSidebar}
                  className="hidden lg:flex h-8 w-8 text-sidebar-foreground hover:bg-sidebar-accent flex-shrink-0"
                  title="Colapsar menu"
                >
                  <ChevronLeft size={16} />
                </Button>
              </>
            )}
            {/* Botão para expandir quando colapsado (apenas desktop) */}
            {isCollapsed && (
              <Button
                variant="ghost"
                size="icon"
                onClick={toggleSidebar}
                className="hidden lg:flex h-8 w-8 text-sidebar-foreground hover:bg-sidebar-accent absolute -right-2 top-6 bg-sidebar border border-sidebar-border rounded-full shadow-md"
                title="Expandir menu"
              >
                <ChevronRight size={16} />
              </Button>
            )}
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-1">
            {navItems
              .filter((item) => {
                // Filtrar itens baseado no role do usuário
                if (!user) return false;
                const userRole = user.role;
                return item.roles.includes(userRole);
              })
              .map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={(e) => {
                    console.log('🔗 Navegando para:', item.path);
                    setIsMobileOpen(false);
                  }}
                  className={cn(
                    'flex items-center gap-3 rounded-lg transition-all duration-200 group relative overflow-hidden cursor-pointer',
                    isCollapsed ? 'px-3 py-3 justify-center' : 'px-4 py-3',
                    isActive
                      ? 'bg-gradient-to-r from-sidebar-primary via-sidebar-primary/90 to-sidebar-primary text-sidebar-primary-foreground shadow-glow-blue'
                      : 'text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground hover:translate-x-1 hover:shadow-glow-purple/30'
                  )}
                  style={{ 
                    pointerEvents: 'auto', 
                    zIndex: 100,
                    position: 'relative'
                  }}
                  title={isCollapsed ? item.label : undefined}
                >
                  {/* Efeito shimmer no item ativo - com pointer-events: none */}
                  {isActive && (
                    <div 
                      className="absolute inset-0 animate-shimmer opacity-30"
                      style={{ pointerEvents: 'none', zIndex: 1 }}
                    />
                  )}
                  <item.icon 
                    size={20} 
                    className={cn(
                      'transition-all duration-200 relative flex-shrink-0',
                      isActive 
                        ? 'scale-110 drop-shadow-[0_0_8px_hsl(200_100%_55%)]' 
                        : 'group-hover:scale-110 group-hover:drop-shadow-[0_0_4px_hsl(270_80%_60%)]'
                    )}
                    style={{ zIndex: 10, pointerEvents: 'none' }}
                  />
                  {!isCollapsed && (
                    <>
                      <span 
                        className={cn(
                          'font-medium relative',
                          isActive && 'text-shadow-[0_0_8px_hsl(200_100%_55%)]'
                        )}
                        style={{ zIndex: 10, pointerEvents: 'none' }}
                      >
                        {item.label}
                      </span>
                      {isActive && (
                        <div 
                          className="absolute right-2 w-1.5 h-1.5 rounded-full bg-sidebar-primary-foreground animate-pulse-glow shadow-glow-blue"
                          style={{ pointerEvents: 'none', zIndex: 5 }}
                        />
                      )}
                    </>
                  )}
                </Link>
              );
            })}
          </nav>

          {/* User section e controles */}
          <div className="p-4 border-t border-sidebar-border space-y-2">
            {/* Toggle de tema */}
            <Button
              variant="ghost"
              size={isCollapsed ? "icon" : "default"}
              className={cn(
                "w-full text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                isCollapsed ? "justify-center" : "justify-start gap-3"
              )}
              onClick={() => {
                if (mounted) {
                  setTheme(theme === 'dark' ? 'light' : 'dark');
                }
              }}
              title={isCollapsed ? (theme === 'dark' ? 'Tema claro' : 'Tema escuro') : undefined}
              style={{ pointerEvents: 'auto', zIndex: 100, position: 'relative' }}
            >
              {mounted && theme === 'dark' ? (
                <Sun size={20} />
              ) : (
                <Moon size={20} />
              )}
              {!isCollapsed && (
                <span>{mounted && theme === 'dark' ? 'Tema Claro' : 'Tema Escuro'}</span>
              )}
            </Button>

            {!isCollapsed && (
              <div className="flex items-center gap-3 px-2 py-2 mb-3">
                <div className="w-10 h-10 rounded-full bg-sidebar-accent flex items-center justify-center">
                  <span className="text-sm font-semibold text-sidebar-accent-foreground">
                    {user?.nome?.charAt(0).toUpperCase() || 'U'}
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm text-sidebar-foreground truncate">
                    {user?.nome || 'Usuário'}
                  </p>
                  <p className="text-xs text-muted-foreground truncate">
                    {user?.username || 'admin'}
                  </p>
                </div>
              </div>
            )}
            {isCollapsed && (
              <div className="flex justify-center mb-3">
                <div className="w-10 h-10 rounded-full bg-sidebar-accent flex items-center justify-center">
                  <span className="text-sm font-semibold text-sidebar-accent-foreground">
                    {user?.nome?.charAt(0).toUpperCase() || 'U'}
                  </span>
                </div>
              </div>
            )}
            <Button
              variant="ghost"
              size={isCollapsed ? "icon" : "default"}
              className={cn(
                "w-full text-muted-foreground hover:text-destructive",
                isCollapsed ? "justify-center" : "justify-start gap-3"
              )}
              onClick={(e) => {
                console.log('🚪 Fazendo logout...');
                logout();
              }}
              title={isCollapsed ? 'Sair' : undefined}
              style={{ pointerEvents: 'auto', zIndex: 100, position: 'relative' }}
            >
              <LogOut size={20} />
              {!isCollapsed && <span>Sair</span>}
            </Button>
          </div>
        </div>
      </aside>
    </>
  );
}
