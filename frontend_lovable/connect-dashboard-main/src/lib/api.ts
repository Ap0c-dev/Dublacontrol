// Usa variável de ambiente ou localhost por padrão
// Remove barra final se existir para evitar barras duplas
const rawUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api/v1';
const API_BASE_URL = rawUrl.endsWith('/') ? rawUrl.slice(0, -1) : rawUrl;

// Log para debug
console.log('🔧 API_BASE_URL:', API_BASE_URL);
console.log('🔧 VITE_API_BASE_URL:', import.meta.env.VITE_API_BASE_URL);

interface ApiResponse<T> {
  success: boolean;
  data: T;
  count?: number;
  error?: string;
  message?: string;
}

interface LoginResponse {
  success: boolean;
  token: string;
  user: {
    id: number;
    username: string;
    nome: string;
    role: string;
    is_admin: boolean;
    is_professor: boolean;
    is_aluno: boolean;
    is_gerente: boolean;
    is_readonly: boolean;
    professor_id?: number | null;
    aluno_id?: number | null;
  };
  message?: string;
  error?: string;
}

interface DashboardStats {
  total_alunos: number;
  total_professores: number;
  total_pagamentos: number;
  pagamentos_atrasados: number;
  receita_mensal: number;
}

interface Aluno {
  id: number;
  nome: string;
  email: string;
  telefone: string;
  data_nascimento: string;
  status: string;
  created_at: string;
}

interface Professor {
  id: number;
  nome: string;
  email: string;
  especialidade: string;
  status: string;
  ativo?: boolean;
}

interface Pagamento {
  id: number;
  aluno_id: number;
  aluno_nome: string;
  valor: number;
  data_vencimento: string;
  data_pagamento: string | null;
  status: string;
}

interface Nota {
  id: number;
  aluno_id: number;
  aluno_nome: string;
  professor_id: number;
  professor_nome: string;
  tipo_curso: string;
  valor: number | null;
  media: number | null;
  criterio1: number | null;
  criterio2: number | null;
  criterio3: number | null;
  criterio4: number | null;
  numero_prova: number | null;
  tipo_avaliacao: string | null;
  observacao: string | null;
  data_avaliacao: string;
  data_cadastro: string;
}

class ApiClient {
  private getToken(): string | null {
    return localStorage.getItem('token');
  }

