import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { MainLayout } from '@/components/layout/MainLayout';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, ArrowLeft, Upload, Image as ImageIcon } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

const MESES = [
  { value: '1', label: 'Janeiro' },
  { value: '2', label: 'Fevereiro' },
  { value: '3', label: 'Março' },
  { value: '4', label: 'Abril' },
  { value: '5', label: 'Maio' },
  { value: '6', label: 'Junho' },
  { value: '7', label: 'Julho' },
  { value: '8', label: 'Agosto' },
  { value: '9', label: 'Setembro' },
  { value: '10', label: 'Outubro' },
  { value: '11', label: 'Novembro' },
  { value: '12', label: 'Dezembro' },
];

export default function UploadComprovante() {
  const { alunoId } = useParams<{ alunoId: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingData, setIsLoadingData] = useState(!!alunoId);
  const [aluno, setAluno] = useState<any>(null);
  const [preview, setPreview] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    mes_referencia: '',
    ano_referencia: new Date().getFullYear().toString(),
    valor_pago: '',
    data_pagamento: new Date().toISOString().split('T')[0],
    observacoes: '',
  });

  const [comprovante, setComprovante] = useState<File | null>(null);

  useEffect(() => {
    if (alunoId) {
      const fetchAluno = async () => {
        setIsLoadingData(true);
        try {
          const response = await api.getAluno(parseInt(alunoId));
          if (response.success) {
            setAluno(response.data);
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
  }, [alunoId, toast]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setComprovante(file);
      
      // Criar preview se for imagem
      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
          setPreview(e.target?.result as string);
        };
        reader.readAsDataURL(file);
      } else {
        setPreview(null);
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      if (!comprovante) {
        toast({
          title: 'Erro',
          description: 'Selecione um arquivo de comprovante',
          variant: 'destructive',
        });
        setIsLoading(false);
        return;
      }

      if (!alunoId) {
        toast({
          title: 'Erro',
          description: 'ID do aluno não encontrado',
          variant: 'destructive',
        });
        setIsLoading(false);
        return;
      }

      const response = await api.uploadComprovante(
        parseInt(alunoId),
        parseInt(formData.mes_referencia),
        parseInt(formData.ano_referencia),
        parseFloat(formData.valor_pago.replace(',', '.')),
        formData.data_pagamento,
        comprovante,
        formData.observacoes || undefined
      );

      if (response.success) {
        toast({
          title: 'Sucesso',
          description: 'Comprovante enviado com sucesso! Aguardando aprovação.',
        });
        navigate(`/alunos/${alunoId}`);
      } else {
        toast({
          title: 'Erro',
          description: response.error || 'Erro ao enviar comprovante',
          variant: 'destructive',
        });
      }
    } catch (error) {
      toast({
        title: 'Erro',
        description: 'Erro ao enviar comprovante',
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
          <Button variant="ghost" onClick={() => navigate(alunoId ? `/alunos/${alunoId}` : '/alunos')}>
            <ArrowLeft size={18} className="mr-2" />
            Voltar
          </Button>
          <h1 className="text-2xl lg:text-3xl font-bold text-foreground">
            Enviar Comprovante de Pagamento
          </h1>
        </div>

        {aluno && (
          <Card>
            <CardHeader>
              <CardTitle>Informações do Aluno</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="font-medium">{aluno.nome}</p>
              <p className="text-sm text-muted-foreground">
                Total de Mensalidades: R$ {aluno.total_mensalidades?.toFixed(2) || '0.00'}
              </p>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader>
            <CardTitle>Dados do Pagamento</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <Label>Mês de Referência *</Label>
                  <Select
                    value={formData.mes_referencia}
                    onValueChange={(value) =>
                      setFormData({ ...formData, mes_referencia: value })
                    }
                    required
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione o mês" />
                    </SelectTrigger>
                    <SelectContent>
                      {MESES.map((mes) => (
                        <SelectItem key={mes.value} value={mes.value}>
                          {mes.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label>Ano de Referência *</Label>
                  <Input
                    type="number"
                    value={formData.ano_referencia}
                    onChange={(e) =>
                      setFormData({ ...formData, ano_referencia: e.target.value })
                    }
                    min="2020"
                    max="2100"
                    required
                  />
                </div>

                <div>
                  <Label>Valor Pago (R$) *</Label>
                  <Input
                    type="text"
                    value={formData.valor_pago}
                    onChange={(e) => {
                      const valor = e.target.value.replace(/[^\d,.-]/g, '');
                      setFormData({ ...formData, valor_pago: valor });
                    }}
                    placeholder="0.00"
                    required
                  />
                </div>

                <div>
                  <Label>Data do Pagamento *</Label>
                  <Input
                    type="date"
                    value={formData.data_pagamento}
                    onChange={(e) =>
                      setFormData({ ...formData, data_pagamento: e.target.value })
                    }
                    required
                  />
                </div>
              </div>

              <div>
                <Label>Comprovante *</Label>
                <div className="mt-2">
                  <Input
                    type="file"
                    accept="image/*,.pdf"
                    onChange={handleFileChange}
                    required
                  />
                  <p className="text-sm text-muted-foreground mt-1">
                    Formatos aceitos: PNG, JPG, JPEG, GIF, PDF, WEBP (máx. 10MB)
                  </p>
                </div>
                {preview && (
                  <div className="mt-4 p-4 bg-muted/50 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <ImageIcon size={18} className="text-muted-foreground" />
                      <span className="text-sm font-medium">Preview</span>
                    </div>
                    <img
                      src={preview}
                      alt="Preview do comprovante"
                      className="max-w-full max-h-64 rounded-lg border border-border"
                    />
                  </div>
                )}
              </div>

              <div>
                <Label>Observações (opcional)</Label>
                <Textarea
                  value={formData.observacoes}
                  onChange={(e) =>
                    setFormData({ ...formData, observacoes: e.target.value })
                  }
                  placeholder="Informações adicionais sobre o pagamento..."
                  rows={4}
                />
              </div>

              <div className="flex gap-4">
                <Button type="submit" disabled={isLoading}>
                  {isLoading ? (
                    <>
                      <Loader2 size={18} className="mr-2 animate-spin" />
                      Enviando...
                    </>
                  ) : (
                    <>
                      <Upload size={18} className="mr-2" />
                      Enviar Comprovante
                    </>
                  )}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => navigate(alunoId ? `/alunos/${alunoId}` : '/alunos')}
                >
                  Cancelar
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}


