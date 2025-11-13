# Documentação da API de Submissão de Exames

Este documento explica como usar as funcionalidades de submissão de exames e visualização de resultados.

## Visão Geral

O sistema fornece duas funcionalidades principais:
1. **Submeter Respostas do Exame**: Estudantes podem submeter todas as suas respostas de um exame de uma só vez
2. **Visualizar Resultados**: Estudantes podem visualizar seus resultados detalhados incluindo respostas corretas/incorretas e porcentagem de acerto

## Modelos do Banco de Dados

### ExamSubmission (Submissão de Exame)
- `student`: Chave estrangeira para o modelo Student
- `exam`: Chave estrangeira para o modelo Exam
- `submitted_at`: Timestamp de quando foi submetido
- `score`: Propriedade que calcula a porcentagem de acerto
- `correct_answers_count`: Propriedade que conta as respostas corretas
- Constraint único em (student, exam) - uma submissão por estudante por exame

### SubmissionAnswer (Resposta da Submissão)
- `submission`: Chave estrangeira para ExamSubmission
- `question`: Chave estrangeira para Question
- `selected_alternative_option`: Inteiro (1-5 representando A-E)
- `is_correct`: Propriedade que verifica se a resposta está correta
- Constraint único em (submission, question) - uma resposta por questão por submissão

## Endpoints da API

### 1. Submeter Respostas do Exame
**POST** `/api/exam/submit/`

Submete todas as respostas de um exame de uma só vez.

**Corpo da Requisição:**
```json
{
    "student_id": 1,
    "exam_id": 1,
    "answers": [
        {"question_id": 1, "selected_option": 3},
        {"question_id": 2, "selected_option": 2},
        {"question_id": 3, "selected_option": 1},
        {"question_id": 4, "selected_option": 4},
        {"question_id": 5, "selected_option": 2}
    ]
}
```

**Resposta (Sucesso - 201):**
```json
{
    "success": true,
    "message": "Exame submetido com sucesso",
    "submission_id": 1,
    "submitted_at": "2025-11-13T14:53:21.123456Z",
    "total_answers": 5
}
```

**Resposta (Erro - 400):**
```json
{
    "success": false,
    "errors": {
        "student_id": ["Estudante não existe"],
        "answers": ["Questões [6, 7] não pertencem ao exame 1"]
    }
}
```

### 2. Obter Resultados do Exame (por ID da submissão)
**GET** `/api/exam/results/{submission_id}/`

Obtém resultados detalhados para uma submissão específica.

**Resposta (200):**
```json
{
    "success": true,
    "results": {
        "id": 1,
        "student_name": "João Silva",
        "exam_name": "Prova Falsa 1",
        "submitted_at": "2025-11-13T14:53:21.123456Z",
        "total_questions": 5,
        "correct_answers": 4,
        "score_percentage": 80.0,
        "questions": [
            {
                "id": 1,
                "content": "Qual parte do corpo usamos para ouvir?",
                "student_answer": 3,
                "student_answer_letter": "C",
                "correct_answer": 3,
                "correct_answer_letter": "C",
                "is_correct": true,
                "alternatives": [
                    {"option": 1, "option_letter": "A", "content": "Dentes", "is_correct": false},
                    {"option": 2, "option_letter": "B", "content": "Cabelos", "is_correct": false},
                    {"option": 3, "option_letter": "C", "content": "Ouvidos", "is_correct": true},
                    {"option": 4, "option_letter": "D", "content": "Braços", "is_correct": false}
                ]
            }
            // ... mais questões
        ]
    }
}
```

### 3. Obter Resultados do Exame (por ID do estudante e exame)
**GET** `/api/exam/student/{student_id}/exam/{exam_id}/results/`

Endpoint alternativo para obter resultados usando IDs do estudante e exame.

Mesmo formato de resposta do endpoint anterior.

## Regras de Validação

### Validação da Submissão
- Estudante deve existir
- Exame deve existir
- Todas as questões devem existir e pertencer ao exame especificado
- Não pode haver questões duplicadas na lista de respostas
- Estudante não pode submeter o mesmo exame duas vezes
- Opção selecionada deve estar entre 1-5 (A-E)

### Cenários de Erro
- **404**: Submissão não encontrada (para endpoints de resultados)
- **400**: Erros de validação (dados inválidos, submissão duplicada, etc.)

## Exemplos de Uso

### Exemplo 1: Fluxo completo
1. Estudante submete respostas para o exame ID 1
2. Sistema valida todos os dados e cria a submissão
3. Estudante pode visualizar resultados usando o ID da submissão ou IDs do estudante/exame

### Exemplo 2: Opções de resposta
- Opção 1 = A
- Opção 2 = B  
- Opção 3 = C
- Opção 4 = D
- Opção 5 = E

## Configuração do Banco de Dados

Para aplicar as migrações:
```bash
python manage.py makemigrations exam
python manage.py migrate
```

O sistema cria automaticamente as tabelas ExamSubmission e SubmissionAnswer com os relacionamentos e constraints apropriados.