  private getHeaders(): HeadersInit {
    const token = this.getToken();
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
      console.log('🔑 Token sendo enviado:', token.substring(0, 20) + '...');
    } else {
      console.warn('⚠️ Nenhum token encontrado no localStorage');
      console.warn('⚠️ localStorage.getItem("token"):', localStorage.getItem('token'));
      console.warn('⚠️ localStorage.getItem("user"):', localStorage.getItem('user'));
    }
    return headers;
  }

  async login(username: string, password: string): Promise<LoginResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success && data.token) {
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
        console.log('✅ Token salvo no localStorage:', data.token.substring(0, 20) + '...');
      } else {
        console.error('❌ Login falhou ou token não recebido:', data);
      }
      
      return data;
    } catch (error) {
      console.error('Erro ao fazer login:', error);
      return {
        success: false,
        error: 'Erro de conexão com o servidor. Verifique se o servidor está rodando.',
        message: error instanceof Error ? error.message : 'Erro desconhecido'
      };
    }
  }

  async logout(): Promise<void> {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }

  async getMe(): Promise<ApiResponse<LoginResponse['user']>> {
    try {
      const headers = this.getHeaders();
      console.log('🔍 Verificando token com /auth/me...');
      
      const response = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: headers,
      });
      
      if (response.status === 401) {
        console.error('❌ Token inválido ou expirado');
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        return {
          success: false,
          error: 'Token inválido ou expirado',
          data: { 
            id: 0, 
            username: '', 
            nome: '',
            role: '',
            is_admin: false,
            is_professor: false,
            is_aluno: false,
            is_gerente: false,
            is_readonly: false
          }
        };
      }
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Erro na resposta:', response.status, errorText);
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('✅ Usuário autenticado:', data);
      // Atualizar localStorage com dados completos
      if (data.success && data.data) {
        localStorage.setItem('user', JSON.stringify(data.data));
      }
      return data;
    } catch (error) {
      console.error('❌ Erro ao buscar dados do usuário:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Erro de conexão com o servidor',
        data: { 
          id: 0, 
          username: '', 
          nome: '',
          role: '',
          is_admin: false,
          is_professor: false,
          is_aluno: false,
          is_gerente: false,
          is_readonly: false
        }
      };
    }
  }

  async getDashboardStats(): Promise<ApiResponse<DashboardStats>> {
    try {
      const headers = this.getHeaders();
      console.log('🔍 Headers sendo enviados:', headers);
      
      const response = await fetch(`${API_BASE_URL}/dashboard/stats`, {
        headers: headers,
      });
      
      console.log('📡 Resposta do servidor:', response.status, response.statusText);
      
      if (response.status === 401) {
        console.error('❌ Erro 401: Não autenticado. Token pode estar inválido ou expirado.');
        // Limpar token inválido
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        // Redirecionar para login será feito pelo ProtectedRoute
        return {
          success: false,
          error: 'Não autenticado. Por favor, faça login novamente.',
          data: {
            total_alunos: 0,
            total_professores: 0,
            total_pagamentos: 0,
            pagamentos_atrasados: 0,
            receita_mensal: 0
          }
        };
      }
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Erro na resposta:', response.status, errorText);
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('✅ Dados recebidos:', data);
      console.log('📊 Pagamentos atrasados na resposta:', data?.data?.pagamentos_atrasados);
      // Garantir que pagamentos_atrasados existe e é um número
      if (data.success && data.data) {
        if (!('pagamentos_atrasados' in data.data) || data.data.pagamentos_atrasados === null || data.data.pagamentos_atrasados === undefined) {
          console.warn('⚠️ Campo pagamentos_atrasados não encontrado ou inválido na resposta, usando 0');
          data.data.pagamentos_atrasados = 0;
        } else {
          data.data.pagamentos_atrasados = Number(data.data.pagamentos_atrasados) || 0;
        }
        console.log('📊 Pagamentos atrasados após tratamento:', data.data.pagamentos_atrasados);
      }
      return data;
    } catch (error) {
      console.error('❌ Erro ao buscar estatísticas:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Erro de conexão com o servidor',
        data: {
          total_alunos: 0,
          total_professores: 0,
          total_pagamentos: 0,
          pagamentos_atrasados: 0,
          receita_mensal: 0
        }
      };
    }
  }

  async getAlunos(filters?: { search?: string; status?: string; professor_id?: string }): Promise<ApiResponse<Aluno[]>> {
    try {
      const params = new URLSearchParams();
      if (filters?.search) params.append('search', filters.search);
      if (filters?.status) params.append('status', filters.status);
      if (filters?.professor_id) params.append('professor_id', filters.professor_id);
      
      const url = `${API_BASE_URL}/alunos${params.toString() ? `?${params}` : ''}`;
      const response = await fetch(url, {
        headers: this.getHeaders(),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    } catch (error) {
      console.error('Erro ao buscar alunos:', error);
      return {
        success: false,
        error: 'Erro de conexão com o servidor',
        data: []
      };
    }
  }

  async getAluno(id: number): Promise<ApiResponse<Aluno>> {
    try {
      const response = await fetch(`${API_BASE_URL}/alunos/${id}`, {
        headers: this.getHeaders(),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    } catch (error) {
      console.error('Erro ao buscar aluno:', error);
      return {
        success: false,
        error: 'Erro de conexão com o servidor',
        data: {} as Aluno
      };
    }
  }

  async getProfessores(): Promise<ApiResponse<Professor[]>> {
    try {
      const response = await fetch(`${API_BASE_URL}/professores`, {
        headers: this.getHeaders(),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    } catch (error) {
      console.error('Erro ao buscar professores:', error);
      return {
        success: false,
        error: 'Erro de conexão com o servidor',
        data: []
      };
    }
  }

  async getProfessor(id: number): Promise<ApiResponse<Professor>> {
    try {
      const response = await fetch(`${API_BASE_URL}/professores/${id}`, {
        headers: this.getHeaders(),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    } catch (error) {
      console.error('Erro ao buscar professor:', error);
      return {
        success: false,
        error: 'Erro de conexão com o servidor',
        data: {} as Professor
      };
    }
  }

  async getPagamentos(filters?: { status?: string; aluno_id?: number; professor_id?: number }): Promise<ApiResponse<Pagamento[]>> {
    try {
      const params = new URLSearchParams();
      if (filters?.status) params.append('status', filters.status);
      if (filters?.aluno_id) params.append('aluno_id', filters.aluno_id.toString());
      if (filters?.professor_id) params.append('professor_id', filters.professor_id.toString());
      
      const url = `${API_BASE_URL}/pagamentos${params.toString() ? `?${params}` : ''}`;
      const response = await fetch(url, {
        headers: this.getHeaders(),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    } catch (error) {
      console.error('Erro ao buscar pagamentos:', error);
      return {
        success: false,
        error: 'Erro de conexão com o servidor',
        data: []
      };
    }
  }

  async getNotas(filters?: { aluno_id?: number; professor_id?: number; tipo_curso?: string }): Promise<ApiResponse<Nota[]>> {
    try {
      const params = new URLSearchParams();
      if (filters?.aluno_id) params.append('aluno_id', filters.aluno_id.toString());
      if (filters?.professor_id) params.append('professor_id', filters.professor_id.toString());
      if (filters?.tipo_curso) params.append('tipo_curso', filters.tipo_curso);
      
      const url = `${API_BASE_URL}/notas${params.toString() ? `?${params}` : ''}`;
      const response = await fetch(url, {
        headers: this.getHeaders(),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    } catch (error) {
      console.error('Erro ao buscar notas:', error);
      return {
        success: false,
        error: 'Erro de conexão com o servidor',
        data: []
      };
    }
  }

  async getNota(id: number): Promise<ApiResponse<Nota>> {
    try {
      const response = await fetch(`${API_BASE_URL}/notas/${id}`, {
        headers: this.getHeaders(),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    } catch (error) {
      console.error('Erro ao buscar nota:', error);
      return {
        success: false,
        error: 'Erro de conexão com o servidor',
        data: {} as Nota
      };
    }
  }

  async criarNota(nota: Partial<Nota>): Promise<ApiResponse<Nota>> {
    try {
      const response = await fetch(`${API_BASE_URL}/notas`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(nota),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    } catch (error) {
      console.error('Erro ao criar nota:', error);
      return {
        success: false,
        error: 'Erro ao criar nota',
        data: {} as Nota
      };
    }
  }

  async editarNota(id: number, nota: Partial<Nota>): Promise<ApiResponse<Nota>> {
    try {
      const response = await fetch(`${API_BASE_URL}/notas/${id}`, {
        method: 'PUT',
        headers: this.getHeaders(),
        body: JSON.stringify(nota),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    } catch (error) {
      console.error('Erro ao editar nota:', error);
      return {
        success: false,
        error: 'Erro ao editar nota',
        data: {} as Nota
      };
    }
  }

  async excluirNota(id: number): Promise<ApiResponse<void>> {
    try {
      const response = await fetch(`${API_BASE_URL}/notas/${id}`, {
        method: 'DELETE',
        headers: this.getHeaders(),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    } catch (error) {
      console.error('Erro ao excluir nota:', error);
      return {
        success: false,
        error: 'Erro ao excluir nota',
        data: undefined
      };
    }
  }

  async criarAluno(aluno: Partial<Aluno>): Promise<ApiResponse<Aluno>> {
    try {
      const response = await fetch(`${API_BASE_URL}/alunos`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(aluno),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        console.error('❌ Erro na resposta da API:', response.status, data);
        return {
          success: false,
          error: data.error || `Erro HTTP ${response.status}`,
          data: {} as Aluno
        };
      }
      
      return data;
    } catch (error) {
      console.error('Erro ao criar aluno:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Erro ao criar aluno',
        data: {} as Aluno
      };
    }
  }

  async editarAluno(id: number, aluno: Partial<Aluno>): Promise<ApiResponse<Aluno>> {
    try {
      const response = await fetch(`${API_BASE_URL}/alunos/${id}`, {
        method: 'PUT',
        headers: this.getHeaders(),
        body: JSON.stringify(aluno),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    } catch (error) {
      console.error('Erro ao editar aluno:', error);
      return {
        success: false,
        error: 'Erro ao editar aluno',
        data: {} as Aluno
      };
    }
  }

  async excluirAluno(id: number): Promise<ApiResponse<void>> {
    try {
      const response = await fetch(`${API_BASE_URL}/alunos/${id}`, {
        method: 'DELETE',
        headers: this.getHeaders(),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    } catch (error) {
      console.error('Erro ao excluir aluno:', error);
      return {
        success: false,
        error: 'Erro ao excluir aluno',
        data: undefined
      };
    }
  }

  async criarProfessor(professor: Partial<Professor>): Promise<ApiResponse<Professor>> {
    try {
      const response = await fetch(`${API_BASE_URL}/professores`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(professor),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    } catch (error) {
      console.error('Erro ao criar professor:', error);
      return {
        success: false,
        error: 'Erro ao criar professor',
        data: {} as Professor
      };
    }
  }

  async editarProfessor(id: number, professor: Partial<Professor>): Promise<ApiResponse<Professor>> {
    try {
      const headers = this.getHeaders();
      console.log('🔍 Editando professor:', id);
      console.log('🔑 Headers:', headers);
      
      const response = await fetch(`${API_BASE_URL}/professores/${id}`, {
        method: 'PUT',
        headers: headers,
        body: JSON.stringify(professor),
      });
      
      console.log('📡 Resposta do servidor:', response.status, response.statusText);
      
      if (response.status === 401) {
        console.error('❌ Erro 401: Não autenticado. Token pode estar inválido ou expirado.');
        // Limpar token inválido
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        // Redirecionar para login
        setTimeout(() => {
          window.location.href = '/login';
        }, 1000);
        throw new Error('Sessão expirada. Redirecionando para login...');
      }
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`HTTP error! status: ${response.status} - ${errorData.error || response.statusText}`);
      }
      return response.json();
    } catch (error) {
      console.error('Erro ao editar professor:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Erro ao editar professor',
        data: {} as Professor
      };
    }
  }

  async getProfessoresPorModalidade(modalidade: string): Promise<ApiResponse<Professor[]>> {
    try {
      const headers = this.getHeaders();
      console.log('🔍 Buscando professores por modalidade:', modalidade);
      console.log('🔑 Headers:', headers);
      
      const response = await fetch(`${API_BASE_URL}/professores/por-modalidade?modalidade=${encodeURIComponent(modalidade)}`, {
        headers: headers,
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Erro na resposta:', response.status, errorText);
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    } catch (error) {
      console.error('Erro ao buscar professores por modalidade:', error);
      return {
        success: false,
        error: 'Erro de conexão com o servidor',
        data: []
      };
    }
  }

  async getHorariosProfessor(professorId: number, modalidade?: string): Promise<ApiResponse<any[]>> {
    try {
      let url = `${API_BASE_URL}/professores/${professorId}/horarios`;
      if (modalidade) {
        url += `?modalidade=${encodeURIComponent(modalidade)}`;
      }
      console.log('🔍 Buscando horários do professor:', professorId, 'modalidade:', modalidade);
      console.log('🔍 URL:', url);
      
      const headers = this.getHeaders();
      const response = await fetch(url, {
        headers: headers,
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Erro na resposta:', response.status, errorText);
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('✅ Horários recebidos:', data);
      return data;
    } catch (error) {
      console.error('Erro ao buscar horários do professor:', error);
      return {
        success: false,
        error: 'Erro de conexão com o servidor',
        data: []
      };
    }
  }

  async excluirProfessor(id: number): Promise<ApiResponse<void>> {
    try {
      const response = await fetch(`${API_BASE_URL}/professores/${id}`, {
        method: 'DELETE',
        headers: this.getHeaders(),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    } catch (error) {
      console.error('Erro ao excluir professor:', error);
      return {
        success: false,
        error: 'Erro ao excluir professor',
        data: undefined
      };
    }
  }

  async aprovarPagamento(id: number, observacoes?: string): Promise<ApiResponse<Pagamento>> {
    try {
      const response = await fetch(`${API_BASE_URL}/pagamentos/${id}/aprovar`, {
        method: 'PUT',
        headers: this.getHeaders(),
        body: JSON.stringify({ observacoes_admin: observacoes }),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    } catch (error) {
      console.error('Erro ao aprovar pagamento:', error);
      return {
        success: false,
        error: 'Erro ao aprovar pagamento',
        data: {} as Pagamento
      };
    }
  }

  async rejeitarPagamento(id: number, observacoes?: string): Promise<ApiResponse<Pagamento>> {
    try {
      const response = await fetch(`${API_BASE_URL}/pagamentos/${id}/rejeitar`, {
        method: 'PUT',
        headers: this.getHeaders(),
        body: JSON.stringify({ observacoes_admin: observacoes }),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    } catch (error) {
      console.error('Erro ao rejeitar pagamento:', error);
      return {
        success: false,
        error: 'Erro ao rejeitar pagamento',
        data: {} as Pagamento
      };
    }
  }

  async getMatriculas(filters?: { aluno_id?: number; professor_id?: number; tipo_curso?: string }): Promise<ApiResponse<any[]>> {
    try {
      const params = new URLSearchParams();
      if (filters?.aluno_id) params.append('aluno_id', filters.aluno_id.toString());
      if (filters?.professor_id) params.append('professor_id', filters.professor_id.toString());
      if (filters?.tipo_curso) params.append('tipo_curso', filters.tipo_curso);
      
      const url = `${API_BASE_URL}/matriculas${params.toString() ? `?${params}` : ''}`;
      const response = await fetch(url, {
        headers: this.getHeaders(),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    } catch (error) {
      console.error('Erro ao buscar matrículas:', error);
      return {
        success: false,
        error: 'Erro de conexão com o servidor',
        data: []
      };
    }
  }

  async uploadComprovante(
    alunoId: number,
    mesReferencia: number,
    anoReferencia: number,
    valorPago: number,
    dataPagamento: string,
    comprovante: File,
    observacoes?: string
  ): Promise<ApiResponse<any>> {
    try {
      const formData = new FormData();
      formData.append('aluno_id', alunoId.toString());
      formData.append('mes_referencia', mesReferencia.toString());
      formData.append('ano_referencia', anoReferencia.toString());
      formData.append('valor_pago', valorPago.toString());
      formData.append('data_pagamento', dataPagamento);
      formData.append('comprovante', comprovante);
      if (observacoes) {
        formData.append('observacoes', observacoes);
      }

      const response = await fetch(`${API_BASE_URL}/pagamentos/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.getToken()}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }
      return response.json();
    } catch (error) {
      console.error('Erro ao fazer upload do comprovante:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Erro ao fazer upload do comprovante',
        data: null
      };
    }
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  getUser(): LoginResponse['user'] | null {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  }

  // ==================== RECUPERAÇÃO DE SENHA ====================

  async gerarCodigoRecuperacao(username: string): Promise<ApiResponse<{ codigo: string; usuario: string; valido_ate: string }>> {
    try {
      const headers = this.getHeaders();
      const response = await fetch(`${API_BASE_URL}/auth/reset-password/generate-code`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({ username }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Erro ao gerar código de recuperação:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Erro ao gerar código de recuperação',
        data: { codigo: '', usuario: '', valido_ate: '' }
      };
    }
  }

  async usarCodigoRecuperacao(codigo: string, novaSenha: string): Promise<ApiResponse<void>> {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/reset-password/use-code`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ codigo: codigo.toUpperCase(), nova_senha: novaSenha }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Erro ao usar código de recuperação:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Erro ao resetar senha',
        data: undefined
      };
    }
  }

  async resetarSenhaAdmin(username: string, novaSenha: string): Promise<ApiResponse<void>> {
    try {
      const headers = this.getHeaders();
      const response = await fetch(`${API_BASE_URL}/auth/reset-password/admin`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({ username, nova_senha: novaSenha }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Erro ao resetar senha via admin:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Erro ao resetar senha',
        data: undefined
      };
    }
  }

  async alterarSenha(senhaAtual: string, novaSenha: string): Promise<ApiResponse<void>> {
    try {
      const headers = this.getHeaders();
      const response = await fetch(`${API_BASE_URL}/auth/reset-password/change`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({ senha_atual: senhaAtual, nova_senha: novaSenha }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Erro ao alterar senha:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Erro ao alterar senha',
        data: undefined
      };
    }
  }
}

export const api = new ApiClient();
export type { Aluno, Professor, Pagamento, Nota, DashboardStats, LoginResponse, ApiResponse };
