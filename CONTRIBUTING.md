# 🤝 Guia de Contribuição

Este documento fornece diretrizes para contribuir com o projeto da Plataforma Estudantil.

## 📋 Antes de Começar

### Pré-requisitos
- Docker e Docker Compose instalados
- Git configurado
- Conhecimento básico em Django e Python

### Configuração do Ambiente de Desenvolvimento

1. **Clone o repositório**
```bash
git clone <repository-url>
cd backend_student_plataform
```

2. **Execute o ambiente de desenvolvimento**
```bash
docker compose up --build
```

3. **Configure o ambiente de testes**
```bash
docker exec -it medway-api bash
pip install pytest pytest-django
python run_tests.py
```

## 🔧 Estrutura do Projeto

### Apps Django
- **`exam/`** - Funcionalidades relacionadas a exames e submissões
- **`question/`** - Modelos de questões e alternativas
- **`student/`** - Modelo customizado de usuário/estudante
- **`utils/`** - Utilitários e comandos compartilhados

### Arquivos Importantes
- **`API_DOCUMENTATION.md`** - Documentação completa da API
- **`TESTS_README.md`** - Guia dos testes automatizados
- **`requirements.txt`** - Dependências Python
- **`docker-compose.yml`** - Configuração do ambiente

## ✅ Fluxo de Desenvolvimento

### 1. Criando uma Nova Funcionalidade

1. **Crie uma branch para sua feature**
```bash
git checkout -b feature/nova-funcionalidade
```

2. **Desenvolva seguindo o padrão Django**
   - Models em `models.py`
   - Views em `views.py` (use DRF ViewSets ou function-based views)
   - Serializers em `serializers.py`
   - URLs em `urls.py`

3. **Escreva testes**
   - Testes unitários para models
   - Testes de integração para APIs
   - Use o pytest como padrão

4. **Valide sua implementação**
```bash
python run_tests.py
```

### 2. Padrões de Código

#### Models
```python
class ExampleModel(models.Model):
    """Docstring explicando o propósito do modelo"""
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Exemplo'
        verbose_name_plural = 'Exemplos'
    
    def __str__(self):
        return self.name
```

#### Views (DRF)
```python
@api_view(['POST'])
def example_view(request):
    """
    Docstring explicando o que a view faz
    """
    serializer = ExampleSerializer(data=request.data)
    
    if serializer.is_valid():
        instance = serializer.save()
        return Response({
            'success': True,
            'data': ExampleSerializer(instance).data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)
```

#### Serializers
```python
class ExampleSerializer(serializers.ModelSerializer):
    """Serializer para o modelo Example"""
    
    class Meta:
        model = Example
        fields = ['id', 'name', 'created_at']
    
    def validate_name(self, value):
        """Validação customizada para o campo name"""
        if len(value) < 3:
            raise serializers.ValidationError("Nome deve ter pelo menos 3 caracteres")
        return value
```

### 3. Testes

#### Estrutura dos Testes
```python
import pytest
from django.test import TestCase
from rest_framework.test import APITestCase

@pytest.mark.django_db
class TestExampleModel(TestCase):
    """Testes para o modelo Example"""
    
    def setUp(self):
        """Setup executado antes de cada teste"""
        self.example = Example.objects.create(name="Test Example")
    
    def test_model_creation(self):
        """Teste de criação do modelo"""
        assert self.example.name == "Test Example"
        assert self.example.id is not None

@pytest.mark.django_db  
class TestExampleAPI(APITestCase):
    """Testes para a API do Example"""
    
    def test_create_example(self):
        """Teste de criação via API"""
        url = '/api/examples/'
        data = {'name': 'teste'}
        
        response = self.client.post(url, data, format='json')
        
        assert response.status_code == 201
        assert response.data['success'] == True
```

## 🧪 Executando Testes

### Todos os Testes
```bash
python run_tests.py
```

### Testes Específicos
```bash
python -m pytest test_exam_functionality.py -v
python -m pytest test_api_integration.py::TestExamSubmissionAPI -v
```

### Cobertura de Testes
```bash
python -m pytest --cov=exam --cov-report=html
```

## 📝 Migrações

### Criando Migrações
```bash
python manage.py makemigrations app_name
python manage.py migrate
```

### Populando Dados de Teste
Se criar novos dados de teste, adicione em uma migration:
```python
def populate_data(apps, schema_editor):
    Model = apps.get_model('app_name', 'ModelName')
    # Criar dados...

class Migration(migrations.Migration):
    operations = [
        migrations.RunPython(populate_data),
    ]
```

## 📋 Checklist para Pull Requests

Antes de submeter um PR, verifique:

- [ ] ✅ Todos os testes estão passando (`python run_tests.py`)
- [ ] 📝 Código está documentado (docstrings)
- [ ] 🧪 Testes foram escritos para nova funcionalidade
- [ ] 📚 Documentação da API foi atualizada (se aplicável)
- [ ] 🔄 Migrações foram criadas e testadas
- [ ] 🚀 Funcionalidade foi testada manualmente
- [ ] 📋 Commit messages são descritivos

## 🚀 Submissão de Pull Request

### Título e Descrição
```
feat: Adicionar endpoint de upload de arquivos

- Implementa upload de imagens para questões
- Adiciona validação de tipo de arquivo
- Inclui testes de integração
- Atualiza documentação da API

Closes #123
```

### Tipos de Commit
- `feat:` - Nova funcionalidade
- `fix:` - Correção de bug
- `docs:` - Alterações na documentação
- `test:` - Adição/alteração de testes
- `refactor:` - Refatoração de código
- `style:` - Alterações de formatação

## 🐛 Reportando Bugs

### Informações Necessárias
1. **Descrição clara** do problema
2. **Passos para reproduzir** o erro
3. **Comportamento esperado** vs **comportamento atual**
4. **Logs/screenshots** se aplicável
5. **Ambiente** (versão Python, Docker, etc.)

### Template de Issue
```markdown
## Descrição
Breve descrição do problema

## Passos para Reproduzir
1. Execute `comando x`
2. Acesse `endpoint y`
3. Observe o erro

## Comportamento Esperado
O que deveria acontecer

## Comportamento Atual
O que realmente acontece

## Ambiente
- Python: 3.11
- Django: 5.0.6
- OS: Windows/Linux/Mac
```

## ❓ Dúvidas e Suporte

- 📖 Consulte a [documentação da API](API_DOCUMENTATION.md)
- 🧪 Veja o [guia de testes](TESTS_README.md)
- 💬 Abra uma issue para discussões
- 📧 Entre em contato com os maintainers

## 🎯 Boas Práticas

### Código Limpo
- Use nomes descritivos para variáveis e funções
- Mantenha funções pequenas e focadas
- Adicione comentários quando necessário
- Siga o PEP 8 para Python

### Performance
- Use `select_related()` e `prefetch_related()` para otimizar queries
- Implemente paginação para listagens grandes
- Cache dados frequentemente acessados

### Segurança
- Valide sempre dados de entrada
- Use o sistema de permissões do Django
- Não exponha informações sensíveis nos logs
- Implemente rate limiting quando necessário

---

**Obrigado por contribuir! 🚀**