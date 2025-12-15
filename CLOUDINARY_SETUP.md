# Configuração do Cloudinary

## Variáveis de Ambiente Necessárias

Para que o sistema de upload de comprovantes funcione, você precisa configurar as seguintes variáveis de ambiente:

### Local (Desenvolvimento)

Crie um arquivo `.env` na raiz do projeto (ou configure no seu sistema):

```bash
CLOUDINARY_CLOUD_NAME=docvxvt4v
CLOUDINARY_API_KEY=456143563259539
CLOUDINARY_API_SECRET=2Pa5SBVCTrGlFpKmFJGaX86vc9Y
```

**⚠️ IMPORTANTE**: O arquivo `.env` está no `.gitignore` e NÃO será commitado no Git.

### Render (Produção)

No painel do Render, vá em **Environment** e adicione as seguintes variáveis:

- **CLOUDINARY_CLOUD_NAME**: `docvxvt4v`
- **CLOUDINARY_API_KEY**: `456143563259539`
- **CLOUDINARY_API_SECRET**: `2Pa5SBVCTrGlFpKmFJGaX86vc9Y`

## Como Funciona

1. **Upload**: Quando um aluno envia um comprovante, a imagem é enviada para o Cloudinary
2. **Armazenamento**: O Cloudinary armazena a imagem de forma segura e otimizada
3. **URL**: Uma URL segura (HTTPS) é gerada e armazenada no banco de dados
4. **Acesso**: Administradores podem visualizar os comprovantes através da URL

## Segurança

- ✅ As credenciais são armazenadas apenas em variáveis de ambiente
- ✅ Nenhuma credencial é commitada no Git
- ✅ URLs geradas são seguras (HTTPS)
- ✅ Arquivos são organizados por aluno no Cloudinary (`comprovantes/{aluno_id}/`)

## Limites do Plano Gratuito

- **Armazenamento**: 25 GB
- **Bandwidth**: 25 GB/mês
- **Transformações**: Ilimitadas

## Troubleshooting

### Erro: "Invalid API Key"
- Verifique se as variáveis de ambiente estão configuradas corretamente
- Certifique-se de que não há espaços extras nas credenciais

### Erro: "Upload failed"
- Verifique sua conexão com a internet
- Verifique se o arquivo não excede 10MB
- Verifique se o formato do arquivo é suportado (PNG, JPG, JPEG, GIF, PDF, WEBP)

### Imagens não aparecem
- Verifique se a URL do Cloudinary está sendo gerada corretamente
- Verifique se o Cloudinary está acessível (pode ser bloqueado por firewall)

