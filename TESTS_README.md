# Testes – Funcionalidade de Submissão de Exames

Este documento explica como executar e entender os testes da funcionalidade de submissão de exames.

## Visão Geral dos Testes

Os testes foram implementados usando **pytest** com **pytest-django** e cobrem:

### ✅ **Testes de Estrutura** (`test_exam_functionality.py`)
- **Importações**: Verifica se todos os módulos podem ser importados
- **Estrutura dos Models**: Valida campos, relacionamentos e constraints
- **Serializers**: Testa estrutura dos serializers da API
- **URLs**: Verifica configuração das rotas
- **Funcionalidade dos Models**: Testa criação, propriedades e validações

### Testes de Integração da API (`test_api_integration.py`)
- **Submissão de Exames**: Testa endpoint de submissão com cenários válidos e inválidos
- **Resultados de Exames**: Testa endpoints de consulta de resultados
- **Workflow Completo**: Testa fluxo completo (submissão → consulta de resultados)

## Como Executar os Testes

### Opção 1: Script automatizado (recomendado)
```powershell
python app/run_tests.py
```

### Opção 2: Pytest Direto
```powershell
# Todos os testes
python -m pytest app/test_exam_functionality.py app/test_api_integration.py -v

# Apenas testes de estrutura
python -m pytest test_exam_functionality.py -v

# Apenas testes de API
python -m pytest test_api_integration.py -v

# Teste específico
python -m pytest test_exam_functionality.py::TestModelFunctionality::test_exam_submission_creation -v
```

### Opção 3: Teste Específico
```powershell
python app/run_tests.py app/test_exam_functionality.py::TestImports
```

## Cobertura dos Testes

### Models Testados
- ✅ `ExamSubmission`: Criação, propriedades, constraints
- ✅ `SubmissionAnswer`: Criação, validação, propriedade `is_correct`
- ✅ Cálculo de score e contagem de respostas corretas
- ✅ Constraint de unicidade (estudante + exame)

### API Endpoints Testados
- ✅ `POST /api/exam/submissions/` (assíncrono) – Submissão de respostas
  - Cenário de sucesso
  - Validação de estudante inválido
  - Validação de exame inválido
  - Validação de questões inválidas
  - Prevenção de submissões duplicadas
  - Validação de opções de resposta

- ✅ `GET /api/exam/submissions/status/?task_id=<uuid>` – Acompanhar processamento da submissão

- ✅ `GET /api/exam/results/{submission_id}/` - Resultados por ID
  - Consulta bem-sucedida
  - Detalhes das questões
  - Cálculo de score
  - Tratamento de 404

- ✅ `GET /api/exam/submissions/?student_id={student_id}&exam_id={exam_id}` – Resultados por estudante+exame
  - Consulta bem-sucedida
  - Mesmos dados do endpoint principal

### Serializers Testados
- ✅ `ExamSubmissionCreateSerializer`: Estrutura e validações
- ✅ `ExamResultSerializer`: Estrutura e dados de resultado
- ✅ `AnswerSubmissionSerializer`: Validação de opções

## Configuração dos Testes

### Arquivos de configuração
- **`pytest.ini`**: Configurações do pytest
- **`conftest.py`**: Setup do Django para pytest
- **`test_settings.py`**: Settings específicos para testes (SQLite em memória)

### Banco de dados de teste
Os testes usam SQLite em memória (`:memory:`) para:
- ✅ Execução rápida
- ✅ Isolamento completo
- ✅ Limpeza automática

## Cenários de Teste Cobertos

### Cenários de sucesso
- Submissão completa de um exame
- Consulta de resultados detalhados
- Cálculo correto de score
- Workflow completo (submissão → resultados)

### Cenários de erro
- Estudante inexistente
- Exame inexistente
- Questões que não pertencem ao exame
- Submissões duplicadas
- Opções de resposta inválidas
- Consulta de resultados inexistentes

### Validações testadas
- Unicidade de submissão por estudante/exame
- Integridade referencial (FK constraints)
- Validação de dados de entrada
- Serialização correta de respostas

## Interpretando os Resultados

### Saída de Sucesso
```
TODOS OS TESTES PASSARAM!
Total: 3/3 testes passaram
============================= 27 passed in 0.37s ==============================
```

### Saída de Falha
```
❌ ALGUNS TESTES FALHARAM
FAILED test_exam_functionality.py::TestModelFunctionality::test_name - AssertionError: ...
```

## Debugging de testes

### Executar com mais detalhes
```powershell
python -m pytest test_exam_functionality.py -v -s --tb=long
```

### Executar teste específico que falhou
```powershell
python -m pytest test_api_integration.py::TestExamSubmissionAPI::test_submit_exam_success -v -s
```

### Ver duração dos testes
```powershell
python -m pytest test_exam_functionality.py --durations=10
```

## Execução Contínua

Para desenvolvimento ativo, use:
```powershell
python -m pytest test_exam_functionality.py --lf  # Apenas testes que falharam
python -m pytest test_exam_functionality.py -x    # Para no primeiro erro
```

---

## Checklist de Testes

- ✅ Todos os imports funcionam
- ✅ Models têm estrutura correta  
- ✅ Serializers têm campos necessários
- ✅ URLs estão configuradas
- ✅ Submissão de exame funciona
- ✅ Validações impedem dados inválidos
- ✅ Resultados são calculados corretamente
- ✅ Endpoints retornam dados esperados
- ✅ Workflow completo funciona

**Status**: ✅ **27/27 testes passando**
