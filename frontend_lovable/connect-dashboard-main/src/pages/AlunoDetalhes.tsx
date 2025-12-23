import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { MainLayout } from '@/components/layout/MainLayout';
import { api } from '@/lib/api';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Loader2, ArrowLeft, User, Phone, MapPin, Calendar, CreditCard, BookOpen, GraduationCap, Upload } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function AlunoDetalhes() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [aluno, setAluno] = useState<any>(null);
  const [notas, setNotas] = useState<any[]>([]);
  const [pagamentos, setPagamentos] = useState<any[]>([]);
  const [matriculas, setMatriculas] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    const fetchData = async () => {
      if (!id) return;
      
      setIsLoading(true);
      try {
        const [alunoRes, notasRes, pagamentosRes, matriculasRes] = await Promise.all([
          api.getAluno(parseInt(id)),
          api.getNotas({ aluno_id: parseInt(id) }),
          api.getPagamentos({ aluno_id: parseInt(id) }),
          api.getMatriculas({ aluno_id: parseInt(id) })
        ]);

        if (alunoRes.success) setAluno(alunoRes.data);
        if (notasRes.success) setNotas(notasRes.data);
        if (pagamentosRes.success) setPagamentos(pagamentosRes.data);
        if (matriculasRes.success) setMatriculas(matriculasRes.data);
      } catch (error) {
        toast({
          title: 'Erro ao carregar dados',
          description: 'Não foi possível carregar os dados do aluno.',
          variant: 'destructive',
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [id, toast]);

  if (isLoading) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-primary" />
        </div>
      </MainLayout>
    );
  }

  if (!aluno) {
    return (
      <MainLayout>
        <div className="text-center py-12">
          <p className="text-muted-foreground">Aluno não encontrado.</p>
          <Button onClick={() => navigate('/alunos')} className="mt-4">
            Voltar
          </Button>
        </div>
      </MainLayout>
    );
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR');
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4 animate-fade-in">
          <Button variant="ghost" onClick={() => navigate('/alunos')}>
            <ArrowLeft size={18} className="mr-2" />
            Voltar
          </Button>
          <div>
            <h1 className="text-2xl lg:text-3xl font-bold text-foreground">{aluno.nome}</h1>
            <p className="text-muted-foreground mt-1">Detalhes do aluno</p>
          </div>
        </div>

        {/* Informações Básicas */}
        <Card>
          <CardHeader>
            <CardTitle>Informações Básicas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="flex items-center gap-3">
                <User className="text-muted-foreground" size={18} />
                <div>
                  <p className="text-sm text-muted-foreground">Nome</p>
                  <p className="font-medium">{aluno.nome}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Phone className="text-muted-foreground" size={18} />
                <div>
                  <p className="text-sm text-muted-foreground">Telefone</p>
                  <p className="font-medium">{aluno.telefone}</p>
                </div>
              </div>
              {aluno.telefone_responsavel && (
                <div className="flex items-center gap-3">
                  <Phone className="text-muted-foreground" size={18} />
                  <div>
                    <p className="text-sm text-muted-foreground">Telefone Responsável</p>
                    <p className="font-medium">{aluno.telefone_responsavel}</p>
                  </div>
                </div>
              )}
              <div className="flex items-center gap-3">
                <MapPin className="text-muted-foreground" size={18} />
                <div>
                  <p className="text-sm text-muted-foreground">Localização</p>
                  <p className="font-medium">{aluno.cidade}, {aluno.estado}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Calendar className="text-muted-foreground" size={18} />
                <div>
                  <p className="text-sm text-muted-foreground">Data de Vencimento</p>
                  <p className="font-medium">
                    {aluno.data_vencimento ? formatDate(aluno.data_vencimento) : '-'}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <CreditCard className="text-muted-foreground" size={18} />
                <div>
                  <p className="text-sm text-muted-foreground">Forma de Pagamento</p>
                  <p className="font-medium">{aluno.forma_pagamento}</p>
                </div>
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-2">Total de Mensalidades</p>
                <p className="text-2xl font-bold text-primary">
                  {formatCurrency(aluno.total_mensalidades || 0)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Tabs */}
        <Tabs defaultValue="matriculas" className="space-y-4">
          <TabsList>
            <TabsTrigger value="matriculas">
              <GraduationCap size={16} className="mr-2" />
              Matrículas ({matriculas.length})
            </TabsTrigger>
            <TabsTrigger value="notas">
              <BookOpen size={16} className="mr-2" />
              Notas ({notas.length})
            </TabsTrigger>
            <TabsTrigger value="pagamentos">
              <CreditCard size={16} className="mr-2" />
              Pagamentos ({pagamentos.length})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="matriculas">
            <Card>
              <CardHeader>
                <CardTitle>Matrículas</CardTitle>
              </CardHeader>
              <CardContent>
                {matriculas.length > 0 ? (
                  <div className="space-y-4">
                    {matriculas.map((mat) => (
                      <div key={mat.id} className="p-4 border rounded-lg">
                        <div className="flex justify-between items-start">
                          <div>
                            <p className="font-medium">{mat.tipo_curso}</p>
                            <p className="text-sm text-muted-foreground">
                              Professor: {mat.professor_nome}
                            </p>
                            {mat.valor_mensalidade && (
                              <p className="text-sm text-muted-foreground">
                                Mensalidade: {formatCurrency(mat.valor_mensalidade)}
                              </p>
                            )}
                          </div>
                          <Badge variant="outline">
                            {mat.data_inicio ? formatDate(mat.data_inicio) : 'Sem data'}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted-foreground">Nenhuma matrícula encontrada.</p>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="notas">
            <Card>
              <CardHeader>
                <CardTitle>Notas</CardTitle>
              </CardHeader>
              <CardContent>
                {notas.length > 0 ? (
                  <div className="space-y-4">
                    {notas.map((nota) => (
                      <div key={nota.id} className="p-4 border rounded-lg">
                        <div className="flex justify-between items-start">
                          <div>
                            <p className="font-medium">{nota.tipo_curso}</p>
                            <p className="text-sm text-muted-foreground">
                              {nota.tipo_avaliacao || 'Avaliação'} - {nota.professor_nome}
                            </p>
                            {nota.data_avaliacao && (
                              <p className="text-sm text-muted-foreground">
                                {formatDate(nota.data_avaliacao)}
                              </p>
                            )}
                          </div>
                          <div className="text-right">
                            {nota.media !== null ? (
                              <p className="text-2xl font-bold">{nota.media.toFixed(1)}</p>
                            ) : nota.valor !== null ? (
                              <p className="text-2xl font-bold">{nota.valor.toFixed(1)}</p>
                            ) : (
                              <p className="text-muted-foreground">-</p>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted-foreground">Nenhuma nota encontrada.</p>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="pagamentos">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>Pagamentos</CardTitle>
                <Button
                  onClick={() => navigate(`/alunos/${id}/pagamento/upload`)}
                  size="sm"
                >
                  <Upload size={16} className="mr-2" />
                  Enviar Comprovante
                </Button>
              </CardHeader>
              <CardContent>
                {pagamentos.length > 0 ? (
                  <div className="space-y-4">
                    {pagamentos.map((pag) => (
                      <div key={pag.id} className="p-4 border rounded-lg">
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <p className="font-medium">{formatCurrency(pag.valor || pag.valor_pago || 0)}</p>
                            <p className="text-sm text-muted-foreground">
                              {pag.mes_referencia && pag.ano_referencia 
                                ? `${pag.mes_referencia}/${pag.ano_referencia}`
                                : pag.data_vencimento 
                                ? formatDate(pag.data_vencimento) 
                                : '-'}
                            </p>
                            {pag.data_pagamento && (
                              <p className="text-sm text-muted-foreground">
                                Data do pagamento: {formatDate(pag.data_pagamento)}
                              </p>
                            )}
                            {pag.url_comprovante && (
                              <a
                                href={pag.url_comprovante}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-sm text-primary hover:underline mt-1 inline-block"
                              >
                                Ver comprovante
                              </a>
                            )}
                          </div>
                          <Badge
                            variant={
                              pag.status === 'aprovado' || pag.status === 'pago' ? 'default' :
                              pag.status === 'pendente' ? 'secondary' : 'destructive'
                            }
                          >
                            {pag.status === 'aprovado' ? 'Aprovado' :
                             pag.status === 'pendente' ? 'Pendente' :
                             pag.status === 'rejeitado' ? 'Rejeitado' : pag.status}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <p className="text-muted-foreground mb-4">Nenhum pagamento encontrado.</p>
                    <Button
                      onClick={() => navigate(`/alunos/${id}/pagamento/upload`)}
                      variant="outline"
                    >
                      <Upload size={16} className="mr-2" />
                      Enviar Primeiro Comprovante
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </MainLayout>
  );
}

