# 🔌 API ViewSets - Documentação Completa

Esta documentação descreve as novas APIs baseadas em ViewSets que seguem as melhores práticas do Django REST Framework.

## 📋 Visão Geral das Melhorias

### ✅ **Implementação com ViewSets**
- **ModelViewSet** completo com operações CRUD
- **Filtros avançados** com django-filter
- **Paginação automática** 
- **Busca textual** integrada
- **Ordenação flexível**
- **Permissões granulares**

### ✅ **Endpoints Otimizados**
- **select_related** e **prefetch_related** para performance
- **Serializers específicos** por action
- **Actions customizadas** para funcionalidades especiais
- **Validações robustas**

---

## 🎯 **ExamViewSet - Gerenciamento de Exames**

**Base URL:** `/api/exam/exams/`

### **Endpoints CRUD**

| Método | URL | Descrição | Permissão |
|--------|-----|-----------|-----------|
| `GET` | `/api/exam/exams/` | Listar todos os exames | Público |
| `POST` | `/api/exam/exams/` | Criar novo exame | Autenticado |
| `GET` | `/api/exam/exams/{id}/` | Obter exame específico | Público |
| `PUT` | `/api/exam/exams/{id}/` | Atualizar exame completo | Autenticado |
| `PATCH` | `/api/exam/exams/{id}/` | Atualizar exame parcialmente | Autenticado |
| `DELETE` | `/api/exam/exams/{id}/` | Deletar exame | Autenticado |

### **Actions Customizadas**

#### **📊 Estatísticas do Exame**
```http
GET /api/exam/exams/{id}/statistics/
```

**Resposta:**
```json
{
    "success": true,
    "exam_name": "Prova de Matemática",
    "statistics": {
        "total_submissions": 45,
        "average_score": 78.5,
        "questions_statistics": [
            {
                "question_id": 1,
                "question_content": "Quanto é 2+2?",
                "question_number": 1,
                "correct_answers": 42,
                "total_answers": 45,
                "accuracy_percentage": 93.33
            }
        ]
    }
}
```

### **Filtros e Busca**

#### **Parâmetros de URL Suportados:**

| Parâmetro | Tipo | Descrição | Exemplo |
|-----------|------|-----------|---------|
| `search` | String | Busca por nome | `?search=matemática` |
| `name` | String | Filtro por nome (contém) | `?name=prova` |
| `has_questions` | Boolean | Exames com/sem questões | `?has_questions=true` |
| `min_questions` | Integer | Mínimo de questões | `?min_questions=5` |
| `ordering` | String | Ordenação | `?ordering=name` ou `?ordering=-name` |

#### **Exemplos de Uso:**
```bash
# Buscar exames por nome
GET /api/exam/exams/?search=matemática

# Filtrar exames com pelo menos 10 questões
GET /api/exam/exams/?min_questions=10

# Ordenar por nome (A-Z)
GET /api/exam/exams/?ordering=name

# Combinando filtros
GET /api/exam/exams/?has_questions=true&ordering=-name&search=prova
```

---

## 🎯 **ExamSubmissionViewSet - Gerenciamento de Submissões**

**Base URL:** `/api/exam/submissions/`

### **Endpoints CRUD**

| Método | URL | Descrição | Permissão |
|--------|-----|-----------|-----------|
| `GET` | `/api/exam/submissions/` | Listar submissões | Público |
| `POST` | `/api/exam/submissions/` | Criar nova submissão | Público |
| `GET` | `/api/exam/submissions/{id}/` | Obter submissão específica | Público |
| `PUT` | `/api/exam/submissions/{id}/` | Atualizar submissão | Autenticado |
| `DELETE` | `/api/exam/submissions/{id}/` | Deletar submissão | Autenticado |

### **Actions Customizadas**

#### **👤 Minhas Submissões**
```http
GET /api/exam/submissions/student_submission/?student_id={id}
```

**Resposta:**
```json
{
    "success": true,
    "student_id": "1",
    "total_submissions": 3,
    "average_score": 85.5,
    "submissions": [
        {
            "id": 1,
            "exam_name": "Matemática",
            "score_percentage": 90.0,
            "submitted_at": "2025-11-13T10:30:00Z"
        }
    ]
}
```

#### **📈 Análise Detalhada**
```http
GET /api/exam/submissions/{id}/detailed_analysis/
```

