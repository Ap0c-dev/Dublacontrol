import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MainLayout } from '@/components/layout/MainLayout';
import { api, Professor } from '@/lib/api';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Loader2, GraduationCap, Mail, Plus, Pencil, Trash2 } from 'lucide-react';
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

export default function Professores() {
  const [professores, setProfessores] = useState<Professor[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { toast } = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProfessores = async () => {
      try {
        const response = await api.getProfessores();
        if (response.success) {
          setProfessores(response.data);
        } else {
          toast({
            title: 'Erro ao carregar professores',
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

    fetchProfessores();
  }, [toast]);

  const getStatusBadge = (status: string) => {
    const isAtivo = status.toLowerCase() === 'ativo';
    return (
      <Badge 
        variant={isAtivo ? 'default' : 'secondary'}
        className={cn(
          isAtivo && 'bg-success/10 text-success border-success/20 hover:bg-success/20'
        )}
      >
        {isAtivo ? 'Ativo' : 'Inativo'}
      </Badge>
    );
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 animate-fade-in">
          <div>
            <h1 className="text-2xl lg:text-3xl font-bold text-foreground">Professores</h1>
            <p className="text-muted-foreground mt-1">
              Quadro de professores da instituição
            </p>
          </div>
          <Button onClick={() => navigate('/professores/novo')}>
            <Plus size={18} className="mr-2" />
            Novo Professor
          </Button>
        </div>

        {/* Cards Grid */}
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
          </div>
        ) : professores.length > 0 ? (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {professores.map((professor, index) => (
              <div
                key={professor.id}
                className="bg-card rounded-xl border border-border p-6 shadow-card hover:shadow-card-hover transition-all duration-300 animate-slide-up"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
                    <span className="text-lg font-semibold text-primary">
                      {professor.nome?.charAt(0).toUpperCase() || 'P'}
                    </span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-2 mb-2">
                      <h3 className="font-semibold text-foreground truncate">
                        {professor.nome}
                      </h3>
                      {getStatusBadge(professor.status)}
                    </div>
                    <div className="space-y-2">
                      {professor.especialidade && (
                        <p className="text-sm text-primary font-medium">
                          {professor.especialidade}
                        </p>
                      )}
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Mail size={14} />
                        <span className="truncate">{professor.email}</span>
                      </div>
                    </div>
                    <div className="flex gap-2 mt-4">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => navigate(`/professores/${professor.id}/editar`)}
                      >
                        <Pencil size={16} className="mr-1" />
                        Editar
                      </Button>
                      <AlertDialog>
                        <AlertDialogTrigger asChild>
                          <Button variant="outline" size="sm">
                            <Trash2 size={16} className="mr-1 text-destructive" />
                            Excluir
                          </Button>
                        </AlertDialogTrigger>
                        <AlertDialogContent>
                          <AlertDialogHeader>
                            <AlertDialogTitle>Excluir Professor</AlertDialogTitle>
                            <AlertDialogDescription>
                              Tem certeza que deseja excluir este professor? Esta ação não pode ser desfeita.
                            </AlertDialogDescription>
                          </AlertDialogHeader>
                          <AlertDialogFooter>
                            <AlertDialogCancel>Cancelar</AlertDialogCancel>
                            <AlertDialogAction
                              onClick={async () => {
                                const response = await api.excluirProfessor(professor.id);
                                if (response.success) {
                                  toast({
                                    title: 'Sucesso',
                                    description: 'Professor excluído com sucesso!',
                                  });
                                  const res = await api.getProfessores();
                                  if (res.success) setProfessores(res.data);
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
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12 bg-card rounded-xl border border-border">
            <GraduationCap className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground">Nenhum professor cadastrado.</p>
          </div>
        )}
      </div>
    </MainLayout>
  );
}
