# 🎓 Plataforma Estudantil - Backend

Este repositório contém um projeto Django REST Framework para uma plataforma de exames estudantis, já configurado e pronto para uso.

## 🚀 Funcionalidades Implementadas

### ✅ **Sistema de Exames**
- **Submissão de Respostas**: Estudantes podem submeter todas as respostas de um exame de uma vez
- **Visualização de Resultados**: Consulta detalhada de resultados com pontuação e análise por questão
- **Validações Completas**: Sistema robusto de validação para prevenir erros e duplicações

### 📊 **Modelos de Dados**
- **Estudantes (Student)**: Modelo customizado de usuário
- **Questões (Question)** e **Alternativas (Alternative)**: Sistema de múltipla escolha
- **Exames (Exam)**: Coleção organizada de questões
- **Submissões (ExamSubmission)** e **Respostas (SubmissionAnswer)**: Armazenamento de respostas dos estudantes

## 🔧 Configuração e Execução

### Pré-requisitos
- Docker e Docker Compose instalados no computador

### 1. Executar o Projeto
```bash
docker compose up --build
```

Isso inicializará o servidor na porta 8000.

### 2. Acessar o Container
Com o projeto rodando, abra outro terminal e execute:
```bash
docker exec -it medway-api bash
```

### 3. Criar Superusuário
Dentro do container, crie um usuário administrador:
```bash
python manage.py createsuperuser
```

### 4. Acessar o Admin
Use as credenciais criadas para acessar: http://localhost:8000/admin/

## 📋 Dados de Teste

O projeto já vem com dados populados para facilitar o desenvolvimento:
- ✅ 3 exames de exemplo ("Prova Falsa 1", "Prova Falsa 2", "Prova Falsa 3")
- ✅ Questões de múltipla escolha sobre anatomia humana
- ✅ Alternativas A-E para cada questão
- ✅ Respostas corretas já definidas

## 🔌 API Endpoints

### Submissão de Exames
```http
POST /api/exam/submit/
```

### Resultados por ID da Submissão  
```http
GET /api/exam/results/{submission_id}/
```

### Resultados por Estudante e Exame
```http
GET /api/exam/student/{student_id}/exam/{exam_id}/results/
```

## 📚 Documentação Completa

- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Documentação completa da API com exemplos
- **[TESTS_README.md](TESTS_README.md)** - Guia completo de testes com pytest

## 🧪 Executar Testes

```bash
# Entrar no container
docker exec -it medway-api bash

# Executar todos os testes
python run_tests.py

# Ou executar com pytest direto
python -m pytest -v
```

## 🎯 Status do Projeto

- ✅ **Backend Completo**: API REST totalmente funcional
- ✅ **Testes Abrangentes**: 27 testes passando (100% de sucesso)
- ✅ **Documentação**: Guias detalhados de uso e desenvolvimento
- ✅ **Validações Robustas**: Sistema seguro com validação de dados
- ✅ **Docker Ready**: Ambiente containerizado para fácil execução

## 🏗️ Estrutura do Projeto

```
app/
├── exam/           # App principal de exames
├── question/       # App de questões e alternativas  
├── student/        # App de estudantes (usuários)
├── utils/          # Utilitários compartilhados
├── medway_api/     # Configurações do Django
└── tests/          # Testes automatizados
```

## 🚀 Próximos Passos

1. Execute `docker compose up --build`
2. Acesse http://localhost:8000/admin/ 
3. Consulte a documentação da API para testar os endpoints
4. Execute os testes para validar o funcionamento
