# Como Usar o Sistema em Múltiplas Máquinas

## Problema
SQLite usa um arquivo local, então cada máquina teria seu próprio banco de dados isolado. Para usar o sistema em múltiplas máquinas com dados compartilhados, você precisa de uma das soluções abaixo.

## ✅ Solução Recomendada: PostgreSQL (Banco de Dados Servidor)

### Por que PostgreSQL?
- ✅ Múltiplas máquinas podem acessar o mesmo banco simultaneamente
- ✅ Melhor desempenho e escalabilidade
- ✅ Transações e integridade de dados garantidas
- ✅ Backup e recuperação mais fáceis
- ✅ O sistema já está preparado para isso!

### Como Configurar

#### 1. Instalar PostgreSQL em um servidor

**No servidor (máquina central):**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# Criar banco de dados
sudo -u postgres psql
CREATE DATABASE controle_dublagem;
CREATE USER controle_user WITH PASSWORD 'sua_senha_segura';
GRANT ALL PRIVILEGES ON DATABASE controle_dublagem TO controle_user;
\q
```

#### 2. Configurar acesso remoto (opcional)

Edite `/etc/postgresql/[versão]/main/postgresql.conf`:
```
listen_addresses = '*'  # ou o IP específico do servidor
```

Edite `/etc/postgresql/[versão]/main/pg_hba.conf`:
```
# Permitir conexões de outras máquinas
host    controle_dublagem    controle_user    0.0.0.0/0    md5
```

Reinicie o PostgreSQL:
```bash
sudo systemctl restart postgresql
```

#### 3. Configurar cada máquina cliente

Em cada máquina que vai usar o sistema, defina a variável de ambiente:

```bash
# Linux/Mac
export DATABASE_URL="postgresql://controle_user:sua_senha_segura@IP_DO_SERVIDOR:5432/controle_dublagem"

# Windows (PowerShell)
$env:DATABASE_URL="postgresql://controle_user:sua_senha_segura@IP_DO_SERVIDOR:5432/controle_dublagem"

# Windows (CMD)
set DATABASE_URL=postgresql://controle_user:sua_senha_segura@IP_DO_SERVIDOR:5432/controle_dublagem
```

**Exemplo:**
```bash
export DATABASE_URL="postgresql://usuario:SUA_SENHA@IP_DO_SERVIDOR:5432/nome_do_banco"
```

#### 4. Instalar driver PostgreSQL no Python

Em cada máquina cliente:
```bash
pip install psycopg2-binary
```

Ou adicione ao `requirements.txt`:
```
psycopg2-binary>=2.9.0
```

#### 5. Executar o sistema

Agora todas as máquinas usarão o mesmo banco PostgreSQL:
```bash
python wsgi.py
```

### Migrar dados do SQLite para PostgreSQL

Se você já tem dados no SQLite e quer migrar:

```bash
# 1. Fazer backup do SQLite
cp /home/tiago/banco_lucy_prd /home/tiago/banco_lucy_prd_backup

# 2. Usar ferramenta de migração (ex: sqlite3 + psql)
# Ou criar um script Python para migrar os dados
```

---

## 🔄 Solução Alternativa: SQLite em Servidor de Arquivos Compartilhado

### Quando usar?
- Se você não pode instalar PostgreSQL
- Se todas as máquinas estão na mesma rede local
- ⚠️ **ATENÇÃO**: SQLite não é ideal para acesso simultâneo de múltiplos usuários

### Como Configurar

#### 1. Colocar o arquivo SQLite em um servidor de arquivos

**Opção A: Servidor NFS (Linux)**
```bash
# No servidor
sudo apt install nfs-kernel-server
sudo mkdir -p /shared/controle_dublagem
sudo chmod 777 /shared/controle_dublagem

# Adicionar ao /etc/exports
/shared/controle_dublagem *(rw,sync,no_subtree_check)

sudo exportfs -ra
sudo systemctl restart nfs-kernel-server

