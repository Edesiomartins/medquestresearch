# 🔧 Correção do Erro de Build no Vercel

## ❌ Erro Encontrado

```
Error: > Couldn't find any `pages` or `app` directory. Please create one under the project root
```

## ✅ Soluções

### Solução 1: Verificar Root Directory no Vercel (Recomendado)

1. Acesse o painel do Vercel: https://vercel.com
2. Selecione seu projeto **MedquestResearch**
3. Vá em **Settings** → **General**
4. Role até a seção **Root Directory**
5. Certifique-se de que está configurado como:
   - **`.`** (ponto) ou **vazio** (raiz do projeto)
   - **NÃO** deve ter nenhum subdiretório como `frontend` ou `app`

### Solução 2: Verificar Estrutura do Projeto

Certifique-se de que a estrutura está assim na raiz:

```
MedquestResearch/
├── app/              ← Deve estar na raiz
│   ├── page.tsx
│   ├── layout.tsx
│   └── ...
├── package.json      ← Deve estar na raiz
├── next.config.ts    ← Deve estar na raiz
├── tsconfig.json     ← Deve estar na raiz
└── vercel.json       ← Deve estar na raiz
```

### Solução 3: Atualizar vercel.json

O arquivo `vercel.json` foi atualizado para garantir que o root directory está correto:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "installCommand": "npm install",
  "framework": "nextjs"
}
```

⚠️ **NOTA**: A propriedade `rootDirectory` não é mais suportada pelo Vercel. Configure o Root Directory nas Settings do projeto no Vercel.

### Solução 4: Verificar no Painel do Vercel

1. Vá em **Settings** → **General**
2. Verifique as seguintes configurações:

   **Build & Development Settings:**
   - Framework Preset: `Next.js`
   - Root Directory: `.` (ou vazio)
   - Build Command: `npm run build` (ou deixe vazio para auto-detectar)
   - Output Directory: `.next` (ou deixe vazio para auto-detectar)
   - Install Command: `npm install` (ou deixe vazio para auto-detectar)

### Solução 5: Limpar Cache e Fazer Novo Deploy

Se ainda não funcionar:

1. No Vercel, vá em **Deployments**
2. Clique nos três pontos (⋯) do último deploy
3. Selecione **"Redeploy"**
4. Marque a opção **"Use existing Build Cache"** como **DESMARCADA**
5. Clique em **"Redeploy"**

## 🔍 Verificações Adicionais

### Verificar se os arquivos estão no Git

Certifique-se de que os seguintes arquivos estão commitados:

```bash
# Verificar estrutura
ls -la app/
ls -la package.json
ls -la next.config.ts
ls -la tsconfig.json
```

### Verificar package.json

O `package.json` deve ter os scripts corretos:

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  }
}
```

### Verificar next.config.ts

O arquivo `next.config.ts` deve existir e estar configurado corretamente.

## 📝 Passos para Resolver

1. ✅ Verifique o Root Directory no Vercel (deve ser `.` ou vazio)
2. ✅ Certifique-se de que o diretório `app/` está na raiz do projeto
3. ✅ Verifique se `package.json` e `next.config.ts` estão na raiz
4. ✅ Faça commit e push das alterações
5. ✅ Faça um novo deploy no Vercel (ou aguarde deploy automático)
6. ✅ Se ainda não funcionar, limpe o cache e faça redeploy

## 🆘 Se Nada Funcionar

1. **Verifique os logs do build** no Vercel:
   - Vá em **Deployments** → Clique no deploy que falhou
   - Veja os logs completos do build

2. **Teste localmente**:
   ```bash
   npm install
   npm run build
   ```
   Se funcionar localmente, o problema é na configuração do Vercel.

3. **Crie um novo projeto** no Vercel:
   - Às vezes recriar o projeto resolve problemas de configuração
   - Importe o mesmo repositório do GitHub
   - Configure as variáveis de ambiente novamente

## ✅ Estrutura Correta Esperada

```
MedquestResearch/                    ← Raiz do repositório Git
├── app/                            ← Diretório do Next.js App Router
│   ├── page.tsx
│   ├── layout.tsx
│   ├── globals.css
│   └── lib/
│       └── api-config.ts
├── package.json                    ← Deve estar na raiz
├── next.config.ts                  ← Deve estar na raiz
├── tsconfig.json                   ← Deve estar na raiz
├── vercel.json                     ← Configuração do Vercel
└── ... (outros arquivos)
```

