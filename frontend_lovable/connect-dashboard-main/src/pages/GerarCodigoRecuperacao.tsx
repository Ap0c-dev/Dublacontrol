import { useState } from 'react';
import { MainLayout } from '@/components/layout/MainLayout';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, Copy, Check } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@/contexts/AuthContext';

export default function GerarCodigoRecuperacao() {
  const [username, setUsername] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [codigoGerado, setCodigoGerado] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const { toast } = useToast();
  const { isAdmin } = useAuth();

  if (!isAdmin()) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-destructive mb-2">Acesso Negado</h1>
            <p className="text-muted-foreground">
              Apenas administradores podem acessar esta página.
            </p>
          </div>
        </div>
      </MainLayout>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!username) {
      toast({
        title: 'Campo obrigatório',
        description: 'Por favor, digite o username do usuário.',
        variant: 'destructive',
      });
      return;
    }

    setIsLoading(true);
    setCodigoGerado(null);

    try {
      const result = await api.gerarCodigoRecuperacao(username);
      
      if (result.success && result.data) {
        setCodigoGerado(result.data.codigo);
        toast({
          title: 'Código gerado!',
          description: `Código gerado com sucesso para o usuário ${result.data.usuario}.`,
        });
      } else {
        toast({
          title: 'Erro ao gerar código',
          description: result.error || 'Não foi possível gerar o código.',
          variant: 'destructive',
        });
      }
    } catch (error) {
      toast({
        title: 'Erro de conexão',
        description: 'Não foi possível conectar ao servidor.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = () => {
    if (codigoGerado) {
      navigator.clipboard.writeText(codigoGerado);
      setCopied(true);
      toast({
        title: 'Código copiado!',
        description: 'O código foi copiado para a área de transferência.',
      });
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <MainLayout>
      <div className="space-y-6 max-w-2xl mx-auto">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-gradient">Gerar Código de Recuperação</h1>
          <p className="text-muted-foreground mt-1">
            Gere um código de recuperação de senha para um usuário
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Gerar Código</CardTitle>
            <CardDescription>
              Digite o username do usuário para gerar um código de recuperação de senha.
              O código será válido por 24 horas.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="username">Username do Usuário</Label>
                <Input
                  id="username"
                  type="text"
                  placeholder="Digite o username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  disabled={isLoading}
                />
              </div>

              <Button
                type="submit"
                variant="gradient"
                className="w-full"
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="animate-spin mr-2" />
                    Gerando código...
                  </>
                ) : (
                  'Gerar Código'
                )}
              </Button>
            </form>

            {codigoGerado && (
              <div className="mt-6 p-4 bg-card border border-border rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <Label className="text-sm font-semibold">Código Gerado:</Label>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={copyToClipboard}
                    className="h-8"
                  >
                    {copied ? (
                      <>
                        <Check size={16} className="mr-2" />
                        Copiado!
                      </>
                    ) : (
                      <>
                        <Copy size={16} className="mr-2" />
                        Copiar
                      </>
                    )}
                  </Button>
                </div>
                <div className="bg-muted p-3 rounded-md font-mono text-lg text-center tracking-wider font-bold">
                  {codigoGerado}
                </div>
                <p className="text-xs text-muted-foreground mt-3 text-center">
                  ⚠️ Compartilhe este código com o usuário. Ele será válido por 24 horas e pode ser usado apenas uma vez.
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Como funciona?</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-muted-foreground">
            <p>1. Digite o username do usuário que precisa recuperar a senha</p>
            <p>2. Clique em "Gerar Código" para criar um código único</p>
            <p>3. Compartilhe o código com o usuário (via WhatsApp, pessoalmente, etc.)</p>
            <p>4. O usuário acessa a página de recuperação de senha e usa o código</p>
            <p>5. O código expira em 24 horas e pode ser usado apenas uma vez</p>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}

