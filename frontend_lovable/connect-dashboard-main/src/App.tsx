import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "next-themes";
import { AuthProvider } from "@/contexts/AuthContext";
import { SidebarProvider } from "@/contexts/SidebarContext";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { RoleProtectedRoute } from "@/components/RoleProtectedRoute";
import Index from "./pages/Index";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Alunos from "./pages/Alunos";
import AlunoDetalhes from "./pages/AlunoDetalhes";
import AlunoForm from "./pages/AlunoForm";
import Professores from "./pages/Professores";
import ProfessorForm from "./pages/ProfessorForm";
import Pagamentos from "./pages/Pagamentos";
import Notas from "./pages/Notas";
import NotaForm from "./pages/NotaForm";
import UploadComprovante from "./pages/UploadComprovante";
import RecuperarSenha from "./pages/RecuperarSenha";
import GerarCodigoRecuperacao from "./pages/GerarCodigoRecuperacao";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <ThemeProvider attribute="class" defaultTheme="dark" enableSystem={false}>
      <BrowserRouter>
        <AuthProvider>
          <SidebarProvider>
            <TooltipProvider>
              <Toaster />
              <Sonner />
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/login" element={<Login />} />
            <Route path="/recuperar-senha" element={<RecuperarSenha />} />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/alunos"
              element={
                <ProtectedRoute>
                  <Alunos />
                </ProtectedRoute>
              }
            />
            <Route
              path="/alunos/:id"
              element={
                <ProtectedRoute>
                  <AlunoDetalhes />
                </ProtectedRoute>
              }
            />
            <Route
              path="/alunos/novo"
              element={
                <RoleProtectedRoute allowedRoles={['admin']} requireWrite={true}>
                  <AlunoForm />
                </RoleProtectedRoute>
              }
            />
            <Route
              path="/alunos/:id/editar"
              element={
                <RoleProtectedRoute allowedRoles={['admin']} requireWrite={true}>
                  <AlunoForm />
                </RoleProtectedRoute>
              }
            />
            <Route
              path="/professores"
              element={
                <RoleProtectedRoute allowedRoles={['admin', 'gerente']}>
                  <Professores />
                </RoleProtectedRoute>
              }
            />
            <Route
              path="/professores/novo"
              element={
                <RoleProtectedRoute allowedRoles={['admin']} requireWrite={true}>
                  <ProfessorForm />
                </RoleProtectedRoute>
              }
            />
            <Route
              path="/professores/:id/editar"
              element={
                <RoleProtectedRoute allowedRoles={['admin']} requireWrite={true}>
                  <ProfessorForm />
                </RoleProtectedRoute>
              }
            />
            <Route
              path="/pagamentos"
              element={
                <ProtectedRoute>
                  <Pagamentos />
                </ProtectedRoute>
              }
            />
            <Route
              path="/notas"
              element={
                <ProtectedRoute>
                  <Notas />
                </ProtectedRoute>
              }
            />
            <Route
              path="/notas/novo"
              element={
                <ProtectedRoute>
                  <NotaForm />
                </ProtectedRoute>
              }
            />
            <Route
              path="/notas/:id/editar"
              element={
                <ProtectedRoute>
                  <NotaForm />
                </ProtectedRoute>
              }
            />
            <Route
              path="/alunos/:alunoId/pagamento/upload"
              element={
                <RoleProtectedRoute allowedRoles={['admin', 'aluno']} requireWrite={true}>
                  <UploadComprovante />
                </RoleProtectedRoute>
              }
            />
            <Route
              path="/admin/gerar-codigo-recuperacao"
              element={
                <RoleProtectedRoute allowedRoles={['admin']}>
                  <GerarCodigoRecuperacao />
                </RoleProtectedRoute>
              }
            />
            <Route path="*" element={<NotFound />} />
          </Routes>
            </TooltipProvider>
          </SidebarProvider>
        </AuthProvider>
      </BrowserRouter>
    </ThemeProvider>
  </QueryClientProvider>
);

export default App;
