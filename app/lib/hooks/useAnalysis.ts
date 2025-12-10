'use client';

import { useState } from 'react';
import { explicarConceito, analisarCritica, verificarFatos, pesquisarPerspectiva, uploadPdf, ApiResponse } from '../api';

export function useAnalysis(token: string) {
  const [loading, setLoading] = useState(false);
  const [erro, setErro] = useState<string>('');
  const [resultado, setResultado] = useState<string>('');

  const explicar = async (data: { texto_artigo: string; trecho: string; nivel: string }) => {
    setLoading(true);
    setErro('');
    setResultado('');
    try {
      const res = await explicarConceito(token, data.texto_artigo, data.trecho, data.nivel);
      if (res.erro) {
        setErro(res.erro);
      } else {
        setResultado(res.resultado || '');
      }
    } catch (error: any) {
      setErro(error.message || 'Erro ao explicar conceito');
    } finally {
      setLoading(false);
    }
  };

  const critica = async (texto_artigo: string) => {
    setLoading(true);
    setErro('');
    setResultado('');
    try {
      const res = await analisarCritica(token, texto_artigo);
      if (res.erro) {
        setErro(res.erro);
      } else {
        setResultado(res.resultado || '');
      }
    } catch (error: any) {
      setErro(error.message || 'Erro ao analisar crítica');
    } finally {
      setLoading(false);
    }
  };

  const fatos = async (texto_artigo: string) => {
    setLoading(true);
    setErro('');
    setResultado('');
    try {
      const res = await verificarFatos(token, texto_artigo);
      if (res.erro) {
        setErro(res.erro);
      } else {
        setResultado(res.resultado || '');
      }
    } catch (error: any) {
      setErro(error.message || 'Erro ao verificar fatos');
    } finally {
      setLoading(false);
    }
  };

  const perspectiva = async (texto_artigo: string) => {
    setLoading(true);
    setErro('');
    setResultado('');
    try {
      const res = await pesquisarPerspectiva(token, texto_artigo);
      if (res.erro) {
        setErro(res.erro);
      } else {
        setResultado(res.resultado || '');
      }
    } catch (error: any) {
      setErro(error.message || 'Erro ao pesquisar perspectiva');
    } finally {
      setLoading(false);
    }
  };

  const pdf = async (file: File) => {
    setLoading(true);
    setErro('');
    setResultado('');
    try {
      const res = await uploadPdf(token, file);
      if (res.erro) {
        setErro(res.erro);
      } else {
        setResultado(res.resultado || '');
      }
    } catch (error: any) {
      setErro(error.message || 'Erro ao fazer upload do PDF');
    } finally {
      setLoading(false);
    }
  };

  return {
    loading,
    erro,
    resultado,
    explicar,
    critica,
    fatos,
    perspectiva,
    pdf,
  };
}

