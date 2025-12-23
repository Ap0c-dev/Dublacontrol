import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MainLayout } from '@/components/layout/MainLayout';
import { StatCard } from '@/components/dashboard/StatCard';
import { api, DashboardStats } from '@/lib/api';
import { Users, GraduationCap, CreditCard, AlertCircle, Loader2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const { toast } = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchStats = async () => {
      try {
        console.log('🔍 Buscando estatísticas do dashboard...');
        const response = await api.getDashboardStats();
        console.log('📊 Resposta da API:', response);
        if (response.success) {
          console.log('📊 Dados recebidos:', response.data);
          console.log('📊 Pagamentos atrasados:', response.data?.pagamentos_atrasados);
          setStats(response.data);
          console.log('✅ Estatísticas carregadas:', response.data);
        } else {
          console.error('❌ Erro na resposta:', response.error);
          
          // Se for erro de autenticação, redirecionar para login
          if (response.error?.includes('Não autenticado') || response.error?.includes('Token')) {
            toast({
              title: 'Sessão expirada',
              description: 'Por favor, faça login novamente.',
              variant: 'destructive',
            });
            // O ProtectedRoute vai redirecionar automaticamente
            return;
          }
          
          toast({
            title: 'Erro ao carregar dados',
            description: response.error || 'Não foi possível obter as estatísticas.',
            variant: 'destructive',
          });
        }
      } catch (error) {
        console.error('❌ Erro ao buscar estatísticas:', error);
        toast({
          title: 'Erro de conexão',
          description: error instanceof Error ? error.message : 'Verifique se o servidor está rodando.',
          variant: 'destructive',
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchStats();
  }, [toast]);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  return (
    <MainLayout>
      <div className="space-y-8">
        {/* Header */}
        <div className="animate-fade-in">
          <h1 className="text-2xl lg:text-3xl font-bold text-gradient animate-float">Dashboard</h1>
          <p className="text-muted-foreground mt-1 font-mono">
            Visão geral do sistema
          </p>
        </div>

        {/* Stats Grid */}
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
          </div>
        ) : stats ? (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            <StatCard
              title="Total de Alunos"
              value={stats.total_alunos}
              icon={Users}
              variant="primary"
              trend={{ value: 12, isPositive: true }}
            />
            <StatCard
              title="Professores"
              value={stats.total_professores}
              icon={GraduationCap}
              variant="default"
            />
            <StatCard
              title="Receita Mensal"
              value={formatCurrency(stats.receita_mensal || 0)}
              icon={CreditCard}
              variant="success"
              trend={{ value: 8, isPositive: true }}
            />
            <StatCard
              title="Pagamentos Atrasados"
              value={stats.pagamentos_atrasados ?? 0}
              icon={AlertCircle}
              variant="destructive"
              onClick={() => navigate('/pagamentos?status=atrasado')}
            />
          </div>
        ) : (
          <div className="text-center py-12">
            <AlertCircle className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground">Não foi possível carregar os dados.</p>
          </div>
        )}

        {/* Quick Info Section */}
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="bg-card rounded-xl border border-border p-6 shadow-card animate-slide-up">
            <h2 className="text-lg font-semibold text-foreground mb-4">
              Bem-vindo ao Voxen
            </h2>
            <p className="text-muted-foreground text-sm leading-relaxed">
              Gerencie alunos, professores e pagamentos de forma simples e eficiente.
              Utilize o menu lateral para navegar entre as diferentes seções do sistema.
            </p>
          </div>

          <div className="bg-card rounded-xl border border-border p-6 shadow-card animate-slide-up" style={{ animationDelay: '100ms' }}>
            <h2 className="text-lg font-semibold text-foreground mb-4">
              Ações Rápidas
            </h2>
            <ul className="space-y-3 text-sm text-muted-foreground">
              <li className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-primary" />
                Visualize a lista completa de alunos
              </li>
              <li className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-success" />
                Acompanhe os pagamentos atrasados
              </li>
              <li className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-warning" />
                Gerencie o quadro de professores
              </li>
            </ul>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