# Em cada máquina cliente
sudo apt install nfs-common
sudo mount -t nfs SERVIDOR_IP:/shared/controle_dublagem /mnt/controle_dublagem
```

**Opção B: Servidor SMB/CIFS (Windows/Linux)**
```bash
# No servidor (Linux com Samba)
sudo apt install samba
sudo mkdir -p /shared/controle_dublagem
sudo chmod 777 /shared/controle_dublagem

# Configurar /etc/samba/smb.conf
[controle_dublagem]
   path = /shared/controle_dublagem
   writable = yes
   guest ok = yes

sudo systemctl restart smbd

# Em cada máquina cliente (Linux)
sudo apt install cifs-utils
sudo mount -t cifs //SERVIDOR_IP/controle_dublagem /mnt/controle_dublagem -o username=guest
```

#### 2. Configurar o caminho do banco

Em cada máquina, defina:
```bash
export DATABASE_PATH="/mnt/controle_dublagem"
export ENVIRONMENT=prd
```

Ou edite o `config.py` para usar o caminho compartilhado.

#### 3. Limitações

⚠️ **IMPORTANTE**: SQLite não é recomendado para acesso simultâneo:
- Pode haver conflitos se múltiplos usuários escreverem ao mesmo tempo
- Performance degrada com muitos acessos simultâneos
- Risco de corrupção de dados em alta concorrência

---

## 🌐 Solução 3: Deploy em Servidor Web Único

### Quando usar?
- Se você quer acesso via navegador de qualquer lugar
- Se não precisa instalar em cada máquina

### Como Configurar

#### 1. Deploy em servidor web (já configurado para Render)

O sistema já está preparado para deploy no Render ou similar:

1. Configure `DATABASE_URL` no painel do Render
2. Faça deploy da aplicação
3. Acesse via navegador de qualquer máquina

Veja `RENDER_DEPLOY.md` para instruções detalhadas.

#### 2. Deploy local com acesso de rede

```bash
# No servidor
export DATABASE_PATH="/caminho/compartilhado"
export ENVIRONMENT=prd
python wsgi.py --host=0.0.0.0 --port=5000

# Acesse de outras máquinas via navegador
http://IP_DO_SERVIDOR:5000
```

---

## 📊 Comparação das Soluções

| Solução | Acesso Simultâneo | Facilidade | Performance | Recomendado |
|---------|-------------------|------------|-------------|-------------|
| PostgreSQL | ✅ Excelente | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ SIM |
| SQLite Compartilhado | ⚠️ Limitado | ⭐⭐ | ⭐⭐ | ⚠️ Não ideal |
| Servidor Web Único | ✅ Excelente | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ SIM |

---

## 🚀 Recomendação Final

**Para produção com múltiplas máquinas:**
1. **Use PostgreSQL** - É a solução mais robusta e o sistema já está preparado
2. Configure um servidor PostgreSQL centralizado
3. Configure `DATABASE_URL` em cada máquina cliente
4. Instale `psycopg2-binary` em cada máquina

**Para desenvolvimento/teste:**
- SQLite local está OK
- Para compartilhar entre poucas máquinas na mesma rede, SQLite compartilhado pode funcionar, mas com limitações

---

## 📝 Checklist de Migração para PostgreSQL

- [ ] Instalar PostgreSQL no servidor
- [ ] Criar banco de dados e usuário
- [ ] Configurar acesso remoto (se necessário)
- [ ] Instalar `psycopg2-binary` em cada máquina cliente
- [ ] Configurar `DATABASE_URL` em cada máquina
- [ ] Testar conexão de cada máquina
- [ ] Migrar dados do SQLite (se houver)
- [ ] Fazer backup regular do PostgreSQL

---

## 🔧 Troubleshooting

### Erro: "could not connect to server"
- Verifique se o PostgreSQL está rodando: `sudo systemctl status postgresql`
- Verifique firewall: `sudo ufw allow 5432`
- Verifique `postgresql.conf` e `pg_hba.conf`

### Erro: "password authentication failed"
- Verifique usuário e senha no `DATABASE_URL`
- Verifique permissões no `pg_hba.conf`

### Erro: "database does not exist"
- Crie o banco: `CREATE DATABASE controle_dublagem;`
- Verifique o nome no `DATABASE_URL`

