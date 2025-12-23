import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { MainLayout } from '@/components/layout/MainLayout';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Loader2, ArrowLeft, Save, Plus, Trash2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { capitalizarNome, gerarUsernameVoxen } from '@/lib/utils';

interface Horario {
  id?: number;
  dia_semana: string;
  modalidade: string;
  horario_inicio: string;
  horario_termino: string;
  idade_minima: string;
  idade_maxima: string;
}

const DIAS_SEMANA = [
  'Segunda-feira',
  'Terça-feira',
  'Quarta-feira',
  'Quinta-feira',
  'Sexta-feira',
  'Sábado',
  'Domingo',
];

const MODALIDADES = [
  { value: 'dublagem_online', label: 'Dublagem Online' },
  { value: 'dublagem_presencial', label: 'Dublagem Presencial' },
  { value: 'teatro_online', label: 'Teatro Online' },
  { value: 'teatro_presencial', label: 'Teatro Presencial' },
  { value: 'locucao', label: 'Locução' },
  { value: 'teatro_tv_cinema', label: 'Teatro TV/Cinema' },
  { value: 'musical', label: 'Musical' },
  { value: 'curso_apresentador', label: 'Curso Apresentador' },
];

export default function ProfessorForm() {
  const { id } = useParams<{ id?: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingData, setIsLoadingData] = useState(!!id);
  
  const [formData, setFormData] = useState({
    nome: '',
    telefone: '',
    ativo: true,
  });

  const [username, setUsername] = useState('');
  const [senhaUsuario, setSenhaUsuario] = useState('');

  const [horarios, setHorarios] = useState<Horario[]>([
    {
      dia_semana: '',
      modalidade: '',
      horario_inicio: '',
      horario_termino: '',
      idade_minima: '',
      idade_maxima: '',
    },
  ]);

  useEffect(() => {
    if (id) {
      const fetchProfessor = async () => {
        setIsLoadingData(true);
        try {
          const response = await api.getProfessor(parseInt(id));
          if (response.success) {
            const professor = response.data;
            setFormData({
              nome: professor.nome || '',
              telefone: professor.telefone || '',
              ativo: professor.ativo ?? true,
            });

            // Carregar horários do professor
            if (professor.horarios && professor.horarios.length > 0) {
              const horariosFormatados = professor.horarios.map((h: any) => {
                // Extrair horário início e término do formato "HH:MM às HH:MM"
                const horarioParts = h.horario_aula?.split(' às ') || ['', ''];
                return {
                  id: h.id,
                  dia_semana: h.dia_semana || '',
                  modalidade: h.modalidade || '',
                  horario_inicio: horarioParts[0] || '',
                  horario_termino: horarioParts[1] || '',
                  idade_minima: h.idade_minima?.toString() || '',
                  idade_maxima: h.idade_maxima?.toString() || '',
                };
              });
              setHorarios(horariosFormatados);
            } else {
              // Se não houver horários, manter um horário vazio
              setHorarios([
                {
                  dia_semana: '',
                  modalidade: '',
                  horario_inicio: '',
                  horario_termino: '',
                  idade_minima: '',
                  idade_maxima: '',
                },
              ]);
            }
          }
        } catch (error) {
          toast({
            title: 'Erro',
            description: 'Erro ao carregar dados do professor',
            variant: 'destructive',
          });
        } finally {
          setIsLoadingData(false);
        }
      };
      fetchProfessor();
    }
  }, [id, toast]);

  const adicionarHorario = () => {
    setHorarios([
      ...horarios,
      {
        dia_semana: '',
        modalidade: '',
        horario_inicio: '',
        horario_termino: '',
        idade_minima: '',
        idade_maxima: '',
      },
    ]);
  };

  const removerHorario = (index: number) => {
    if (horarios.length > 1) {
      setHorarios(horarios.filter((_, i) => i !== index));
    } else {
      toast({
        title: 'Atenção',
        description: 'É necessário ter pelo menos um horário',
        variant: 'destructive',
      });
    }
  };

  const atualizarHorario = (index: number, campo: keyof Horario, valor: string) => {
    const novosHorarios = [...horarios];
    novosHorarios[index] = { ...novosHorarios[index], [campo]: valor };
    setHorarios(novosHorarios);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      // Validar senha se estiver criando novo professor
      if (!id && senhaUsuario && senhaUsuario.length < 6) {
        toast({
          title: 'Erro',
          description: 'A senha deve ter pelo menos 6 caracteres',
          variant: 'destructive',
        });
        setIsLoading(false);
        return;
      }

      // Validar horários
      const horariosValidos = horarios.filter(
        (h) => h.dia_semana && h.modalidade && h.horario_inicio && h.horario_termino
      );

      if (horariosValidos.length === 0) {
        toast({
          title: 'Erro',
          description: 'Adicione pelo menos um horário completo (dia, modalidade e horários)',
          variant: 'destructive',
        });
        setIsLoading(false);
        return;
      }

      const data = {
        nome: formData.nome,
        telefone: formData.telefone,
        ativo: formData.ativo,
        senha_usuario: senhaUsuario || 'voxen123',
        horarios: horariosValidos.map((h) => ({
          dia_semana: h.dia_semana,
          modalidade: h.modalidade,
          horario_inicio: h.horario_inicio,
          horario_termino: h.horario_termino,
          idade_minima: h.idade_minima ? parseInt(h.idade_minima) : null,
          idade_maxima: h.idade_maxima ? parseInt(h.idade_maxima) : null,
        })),
      };

      let response;
      if (id) {
        response = await api.editarProfessor(parseInt(id), data);
      } else {
        response = await api.criarProfessor(data);
      }

      if (response.success) {
        toast({
          title: 'Sucesso',
          description: id ? 'Professor atualizado com sucesso!' : 'Professor criado com sucesso!',
        });
        navigate('/professores');
      } else {
        toast({
          title: 'Erro',
          description: response.error || 'Erro ao salvar professor',
          variant: 'destructive',
        });
      }
    } catch (error) {
      toast({
        title: 'Erro',
        description: 'Erro ao salvar professor',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoadingData) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => navigate('/professores')}>
            <ArrowLeft size={18} className="mr-2" />
            Voltar
          </Button>
          <h1 className="text-2xl lg:text-3xl font-bold text-foreground">
            {id ? 'Editar Professor' : 'Novo Professor'}
          </h1>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Informações Básicas</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <Label>Nome *</Label>
                  <Input
                    value={formData.nome}
                    onChange={(e) => {
                      const nomeCapitalizado = capitalizarNome(e.target.value);
                      setFormData({ ...formData, nome: nomeCapitalizado });
                      // Gerar username automaticamente
                      if (!id) { // Só gerar username ao criar novo professor
                        const novoUsername = gerarUsernameVoxen(nomeCapitalizado);
                        setUsername(novoUsername);
                      }
                    }}
                    required
                  />
                </div>
                <div>
                  <Label>Telefone *</Label>
                  <Input
                    value={formData.telefone}
                    onChange={(e) => setFormData({ ...formData, telefone: e.target.value })}
                    required
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {!id && (
            <Card>
              <CardHeader>
                <CardTitle>Credenciais de Acesso</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <Label>Username *</Label>
                    <Input
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      placeholder="Será gerado automaticamente"
                      required
                      disabled={!formData.nome}
                    />
                    <p className="text-xs text-muted-foreground mt-1">
                      Username gerado automaticamente baseado no nome
                    </p>
                  </div>
                  <div>
                    <Label>Senha *</Label>
                    <Input
                      type="password"
                      value={senhaUsuario}
                      onChange={(e) => setSenhaUsuario(e.target.value)}
                      placeholder="Mínimo 6 caracteres"
                      required
                      minLength={6}
                    />
                    <p className="text-xs text-muted-foreground mt-1">
                      Senha padrão: voxen123 (se não preenchida)
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Horários e Modalidades *</CardTitle>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={adicionarHorario}
              >
                <Plus size={16} className="mr-2" />
                Adicionar Horário
              </Button>
            </CardHeader>
            <CardContent className="space-y-4">
              {horarios.map((horario, index) => (
                <div
                  key={index}
                  className="p-4 border rounded-lg space-y-4 bg-card"
                >
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-sm text-muted-foreground">
                      Horário {index + 1}
                    </h4>
                    {horarios.length > 1 && (
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => removerHorario(index)}
                        className="text-destructive hover:text-destructive"
                      >
                        <Trash2 size={16} />
                      </Button>
                    )}
                  </div>

                  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                    <div>
                      <Label>Dia da Semana *</Label>
                      <Select
                        value={horario.dia_semana}
                        onValueChange={(value) =>
                          atualizarHorario(index, 'dia_semana', value)
                        }
                        required
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Selecione o dia" />
                        </SelectTrigger>
                        <SelectContent>
                          {DIAS_SEMANA.map((dia) => (
                            <SelectItem key={dia} value={dia}>
                              {dia}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <Label>Modalidade *</Label>
                      <Select
                        value={horario.modalidade}
                        onValueChange={(value) =>
                          atualizarHorario(index, 'modalidade', value)
                        }
                        required
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Selecione a modalidade" />
                        </SelectTrigger>
                        <SelectContent>
                          {MODALIDADES.map((mod) => (
                            <SelectItem key={mod.value} value={mod.value}>
                              {mod.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <Label>Horário Início *</Label>
                      <Input
                        type="time"
                        value={horario.horario_inicio}
                        onChange={(e) =>
                          atualizarHorario(index, 'horario_inicio', e.target.value)
                        }
                        required
                      />
                    </div>

                    <div>
                      <Label>Horário Término *</Label>
                      <Input
                        type="time"
                        value={horario.horario_termino}
                        onChange={(e) =>
                          atualizarHorario(index, 'horario_termino', e.target.value)
                        }
                        required
                      />
                    </div>

                    <div>
                      <Label>Idade Mínima</Label>
                      <Input
                        type="number"
                        min="0"
                        value={horario.idade_minima}
                        onChange={(e) =>
                          atualizarHorario(index, 'idade_minima', e.target.value)
                        }
                        placeholder="Ex: 8"
                      />
                    </div>

                    <div>
                      <Label>Idade Máxima</Label>
                      <Input
                        type="number"
                        min="0"
                        value={horario.idade_maxima}
                        onChange={(e) =>
                          atualizarHorario(index, 'idade_maxima', e.target.value)
                        }
                        placeholder="Ex: 15"
                      />
                    </div>
                  </div>
                </div>
              ))}

              <p className="text-sm text-muted-foreground">
                * As modalidades do professor serão definidas automaticamente com base nos horários cadastrados.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="ativo"
                  checked={formData.ativo}
                  onCheckedChange={(checked) =>
                    setFormData({ ...formData, ativo: checked as boolean })
                  }
                />
                <Label htmlFor="ativo" className="cursor-pointer">Ativo</Label>
              </div>
            </CardContent>
          </Card>

          <div className="flex justify-end gap-4">
            <Button type="button" variant="outline" onClick={() => navigate('/professores')}>
              Cancelar
            </Button>
            <Button type="submit" disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Salvando...
                </>
              ) : (
                <>
                  <Save className="mr-2 h-4 w-4" />
                  Salvar
                </>
              )}
            </Button>
          </div>
        </form>
      </div>
    </MainLayout>
  );
}
