import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MainLayout } from '@/components/layout/MainLayout';
import { api, Aluno, Professor } from '@/lib/api';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Search, Loader2, Users, Mail, Phone, Eye, Plus, GraduationCap, Pencil, Upload, Download, Clock } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { cn } from '@/lib/utils';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

export default function Alunos() {
  const [alunos, setAlunos] = useState<Aluno[]>([]);
  const [professores, setProfessores] = useState<Professor[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filterProfessor, setFilterProfessor] = useState<string>('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'ativo' | 'inativo'>('ativo');
  const { toast } = useToast();
  const navigate = useNavigate();

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
    const fetchAlunos = async () => {
      try {
        const filters: any = {};
        if (search) {
          filters.search = search;
        }
        if (filterProfessor) {
          filters.professor_id = filterProfessor;
        }
        if (filterStatus === 'ativo') {
          filters.ativo = true;
        } else if (filterStatus === 'inativo') {
          filters.ativo = false;
        }
        // Se filterStatus === 'all', não adiciona filtro de ativo
        
        const response = await api.getAlunos(filters);
        if (response.success) {
          setAlunos(response.data);
        } else {
          toast({
            title: 'Erro ao carregar alunos',
            description: 'Não foi possível obter a lista de alunos.',
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

    const debounce = setTimeout(fetchAlunos, 300);
    return () => clearTimeout(debounce);
  }, [search, filterProfessor, filterStatus, toast]);

  const handleExportarExcel = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        toast({
          title: 'Erro',
          description: 'Você precisa estar autenticado para exportar.',
          variant: 'destructive',
        });
        return;
      }

      // Construir URL com filtros atuais
      const params = new URLSearchParams();
      if (search) params.append('search', search);
      if (filterProfessor) params.append('professor_id', filterProfessor);
      if (filterStatus === 'ativo') {
        params.append('ativo', 'true');
      } else if (filterStatus === 'inativo') {
        params.append('ativo', 'false');
      }
      // Se filterStatus === 'all', não adiciona parâmetro ativo

      const rawUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api/v1';
      const API_BASE_URL = rawUrl.endsWith('/') ? rawUrl.slice(0, -1) : rawUrl;
      const url = `${API_BASE_URL}/alunos/exportar${params.toString() ? `?${params}` : ''}`;

      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          toast({
            title: 'Erro de autenticação',
            description: 'Sua sessão expirou. Por favor, faça login novamente.',
            variant: 'destructive',
          });
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          navigate('/login');
          return;
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Obter o blob do arquivo
      const blob = await response.blob();
      
      // Criar link de download
      const url_blob = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url_blob;
      
      // Obter nome do arquivo do header Content-Disposition ou usar padrão
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = 'alunos_export.xlsx';
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/['"]/g, '');
        }
      }
      
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url_blob);

      toast({
        title: 'Sucesso',
        description: 'Arquivo Excel exportado com sucesso!',
      });
    } catch (error) {
      console.error('Erro ao exportar alunos:', error);
      toast({
        title: 'Erro ao exportar',
        description: 'Não foi possível exportar o arquivo Excel.',
        variant: 'destructive',
      });
    }
  };

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { label: string; variant: 'default' | 'secondary' | 'destructive' | 'outline' }> = {
      ativo: { label: 'Ativo', variant: 'default' },
      inativo: { label: 'Inativo', variant: 'secondary' },
      pendente: { label: 'Pendente', variant: 'outline' },
    };

    const config = statusMap[status.toLowerCase()] || { label: status, variant: 'secondary' };
    
    return (
      <Badge 
        variant={config.variant}
        className={cn(
          status.toLowerCase() === 'ativo' && 'bg-success/10 text-success border-success/20 hover:bg-success/20'
        )}
      >
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
            <h1 className="text-2xl lg:text-3xl font-bold text-foreground">Alunos</h1>
            <p className="text-muted-foreground mt-1">
              Gerencie os alunos cadastrados
            </p>
          </div>
          <div className="flex gap-2">
            <Button onClick={() => navigate('/alunos/novo')}>
              <Plus size={18} className="mr-2" />
              Novo Aluno
            </Button>
            <Button variant="outline" onClick={() => navigate('/alunos/importar')}>
              <Upload size={18} className="mr-2" />
              Importar Excel
            </Button>
            <Button variant="outline" onClick={() => navigate('/alunos/lista-espera')}>
              <Clock size={18} className="mr-2" />
              Lista de Espera
            </Button>
            <Button 
              variant="outline" 
              onClick={handleExportarExcel}
              disabled={isLoading || alunos.length === 0}
            >
              <Download size={18} className="mr-2" />
              Exportar Excel
            </Button>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="flex flex-col sm:flex-row gap-4 animate-fade-in">
          <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={18} />
          <Input
              placeholder="Buscar por nome ou telefone..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
          </div>
          <div className="w-full sm:w-[250px]">
            <Select
              value={filterProfessor || 'all'}
              onValueChange={(value) => setFilterProfessor(value === 'all' ? '' : value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Filtrar por professor" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos os professores</SelectItem>
                {professores
                  .filter(p => p.ativo)
                  .map((professor) => (
                    <SelectItem key={professor.id} value={professor.id.toString()}>
                      {professor.nome}
                    </SelectItem>
                  ))}
              </SelectContent>
            </Select>
          </div>
          <div className="w-full sm:w-[200px]">
            <Select
              value={filterStatus}
              onValueChange={(value) => setFilterStatus(value as 'all' | 'ativo' | 'inativo')}
            >
              <SelectTrigger>
                <SelectValue placeholder="Filtrar por status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ativo">Alunos Ativos</SelectItem>
                <SelectItem value="inativo">Alunos Inativos</SelectItem>
                <SelectItem value="all">Todos</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Table */}
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
          </div>
        ) : alunos.length > 0 ? (
          <div className="bg-card rounded-xl border border-border shadow-card overflow-hidden animate-slide-up">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-muted/50">
                  <tr>
                    <th className="text-left text-sm font-medium text-muted-foreground px-6 py-4">
                      Aluno
                    </th>
                    <th className="text-left text-sm font-medium text-muted-foreground px-6 py-4 hidden md:table-cell">
                      Contato
                    </th>
                    <th className="text-left text-sm font-medium text-muted-foreground px-6 py-4 hidden lg:table-cell">
                      Data de Início
                    </th>
                    <th className="text-left text-sm font-medium text-muted-foreground px-6 py-4">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {alunos.map((aluno, index) => (
                    <tr 
                      key={aluno.id} 
                      className="hover:bg-muted/30 transition-colors"
                      style={{ animationDelay: `${index * 50}ms` }}
                    >
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                            <span className="text-sm font-semibold text-primary">
                              {aluno.nome?.charAt(0).toUpperCase() || 'A'}
                            </span>
                          </div>
                          <div>
                            <p className="font-medium text-foreground">{aluno.nome}</p>
                            <p className="text-sm text-muted-foreground md:hidden">{aluno.email}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 hidden md:table-cell">
                        <div className="space-y-1">
                          <div className="flex items-center gap-2 text-sm text-muted-foreground">
                            <Mail size={14} />
                            {aluno.email}
                          </div>
                          {aluno.telefone && (
                            <div className="flex items-center gap-2 text-sm text-muted-foreground">
                              <Phone size={14} />
                              {aluno.telefone}
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 hidden lg:table-cell text-sm text-muted-foreground">
                        {aluno.created_at
                          ? new Date(aluno.created_at).toLocaleDateString('pt-BR')
                          : '-'}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                        {getStatusBadge(aluno.status)}
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => navigate(`/alunos/${aluno.id}`)}
                            title="Visualizar"
                          >
                            <Eye size={16} />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => navigate(`/alunos/${aluno.id}/editar`)}
                            title="Editar"
                          >
                            <Pencil size={16} />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div className="text-center py-12 bg-card rounded-xl border border-border">
            <Users className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground">Nenhum aluno encontrado.</p>
          </div>
        )}
      </div>
    </MainLayout>
  );
}