**Resposta:**
```json
{
    "success": true,
    "submission": {
        "id": 1,
        "student_name": "João Silva",
        "exam_name": "Matemática",
        "score_percentage": 85.0,
        "correct_answers": 17,
        "total_questions": 20
    },
    "comparison": {
        "exam_average_score": 72.5,
        "your_score": 85.0,
        "percentile": 78.5,
        "total_submissions": 150
    }
}
```

#### **🔍 Busca por Estudante/Exame**
```http
GET /api/exam/submissions/student/{student_id}/exam/{exam_id}/
```

### **Filtros e Busca**

#### **Parâmetros de URL Suportados:**

| Parâmetro | Tipo | Descrição | Exemplo |
|-----------|------|-----------|---------|
| `search` | String | Busca por nome do estudante/exame | `?search=joão` |
| `student` | Integer | ID do estudante | `?student=1` |
| `exam` | Integer | ID do exame | `?exam=2` |
| `student_name` | String | Nome do estudante (contém) | `?student_name=silva` |
| `exam_name` | String | Nome do exame (contém) | `?exam_name=matemática` |
| `min_score` | Float | Pontuação mínima | `?min_score=70` |
| `max_score` | Float | Pontuação máxima | `?max_score=90` |
| `submitted_date_after` | Date | Data mínima | `?submitted_date_after=2025-11-01` |
| `submitted_date_before` | Date | Data máxima | `?submitted_date_before=2025-11-30` |
| `ordering` | String | Ordenação | `?ordering=-submitted_at` |

#### **Exemplos de Uso:**
```bash
# Submissões de um estudante específico
GET /api/exam/submissions/?student=1

# Submissões com pontuação entre 70 e 90
GET /api/exam/submissions/?min_score=70&max_score=90

# Submissões do último mês, ordenadas por data
GET /api/exam/submissions/?submitted_date_after=2025-10-13&ordering=-submitted_at

# Busca por nome do estudante
GET /api/exam/submissions/?search=joão silva
```

---

## 🔄 **Compatibilidade com APIs Antigas**

Para manter compatibilidade, os endpoints antigos continuam funcionando:

| Antigo | Novo Equivalente |
|--------|------------------|
| `POST /api/exam/submit/` | `POST /api/exam/submissions/` |
| `GET /api/exam/results/{id}/` | `GET /api/exam/submissions/{id}/` |

---

## 📝 **Exemplo Completo de Uso**

### **1. Criar Submissão**
```bash
curl -X POST http://localhost:8000/api/exam/submissions/ \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "exam_id": 2,
    "answers": [
      {"question_id": 5, "selected_option": 3},
      {"question_id": 6, "selected_option": 1}
    ]
  }'
```

### **2. Obter Resultados**
```bash
curl http://localhost:8000/api/exam/submissions/1/
```

### **3. Ver Análise Detalhada**
```bash
curl http://localhost:8000/api/exam/submissions/1/detailed_analysis/
```

### **4. Listar Submissões Filtradas**
```bash
curl "http://localhost:8000/api/exam/submissions/?student_name=joão&min_score=80&ordering=-submitted_at"
```

---

## 🧪 **Testando as APIs**

### **Executar Testes**
```bash
# Testes específicos das ViewSets
python -m pytest test_exam_viewsets.py -v

# Todos os testes
python run_tests.py
```

### **Testes Incluídos**
- ✅ CRUD completo para Exams e Submissions
- ✅ Filtros e busca
- ✅ Actions customizadas
- ✅ Validações de dados
- ✅ Permissões
- ✅ Performance com select_related

---

## 🎯 **Benefícios das Novas ViewSets**

### **📈 Performance**
- Queries otimizadas com select_related/prefetch_related
- Paginação automática para grandes datasets
- Cache de querysets quando apropriado

### **🔍 Flexibilidade**
- Filtros avançados para consultas específicas
- Busca textual integrada
- Ordenação por múltiplos campos
- Serializers diferentes por action

### **🛡️ Robustez**
- Validações automáticas do DRF
- Tratamento de erros consistente
- Permissões granulares
- Logs automáticos de operações

### **📋 Manutenibilidade**
- Código organizado em classes
- Padrões consistentes do DRF
- Testes abrangentes
- Documentação automática via DRF

**As ViewSets oferecem uma API moderna, robusta e escalável seguindo as melhores práticas do Django REST Framework!** 🚀