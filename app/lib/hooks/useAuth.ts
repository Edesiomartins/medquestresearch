'use client';

import { useState, useEffect } from 'react';
import { login as apiLogin, getCreditos, ApiResponse } from '../api';

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

  const logout = () => {
    setToken(null);
    setUsuario(null);
    setCreditos(0);
    setErro('');
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
    }
  };

  const fetchUserData = async (tokenValue: string) => {
    try {
      const res = await getCreditos(tokenValue);
      if (res.erro) {
        setErro(res.erro);
        logout();
      } else {
        setCreditos(res.creditos || 0);
        setUsuario(res.usuario || null);
      }
    } catch (error: any) {
      console.error('Erro ao buscar dados do usuário:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Verificar token no localStorage ao montar
    if (typeof window !== 'undefined') {
      const storedToken = localStorage.getItem('token');
      if (storedToken) {
        setToken(storedToken);
        // Buscar créditos e informações do usuário
        fetchUserData(storedToken);
      } else {
        setLoading(false);
      }
    }
  }, []);

  const login = async (email: string, senha: string): Promise<boolean> => {
    setLoading(true);
    setErro('');
    try {
      const res = await apiLogin(email, senha);
      if (res.erro) {
        setErro(res.erro);
        setLoading(false);
        return false;
      }
      if (res.token) {
        setToken(res.token);
        if (typeof window !== 'undefined') {
          localStorage.setItem('token', res.token);
        }
        setUsuario(res.usuario || null);
        setCreditos(res.creditos || 0);
        setLoading(false);
        return true;
      }
      setLoading(false);
      return false;
    } catch (error: any) {
      setErro(error.message || 'Erro ao fazer login');
      setLoading(false);
      return false;
    }
  };

  return {
    token,
    usuario,
    creditos,
    loading,
    erro,
    login,
    logout,
  };
}

