# 💰 Como Adicionar Créditos aos Usuários

## 📋 Métodos Disponíveis

### 1. **Via API REST** (Recomendado)

#### Endpoint
```
POST /genapi/admin/adicionar-creditos
```

#### Autenticação
Requer token Bearer no header:
```
Authorization: Bearer SEU_TOKEN
```

#### Body da Requisição
```json
{
  "usuario_id": 1,        // Opcional - ID do usuário
  "email": "user@email.com",  // Opcional - Email do usuário
  "quantidade": 100       // Obrigatório - Quantidade de créditos a adicionar
}
```

**Nota:** Deve fornecer `usuario_id` OU `email` (não ambos necessariamente, mas pelo menos um).

#### Exemplo com cURL
```bash
# Por email
curl -X POST https://medquestresearch-api.up.railway.app/genapi/admin/adicionar-creditos \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -d '{
    "email": "usuario@email.com",
    "quantidade": 100
  }'

# Por ID
curl -X POST https://medquestresearch-api.up.railway.app/genapi/admin/adicionar-creditos \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -d '{
    "usuario_id": 1,
    "quantidade": 50
  }'
```

#### Resposta de Sucesso
```json
{
  "mensagem": "Créditos adicionados com sucesso",
  "usuario": {
    "id": 1,
    "nome": "Nome do Usuário",
    "email": "usuario@email.com",
    "creditos_anteriores": 50,
    "creditos_adicionados": 100,
    "creditos_atuais": 150,
    "creditos_usados": 10,
    "creditos_disponiveis": 140
  }
}
```

### 2. **Via Script Python** (Linha de Comando)

#### Localização
```
backend/adicionar_creditos.py
```

#### Uso
```bash
# Por email
python backend/adicionar_creditos.py usuario@email.com 100

# Por ID
python backend/adicionar_creditos.py 1 50
```

#### Exemplo
```bash
cd backend
python adicionar_creditos.py usuario@exemplo.com 100
```

#### Saída
```
✅ Créditos adicionados com sucesso!
   Usuário: João Silva (usuario@exemplo.com)
   Créditos anteriores: 50
   Créditos adicionados: 100
   Créditos atuais: 150
   Créditos usados: 5
   Créditos disponíveis: 145
```

### 3. **Via Frontend** (Função JavaScript)

#### Função Disponível
```typescript
import { adicionarCreditos } from '@/app/lib/api';

// Por email
const resultado = await adicionarCreditos(token, {
  email: 'usuario@email.com',
  quantidade: 100
});

// Por ID
const resultado = await adicionarCreditos(token, {
  usuario_id: 1,
  quantidade: 50
});
```

## 🔒 Segurança

- ✅ Requer autenticação (token Bearer)
- ✅ Rate limiting: 20 requisições por minuto
- ✅ Validação de entrada (quantidade > 0)
- ✅ Validação de usuário existente

## ⚠️ Observações

1. **Quantidade mínima:** Deve ser maior que zero
2. **Identificação:** Pode usar `usuario_id` OU `email` (não precisa dos dois)
3. **Créditos acumulativos:** Os créditos são somados aos créditos existentes
4. **Não há limite máximo:** Pode adicionar qualquer quantidade de créditos

## 📊 Estrutura do Banco de Dados

A tabela `usuarios` possui os campos:
- `id`: ID único do usuário
- `email`: Email do usuário
- `creditos`: Total de créditos do usuário
- `creditos_usados`: Créditos já utilizados

## 🧪 Testando

### 1. Verificar créditos atuais
```bash
GET /genapi/creditos
Authorization: Bearer TOKEN
```

### 2. Adicionar créditos
```bash
POST /genapi/admin/adicionar-creditos
Authorization: Bearer TOKEN
{
  "email": "usuario@email.com",
  "quantidade": 100
}
```

### 3. Verificar créditos atualizados
```bash
GET /genapi/creditos
Authorization: Bearer TOKEN
```

## 🔍 Troubleshooting

### Erro: "Usuário não encontrado"
- Verifique se o email ou ID está correto
- Verifique se o usuário existe no banco de dados

### Erro: "Quantidade deve ser maior que zero"
- A quantidade deve ser um número positivo
- Exemplo válido: `100`, `50`, `1`
- Exemplo inválido: `0`, `-10`

### Erro: "Deve fornecer usuario_id ou email"
- Forneça pelo menos um dos campos: `usuario_id` ou `email`
