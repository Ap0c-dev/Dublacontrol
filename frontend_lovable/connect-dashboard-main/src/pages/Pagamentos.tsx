import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { MainLayout } from '@/components/layout/MainLayout';
import { api, Pagamento, Professor } from '@/lib/api';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Loader2, CreditCard, Calendar, User, Check, X } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { cn } from '@/lib/utils';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

export default function Pagamentos() {
  const [searchParams] = useSearchParams();
  const [pagamentos, setPagamentos] = useState<Pagamento[]>([]);
  const [professores, setProfessores] = useState<Professor[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState<string>(searchParams.get('status') || '');
  const [filterProfessor, setFilterProfessor] = useState<string>('');
  const [observacoes, setObservacoes] = useState<{ [key: number]: string }>({});
  const { toast } = useToast();

  // Carregar professores
  useEffect(() => {
    const fetchProfessores = async () => {
      try {
        const response = await api.getProfessores();
        if (response.success) {
          setProfessores(response.data);
        }
      } catch (error) {
        console.error('Erro ao carregar professores:', error);
      }
    };
    fetchProfessores();
  }, []);

  useEffect(() => {
    const fetchPagamentos = async () => {
      setIsLoading(true);
      try {
        const filters: any = {};
        if (filter) {
          filters.status = filter;
        }
        if (filterProfessor && filterProfessor !== 'all') {
          filters.professor_id = parseInt(filterProfessor);
        }
        
        const response = await api.getPagamentos(filters);
        if (response.success) {
          setPagamentos(response.data);
        } else {
          toast({
            title: 'Erro ao carregar pagamentos',
            description: 'Não foi possível obter a lista.',
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
        setIsLoading(false);
      }
    };

    fetchPagamentos();
  }, [filter, filterProfessor, toast]);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { label: string; className: string }> = {
      pago: { 
        label: 'Pago', 
        className: 'bg-success/10 text-success border-success/20' 
      },
      pendente: { 
        label: 'Pendente', 
        className: 'bg-warning/10 text-warning border-warning/20' 
      },
      atrasado: { 
        label: 'Atrasado', 
        className: 'bg-destructive/10 text-destructive border-destructive/20' 
      },
    };

    const config = statusMap[status.toLowerCase()] || { 
      label: status, 
      className: 'bg-muted text-muted-foreground' 
    };
    
    return (
      <Badge variant="outline" className={config.className}>
        {config.label}
      </Badge>
    );
  };

  const handleAprovar = async (id: number) => {
    try {
      const response = await api.aprovarPagamento(id, observacoes[id]);
      if (response.success) {
        toast({
          title: 'Sucesso',
          description: 'Pagamento aprovado com sucesso!',
        });
        // Recarregar pagamentos
        const res = await api.getPagamentos({ status: filter || undefined });
        if (res.success) {
          setPagamentos(res.data);
        }
        setObservacoes({ ...observacoes, [id]: '' });
      } else {
        toast({
          title: 'Erro',
          description: response.error || 'Erro ao aprovar pagamento',
          variant: 'destructive',
        });
      }
    } catch (error) {
      toast({
        title: 'Erro',
        description: 'Erro ao aprovar pagamento',
        variant: 'destructive',
      });
    }
  };

  const handleRejeitar = async (id: number) => {
    try {
      const response = await api.rejeitarPagamento(id, observacoes[id]);
      if (response.success) {
        toast({
          title: 'Sucesso',
          description: 'Pagamento rejeitado',
        });
        // Recarregar pagamentos
        const res = await api.getPagamentos({ status: filter || undefined });
        if (res.success) {
          setPagamentos(res.data);
        }
        setObservacoes({ ...observacoes, [id]: '' });
      } else {
        toast({
          title: 'Erro',
          description: response.error || 'Erro ao rejeitar pagamento',
          variant: 'destructive',
        });
      }
    } catch (error) {
      toast({
        title: 'Erro',
        description: 'Erro ao rejeitar pagamento',
        variant: 'destructive',
      });
    }
  };

  const filters = [
    { value: '', label: 'Todos' },
    { value: 'pendente', label: 'Pendentes' },
    { value: 'pago', label: 'Pagos' },
    { value: 'atrasado', label: 'Atrasados' },
  ];

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="animate-fade-in">
          <h1 className="text-2xl lg:text-3xl font-bold text-foreground">Pagamentos</h1>
          <p className="text-muted-foreground mt-1">
            Controle financeiro e cobranças
          </p>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-4 animate-fade-in">
          <div className="flex flex-wrap gap-2">
            {filters.map((f) => (
              <Button
                key={f.value}
                variant={filter === f.value ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilter(f.value)}
              >
                {f.label}
              </Button>
            ))}
          </div>
          
          <div className="flex items-center gap-2">
            <Select value={filterProfessor} onValueChange={setFilterProfessor}>
              <SelectTrigger className="w-[200px]">
                <SelectValue placeholder="Filtrar por professor" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos os professores</SelectItem>
                {professores.map((professor) => (
                  <SelectItem key={professor.id} value={professor.id.toString()}>
                    {professor.nome}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Table */}
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
          </div>
        ) : pagamentos.length > 0 ? (
          <div className="bg-card rounded-xl border border-border shadow-card overflow-hidden animate-slide-up">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-muted/50">
                  <tr>
                    <th className="text-left text-sm font-medium text-muted-foreground px-6 py-4">
                      Aluno
                    </th>
                    <th className="text-left text-sm font-medium text-muted-foreground px-6 py-4">
                      Valor
                    </th>
                    <th className="text-left text-sm font-medium text-muted-foreground px-6 py-4 hidden md:table-cell">
                      Vencimento
                    </th>
                    <th className="text-left text-sm font-medium text-muted-foreground px-6 py-4 hidden lg:table-cell">
                      Pagamento
                    </th>
                    <th className="text-left text-sm font-medium text-muted-foreground px-6 py-4">
                      Status
                    </th>
                    <th className="text-left text-sm font-medium text-muted-foreground px-6 py-4">
                      Ações
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {pagamentos.map((pagamento, index) => (
                    <tr 
                      key={pagamento.id} 
                      className="hover:bg-muted/30 transition-colors"
                      style={{ animationDelay: `${index * 50}ms` }}
                    >
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                            <User size={18} className="text-primary" />
                          </div>
                          <span className="font-medium text-foreground">
                            {pagamento.aluno_nome || `Aluno #${pagamento.aluno_id}`}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="font-semibold text-foreground">
                          {formatCurrency(pagamento.valor)}
                        </span>
                      </td>
                      <td className="px-6 py-4 hidden md:table-cell">
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <Calendar size={14} />
                          {pagamento.data_vencimento
                            ? new Date(pagamento.data_vencimento).toLocaleDateString('pt-BR')
                            : '-'}
                        </div>
                      </td>
                      <td className="px-6 py-4 hidden lg:table-cell text-sm text-muted-foreground">
                        {pagamento.data_pagamento
                          ? new Date(pagamento.data_pagamento).toLocaleDateString('pt-BR')
                          : '-'}
                      </td>
                      <td className="px-6 py-4">
                        {getStatusBadge(pagamento.status)}
                      </td>
                      <td className="px-6 py-4">
                        {pagamento.status === 'pendente' && (
                          <div className="flex gap-2">
                            <AlertDialog>
                              <AlertDialogTrigger asChild>
                                <Button size="sm" variant="default">
                                  <Check size={16} className="mr-1" />
                                  Aprovar
                                </Button>
                              </AlertDialogTrigger>
                              <AlertDialogContent>
                                <AlertDialogHeader>
                                  <AlertDialogTitle>Aprovar Pagamento</AlertDialogTitle>
                                  <AlertDialogDescription>
                                    Deseja aprovar este pagamento?
                                  </AlertDialogDescription>
                                </AlertDialogHeader>
                                <div className="space-y-4">
                                  <div>
                                    <Label>Observações (opcional)</Label>
                                    <Textarea
                                      value={observacoes[pagamento.id] || ''}
                                      onChange={(e) => setObservacoes({ ...observacoes, [pagamento.id]: e.target.value })}
                                      placeholder="Adicione observações sobre a aprovação..."
                                    />
                                  </div>
                                </div>
                                <AlertDialogFooter>
                                  <AlertDialogCancel>Cancelar</AlertDialogCancel>
                                  <AlertDialogAction onClick={() => handleAprovar(pagamento.id)}>
                                    Aprovar
                                  </AlertDialogAction>
                                </AlertDialogFooter>
                              </AlertDialogContent>
                            </AlertDialog>
                            <AlertDialog>
                              <AlertDialogTrigger asChild>
                                <Button size="sm" variant="destructive">
                                  <X size={16} className="mr-1" />
                                  Rejeitar
                                </Button>
                              </AlertDialogTrigger>
                              <AlertDialogContent>
                                <AlertDialogHeader>
                                  <AlertDialogTitle>Rejeitar Pagamento</AlertDialogTitle>
                                  <AlertDialogDescription>
                                    Deseja rejeitar este pagamento?
                                  </AlertDialogDescription>
                                </AlertDialogHeader>
                                <div className="space-y-4">
                                  <div>
                                    <Label>Motivo da Rejeição</Label>
                                    <Textarea
                                      value={observacoes[pagamento.id] || ''}
                                      onChange={(e) => setObservacoes({ ...observacoes, [pagamento.id]: e.target.value })}
                                      placeholder="Informe o motivo da rejeição..."
                                    />
                                  </div>
                                </div>
                                <AlertDialogFooter>
                                  <AlertDialogCancel>Cancelar</AlertDialogCancel>
                                  <AlertDialogAction onClick={() => handleRejeitar(pagamento.id)}>
                                    Rejeitar
                                  </AlertDialogAction>
                                </AlertDialogFooter>
                              </AlertDialogContent>
                            </AlertDialog>
                          </div>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div className="text-center py-12 bg-card rounded-xl border border-border">
            <CreditCard className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground">Nenhum pagamento encontrado.</p>
          </div>
        )}
      </div>
    </MainLayout>
  );
}
