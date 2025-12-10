'use client';

import { useState, useEffect } from 'react';
import ExplicarForm from '@/app/components/ui/Explicarform';
import LoginForm from '@/app/components/ui/loginform';

export default function DashboardHome() {
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Verificar token no localStorage ao carregar
    if (typeof window !== 'undefined') {
      const storedToken = localStorage.getItem('token');
      setToken(storedToken);
    }
    setLoading(false);
  }, []);

  const handleLoginSuccess = (newToken: string) => {
    setToken(newToken);
  };

  const handleLogout = () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
      setToken(null);
    }
  };

  if (loading) {
    return <div className="main-content">Carregando...</div>;
  }

  if (!token) {
    return (
      <div className="main-content" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <LoginForm onLoginSuccess={handleLoginSuccess} />
      </div>
    );
  }

  return (
    <div className="main-content">
      <div style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 'bold', color: '#1e40af' }}>Dashboard MedQuest Research</h1>
        <button 
          onClick={handleLogout}
          className="card-button"
          style={{ backgroundColor: '#dc2626' }}
        >
          Sair
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6" style={{ marginBottom: '2rem' }}>
        {/* CARD 1 */}
        <div className="analysis-card">
          <h2 className="card-title">Bem-vindo ao MedQuestResearch</h2>
          <p style={{ color: '#64748b', lineHeight: '1.6' }}>
            Aqui você pode analisar artigos, gerar relatórios críticos,
            organizar estudos e acompanhar suas análises realizadas.
          </p>
        </div>

        {/* CARD 2 */}
        <div className="analysis-card">
          <h2 className="card-title">Últimas Análises</h2>
          <p style={{ color: '#64748b' }}>Nenhuma análise recente.</p>
        </div>

        {/* CARD 3 */}
        <div className="analysis-card">
          <h2 className="card-title">Próximos Passos</h2>
          <ul style={{ color: '#64748b', lineHeight: '1.8' }}>
            <li>Enviar um novo artigo</li>
            <li>Executar análise IA</li>
            <li>Visualizar relatórios</li>
          </ul>
        </div>
      </div>

      {/* Formulário de Explicar Conceito */}
      <ExplicarForm token={token} />
    </div>
  );
}
  