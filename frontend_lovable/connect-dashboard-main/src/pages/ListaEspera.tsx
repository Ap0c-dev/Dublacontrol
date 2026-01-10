import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MainLayout } from '@/components/layout/MainLayout';
import { api } from '@/lib/api';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Search, Loader2, Plus, Pencil, Trash2, CheckCircle, X } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { capitalizarNome } from '@/lib/utils';

interface ListaEsperaItem {
  id: number;
  nome: string;
  telefone: string;
  curso?: string;
  idade?: number;
  cidade?: string;
  regiao?: string;
  estado?: string;
  dia_semana?: string;
  data_pretende_entrar?: string;
  nome_responsavel?: string;
  telefone_responsavel?: string;
  observacao?: string;
  data_cadastro: string;
  efetivado: boolean;
  aluno_id?: number;
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

export default function ListaEspera() {
  const [listaEspera, setListaEspera] = useState<ListaEsperaItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isEfetivarDialogOpen, setIsEfetivarDialogOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState<ListaEsperaItem | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const { toast } = useToast();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    nome: '',
    telefone: '',
    curso: '',
    idade: '',
    cidade: '',
    regiao: '',
    estado: '',
    dia_semana: '',
    data_pretende_entrar: '',
    nome_responsavel: '',
    telefone_responsavel: '',
    observacao: '',
  });

  useEffect(() => {
    fetchListaEspera();
  }, []);

  const fetchListaEspera = async () => {
    setIsLoading(true);
    try {
      const response = await api.getListaEspera(false); // Apenas não efetivados
      if (response.success) {
        setListaEspera(response.data);
      } else {
        toast({
          title: 'Erro ao carregar lista de espera',
          description: response.error || 'Não foi possível obter a lista.',
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

  const handleCreate = () => {
    setSelectedItem(null);
    setFormData({
      nome: '',
      telefone: '',
      curso: '',
      idade: '',
      cidade: '',
      regiao: '',
      estado: '',
      dia_semana: '',
      data_pretende_entrar: '',
      nome_responsavel: '',
      telefone_responsavel: '',
      observacao: '',
    });
    setIsDialogOpen(true);
  };

  const handleEdit = (item: ListaEsperaItem) => {
    setSelectedItem(item);
    setFormData({
      nome: item.nome || '',
      telefone: item.telefone || '',
      curso: item.curso || '',
      idade: item.idade?.toString() || '',
      cidade: item.cidade || '',
      regiao: item.regiao || '',
      estado: item.estado || '',
      dia_semana: item.dia_semana || '',
      data_pretende_entrar: item.data_pretende_entrar ? item.data_pretende_entrar.split('T')[0] : '',
      nome_responsavel: item.nome_responsavel || '',
      telefone_responsavel: item.telefone_responsavel || '',
      observacao: item.observacao || '',
    });
    setIsDialogOpen(true);
  };

  const handleSave = async () => {
    if (!formData.nome || !formData.telefone) {
      toast({
        title: 'Erro',
        description: 'Nome e telefone são obrigatórios',
        variant: 'destructive',
      });
      return;
    }

    setIsSaving(true);
    try {
      const data = {
        nome: capitalizarNome(formData.nome),
        telefone: formData.telefone,
        curso: formData.curso || undefined,
        idade: formData.idade ? parseInt(formData.idade) : undefined,
        cidade: formData.cidade || undefined,
        regiao: formData.regiao || undefined,
        estado: formData.estado || undefined,
        dia_semana: formData.dia_semana || undefined,
        data_pretende_entrar: formData.data_pretende_entrar || undefined,
        nome_responsavel: formData.nome_responsavel || undefined,
        telefone_responsavel: formData.telefone_responsavel || undefined,
        observacao: formData.observacao || undefined,
      };

      let response;
      if (selectedItem) {
        response = await api.editarListaEspera(selectedItem.id, data);
      } else {
        response = await api.criarListaEspera(data);
      }

      if (response.success) {
        toast({
          title: 'Sucesso',
          description: selectedItem ? 'Registro atualizado com sucesso!' : 'Registro criado com sucesso!',
        });
        setIsDialogOpen(false);
        fetchListaEspera();
      } else {
        toast({
          title: 'Erro',
          description: response.error || 'Erro ao salvar registro',
          variant: 'destructive',
        });
      }
    } catch (error) {
      toast({
        title: 'Erro',
        description: 'Erro ao salvar registro',
        variant: 'destructive',
      });
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Tem certeza que deseja excluir este registro?')) {
      return;
    }

    try {
      const response = await api.deletarListaEspera(id);
      if (response.success) {
        toast({
          title: 'Sucesso',
          description: 'Registro excluído com sucesso!',
        });
        fetchListaEspera();
      } else {
        toast({
          title: 'Erro',
          description: response.error || 'Erro ao excluir registro',
          variant: 'destructive',
        });
      }
    } catch (error) {
      toast({
        title: 'Erro',
        description: 'Erro ao excluir registro',
        variant: 'destructive',
      });
    }
  };

  const handleEfetivar = (item: ListaEsperaItem) => {
    setSelectedItem(item);
    setIsEfetivarDialogOpen(true);
  };

  const filteredLista = listaEspera.filter((item) => {
    const searchLower = search.toLowerCase();
    return (
      item.nome.toLowerCase().includes(searchLower) ||
      item.telefone.includes(searchLower) ||
      (item.curso && item.curso.toLowerCase().includes(searchLower)) ||
      (item.nome_responsavel && item.nome_responsavel.toLowerCase().includes(searchLower))
    );
  });

  return (
    <MainLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl lg:text-3xl font-bold text-foreground">Lista de Espera</h1>
          <Button onClick={handleCreate}>
            <Plus size={18} className="mr-2" />
            Novo Registro
          </Button>
        </div>

        <div className="flex gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground" size={18} />
              <Input
                placeholder="Buscar por nome, telefone, curso..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
          </div>
        ) : filteredLista.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <p className="text-muted-foreground">Nenhum registro encontrado</p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {filteredLista.map((item) => (
              <Card key={item.id}>
                <CardHeader>
                  <CardTitle className="text-lg">{item.nome}</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="text-sm">
                    <strong>Telefone:</strong> {item.telefone}
                  </div>
                  {item.curso && (
                    <div className="text-sm">
                      <strong>Curso:</strong> {item.curso}
                    </div>
                  )}
                  {item.idade && (
                    <div className="text-sm">
                      <strong>Idade:</strong> {item.idade} anos
                    </div>
                  )}
                  {item.cidade && (
                    <div className="text-sm">
                      <strong>Localização:</strong> {item.cidade}
                      {item.regiao && ` - ${item.regiao}`}
                      {item.estado && `, ${item.estado}`}
                    </div>
                  )}
                  {item.data_cadastro && (
                    <div className="text-sm text-muted-foreground">
                      <strong>Cadastrado em:</strong> {new Date(item.data_cadastro).toLocaleDateString('pt-BR')}
                    </div>
                  )}
                  {item.data_pretende_entrar && (
                    <div className="text-sm">
                      <strong>Pretende entrar em:</strong> {new Date(item.data_pretende_entrar).toLocaleDateString('pt-BR')}
                    </div>
                  )}
                  {item.dia_semana && (
                    <div className="text-sm">
                      <strong>Dia da semana:</strong> {item.dia_semana}
                    </div>
                  )}
                  {item.nome_responsavel && (
                    <div className="text-sm">
                      <strong>Responsável:</strong> {item.nome_responsavel}
                      {item.telefone_responsavel && ` - ${item.telefone_responsavel}`}
                    </div>
                  )}
                  {item.observacao && (
                    <div className="text-sm">
                      <strong>Observação:</strong> {item.observacao}
                    </div>
                  )}
                  <div className="flex gap-2 mt-4">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleEdit(item)}
                    >
                      <Pencil size={14} className="mr-1" />
                      Editar
                    </Button>
                    <Button
                      size="sm"
                      variant="default"
                      onClick={() => handleEfetivar(item)}
                    >
                      <CheckCircle size={14} className="mr-1" />
                      Efetivar
                    </Button>
                    <Button
                      size="sm"
                      variant="destructive"
                      onClick={() => handleDelete(item.id)}
                    >
                      <Trash2 size={14} className="mr-1" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Dialog de Criar/Editar */}
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>{selectedItem ? 'Editar Registro' : 'Novo Registro'}</DialogTitle>
              <DialogDescription>
                {selectedItem ? 'Edite as informações do registro' : 'Preencha os dados do novo registro'}
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <Label>Nome *</Label>
                  <Input
                    value={formData.nome}
                    onChange={(e) => setFormData({ ...formData, nome: e.target.value })}
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
                  <Label>Curso</Label>
                  <Input
                    value={formData.curso}
                    onChange={(e) => setFormData({ ...formData, curso: e.target.value })}
                  />
                </div>
                <div>
                  <Label>Idade</Label>
                  <Input
                    type="number"
                    min="0"
                    max="150"
                    value={formData.idade}
                    onChange={(e) => setFormData({ ...formData, idade: e.target.value })}
                  />
                </div>
                <div>
                  <Label>Cidade</Label>
                  <Input
                    value={formData.cidade}
                    onChange={(e) => setFormData({ ...formData, cidade: capitalizarNome(e.target.value) })}
                  />
                </div>
                <div>
                  <Label>Região</Label>
                  <Input
                    value={formData.regiao}
                    onChange={(e) => setFormData({ ...formData, regiao: capitalizarNome(e.target.value) })}
                    placeholder="Ex: Zona Norte, Centro, etc."
                  />
                </div>
                <div>
                  <Label>Estado</Label>
                  <Input
                    value={formData.estado}
                    onChange={(e) => setFormData({ ...formData, estado: e.target.value.toUpperCase() })}
                    maxLength={2}
                  />
                </div>
                <div>
                  <Label>Data que Pretende Entrar</Label>
                  <Input
                    type="date"
                    value={formData.data_pretende_entrar}
                    onChange={(e) => setFormData({ ...formData, data_pretende_entrar: e.target.value })}
                  />
                </div>
                <div>
                  <Label>Dia da Semana</Label>
                  <Select
                    value={formData.dia_semana}
                    onValueChange={(value) => setFormData({ ...formData, dia_semana: value })}
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
                  <Label>Nome do Responsável</Label>
                  <Input
                    value={formData.nome_responsavel}
                    onChange={(e) => setFormData({ ...formData, nome_responsavel: capitalizarNome(e.target.value) })}
                  />
                </div>
                <div>
                  <Label>Telefone do Responsável</Label>
                  <Input
                    value={formData.telefone_responsavel}
                    onChange={(e) => setFormData({ ...formData, telefone_responsavel: e.target.value })}
                  />
                </div>
              </div>
              <div>
                <Label>Observação</Label>
                <Textarea
                  value={formData.observacao}
                  onChange={(e) => setFormData({ ...formData, observacao: e.target.value })}
                  rows={4}
                />
              </div>
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
                  Cancelar
                </Button>
                <Button onClick={handleSave} disabled={isSaving}>
                  {isSaving ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Salvando...
                    </>
                  ) : (
                    'Salvar'
                  )}
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>

        {/* Dialog de Efetivar Matrícula */}
        <EfetivarMatriculaDialog
          item={selectedItem}
          isOpen={isEfetivarDialogOpen}
          onClose={() => {
            setIsEfetivarDialogOpen(false);
            setSelectedItem(null);
          }}
          onSuccess={() => {
            setIsEfetivarDialogOpen(false);
            setSelectedItem(null);
            fetchListaEspera();
          }}
        />
      </div>
    </MainLayout>
  );
}

// Componente para dialog de efetivar matrícula
function EfetivarMatriculaDialog({
  item,
  isOpen,
  onClose,
  onSuccess,
}: {
  item: ListaEsperaItem | null;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}) {
  const { toast } = useToast();
  const [isSaving, setIsSaving] = useState(false);
  const [formData, setFormData] = useState({
    forma_pagamento: '',
    data_vencimento: '',
    cidade: '',
    estado: '',
    data_nascimento: '',
    experimental: false,
    matriculas: [
      {
        modalidade: '',
        professor_id: null as number | null,
        horario_id: null as number | null,
        valor_mensalidade: '',
        data_inicio: '',
      },
    ],
  });

  const [professores, setProfessores] = useState<any[]>([]);
  const [professoresPorModalidade, setProfessoresPorModalidade] = useState<Record<string, any[]>>({});
  const [horariosPorProfessor, setHorariosPorProfessor] = useState<Record<string, any[]>>({});

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

  useEffect(() => {
    if (isOpen && item) {
      setFormData({
        forma_pagamento: '',
        data_vencimento: '',
        cidade: item.cidade || '',
        estado: item.estado || '',
        data_nascimento: '',
        experimental: false,
        matriculas: [
          {
            modalidade: '',
            professor_id: null,
            horario_id: null,
            valor_mensalidade: '',
            data_inicio: '',
          },
        ],
      });
      fetchProfessores();
    }
  }, [isOpen, item]);

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

  const carregarProfessores = async (modalidade: string) => {
    if (!modalidade) return;
    if (professoresPorModalidade[modalidade]) return;
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
    }
  };

  const carregarHorarios = async (professorId: number, modalidade: string) => {
    if (!professorId || !modalidade) return;
    const key = `${professorId}_${modalidade}`;
    if (horariosPorProfessor[key]) return;
    try {
      const response = await api.getHorariosProfessor(professorId, modalidade);
      if (response.success && response.data) {
        setHorariosPorProfessor((prev) => ({
          ...prev,
          [key]: response.data,
        }));
      }
    } catch (error) {
      console.error('Erro ao carregar horários:', error);
    }
  };

  const adicionarMatricula = () => {
    setFormData({
      ...formData,
      matriculas: [
        ...formData.matriculas,
        {
          modalidade: '',
          professor_id: null,
          horario_id: null,
          valor_mensalidade: '',
          data_inicio: '',
        },
      ],
    });
  };

  const atualizarMatricula = async (index: number, campo: string, valor: any) => {
    const novasMatriculas = [...formData.matriculas];
    novasMatriculas[index] = { ...novasMatriculas[index], [campo]: valor };

    if (campo === 'modalidade') {
      novasMatriculas[index].professor_id = null;
      novasMatriculas[index].horario_id = null;
      if (valor) {
        await carregarProfessores(valor);
      }
    }

    if (campo === 'professor_id') {
      novasMatriculas[index].horario_id = null;
      const modalidade = novasMatriculas[index].modalidade;
      if (valor && modalidade) {
        await carregarHorarios(valor, modalidade);
      }
    }

    setFormData({ ...formData, matriculas: novasMatriculas });
  };

  const removerMatricula = (index: number) => {
    if (formData.matriculas.length > 1) {
      setFormData({
        ...formData,
        matriculas: formData.matriculas.filter((_, i) => i !== index),
      });
    }
  };

  const handleSave = async () => {
    if (!formData.forma_pagamento || !formData.data_vencimento || !formData.cidade || !formData.estado) {
      toast({
        title: 'Erro',
        description: 'Preencha todos os campos obrigatórios',
        variant: 'destructive',
      });
      return;
    }

    const matriculasValidas = formData.matriculas.filter(
      (m) => m.modalidade && m.professor_id && m.horario_id && m.valor_mensalidade
    );

    if (matriculasValidas.length === 0) {
      toast({
        title: 'Erro',
        description: 'Adicione pelo menos uma matrícula completa',
        variant: 'destructive',
      });
      return;
    }

    setIsSaving(true);
    try {
      const data = {
        forma_pagamento: formData.forma_pagamento,
        data_vencimento: formData.data_vencimento,
        cidade: formData.cidade,
        estado: formData.estado,
        data_nascimento: formData.data_nascimento || undefined,
        experimental: formData.experimental,
        matriculas: matriculasValidas.map((m) => ({
          modalidade: m.modalidade,
          professor_id: m.professor_id!,
          horario_id: m.horario_id!,
          valor_mensalidade: parseFloat(m.valor_mensalidade.replace(',', '.')),
          data_inicio: m.data_inicio || undefined,
        })),
      };

      if (!item) return;

      const response = await api.efetivarListaEspera(item.id, data);
      if (response.success) {
        toast({
          title: 'Sucesso',
          description: 'Matrícula efetivada com sucesso!',
        });
        onSuccess();
      } else {
        toast({
          title: 'Erro',
          description: response.error || 'Erro ao efetivar matrícula',
          variant: 'destructive',
        });
      }
    } catch (error) {
      toast({
        title: 'Erro',
        description: 'Erro ao efetivar matrícula',
        variant: 'destructive',
      });
    } finally {
      setIsSaving(false);
    }
  };

  if (!item) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Efetivar Matrícula - {item.nome}</DialogTitle>
          <DialogDescription>
            Preencha os dados necessários para efetivar a matrícula deste aluno
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <Label>Cidade *</Label>
              <Input
                value={formData.cidade}
                onChange={(e) => setFormData({ ...formData, cidade: e.target.value })}
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
              <Label>Forma de Pagamento *</Label>
              <Select
                value={formData.forma_pagamento}
                onValueChange={(value) => setFormData({ ...formData, forma_pagamento: value })}
                required
              >
                <SelectTrigger>
                  <SelectValue placeholder="Selecione" />
                </SelectTrigger>
                <SelectContent>
                  {FORMAS_PAGAMENTO.map((forma) => (
                    <SelectItem key={forma.value} value={forma.value}>
                      {forma.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Data de Vencimento *</Label>
              <Input
                type="date"
                value={formData.data_vencimento}
                onChange={(e) => setFormData({ ...formData, data_vencimento: e.target.value })}
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
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <Label>Matrículas *</Label>
              <Button type="button" variant="outline" size="sm" onClick={adicionarMatricula}>
                <Plus size={14} className="mr-1" />
                Adicionar
              </Button>
            </div>
            {formData.matriculas.map((matricula, index) => {
              const professores = professoresPorModalidade[matricula.modalidade] || [];
              const horariosKey = matricula.professor_id && matricula.modalidade
                ? `${matricula.professor_id}_${matricula.modalidade}`
                : '';
              const horarios = horariosPorProfessor[horariosKey] || [];

              return (
                <Card key={index}>
                  <CardContent className="pt-4">
                    <div className="flex items-center justify-between mb-4">
                      <Label>Matrícula {index + 1}</Label>
                      {formData.matriculas.length > 1 && (
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => removerMatricula(index)}
                        >
                          <Trash2 size={14} />
                        </Button>
                      )}
                    </div>
                    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                      <div>
                        <Label>Modalidade *</Label>
                        <Select
                          value={matricula.modalidade}
                          onValueChange={(value) => atualizarMatricula(index, 'modalidade', value)}
                          required
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Selecione" />
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
                          onValueChange={(value) => atualizarMatricula(index, 'professor_id', parseInt(value))}
                          disabled={!matricula.modalidade}
                          required
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Selecione" />
                          </SelectTrigger>
                          <SelectContent>
                            {professores.length === 0 ? (
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
                          onValueChange={(value) => atualizarMatricula(index, 'horario_id', parseInt(value))}
                          disabled={!matricula.professor_id || !matricula.modalidade}
                          required
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Selecione" />
                          </SelectTrigger>
                          <SelectContent>
                            {horarios.length === 0 ? (
                              <div className="px-2 py-1.5 text-sm text-muted-foreground">
                                Selecione o professor primeiro
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
                          onChange={(e) => atualizarMatricula(index, 'data_inicio', e.target.value)}
                        />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={onClose}>
              Cancelar
            </Button>
            <Button onClick={handleSave} disabled={isSaving}>
              {isSaving ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Efetivando...
                </>
              ) : (
                <>
                  <CheckCircle className="mr-2 h-4 w-4" />
                  Efetivar Matrícula
                </>
              )}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}

