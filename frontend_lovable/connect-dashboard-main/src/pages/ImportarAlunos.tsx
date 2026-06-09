import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MainLayout } from '@/components/layout/MainLayout';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Loader2, ArrowLeft, Upload, FileSpreadsheet, CheckCircle2, XCircle, AlertCircle } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

export default function ImportarAlunos() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<{
    success: boolean;
    alunos_criados?: number;
    alunos_erro?: Array<{ linha: number; nome: string; erro: string }>;
    alunos_duplicados?: Array<{ linha: number; nome: string; telefone: string }>;
    error?: string;
  } | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      if (!selectedFile.name.endsWith('.xlsx') && !selectedFile.name.endsWith('.xls')) {
        toast({
          title: 'Formato inválido',
          description: 'Por favor, selecione um arquivo Excel (.xlsx ou .xls)',
          variant: 'destructive',
        });
        return;
      }
      setFile(selectedFile);
      setResult(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!file) {
      toast({
        title: 'Arquivo não selecionado',
        description: 'Por favor, selecione um arquivo Excel para importar',
        variant: 'destructive',
      });
      return;
    }

    setIsLoading(true);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('arquivo', file);

      const token = localStorage.getItem('token');
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api/v1';
      const baseUrl = API_BASE_URL.replace(/\/$/, ''); // Remove trailing slash

      const response = await fetch(`${baseUrl}/alunos/importar`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setResult({
          success: true,
          alunos_criados: data.data?.alunos_criados || 0,
          alunos_erro: data.data?.alunos_erro || [],
          alunos_duplicados: data.data?.alunos_duplicados || [],
        });
        
        toast({
          title: 'Importação concluída!',
          description: `${data.data?.alunos_criados || 0} aluno(s) importado(s) com sucesso`,
          variant: 'default',
        });
      } else {
        setResult({
          success: false,
          error: data.error || 'Erro ao importar alunos',
        });
        
        toast({
          title: 'Erro na importação',
          description: data.error || 'Não foi possível importar os alunos',
          variant: 'destructive',
        });
      }
    } catch (error) {
      console.error('Erro ao importar:', error);
      setResult({
        success: false,
        error: error instanceof Error ? error.message : 'Erro desconhecido',
      });
      
      toast({
        title: 'Erro de conexão',
        description: 'Não foi possível conectar ao servidor',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate('/alunos')}
          >
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-2xl lg:text-3xl font-bold text-gradient">
              Importar Alunos
            </h1>
            <p className="text-muted-foreground mt-1 font-mono">
              Importe alunos de um arquivo Excel
            </p>
          </div>
        </div>

        {/* Card de Upload */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileSpreadsheet className="h-5 w-5" />
              Selecionar Arquivo Excel
            </CardTitle>
            <CardDescription>
              Selecione um arquivo Excel (.xlsx) com os dados dos alunos para importar
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="arquivo">Arquivo Excel</Label>
                <Input
                  id="arquivo"
                  type="file"
                  accept=".xlsx,.xls"
                  onChange={handleFileChange}
                  disabled={isLoading}
                />
                {file && (
                  <p className="text-sm text-muted-foreground">
                    Arquivo selecionado: {file.name} ({(file.size / 1024).toFixed(2)} KB)
                  </p>
                )}
              </div>

              <div className="flex gap-4">
                <Button
                  type="submit"
                  disabled={!file || isLoading}
                  className="flex items-center gap-2"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Importando...
                    </>
                  ) : (
                    <>
                      <Upload className="h-4 w-4" />
                      Importar Alunos
                    </>
                  )}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => navigate('/alunos')}
                  disabled={isLoading}
                >
                  Cancelar
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Resultado */}
        {result && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                {result.success ? (
                  <CheckCircle2 className="h-5 w-5 text-green-500" />
                ) : (
                  <XCircle className="h-5 w-5 text-red-500" />
                )}
                Resultado da Importação
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {result.success ? (
                <>
                  <Alert>
                    <CheckCircle2 className="h-4 w-4" />
                    <AlertTitle>Importação concluída!</AlertTitle>
                    <AlertDescription>
                      {result.alunos_criados || 0} aluno(s) foram importados com sucesso.
                    </AlertDescription>
                  </Alert>

                  {result.alunos_duplicados && result.alunos_duplicados.length > 0 && (
                    <Alert variant="default">
                      <AlertCircle className="h-4 w-4" />
                      <AlertTitle>Alunos duplicados (ignorados)</AlertTitle>
                      <AlertDescription>
                        {result.alunos_duplicados.length} aluno(s) foram ignorados porque já existem no sistema:
                        <ul className="list-disc list-inside mt-2 space-y-1">
                          {result.alunos_duplicados.slice(0, 5).map((dup, idx) => (
                            <li key={idx} className="text-sm">
                              Linha {dup.linha}: {dup.nome} ({dup.telefone})
                            </li>
                          ))}
                          {result.alunos_duplicados.length > 5 && (
                            <li className="text-sm text-muted-foreground">
                              ... e mais {result.alunos_duplicados.length - 5} aluno(s)
                            </li>
                          )}
                        </ul>
                      </AlertDescription>
                    </Alert>
                  )}

                  {result.alunos_erro && result.alunos_erro.length > 0 && (
                    <Alert variant="destructive">
                      <XCircle className="h-4 w-4" />
                      <AlertTitle>Erros encontrados</AlertTitle>
                      <AlertDescription>
                        {result.alunos_erro.length} aluno(s) não puderam ser importados:
                        <ul className="list-disc list-inside mt-2 space-y-1">
                          {result.alunos_erro.slice(0, 5).map((erro, idx) => (
                            <li key={idx} className="text-sm">
                              Linha {erro.linha}: {erro.nome} - {erro.erro}
                            </li>
                          ))}
                          {result.alunos_erro.length > 5 && (
                            <li className="text-sm">
                              ... e mais {result.alunos_erro.length - 5} erro(s)
                            </li>
                          )}
                        </ul>
                      </AlertDescription>
                    </Alert>
                  )}

                  <div className="flex gap-4 pt-4">
                    <Button onClick={() => navigate('/alunos')}>
                      Ver Lista de Alunos
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => {
                        setFile(null);
                        setResult(null);
                      }}
                    >
                      Importar Outro Arquivo
                    </Button>
                  </div>
                </>
              ) : (
                <Alert variant="destructive">
                  <XCircle className="h-4 w-4" />
                  <AlertTitle>Erro na importação</AlertTitle>
                  <AlertDescription>
                    {result.error || 'Não foi possível importar os alunos'}
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>
        )}

        {/* Instruções */}
        <Card>
          <CardHeader>
            <CardTitle>Formato do Arquivo Excel</CardTitle>
            <CardDescription>
              O arquivo deve conter as seguintes colunas obrigatórias:
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm">
              <p className="font-semibold">Colunas obrigatórias:</p>
              <ul className="list-disc list-inside space-y-1 text-muted-foreground ml-4">
                <li>aluno ou nome</li>
                <li>telefone</li>
                <li>cidade</li>
                <li>estado</li>
                <li>forma_pagamento</li>
                <li>data_vencimento</li>
              </ul>
              <p className="font-semibold mt-4">Colunas opcionais:</p>
              <ul className="list-disc list-inside space-y-1 text-muted-foreground ml-4">
                <li>nome_responsavel, telefone_responsavel</li>
                <li>data_nascimento</li>
                <li>Modalidades: dublagem_online, dublagem_presencial, teatro_online, etc.</li>
                <li>professor_nome, professor_modalidade, valor_mensalidade</li>
                <li>horario_dia_semana, horario_aula</li>
              </ul>
              <p className="text-xs text-muted-foreground mt-4">
                💡 Use o arquivo exemplo_importacao_alunos.xlsx como modelo
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}

