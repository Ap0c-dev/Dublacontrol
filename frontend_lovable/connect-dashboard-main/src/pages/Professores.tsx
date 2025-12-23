import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MainLayout } from '@/components/layout/MainLayout';
import { api, Professor } from '@/lib/api';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Loader2, GraduationCap, Mail, Plus, Pencil, Trash2, Phone, Clock, BookOpen } from 'lucide-react';
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
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';

interface ProfessorDetalhes extends Professor {
  horarios?: Array<{
    id: number;
    dia_semana: string;
    horario_aula: string;
    modalidade: string;
    idade_minima?: number;
    idade_maxima?: number;
  }>;
}

export default function Professores() {
  const [professores, setProfessores] = useState<Professor[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedProfessor, setSelectedProfessor] = useState<ProfessorDetalhes | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isLoadingDetails, setIsLoadingDetails] = useState(false);
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

  const handleCardClick = async (professorId: number) => {
    setIsLoadingDetails(true);
    setIsDialogOpen(true);
    try {
      // Buscar detalhes completos do professor (já inclui horários)
      const professorResponse = await api.getProfessor(professorId);
      if (professorResponse.success) {
        const professorData = professorResponse.data as ProfessorDetalhes;
        // Os horários já vêm na resposta do backend
        setSelectedProfessor(professorData);
      } else {
        toast({
          title: 'Erro',
          description: 'Não foi possível carregar os detalhes do professor.',
          variant: 'destructive',
        });
        setIsDialogOpen(false);
      }
    } catch (error) {
      toast({
        title: 'Erro',
        description: 'Erro ao carregar informações do professor.',
        variant: 'destructive',
      });
      setIsDialogOpen(false);
    } finally {
      setIsLoadingDetails(false);
    }
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
                onClick={() => handleCardClick(professor.id)}
                className="bg-card rounded-xl border border-border p-6 shadow-card hover:shadow-card-hover transition-all duration-300 animate-slide-up cursor-pointer"
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
                    <div className="flex gap-2 mt-4" onClick={(e) => e.stopPropagation()}>
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

        {/* Modal de Detalhes do Professor */}
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            {isLoadingDetails ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-primary" />
              </div>
            ) : selectedProfessor ? (
              <>
                <DialogHeader>
                  <DialogTitle className="text-2xl flex items-center gap-3">
                    <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
                      <span className="text-lg font-semibold text-primary">
                        {selectedProfessor.nome?.charAt(0).toUpperCase() || 'P'}
                      </span>
                    </div>
                    {selectedProfessor.nome}
                  </DialogTitle>
                  <DialogDescription>
                    Informações completas do professor
                  </DialogDescription>
                </DialogHeader>

                <div className="space-y-6 mt-4">
                  {/* Status e Especialidade */}
                  <div className="flex items-center gap-4">
                    {getStatusBadge(selectedProfessor.status)}
                    {selectedProfessor.especialidade && (
                      <Badge variant="outline" className="text-primary border-primary/20">
                        {selectedProfessor.especialidade}
                      </Badge>
                    )}
                  </div>

                  {/* Informações de Contato */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {selectedProfessor.telefone && (
                      <div className="flex items-center gap-2 text-sm">
                        <Phone size={16} className="text-muted-foreground" />
                        <span className="text-foreground">{selectedProfessor.telefone}</span>
                      </div>
                    )}
                    {selectedProfessor.email && (
                      <div className="flex items-center gap-2 text-sm">
                        <Mail size={16} className="text-muted-foreground" />
                        <span className="text-foreground">{selectedProfessor.email}</span>
                      </div>
                    )}
                  </div>

                  {/* Modalidades */}
                  {(selectedProfessor as any).dublagem_online || (selectedProfessor as any).dublagem_presencial || 
                   (selectedProfessor as any).teatro_online || (selectedProfessor as any).teatro_presencial ||
                   (selectedProfessor as any).locucao || (selectedProfessor as any).musical ||
                   (selectedProfessor as any).teatro_tv_cinema || (selectedProfessor as any).curso_apresentador ? (
                    <div>
                      <h3 className="font-semibold text-foreground mb-3 flex items-center gap-2">
                        <BookOpen size={18} />
                        Modalidades
                      </h3>
                      <div className="flex flex-wrap gap-2">
                        {(selectedProfessor as any).dublagem_online && (
                          <Badge variant="outline">Dublagem Online</Badge>
                        )}
                        {(selectedProfessor as any).dublagem_presencial && (
                          <Badge variant="outline">Dublagem Presencial</Badge>
                        )}
                        {(selectedProfessor as any).teatro_online && (
                          <Badge variant="outline">Teatro Online</Badge>
                        )}
                        {(selectedProfessor as any).teatro_presencial && (
                          <Badge variant="outline">Teatro Presencial</Badge>
                        )}
                        {(selectedProfessor as any).teatro_tv_cinema && (
                          <Badge variant="outline">Teatro TV/Cinema</Badge>
                        )}
                        {(selectedProfessor as any).locucao && (
                          <Badge variant="outline">Locução</Badge>
                        )}
                        {(selectedProfessor as any).musical && (
                          <Badge variant="outline">Musical</Badge>
                        )}
                        {(selectedProfessor as any).curso_apresentador && (
                          <Badge variant="outline">Curso Apresentador</Badge>
                        )}
                      </div>
                    </div>
                  ) : null}

                  {/* Horários */}
                  {(selectedProfessor as any).horarios && Array.isArray((selectedProfessor as any).horarios) && (selectedProfessor as any).horarios.length > 0 && (
                    <div>
                      <h3 className="font-semibold text-foreground mb-3 flex items-center gap-2">
                        <Clock size={18} />
                        Horários de Aula
                      </h3>
                      <div className="space-y-2">
                        {(selectedProfessor as any).horarios.map((horario: any, idx: number) => (
                          <div
                            key={horario.id || idx}
                            className="bg-muted/50 rounded-lg p-3 border border-border"
                          >
                            <div className="flex items-center justify-between">
                              <div>
                                <p className="font-medium text-foreground">{horario.dia_semana || 'N/A'}</p>
                                <p className="text-sm text-muted-foreground">{horario.horario_aula || 'N/A'}</p>
                              </div>
                              <div className="text-right">
                                {horario.modalidade && (
                                  <Badge variant="secondary">{horario.modalidade}</Badge>
                                )}
                                {(horario.idade_minima || horario.idade_maxima) && (
                                  <p className="text-xs text-muted-foreground mt-1">
                                    {horario.idade_minima && horario.idade_maxima
                                      ? `${horario.idade_minima}-${horario.idade_maxima} anos`
                                      : horario.idade_minima
                                      ? `A partir de ${horario.idade_minima} anos`
                                      : `Até ${horario.idade_maxima} anos`}
                                  </p>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {/* Mensagem quando não há horários */}
                  {(!(selectedProfessor as any).horarios || (selectedProfessor as any).horarios.length === 0) && (
                    <div className="text-center py-4 text-muted-foreground text-sm">
                      Nenhum horário cadastrado para este professor.
                    </div>
                  )}

                  {/* Botões de Ação */}
                  <div className="flex gap-2 pt-4 border-t border-border">
                    <Button
                      variant="outline"
                      className="flex-1"
                      onClick={() => {
                        setIsDialogOpen(false);
                        navigate(`/professores/${selectedProfessor.id}/editar`);
                      }}
                    >
                      <Pencil size={16} className="mr-2" />
                      Editar Professor
                    </Button>
                  </div>
                </div>
              </>
            ) : null}
          </DialogContent>
        </Dialog>
      </div>
    </MainLayout>
  );
}
