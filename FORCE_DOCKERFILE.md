# 🔧 Forçar Uso do Dockerfile no Railway

## ❌ Problema

O Railway está usando **Railpack** automaticamente e tentando executar:
```bash
pip install -r backend/requirements.txt
```

Isso causa erro porque o arquivo não está disponível no contexto de build.

## ✅ Solução: Usar Dockerfile

O projeto foi configurado para usar **Dockerfile** em vez de Railpack/Nixpacks.

### Configuração no Railway

1. **No painel do Railway**, vá em **Settings** → **Build**
2. Altere o **Builder** para **DOCKERFILE**
3. O Railway usará o `Dockerfile` que:
   - Instala apenas de `requirements.txt` da raiz
   - Não tenta acessar `backend/requirements.txt`
   - Funciona de forma confiável

### Arquivos Configurados

- ✅ `Dockerfile` - Configurado para usar `requirements.txt` da raiz
- ✅ `railway.toml` - Builder configurado como DOCKERFILE
- ✅ `railway.json` - Builder configurado como DOCKERFILE

### O que o Dockerfile faz

1. Usa Python 3.12
2. Copia `requirements.txt` da raiz
3. Instala todas as dependências de `requirements.txt`
4. Copia todo o código
5. Inicia o servidor no diretório `backend/`

## 🔍 Verificação

Após configurar o Dockerfile no Railway:

1. Faça commit e push das mudanças
2. O Railway fará rebuild usando Dockerfile
3. Verifique os logs - deve mostrar:
   ```
   pip install -r requirements.txt
   ```
4. **Não deve** mais tentar instalar de `backend/requirements.txt`

## ⚠️ Importante

- O `requirements.txt` na raiz contém **todas** as dependências necessárias
- Não é necessário `backend/requirements.txt` separadamente
- O Dockerfile garante que apenas `requirements.txt` da raiz seja usado

## 📝 Alternativa: Configuração Manual

Se o Railway ainda não usar o Dockerfile automaticamente:

1. No Railway, vá em **Settings** → **Build**
2. Em **Builder**, selecione **DOCKERFILE**
3. Em **Dockerfile Path**, deixe como `Dockerfile` (ou vazio)
4. Salve as configurações
