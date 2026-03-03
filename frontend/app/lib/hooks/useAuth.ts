'use client';

import { useState, useEffect } from 'react';
import {
  login as apiLogin,
  cadastro as apiCadastro,
  getCreditos,
} from '../api';

interface Usuario {
  id?: string;
  nome?: string;
  email?: string;
}

export function useAuth() {
  const [token, setToken] = useState<string | null>(null);
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [creditos, setCreditos] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [erro, setErro] = useState<string>('');

  /* =========================
     Helpers internos
  ========================= */

  const hydrateSession = (
    tokenValue: string,
    usuarioValue?: Usuario | null,
    creditosValue?: number
  ) => {
    setToken(tokenValue);
    if (usuarioValue) setUsuario(usuarioValue);
    if (typeof creditosValue === 'number') setCreditos(creditosValue);

    if (typeof window !== 'undefined') {
      localStorage.setItem('token', tokenValue);
      if (usuarioValue) {
        localStorage.setItem('usuario', JSON.stringify(usuarioValue));
      }
      if (typeof creditosValue === 'number') {
        localStorage.setItem('creditos', String(creditosValue));
      }
    }
  };

  const clearSession = () => {
    setToken(null);
    setUsuario(null);
    setCreditos(0);
    setErro('');

    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
      localStorage.removeItem('usuario');
      localStorage.removeItem('creditos');
    }
  };

  /* =========================
     Bootstrap da sessão
  ========================= */

  useEffect(() => {
    if (typeof window === 'undefined') {
      setLoading(false);
      return;
    }

    const storedToken = localStorage.getItem('token');
    
    if (storedToken) {
      // Não define o token ainda - aguarda validação
      // Isso evita flash do dashboard antes da verificação
      fetchUserData(storedToken);
    } else {
      setLoading(false);
    }
  }, []);

  /* =========================
     Fetch pós-login
  ========================= */

  const fetchUserData = async (tokenValue: string) => {
    try {
      const res = await getCreditos(tokenValue);

      if (res.erro) {
        setErro(res.erro);
        clearSession();
        setLoading(false);
      } else {
        // Só define o token após validação bem-sucedida
        setToken(tokenValue);
        // No backend, /creditos retorna:
        // - creditos: total adquirido
        // - creditos_usados: já consumidos
        // - creditos_disponiveis: saldo atual
        if (typeof (res as any).creditos_disponiveis === 'number') {
          setCreditos((res as any).creditos_disponiveis);
        } else if (typeof res.creditos === 'number') {
          // Fallback para compatibilidade antiga
          setCreditos(res.creditos);
        }
        if (res.usuario) {
          setUsuario(res.usuario);
        }
        setLoading(false);
      }
    } catch (error) {
      console.error('Erro ao buscar dados do usuário:', error);
      clearSession();
      setLoading(false);
    }
  };

  /* =========================
     LOGIN
  ========================= */

  const login = async (email: string, senha: string): Promise<boolean> => {
    setLoading(true);
    setErro('');

    try {
      const res = await apiLogin(email, senha);

      if (res.erro || !res.token) {
        setErro(res.erro || 'Erro ao fazer login');
        setLoading(false);
        return false;
      }

      const creditosDisponiveis =
        (res as any).creditos_disponiveis ?? res.creditos;
      hydrateSession(res.token, res.usuario, creditosDisponiveis);
      setLoading(false);
      return true;
    } catch (error: any) {
      setErro(error.message || 'Erro ao fazer login');
      setLoading(false);
      return false;
    }
  };

  /* =========================
     CADASTRO (NOVO)
  ========================= */

  const register = async (
    nome: string,
    email: string,
    senha: string
  ): Promise<boolean> => {
    setLoading(true);
    setErro('');

    try {
      const res = await apiCadastro(nome, email, senha);

      if (res.erro || !res.token) {
        setErro(res.erro || 'Erro ao cadastrar');
        setLoading(false);
        return false;
      }

      const creditosDisponiveis =
        (res as any).creditos_disponiveis ?? res.creditos;
      hydrateSession(res.token, res.usuario, creditosDisponiveis);
      setLoading(false);
      return true;
    } catch (error: any) {
      setErro(error.message || 'Erro ao cadastrar');
      setLoading(false);
      return false;
    }
  };

  /* =========================
     LOGOUT
  ========================= */

  const logout = () => {
    clearSession();
  };

  return {
    token,
    usuario,
    creditos,
    loading,
    erro,
    login,
    register, // 👈 agora existe
    logout,
  };
}
