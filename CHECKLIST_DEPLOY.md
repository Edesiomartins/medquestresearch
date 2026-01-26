# ✅ Checklist de Deploy - Correções CORS

## 📋 Antes de Fazer Deploy

### Backend (já commitado ✅)
- [x] CORS configurado com modo debug
- [x] Middleware HTTP para garantir headers CORS
- [x] Handler OPTIONS melhorado
- [x] Rotas de debug criadas (`/routes`, `/genapi/test`)
- [x] Logs de debug adicionados

### Frontend (já commitado ✅)
- [x] Correção automática de URL antiga
- [x] Logs informativos
- [x] Fallback seguro para URL padrão

## 🚀 Passos para Deploy

### 1. Fazer Push das Alterações
```bash
git push origin main
```

### 2. No Railway - Backend
- [ ] Aguardar deploy automático completar
- [ ] Verificar logs para confirmar que iniciou corretamente
- [ ] Testar rota: `https://medquestresearch-api.up.railway.app/routes`
- [ ] Deve listar todas as rotas incluindo `/genapi/cadastro`

### 3. No Railway - Frontend (CRÍTICO)
- [ ] Ir em **Variables** do serviço frontend
- [ ] Verificar `NEXT_PUBLIC_API_BASE_URL`
- [ ] Deve ser: `https://medquestresearch-api.up.railway.app` (sem hífen)
- [ ] Se estiver com hífen, corrigir e salvar
- [ ] Fazer **Redeploy** ou **Deploy** para forçar novo build

### 4. Testar Aplicação
- [ ] Abrir `https://medquestresearch.up.railway.app`
- [ ] Abrir DevTools (F12) → Console
- [ ] Verificar log: `🔗 API Base URL configurada: https://medquestresearch-api.up.railway.app`
- [ ] Tentar fazer login/cadastro
- [ ] Verificar Network tab - requisições devem ir para URL correta
- [ ] Não deve aparecer erro de CORS

## 🔍 Verificações Pós-Deploy

### Backend
```bash
# Testar rota de debug
curl https://medquestresearch-api.up.railway.app/routes

# Testar rota de teste
curl https://medquestresearch-api.up.railway.app/genapi/test

# Testar health
curl https://medquestresearch-api.up.railway.app/health
```

### Frontend
1. Abrir console do navegador
2. Verificar se não há erros de CORS
3. Verificar se URL está correta nos logs
4. Testar funcionalidades principais

## 🐛 Se Ainda Houver Problemas

### Erro: URL antiga ainda sendo chamada
1. Verificar variável `NEXT_PUBLIC_API_BASE_URL` no Railway
2. Fazer commit vazio para forçar rebuild:
   ```bash
   git commit --allow-empty -m "force rebuild"
   git push
   ```

### Erro: CORS ainda bloqueando
1. Ativar modo debug temporariamente no backend:
   - Adicionar variável: `DEBUG_CORS=true`
   - Fazer redeploy
   - Testar novamente
   - Remover após confirmar funcionamento

### Erro: 404 nas rotas
1. Verificar se router foi incluído nos logs
2. Acessar `/routes` para ver todas as rotas
3. Verificar se `/genapi/cadastro` está listada

## 📞 Suporte

- Ver documentação: `CORRIGIR_URL_RAILWAY.md`
- Ver resumo completo: `RESUMO_CORRECOES_CORS.md`
