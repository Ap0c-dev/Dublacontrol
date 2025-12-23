import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { MainLayout } from '@/components/layout/MainLayout';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Loader2, ArrowLeft, Save } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function NotaForm() {
  const { id } = useParams<{ id?: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingData, setIsLoadingData] = useState(!!id);
  
  const [formData, setFormData] = useState({
    aluno_id: '',
    professor_id: '',
    tipo_curso: '',
    valor: '',
    tipo_avaliacao: '',
    observacao: '',
    data_avaliacao: new Date().toISOString().split('T')[0],
    criterio1: '',
    criterio2: '',
    criterio3: '',
    criterio4: '',
    numero_prova: '',
  });

  const [alunos, setAlunos] = useState<any[]>([]);
  const [professores, setProfessores] = useState<any[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [alunosRes, professoresRes] = await Promise.all([
          api.getAlunos(),
          api.getProfessores()
        ]);

        if (alunosRes.success) setAlunos(alunosRes.data);
        if (professoresRes.success) setProfessores(professoresRes.data);

        if (id) {
          const notaRes = await api.getNota(parseInt(id));
          if (notaRes.success) {
            const nota = notaRes.data;
            setFormData({
              aluno_id: nota.aluno_id.toString(),
              professor_id: nota.professor_id.toString(),
              tipo_curso: nota.tipo_curso,
              valor: nota.valor?.toString() || '',
              tipo_avaliacao: nota.tipo_avaliacao || '',
              observacao: nota.observacao || '',
              data_avaliacao: nota.data_avaliacao ? nota.data_avaliacao.split('T')[0] : new Date().toISOString().split('T')[0],
              criterio1: nota.criterio1?.toString() || '',
              criterio2: nota.criterio2?.toString() || '',
              criterio3: nota.criterio3?.toString() || '',
              criterio4: nota.criterio4?.toString() || '',
              numero_prova: nota.numero_prova?.toString() || '',
            });
          }
        }
      } catch (error) {
        toast({
          title: 'Erro',
          description: 'Erro ao carregar dados',
          variant: 'destructive',
        });
      } finally {
        setIsLoadingData(false);
      }
    };

    fetchData();
  }, [id, toast]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const data = {
        aluno_id: parseInt(formData.aluno_id),
        professor_id: parseInt(formData.professor_id),
        tipo_curso: formData.tipo_curso,
        valor: formData.valor ? parseFloat(formData.valor) : null,
        tipo_avaliacao: formData.tipo_avaliacao || null,
        observacao: formData.observacao || null,
        data_avaliacao: formData.data_avaliacao,
        criterio1: formData.criterio1 ? parseFloat(formData.criterio1) : null,
        criterio2: formData.criterio2 ? parseFloat(formData.criterio2) : null,
        criterio3: formData.criterio3 ? parseFloat(formData.criterio3) : null,
        criterio4: formData.criterio4 ? parseFloat(formData.criterio4) : null,
        numero_prova: formData.numero_prova ? parseInt(formData.numero_prova) : null,
      };

      let response;
      if (id) {
        response = await api.editarNota(parseInt(id), data);
      } else {
        response = await api.criarNota(data);
      }

      if (response.success) {
        toast({
          title: 'Sucesso',
          description: id ? 'Nota atualizada com sucesso!' : 'Nota criada com sucesso!',
        });
        navigate('/notas');
      } else {
        toast({
          title: 'Erro',
          description: response.error || 'Erro ao salvar nota',
          variant: 'destructive',
        });
      }
    } catch (error) {
      toast({
        title: 'Erro',
        description: 'Erro ao salvar nota',
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
          <Button variant="ghost" onClick={() => navigate('/notas')}>
            <ArrowLeft size={18} className="mr-2" />
            Voltar
          </Button>
          <h1 className="text-2xl lg:text-3xl font-bold text-foreground">
            {id ? 'Editar Nota' : 'Nova Nota'}
          </h1>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Informações da Nota</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <Label>Aluno *</Label>
                  <Select
                    value={formData.aluno_id}
                    onValueChange={(value) => setFormData({ ...formData, aluno_id: value })}
                    required
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione o aluno" />
                    </SelectTrigger>
                    <SelectContent>
                      {alunos.map((aluno) => (
                        <SelectItem key={aluno.id} value={aluno.id.toString()}>
                          {aluno.nome}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label>Professor *</Label>
                  <Select
                    value={formData.professor_id}
                    onValueChange={(value) => setFormData({ ...formData, professor_id: value })}
                    required
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione o professor" />
                    </SelectTrigger>
                    <SelectContent>
                      {professores.map((prof) => (
                        <SelectItem key={prof.id} value={prof.id.toString()}>
                          {prof.nome}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label>Tipo de Curso *</Label>
                  <Select
                    value={formData.tipo_curso}
                    onValueChange={(value) => setFormData({ ...formData, tipo_curso: value })}
                    required
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione o tipo" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="dublagem_online">Dublagem Online</SelectItem>
                      <SelectItem value="dublagem_presencial">Dublagem Presencial</SelectItem>
                      <SelectItem value="teatro_online">Teatro Online</SelectItem>
                      <SelectItem value="teatro_presencial">Teatro Presencial</SelectItem>
                      <SelectItem value="locucao">Locução</SelectItem>
                      <SelectItem value="teatro_tv_cinema">Teatro TV/Cinema</SelectItem>
                      <SelectItem value="musical">Musical</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label>Data de Avaliação *</Label>
                  <Input
                    type="date"
                    value={formData.data_avaliacao}
                    onChange={(e) => setFormData({ ...formData, data_avaliacao: e.target.value })}
                    required
                  />
                </div>

                <div>
                  <Label>Valor da Nota (0-10)</Label>
                  <Input
                    type="number"
                    min="0"
                    max="10"
                    step="0.1"
                    value={formData.valor}
                    onChange={(e) => setFormData({ ...formData, valor: e.target.value })}
                    placeholder="Ex: 8.5"
                  />
                </div>

                <div>
                  <Label>Tipo de Avaliação</Label>
                  <Input
                    value={formData.tipo_avaliacao}
                    onChange={(e) => setFormData({ ...formData, tipo_avaliacao: e.target.value })}
                    placeholder="Ex: Prova, Trabalho, Apresentação"
                  />
                </div>

                <div>
                  <Label>Número da Prova</Label>
                  <Input
                    type="number"
                    min="1"
                    max="8"
                    value={formData.numero_prova}
                    onChange={(e) => setFormData({ ...formData, numero_prova: e.target.value })}
                    placeholder="1-8"
                  />
                </div>
              </div>

              <div>
                <Label>Critérios de Avaliação (0-10 cada)</Label>
                <div className="grid gap-4 md:grid-cols-4 mt-2">
                  <div>
                    <Label className="text-sm">Critério 1</Label>
                    <Input
                      type="number"
                      min="0"
                      max="10"
                      step="0.1"
                      value={formData.criterio1}
                      onChange={(e) => setFormData({ ...formData, criterio1: e.target.value })}
                    />
                  </div>
                  <div>
                    <Label className="text-sm">Critério 2</Label>
                    <Input
                      type="number"
                      min="0"
                      max="10"
                      step="0.1"
                      value={formData.criterio2}
                      onChange={(e) => setFormData({ ...formData, criterio2: e.target.value })}
                    />
                  </div>
                  <div>
                    <Label className="text-sm">Critério 3</Label>
                    <Input
                      type="number"
                      min="0"
                      max="10"
                      step="0.1"
                      value={formData.criterio3}
                      onChange={(e) => setFormData({ ...formData, criterio3: e.target.value })}
                    />
                  </div>
                  <div>
                    <Label className="text-sm">Critério 4</Label>
                    <Input
                      type="number"
                      min="0"
                      max="10"
                      step="0.1"
                      value={formData.criterio4}
                      onChange={(e) => setFormData({ ...formData, criterio4: e.target.value })}
                    />
                  </div>
                </div>
              </div>

              <div>
                <Label>Observações</Label>
                <Textarea
                  value={formData.observacao}
                  onChange={(e) => setFormData({ ...formData, observacao: e.target.value })}
                  placeholder="Observações sobre a avaliação..."
                  rows={4}
                />
              </div>

              <div className="flex justify-end gap-4">
                <Button type="button" variant="outline" onClick={() => navigate('/notas')}>
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
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}

