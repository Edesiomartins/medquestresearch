# 🔧 Correção do Erro de Build no Railway

## Problema
O Railway está tentando instalar de `backend/requirements.txt` mas o arquivo não está sendo encontrado no contexto de build.

## Solução

O `requirements.txt` na raiz já contém todas as dependências necessárias. O Railway deve usar esse arquivo.

### Opção 1: Usar Nixpacks (Recomendado)

O `nixpacks.toml` já está configurado para usar `requirements.txt` da raiz:

```toml
[phases.install]
cmds = [
  "pip install --upgrade pip",
  "pip install -r requirements.txt"
]
```

**No Railway:**
1. Vá em **Settings** → **Build**
2. Certifique-se de que o **Builder** está configurado como **NIXPACKS**
3. O Railway deve usar o `nixpacks.toml` automaticamente

### Opção 2: Usar Dockerfile

Se o Nixpacks não funcionar, você pode usar o `Dockerfile` criado:

1. No Railway, vá em **Settings** → **Build**
2. Altere o **Builder** para **DOCKERFILE**
3. O Railway usará o `Dockerfile` que instala de `requirements.txt` da raiz

### Opção 3: Configurar Root Directory

Se o Railway ainda tentar instalar de `backend/requirements.txt`:

1. No Railway, vá em **Settings** → **Service**
2. Configure o **Root Directory** como vazio (raiz do projeto)
3. Isso garante que o Railway veja o `requirements.txt` na raiz

## Verificação

Após fazer as alterações:
1. Faça commit e push das mudanças
2. O Railway fará rebuild automaticamente
3. Verifique os logs para confirmar que está instalando de `requirements.txt` (raiz)

## Arquivos Atualizados

- ✅ `requirements.txt` (raiz) - Contém todas as dependências
- ✅ `nixpacks.toml` - Configurado para usar `requirements.txt` da raiz
- ✅ `Dockerfile` - Alternativa usando Docker
- ✅ `railway.json` - Configuração do Railway
