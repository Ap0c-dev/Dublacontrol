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

interface Matricula {
  modalidade: string;
  professor_id: number | null;
  horario_id: number | null;
  valor_mensalidade: string;
  data_inicio: string;
}

const MODALIDADES = [
  { value: 'dublagem_online', label: 'Dublagem Online' },
  { value: 'dublagem_presencial', label: 'Dublagem Presencial' },
  { value: 'teatro_online', label: 'Teatro Online' },
  { value: 'teatro_presencial', label: 'Teatro Presencial' },
  { value: 'locucao', label: 'Locução' },
  { value: 'teatro_tv_cinema', label: 'Teatro TV/Cinema' },
  { value: 'musical', label: 'Musical' },
];

const FORMAS_PAGAMENTO = [
  { value: 'PIX', label: 'PIX' },
  { value: 'Boleto', label: 'Boleto' },
  { value: 'Cartão de Crédito', label: 'Cartão de Crédito' },
  { value: 'Cartão de Débito', label: 'Cartão de Débito' },
  { value: 'Transferência Bancária', label: 'Transferência Bancária' },
  { value: 'Dinheiro', label: 'Dinheiro' },
];

export default function AlunoForm() {
  const { id } = useParams<{ id?: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingData, setIsLoadingData] = useState(!!id);
  
  const [formData, setFormData] = useState({
    nome: '',
    telefone: '',
    telefone_responsavel: '',
    nome_responsavel: '',
    cidade: '',
    estado: '',
    data_nascimento: '',
    forma_pagamento: '',
    data_vencimento: '',
    ativo: true,
    aprovado: true,
    experimental: false,
  });

  const [username, setUsername] = useState('');
  const [senhaUsuario, setSenhaUsuario] = useState('');

  const [matriculas, setMatriculas] = useState<Matricula[]>([
    {
      modalidade: '',
      professor_id: null,
      horario_id: null,
      valor_mensalidade: '',
      data_inicio: '',
    },
  ]);

  const [professoresPorModalidade, setProfessoresPorModalidade] = useState<Record<string, any[]>>({});
  const [horariosPorProfessor, setHorariosPorProfessor] = useState<Record<string, any[]>>({});

  useEffect(() => {
    if (id) {
      const fetchAluno = async () => {
        setIsLoadingData(true);
        try {
          const response = await api.getAluno(parseInt(id));
          if (response.success) {
            const aluno = response.data;
            setFormData({
              nome: aluno.nome || '',
              telefone: aluno.telefone || '',
              telefone_responsavel: aluno.telefone_responsavel || '',
              nome_responsavel: aluno.nome_responsavel || '',
              cidade: aluno.cidade || '',
              estado: aluno.estado || '',
              data_nascimento: aluno.data_nascimento ? aluno.data_nascimento.split('T')[0] : '',
              forma_pagamento: aluno.forma_pagamento || '',
              data_vencimento: aluno.data_vencimento ? aluno.data_vencimento.split('T')[0] : '',
              ativo: aluno.ativo ?? true,
              aprovado: aluno.aprovado ?? true,
              experimental: aluno.experimental || false,
            });

            // Carregar matrículas
            if (aluno.matriculas && aluno.matriculas.length > 0) {
              const matriculasFormatadas = aluno.matriculas.map((m: any) => ({
                modalidade: m.tipo_curso || '',
                professor_id: m.professor_id || null,
                horario_id: null, // Não temos o ID do horário na matrícula, precisamos buscar
                valor_mensalidade: m.valor_mensalidade?.toString() || '',
                data_inicio: m.data_inicio ? m.data_inicio.split('T')[0] : '',
              }));
              setMatriculas(matriculasFormatadas);
              
              // Carregar professores e horários para cada matrícula
              for (const mat of matriculasFormatadas) {
                if (mat.modalidade && mat.professor_id) {
                  await carregarProfessores(mat.modalidade);
                  await carregarHorarios(mat.professor_id, mat.modalidade);
                }
              }
            }
          }
        } catch (error) {
          toast({
            title: 'Erro',
            description: 'Erro ao carregar dados do aluno',
            variant: 'destructive',
          });
        } finally {
          setIsLoadingData(false);
        }
      };
      fetchAluno();
    }
  }, [id, toast]);

  const carregarProfessores = async (modalidade: string) => {
    if (!modalidade) {
      return;
    }
    // Evitar recarregar se já temos os dados
    if (professoresPorModalidade[modalidade]) {
      return;
    }
    try {
      const response = await api.getProfessoresPorModalidade(modalidade);
      if (response.success && response.data) {
        setProfessoresPorModalidade((prev) => ({
          ...prev,
          [modalidade]: response.data,
        }));
      }
    } catch (error) {
      console.error('Erro ao carregar professores:', error);
      toast({
        title: 'Erro',
        description: 'Erro ao carregar professores. Tente novamente.',
        variant: 'destructive',
      });
    }
  };

  const carregarHorarios = async (professorId: number, modalidade: string) => {
    if (!professorId || !modalidade) {
      console.warn('⚠️ carregarHorarios chamado sem professorId ou modalidade:', { professorId, modalidade });
      return;
    }
    const key = `${professorId}_${modalidade}`;
    // Evitar recarregar se já temos os dados
    if (horariosPorProfessor[key]) {
      console.log('✅ Horários já carregados para:', key);
      return;
    }
    try {
      console.log('🔄 Carregando horários para professor:', professorId, 'modalidade:', modalidade);
      const response = await api.getHorariosProfessor(professorId, modalidade);
      console.log('📦 Resposta da API:', response);
      if (response.success && response.data) {
        console.log('✅ Horários carregados:', response.data);
        setHorariosPorProfessor((prev) => ({
          ...prev,
          [key]: response.data,
        }));
      } else {
        console.warn('⚠️ Resposta não teve sucesso ou não tem data:', response);
      }
    } catch (error) {
      console.error('❌ Erro ao carregar horários:', error);
      toast({
        title: 'Erro',
        description: 'Erro ao carregar horários. Tente novamente.',
        variant: 'destructive',
      });
    }
  };

  const adicionarMatricula = () => {
    setMatriculas([
      ...matriculas,
      {
        modalidade: '',
        professor_id: null,
        horario_id: null,
        valor_mensalidade: '',
        data_inicio: '',
      },
    ]);
  };

  const removerMatricula = (index: number) => {
    if (matriculas.length > 1) {
      setMatriculas(matriculas.filter((_, i) => i !== index));
    } else {
      toast({
        title: 'Atenção',
        description: 'É necessário ter pelo menos uma matrícula',
        variant: 'destructive',
      });
    }
  };

  const atualizarMatricula = async (index: number, campo: keyof Matricula, valor: any) => {
    const novasMatriculas = [...matriculas];
    novasMatriculas[index] = { ...novasMatriculas[index], [campo]: valor };
    
    // Se mudou a modalidade, limpar professor e horário
    if (campo === 'modalidade') {
      novasMatriculas[index].professor_id = null;
      novasMatriculas[index].horario_id = null;
      if (valor) {
        await carregarProfessores(valor);
      }
    }
    
    // Se mudou o professor, limpar horário e carregar novos horários
    if (campo === 'professor_id') {
      novasMatriculas[index].horario_id = null;
      const modalidade = novasMatriculas[index].modalidade;
      if (valor && modalidade) {
        await carregarHorarios(valor, modalidade);
      }
    }
    
    setMatriculas(novasMatriculas);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      // Validar data de vencimento
      if (formData.data_vencimento) {
        const hoje = new Date();
        hoje.setHours(0, 0, 0, 0);
        const dataVencimento = new Date(formData.data_vencimento);
        const dataMaxima = new Date(hoje);
        dataMaxima.setDate(dataMaxima.getDate() + 35);
        
        if (dataVencimento < hoje) {
          toast({
            title: 'Erro',
            description: 'A data de vencimento não pode ser no passado.',
            variant: 'destructive',
          });
          setIsLoading(false);
          return;
        }
        if (dataVencimento > dataMaxima) {
          toast({
            title: 'Erro',
            description: 'A data de vencimento não pode ser mais de 35 dias à frente.',
            variant: 'destructive',
          });
          setIsLoading(false);
          return;
        }
      }

      // Validar senha se estiver criando novo aluno
      if (!id && senhaUsuario && senhaUsuario.length < 6) {
        toast({
          title: 'Erro',
          description: 'A senha deve ter pelo menos 6 caracteres',
          variant: 'destructive',
        });
        setIsLoading(false);
        return;
      }

      // Validar matrículas
      const matriculasValidas = matriculas.filter(
        (m) => m.modalidade && m.professor_id && m.horario_id && m.valor_mensalidade
      );

      if (matriculasValidas.length === 0) {
        toast({
          title: 'Erro',
          description: 'Adicione pelo menos uma matrícula completa (modalidade, professor, horário e valor da mensalidade)',
          variant: 'destructive',
        });
        setIsLoading(false);
        return;
      }
      
      // Validar se todas as matrículas têm valor da mensalidade
      const matriculasSemValor = matriculas.filter(
        (m) => m.modalidade && m.professor_id && m.horario_id && !m.valor_mensalidade
      );
      
      if (matriculasSemValor.length > 0) {
        toast({
          title: 'Erro',
          description: 'Todas as matrículas devem ter um valor de mensalidade preenchido',
          variant: 'destructive',
        });
        setIsLoading(false);
        return;
      }

      const data = {
        nome: formData.nome,
        telefone: formData.telefone,
        telefone_responsavel: formData.telefone_responsavel || null,
        nome_responsavel: formData.nome_responsavel || null,
        cidade: formData.cidade,
        estado: formData.estado,
        data_nascimento: formData.data_nascimento || null,
        forma_pagamento: formData.forma_pagamento,
        data_vencimento: formData.data_vencimento,
        ativo: formData.ativo,
        aprovado: formData.aprovado,
        experimental: formData.experimental,
        senha_usuario: senhaUsuario || '', // Backend gerará senha aleatória se vazio
        matriculas: matriculasValidas.map((m) => {
          // Converter valor_mensalidade para número, tratando strings vazias
          let valor_mensalidade = null;
          if (m.valor_mensalidade && m.valor_mensalidade.toString().trim() !== '') {
            const valor = parseFloat(m.valor_mensalidade.toString().replace(',', '.'));
            if (!isNaN(valor) && valor > 0) {
              valor_mensalidade = valor;
            }
          }
          
          return {
            modalidade: m.modalidade,
            professor_id: m.professor_id,
            horario_id: m.horario_id,
            valor_mensalidade: valor_mensalidade,
            data_inicio: m.data_inicio || null,
          };
        }),
      };

      let response;
      if (id) {
        response = await api.editarAluno(parseInt(id), data);
      } else {
        response = await api.criarAluno(data);
      }

      if (response.success) {
        toast({
          title: 'Sucesso',
          description: id ? 'Aluno atualizado com sucesso!' : 'Aluno criado com sucesso!',
        });
        navigate('/alunos');
      } else {
        toast({
          title: 'Erro',
          description: response.error || 'Erro ao salvar aluno',
          variant: 'destructive',
        });
      }
    } catch (error) {
      toast({
        title: 'Erro',
        description: 'Erro ao salvar aluno',
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
          <Button variant="ghost" onClick={() => navigate('/alunos')}>
            <ArrowLeft size={18} className="mr-2" />
            Voltar
          </Button>
          <h1 className="text-2xl lg:text-3xl font-bold text-foreground">
            {id ? 'Editar Aluno' : 'Novo Aluno'}
          </h1>
        </div>

        <form 
          onSubmit={handleSubmit} 
          className="space-y-6"
          onKeyDown={(e) => {
            // Prevenir submit ao pressionar Enter em campos que não são o botão submit
            if (e.key === 'Enter' && e.target instanceof HTMLInputElement && e.target.type !== 'submit') {
              e.preventDefault();
            }
          }}
        >
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
                      if (!id) { // Só gerar username ao criar novo aluno
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
                <div>
                  <Label>Telefone do Responsável</Label>
                  <Input
                    value={formData.telefone_responsavel}
                    onChange={(e) => setFormData({ ...formData, telefone_responsavel: e.target.value })}
                  />
                </div>
                <div>
                  <Label>Nome do Responsável</Label>
                  <Input
                    value={formData.nome_responsavel}
                    onChange={(e) => setFormData({ ...formData, nome_responsavel: capitalizarNome(e.target.value) })}
                  />
                </div>
                <div>
                  <Label>Cidade *</Label>
                  <Input
                    value={formData.cidade}
                    onChange={(e) => setFormData({ ...formData, cidade: capitalizarNome(e.target.value) })}
                    required
                  />
                </div>
                <div>
                  <Label>Estado *</Label>
                  <Input
                    value={formData.estado}
                    onChange={(e) => setFormData({ ...formData, estado: e.target.value.toUpperCase() })}
                    maxLength={2}
                    required
                  />
                </div>
                <div>
                  <Label>Data de Nascimento</Label>
                  <Input
                    type="date"
                    value={formData.data_nascimento}
                    onChange={(e) => setFormData({ ...formData, data_nascimento: e.target.value })}
                  />
                </div>
                <div>
                  <Label>Forma de Pagamento *</Label>
                  <Select
                    value={formData.forma_pagamento}
                    onValueChange={(value) =>
                      setFormData({ ...formData, forma_pagamento: value })
                    }
                    required
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione a forma de pagamento" />
                    </SelectTrigger>
                    <SelectContent>
                      {FORMAS_PAGAMENTO.map((forma) => (
                        <SelectItem key={forma.value} value={forma.value}>
                          {forma.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  
                  {/* Exibir informações de pagamento quando PIX ou Transferência Bancária for selecionado */}
                  {(formData.forma_pagamento === 'PIX' || formData.forma_pagamento === 'Transferência Bancária') && (
                    <div className="mt-3 p-4 bg-muted/50 rounded-lg border border-border">
                      {formData.forma_pagamento === 'PIX' && (
                        <div className="space-y-2">
                          <h4 className="font-semibold text-sm text-foreground">Dados para PIX:</h4>
                          <div className="text-sm space-y-1">
                            <div>
                              <strong>Chave PIX:</strong> 12.624.494/0001-64
                            </div>
                            <div>
                              <strong>Beneficiário:</strong> OFICINA DE ATORES CURSO DE PREPARAÇÃO EM ARTES CENICAS
                            </div>
                          </div>
                        </div>
                      )}
                      
                      {formData.forma_pagamento === 'Transferência Bancária' && (
                        <div className="space-y-2">
                          <h4 className="font-semibold text-sm text-foreground">Dados para Transferência:</h4>
                          <div className="text-sm space-y-1">
                            <div>
                              <strong>Banco:</strong> ITAÚ
                            </div>
                            <div>
                              <strong>Agência:</strong> 0308
                            </div>
                            <div>
                              <strong>Conta Corrente:</strong> 98743-7
                            </div>
                            <div>
                              <strong>Titular:</strong> OFICINA DE ATORES CURSO DE PREPARAÇÃO EM ARTES CENICAS
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
                <div>
                  <Label>Data de Vencimento *</Label>
                  <Input
                    type="date"
                    value={formData.data_vencimento}
                    onChange={(e) => {
                      // Apenas atualizar o valor, sem validar durante a digitação
                      setFormData({ ...formData, data_vencimento: e.target.value });
                    }}
                    onBlur={(e) => {
                      // Validar apenas quando o campo perder o foco (data completa)
                      const dataSelecionada = e.target.value;
                      if (dataSelecionada) {
                        const hoje = new Date();
                        hoje.setHours(0, 0, 0, 0);
                        const dataVencimento = new Date(dataSelecionada);
                        const dataMaxima = new Date(hoje);
                        dataMaxima.setDate(dataMaxima.getDate() + 35);
                        
                        if (dataVencimento < hoje) {
                          toast({
                            title: 'Data inválida',
                            description: 'A data de vencimento não pode ser no passado.',
                            variant: 'destructive',
                          });
                          // Limpar o campo se a data for inválida
                          setFormData({ ...formData, data_vencimento: '' });
                          return;
                        }
                        if (dataVencimento > dataMaxima) {
                          toast({
                            title: 'Data inválida',
                            description: 'A data de vencimento não pode ser mais de 35 dias à frente.',
                            variant: 'destructive',
                          });
                          // Limpar o campo se a data for inválida
                          setFormData({ ...formData, data_vencimento: '' });
                          return;
                        }
                      }
                    }}
                    min={new Date().toISOString().split('T')[0]}
                    max={new Date(Date.now() + 35 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]}
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
                      Senha será gerada automaticamente se não preenchida
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Matrículas *</CardTitle>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={adicionarMatricula}
              >
                <Plus size={16} className="mr-2" />
                Adicionar Matrícula
              </Button>
            </CardHeader>
            <CardContent className="space-y-4">
              {matriculas.map((matricula, index) => {
                const professores = professoresPorModalidade[matricula.modalidade] || [];
                const horariosKey = matricula.professor_id && matricula.modalidade
                  ? `${matricula.professor_id}_${matricula.modalidade}`
                  : '';
                const horarios = horariosPorProfessor[horariosKey] || [];
                
                // Debug
                if (matricula.professor_id && matricula.modalidade) {
                  console.log(`🔍 Matrícula ${index + 1} - Chave horários:`, horariosKey);
                  console.log(`🔍 Horários disponíveis:`, horarios);
                  console.log(`🔍 Estado horariosPorProfessor:`, Object.keys(horariosPorProfessor));
                }

                return (
                  <div
                    key={index}
                    className="p-4 border rounded-lg space-y-4 bg-card"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-sm text-muted-foreground">
                        Matrícula {index + 1}
                      </h4>
                      {matriculas.length > 1 && (
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => removerMatricula(index)}
                          className="text-destructive hover:text-destructive"
                        >
                          <Trash2 size={16} />
                        </Button>
                      )}
                    </div>

                    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                      <div>
                        <Label>Modalidade *</Label>
                        <Select
                          value={matricula.modalidade}
                          onValueChange={(value) => {
                            atualizarMatricula(index, 'modalidade', value);
                          }}
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
                        <Label>Professor *</Label>
                        <Select
                          value={matricula.professor_id?.toString() || ''}
                          onValueChange={(value) =>
                            atualizarMatricula(index, 'professor_id', parseInt(value))
                          }
                          disabled={!matricula.modalidade}
                          required
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Selecione o professor" />
                          </SelectTrigger>
                          <SelectContent>
                            {professores.length === 0 && matricula.modalidade ? (
                              <div className="px-2 py-1.5 text-sm text-muted-foreground">
                                Carregando...
                              </div>
                            ) : professores.length === 0 ? (
                              <div className="px-2 py-1.5 text-sm text-muted-foreground">
                                Selecione a modalidade primeiro
                              </div>
                            ) : (
                              professores.map((prof) => (
                                <SelectItem key={prof.id} value={prof.id.toString()}>
                                  {prof.nome}
                                </SelectItem>
                              ))
                            )}
                          </SelectContent>
                        </Select>
                      </div>

                      <div>
                        <Label>Horário *</Label>
                        <Select
                          value={matricula.horario_id?.toString() || ''}
                          onValueChange={(value) =>
                            atualizarMatricula(index, 'horario_id', parseInt(value))
                          }
                          disabled={!matricula.professor_id || !matricula.modalidade}
                          required
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Selecione o horário" />
                          </SelectTrigger>
                          <SelectContent>
                            {horarios.length === 0 && matricula.professor_id && matricula.modalidade ? (
                              <div className="px-2 py-1.5 text-sm text-muted-foreground">
                                Nenhum horário disponível para este professor nesta modalidade. 
                                <br />
                                <span className="text-xs">Edite o professor para adicionar horários.</span>
                              </div>
                            ) : horarios.length === 0 ? (
                              <div className="px-2 py-1.5 text-sm text-muted-foreground">
                                {!matricula.modalidade ? 'Selecione a modalidade primeiro' : 'Selecione o professor primeiro'}
                              </div>
                            ) : (
                              horarios.map((horario) => (
                                <SelectItem key={horario.id} value={horario.id.toString()}>
                                  {horario.dia_semana} - {horario.horario_aula}
                                </SelectItem>
                              ))
                            )}
                          </SelectContent>
                        </Select>
                      </div>

                      <div>
                        <Label>Valor da Mensalidade *</Label>
                        <Input
                          type="text"
                          value={matricula.valor_mensalidade}
                          onChange={(e) => {
                            // Permitir apenas números, vírgula e ponto
                            const valor = e.target.value.replace(/[^\d,.-]/g, '');
                            atualizarMatricula(index, 'valor_mensalidade', valor);
                          }}
                          placeholder="Ex: 150 ou 150.50"
                          required
                        />
                      </div>

                      <div>
                        <Label>Data de Início</Label>
                        <Input
                          type="date"
                          value={matricula.data_inicio}
                          onChange={(e) =>
                            atualizarMatricula(index, 'data_inicio', e.target.value)
                          }
                        />
                      </div>
                    </div>
                  </div>
                );
              })}

              <p className="text-sm text-muted-foreground">
                * As modalidades do aluno serão definidas automaticamente com base nas matrículas cadastradas.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
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
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="aprovado"
                    checked={formData.aprovado}
                    onCheckedChange={(checked) =>
                      setFormData({ ...formData, aprovado: checked as boolean })
                    }
                  />
                  <Label htmlFor="aprovado" className="cursor-pointer">Aprovado</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="experimental"
                    checked={formData.experimental}
                    onCheckedChange={(checked) =>
                      setFormData({ ...formData, experimental: checked as boolean })
                    }
                  />
                  <Label htmlFor="experimental" className="cursor-pointer">Experimental</Label>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="flex justify-end gap-4">
            <Button type="button" variant="outline" onClick={() => navigate('/alunos')}>
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
