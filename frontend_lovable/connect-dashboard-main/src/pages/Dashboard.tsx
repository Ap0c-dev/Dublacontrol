import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MainLayout } from '@/components/layout/MainLayout';
import { StatCard } from '@/components/dashboard/StatCard';
import { api, DashboardStats } from '@/lib/api';
import { Users, GraduationCap, CreditCard, AlertCircle, Loader2, Clock, X } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, PieChart, Pie, Cell } from 'recharts';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isEvolucaoOpen, setIsEvolucaoOpen] = useState(false);
  const [evolucaoData, setEvolucaoData] = useState<Array<{ mes: number; ano: number; mes_nome: string; mes_ano: string; total_alunos: number; data_referencia: string }>>([]);
  const [isLoadingEvolucao, setIsLoadingEvolucao] = useState(false);
  const [isFaturamentoOpen, setIsFaturamentoOpen] = useState(false);
  const [faturamentoData, setFaturamentoData] = useState<Array<{ mes: number; ano: number; mes_nome: string; mes_ano: string; receita: number; data_referencia: string }>>([]);
  const [isLoadingFaturamento, setIsLoadingFaturamento] = useState(false);
  const [notificacoes, setNotificacoes] = useState<Array<{
    id: number;
    nome: string;
    telefone: string;
    curso?: string;
    data_pretende_entrar?: string;
    data_cadastro?: string;
    dias_atrasado?: number;
    esta_atrasado?: boolean;
  }>>([]);
  const [notificacoesVisiveis, setNotificacoesVisiveis] = useState<Set<number>>(new Set());
  const [professoresData, setProfessoresData] = useState<Array<{
    professor_id: number;
    professor_nome: string;
    total_matriculas: number;
    matriculas_ativas: number;
    matriculas_encerradas: number;
    alunos_que_mudaram_professor: number;
    total_evasoes: number;
    alunos_ativos: number;
    retencao: number;
    evasao: number;
    receita_mensal: number;
    tempo_medio_permanencia_meses: number;
    taxa_inadimplencia: number;
    alunos_atrasados: number;
    modalidades: string[];
    crescimento: number;
    novos_ultimos_3_meses: number;
    novos_3_meses_anteriores: number;
  }>>([]);
  const [isLoadingProfessores, setIsLoadingProfessores] = useState(false);
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

  // Buscar notificações da lista de espera separadamente
  useEffect(() => {
    const fetchNotificacoes = async () => {
      try {
        const response = await api.getNotificacoesListaEspera();
        if (response.success && response.data) {
          setNotificacoes(response.data);
          // Mostrar notificações que ainda não foram exibidas
          response.data.forEach((notif: any) => {
            setNotificacoesVisiveis((prev) => {
              if (!prev.has(notif.id)) {
                const mensagem = notif.esta_atrasado 
                  ? `${notif.nome} pretendia entrar há ${notif.dias_atrasado} ${notif.dias_atrasado === 1 ? 'dia' : 'dias'}${notif.curso ? ` (${notif.curso})` : ''}`
                  : `${notif.nome} pretende entrar no curso hoje${notif.curso ? ` (${notif.curso})` : ''}`;
                
                toast({
                  title: notif.esta_atrasado ? 'Aluno da Lista de Espera - Atrasado' : 'Aluno da Lista de Espera',
                  description: mensagem,
                  duration: 10000,
                  variant: notif.esta_atrasado ? 'destructive' : 'default',
                });
                return new Set(prev).add(notif.id);
              }
              return prev;
            });
          });
        }
      } catch (error) {
        console.error('Erro ao buscar notificações:', error);
      }
    };
    
    fetchNotificacoes();
    // Verificar notificações a cada 5 minutos
    const interval = setInterval(fetchNotificacoes, 5 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, [toast]);

  const handleOpenEvolucao = async () => {
    setIsEvolucaoOpen(true);
    setIsLoadingEvolucao(true);
    try {
      const response = await api.getAlunosEvolucao();
      if (response.success) {
        setEvolucaoData(response.data);
      } else {
        toast({
          title: 'Erro ao carregar dados',
          description: response.error || 'Não foi possível obter a evolução de alunos.',
          variant: 'destructive',
        });
      }
    } catch (error) {
      toast({
        title: 'Erro de conexão',
        description: 'Verifique se o servidor está rodando.',
        variant: 'destructive',
      });
    } finally {
      setIsLoadingEvolucao(false);
    }
  };

  const handleOpenFaturamento = async () => {
    setIsFaturamentoOpen(true);
    setIsLoadingFaturamento(true);
    try {
      const response = await api.getFaturamentoMensal();
      if (response.success) {
        setFaturamentoData(response.data);
      } else {
        toast({
          title: 'Erro ao carregar dados',
          description: response.error || 'Não foi possível obter o faturamento mensal.',
          variant: 'destructive',
        });
      }
    } catch (error) {
      toast({
        title: 'Erro de conexão',
        description: 'Verifique se o servidor está rodando.',
        variant: 'destructive',
      });
    } finally {
      setIsLoadingFaturamento(false);
    }
  };

  const fetchProfessoresData = async () => {
    if (professoresData.length > 0) return; // Já carregado
    setIsLoadingProfessores(true);
    try {
      const response = await api.getProfessoresPerformance();
      if (response.success) {
        setProfessoresData(response.data);
      } else {
        toast({
          title: 'Erro ao carregar dados',
          description: response.error || 'Não foi possível obter a performance de professores.',
          variant: 'destructive',
        });
      }
    } catch (error) {
      toast({
        title: 'Erro de conexão',
        description: 'Verifique se o servidor está rodando.',
        variant: 'destructive',
      });
    } finally {
      setIsLoadingProfessores(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  const fecharNotificacao = (id: number) => {
    setNotificacoesVisiveis((prev) => {
      const novo = new Set(prev);
      novo.add(id);
      return novo;
    });
  };

  return (
    <MainLayout>
      <div className="space-y-8">
        {/* Notificações da Lista de Espera */}
        {notificacoes.length > 0 && (
          <div className="fixed top-4 right-4 z-50 space-y-2 max-w-md">
            {notificacoes
              .filter((notif) => !notificacoesVisiveis.has(notif.id))
              .map((notif) => {
                const estaAtrasado = notif.esta_atrasado || false;
                const diasAtrasado = notif.dias_atrasado || 0;
                const cardClass = estaAtrasado 
                  ? "border-red-500 bg-red-50 dark:bg-red-950/20 shadow-lg"
                  : "border-orange-500 bg-orange-50 dark:bg-orange-950/20 shadow-lg";
                const iconClass = estaAtrasado
                  ? "text-red-600 dark:text-red-400"
                  : "text-orange-600 dark:text-orange-400";
                const textClass = estaAtrasado
                  ? "text-red-900 dark:text-red-100"
                  : "text-orange-900 dark:text-orange-100";
                const textSecondaryClass = estaAtrasado
                  ? "text-red-800 dark:text-red-200"
                  : "text-orange-800 dark:text-orange-200";
                
                return (
                <Card key={notif.id} className={cardClass}>
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-start gap-3 flex-1">
                        <Clock className={`w-5 h-5 ${iconClass} mt-0.5 flex-shrink-0`} />
                        <div className="flex-1">
                          <h4 className={`font-semibold text-sm ${textClass}`}>
                            {estaAtrasado ? 'Aluno da Lista de Espera - Atrasado' : 'Aluno da Lista de Espera'}
                          </h4>
                          <p className={`text-sm ${textSecondaryClass} mt-1`}>
                            <strong>{notif.nome}</strong> {estaAtrasado 
                              ? `pretendia entrar há ${diasAtrasado} ${diasAtrasado === 1 ? 'dia' : 'dias'}`
                              : 'pretende entrar no curso hoje'}
                            {notif.curso && (
                              <span className="block text-xs mt-1">Curso: {notif.curso}</span>
                            )}
                            {notif.data_pretende_entrar && (
                              <span className="block text-xs mt-1">
                                Data prevista: {new Date(notif.data_pretende_entrar).toLocaleDateString('pt-BR')}
                              </span>
                            )}
                          </p>
                          <Button
                            size="sm"
                            variant="outline"
                            className="mt-2 text-xs"
                            onClick={() => navigate('/alunos/lista-espera')}
                          >
                            Ver Lista de Espera
                          </Button>
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-6 w-6 p-0 flex-shrink-0"
                        onClick={() => fecharNotificacao(notif.id)}
                      >
                        <X className="w-4 h-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
                );
              })}
          </div>
        )}

        {/* Header */}
        <div className="animate-fade-in">
          <h1 className="text-2xl lg:text-3xl font-bold text-gradient animate-float">Dashboard</h1>
          <p className="text-muted-foreground mt-1 font-mono">
            Análises e métricas do sistema
          </p>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="visao-geral" className="w-full">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="visao-geral">Visão Geral</TabsTrigger>
            <TabsTrigger value="professores" onClick={fetchProfessoresData}>Professores</TabsTrigger>
            <TabsTrigger value="alunos">Alunos</TabsTrigger>
            <TabsTrigger value="receita">Receita</TabsTrigger>
            <TabsTrigger value="pagamentos">Pagamentos</TabsTrigger>
          </TabsList>

          {/* Tab: Visão Geral */}
          <TabsContent value="visao-geral" className="space-y-6">
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
                  trend={stats.crescimento_alunos !== undefined ? {
                    value: Math.abs(stats.crescimento_alunos),
                    isPositive: stats.crescimento_alunos >= 0
                  } : undefined}
                  onClick={handleOpenEvolucao}
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
                  trend={stats.crescimento_receita !== undefined ? {
                    value: Math.abs(stats.crescimento_receita),
                    isPositive: stats.crescimento_receita >= 0
                  } : undefined}
                  onClick={handleOpenFaturamento}
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
                  Utilize as abas acima para explorar diferentes análises e métricas do sistema.
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
          </TabsContent>

          {/* Tab: Professores */}
          <TabsContent value="professores" className="space-y-6">
            <div className="bg-card rounded-xl border border-border p-6">
              <h2 className="text-xl font-semibold mb-4">Performance de Professores</h2>
              {isLoadingProfessores ? (
                <div className="flex items-center justify-center h-64">
                  <Loader2 className="w-8 h-8 animate-spin text-primary" />
                </div>
              ) : professoresData.length > 0 ? (
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Professor</TableHead>
                        <TableHead>Alunos Ativos</TableHead>
                        <TableHead>Retenção</TableHead>
                        <TableHead>Evasão</TableHead>
                        <TableHead>Mudaram</TableHead>
                        <TableHead>Receita Mensal</TableHead>
                        <TableHead>Inadimplência</TableHead>
                        <TableHead>Crescimento</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {professoresData.map((prof) => (
                        <TableRow key={prof.professor_id}>
                          <TableCell className="font-medium">{prof.professor_nome}</TableCell>
                          <TableCell>{prof.alunos_ativos}</TableCell>
                          <TableCell>
                            <Badge variant={prof.retencao >= 70 ? "default" : prof.retencao >= 50 ? "secondary" : "destructive"}>
                              {prof.retencao.toFixed(1)}%
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <Badge variant={prof.evasao <= 20 ? "default" : prof.evasao <= 40 ? "secondary" : "destructive"}>
                              {prof.evasao.toFixed(1)}%
                            </Badge>
                          </TableCell>
                          <TableCell>
                            {prof.alunos_que_mudaram_professor > 0 && (
                              <Badge variant="outline">{prof.alunos_que_mudaram_professor}</Badge>
                            )}
                            {prof.alunos_que_mudaram_professor === 0 && <span className="text-muted-foreground">-</span>}
                          </TableCell>
                          <TableCell className="font-semibold">{formatCurrency(prof.receita_mensal)}</TableCell>
                          <TableCell>
                            <Badge variant={prof.taxa_inadimplencia <= 10 ? "default" : prof.taxa_inadimplencia <= 20 ? "secondary" : "destructive"}>
                              {prof.taxa_inadimplencia.toFixed(1)}%
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <Badge variant={prof.crescimento >= 0 ? "default" : "destructive"}>
                              {prof.crescimento >= 0 ? '+' : ''}{prof.crescimento.toFixed(1)}%
                            </Badge>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              ) : (
                <div className="text-center py-12">
                  <GraduationCap className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-muted-foreground">Nenhum dado de professor disponível.</p>
                </div>
              )}
            </div>
          </TabsContent>

          {/* Tab: Alunos */}
          <TabsContent value="alunos" className="space-y-6">
            <div className="bg-card rounded-xl border border-border p-6">
              <h2 className="text-xl font-semibold mb-4">Evolução de Alunos</h2>
              <Button onClick={handleOpenEvolucao} variant="outline">
                Ver Gráfico de Evolução
              </Button>
            </div>
          </TabsContent>

          {/* Tab: Receita */}
          <TabsContent value="receita" className="space-y-6">
            <div className="bg-card rounded-xl border border-border p-6">
              <h2 className="text-xl font-semibold mb-4">Faturamento Mensal</h2>
              <Button onClick={handleOpenFaturamento} variant="outline">
                Ver Gráfico de Faturamento
              </Button>
            </div>
          </TabsContent>

          {/* Tab: Pagamentos */}
          <TabsContent value="pagamentos" className="space-y-6">
            <div className="bg-card rounded-xl border border-border p-6">
              <h2 className="text-xl font-semibold mb-4">Status de Pagamentos</h2>
              <Button onClick={() => navigate('/pagamentos')} variant="outline">
                Ver Todos os Pagamentos
              </Button>
            </div>
          </TabsContent>
        </Tabs>
      </div>

      {/* Modal de Evolução de Alunos */}
      <Dialog open={isEvolucaoOpen} onOpenChange={setIsEvolucaoOpen}>
        <DialogContent className="sm:max-w-[800px]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Users size={24} />
              Evolução de Alunos - Últimos 12 Meses
            </DialogTitle>
            <DialogDescription>
              Gráfico mostrando quantos alunos começaram (data de início) em cada mês
            </DialogDescription>
          </DialogHeader>
          {isLoadingEvolucao ? (
            <div className="flex items-center justify-center h-64">
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
            </div>
          ) : evolucaoData.length > 0 ? (
            <div className="mt-4">
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={evolucaoData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                  <XAxis 
                    dataKey="mes_ano" 
                    className="text-xs"
                    tick={{ fill: 'hsl(var(--muted-foreground))' }}
                  />
                  <YAxis 
                    className="text-xs"
                    tick={{ fill: 'hsl(var(--muted-foreground))' }}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px'
                    }}
                    labelStyle={{ color: 'hsl(var(--foreground))' }}
                  />
                  <Legend />
                  <Bar 
                    dataKey="total_alunos" 
                    fill="hsl(var(--primary))"
                    name="Alunos que começaram"
                    radius={[8, 8, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-muted-foreground">Nenhum dado disponível.</p>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Modal de Faturamento Mensal */}
      <Dialog open={isFaturamentoOpen} onOpenChange={setIsFaturamentoOpen}>
        <DialogContent className="sm:max-w-[800px]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <CreditCard size={24} />
              Faturamento Mensal - Últimos 12 Meses
            </DialogTitle>
            <DialogDescription>
              Gráfico mostrando a receita (pagamentos aprovados) de cada mês
            </DialogDescription>
          </DialogHeader>
          {isLoadingFaturamento ? (
            <div className="flex items-center justify-center h-64">
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
            </div>
          ) : faturamentoData.length > 0 ? (
            <div className="mt-4">
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={faturamentoData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                  <XAxis 
                    dataKey="mes_ano" 
                    className="text-xs"
                    tick={{ fill: 'hsl(var(--muted-foreground))' }}
                  />
                  <YAxis 
                    className="text-xs"
                    tick={{ fill: 'hsl(var(--muted-foreground))' }}
                    tickFormatter={(value) => formatCurrency(value)}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px'
                    }}
                    labelStyle={{ color: 'hsl(var(--foreground))' }}
                    formatter={(value: number) => formatCurrency(value)}
                  />
                  <Legend />
                  <Bar 
                    dataKey="receita" 
                    fill="hsl(var(--success))"
                    name="Receita (R$)"
                    radius={[8, 8, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-muted-foreground">Nenhum dado disponível.</p>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </MainLayout>
  );
}
