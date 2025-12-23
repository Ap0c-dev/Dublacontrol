import { useEffect, useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { MainLayout } from '@/components/layout/MainLayout';
import { api, Nota } from '@/lib/api';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Loader2, BookOpen, Search, User, GraduationCap, Calendar, Plus, Pencil, Trash2, ChevronDown, ChevronRight } from 'lucide-react';
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

interface NotasAgrupadas {
  aluno_id: number;
  aluno_nome: string;
  notas: Nota[];
  totalProvas: number;
  mediaGeral: number | null;
}

export default function Notas() {
  const [notas, setNotas] = useState<Nota[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filterAluno, setFilterAluno] = useState<string>('');
  const [alunosExpandidos, setAlunosExpandidos] = useState<Set<number>>(new Set());
  const { toast } = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchNotas = async () => {
      setIsLoading(true);
      try {
        const filters: any = {};
        if (filterAluno) {
          filters.aluno_id = parseInt(filterAluno);
        }
        
        const response = await api.getNotas(filters);
        if (response.success) {
          let notasFiltradas = response.data;
          
          // Filtrar por busca (nome do aluno)
          if (search) {
            notasFiltradas = notasFiltradas.filter(nota =>
              nota.aluno_nome?.toLowerCase().includes(search.toLowerCase())
            );
          }
          
          setNotas(notasFiltradas);
        } else {
          toast({
            title: 'Erro ao carregar notas',
            description: 'Não foi possível obter a lista de notas.',
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

    const debounce = setTimeout(fetchNotas, 300);
    return () => clearTimeout(debounce);
  }, [search, filterAluno, toast]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR');
  };

  const formatNota = (valor: number | null) => {
    if (valor === null) return '-';
    return valor.toFixed(1);
  };

  // Agrupar notas por aluno
  const notasAgrupadas = useMemo(() => {
    const agrupadas = new Map<number, NotasAgrupadas>();
    
    notas.forEach(nota => {
      if (!agrupadas.has(nota.aluno_id)) {
        agrupadas.set(nota.aluno_id, {
          aluno_id: nota.aluno_id,
          aluno_nome: nota.aluno_nome || `Aluno #${nota.aluno_id}`,
          notas: [],
          totalProvas: 0,
          mediaGeral: null,
        });
      }
      
      const grupo = agrupadas.get(nota.aluno_id)!;
      grupo.notas.push(nota);
    });
    
    // Calcular estatísticas para cada grupo
    agrupadas.forEach(grupo => {
      grupo.totalProvas = grupo.notas.length;
      
      // Calcular média geral (usando media ou valor)
      const notasComValor = grupo.notas
        .map(n => n.media !== null ? n.media : n.valor)
        .filter((v): v is number => v !== null);
      
      if (notasComValor.length > 0) {
        const soma = notasComValor.reduce((acc, val) => acc + val, 0);
        grupo.mediaGeral = soma / notasComValor.length;
      }
    });
    
    return Array.from(agrupadas.values()).sort((a, b) => 
      a.aluno_nome.localeCompare(b.aluno_nome)
    );
  }, [notas]);

  const toggleExpandir = (alunoId: number) => {
    const novosExpandidos = new Set(alunosExpandidos);
    if (novosExpandidos.has(alunoId)) {
      novosExpandidos.delete(alunoId);
    } else {
      novosExpandidos.add(alunoId);
    }
    setAlunosExpandidos(novosExpandidos);
  };

  const getTipoCursoBadge = (tipo: string) => {
    const tipos: Record<string, { label: string; className: string }> = {
      'dublagem_online': { label: 'Dublagem Online', className: 'bg-blue-100 text-blue-800' },
      'dublagem_presencial': { label: 'Dublagem Presencial', className: 'bg-blue-100 text-blue-800' },
      'teatro_online': { label: 'Teatro Online', className: 'bg-purple-100 text-purple-800' },
      'teatro_presencial': { label: 'Teatro Presencial', className: 'bg-purple-100 text-purple-800' },
      'locucao': { label: 'Locução', className: 'bg-green-100 text-green-800' },
      'teatro_tv_cinema': { label: 'Teatro TV/Cinema', className: 'bg-orange-100 text-orange-800' },
      'musical': { label: 'Musical', className: 'bg-pink-100 text-pink-800' },
    };

    const config = tipos[tipo] || { label: tipo, className: 'bg-gray-100 text-gray-800' };
    return (
      <Badge variant="outline" className={config.className}>
        {config.label}
      </Badge>
    );
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 animate-fade-in">
          <div>
            <h1 className="text-2xl lg:text-3xl font-bold text-foreground">Notas</h1>
            <p className="text-muted-foreground mt-1">
              Gerencie as notas e avaliações dos alunos
            </p>
          </div>
          <Button onClick={() => navigate('/notas/novo')}>
            <Plus size={18} className="mr-2" />
            Nova Nota
          </Button>
        </div>

        {/* Search and Filters */}
        <div className="flex flex-col sm:flex-row gap-4 animate-fade-in">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={18} />
            <Input
              placeholder="Buscar por nome do aluno..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10"
            />
          </div>
          <Input
            type="number"
            placeholder="Filtrar por ID do aluno"
            value={filterAluno}
            onChange={(e) => setFilterAluno(e.target.value)}
            className="max-w-xs"
          />
        </div>

        {/* Table */}
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
          </div>
        ) : notasAgrupadas.length > 0 ? (
          <div className="bg-card rounded-xl border border-border shadow-card overflow-hidden animate-slide-up">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-muted/50">
                  <tr>
                    <th className="text-left text-sm font-medium text-muted-foreground px-6 py-4 w-12">
                    </th>
                    <th className="text-left text-sm font-medium text-muted-foreground px-6 py-4">
                      Aluno / Detalhes
                    </th>
                    <th className="text-left text-sm font-medium text-muted-foreground px-6 py-4">
                      Professor / Total
                    </th>
                    <th className="text-left text-sm font-medium text-muted-foreground px-6 py-4">
                      Nota / Média
                    </th>
                    <th className="text-left text-sm font-medium text-muted-foreground px-6 py-4">
                      Ações
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {notasAgrupadas.map((grupo, index) => {
                    const estaExpandido = alunosExpandidos.has(grupo.aluno_id);
                    return (
                      <>
                        {/* Linha do aluno (agrupada) */}
                        <tr 
                          key={`aluno-${grupo.aluno_id}`}
                          className="hover:bg-muted/30 transition-colors cursor-pointer"
                          onClick={() => toggleExpandir(grupo.aluno_id)}
                          style={{ animationDelay: `${index * 50}ms` }}
                        >
                          <td className="px-6 py-4">
                            {estaExpandido ? (
                              <ChevronDown size={18} className="text-muted-foreground" />
                            ) : (
                              <ChevronRight size={18} className="text-muted-foreground" />
                            )}
                          </td>
                          <td className="px-6 py-4">
                            <div className="flex items-center gap-3">
                              <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                                <User size={18} className="text-primary" />
                              </div>
                              <span className="font-medium text-foreground">
                                {grupo.aluno_nome}
                              </span>
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            <Badge variant="outline" className="bg-blue-100 text-blue-800">
                              {grupo.totalProvas} {grupo.totalProvas === 1 ? 'prova' : 'provas'}
                            </Badge>
                          </td>
                          <td className="px-6 py-4">
                            {grupo.mediaGeral !== null ? (
                              <span className="font-semibold text-foreground text-lg">
                                {formatNota(grupo.mediaGeral)}
                              </span>
                            ) : (
                              <span className="text-muted-foreground">-</span>
                            )}
                          </td>
                          <td className="px-6 py-4" onClick={(e) => e.stopPropagation()}>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => navigate(`/alunos/${grupo.aluno_id}`)}
                            >
                              Ver Detalhes
                            </Button>
                          </td>
                        </tr>
                        
                        {/* Linhas das provas (expandidas) */}
                        {estaExpandido && grupo.notas.map((nota) => (
                          <tr 
                            key={nota.id}
                            className="bg-muted/20 hover:bg-muted/40 transition-colors"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <td className="px-6 py-3"></td>
                            <td className="px-6 py-3 pl-12">
                              <div className="flex items-center gap-2 text-sm">
                                {getTipoCursoBadge(nota.tipo_curso)}
                                {nota.numero_prova && (
                                  <Badge variant="outline" className="text-xs">
                                    Prova {nota.numero_prova}
                                  </Badge>
                                )}
                                {nota.tipo_avaliacao && (
                                  <span className="text-xs text-muted-foreground">
                                    ({nota.tipo_avaliacao})
                                  </span>
                                )}
                              </div>
                            </td>
                            <td className="px-6 py-3">
                              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                <GraduationCap size={14} />
                                {nota.professor_nome || '-'}
                                {nota.data_avaliacao && (
                                  <span className="text-xs">
                                    • {formatDate(nota.data_avaliacao)}
                                  </span>
                                )}
                              </div>
                            </td>
                            <td className="px-6 py-3">
                              <div className="flex items-center gap-2">
                                {nota.media !== null ? (
                                  <span className="font-semibold text-foreground">
                                    {formatNota(nota.media)}
                                  </span>
                                ) : nota.valor !== null ? (
                                  <span className="font-semibold text-foreground">
                                    {formatNota(nota.valor)}
                                  </span>
                                ) : (
                                  <span className="text-muted-foreground">-</span>
                                )}
                              </div>
                            </td>
                            <td className="px-6 py-3">
                              <div className="flex gap-2">
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => navigate(`/notas/${nota.id}/editar`)}
                                >
                                  <Pencil size={16} />
                                </Button>
                                <AlertDialog>
                                  <AlertDialogTrigger asChild>
                                    <Button variant="ghost" size="sm">
                                      <Trash2 size={16} className="text-destructive" />
                                    </Button>
                                  </AlertDialogTrigger>
                                  <AlertDialogContent>
                                    <AlertDialogHeader>
                                      <AlertDialogTitle>Excluir Nota</AlertDialogTitle>
                                      <AlertDialogDescription>
                                        Tem certeza que deseja excluir esta nota? Esta ação não pode ser desfeita.
                                      </AlertDialogDescription>
                                    </AlertDialogHeader>
                                    <AlertDialogFooter>
                                      <AlertDialogCancel>Cancelar</AlertDialogCancel>
                                      <AlertDialogAction
                                        onClick={async () => {
                                          const response = await api.excluirNota(nota.id);
                                          if (response.success) {
                                            toast({
                                              title: 'Sucesso',
                                              description: 'Nota excluída com sucesso!',
                                            });
                                            const res = await api.getNotas();
                                            if (res.success) setNotas(res.data);
                                          }
                                        }}
                                        className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                                      >
                                        Excluir
                                      </AlertDialogAction>
                                    </AlertDialogFooter>
                                  </AlertDialogContent>
                                </AlertDialog>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div className="text-center py-12 bg-card rounded-xl border border-border">
            <BookOpen className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground">Nenhuma nota encontrada.</p>
          </div>
        )}
      </div>
    </MainLayout>
  );
}

