#!/usr/bin/env python
"""
Test runner script for exam submission functionality
Usage: python run_tests.py
"""

import subprocess
import sys
import os
from pathlib import Path

def run_tests():
    """Run all pytest tests with detailed output"""
    
    print("=" * 70)
    print("========= EXECUTANDO TESTES COM PYTEST =========")
    print("=" * 70)
    print()
    
    repo_root = Path(__file__).resolve().parent.parent
    env = os.environ.copy()
    env['DJANGO_SETTINGS_MODULE'] = 'app.test_settings'

    test_commands = [
        {
            'name': '========= Testes de Estrutura e Importações =========',
            'cmd': [sys.executable, '-m', 'pytest', '-c', 'app/pytest.ini', 'app/test_exam_functionality.py', '-v', '--tb=short']
        },
        {
            'name': '========= Testes de Integração da API =========',
            'cmd': [sys.executable, '-m', 'pytest', '-c', 'app/pytest.ini', 'app/test_api_integration.py', '-v', '--tb=short']
        },
        {
            'name': '========= Teste Completo (Todos os testes) =========',
            'cmd': [sys.executable, '-m', 'pytest', '-c', 'app/pytest.ini', 'app/test_exam_functionality.py', 'app/test_api_integration.py', 
                   '-v', '--tb=short', '--durations=10']
        }
    ]
    
    results = []
    
    for test in test_commands:
        print(f"\n{test['name']}")
        print("-" * 50)
        
        try:
            result = subprocess.run(test['cmd'], capture_output=True, text=True, cwd=str(repo_root), env=env)
            
            if result.returncode == 0:
                print("✅ SUCESSO")
                print(result.stdout.split('\n')[-3:-1])  
                results.append(True)
            else:
                print("❌ FALHOU")
                print("STDOUT:", result.stdout[-500:])  
                print("STDERR:", result.stderr)
                results.append(False)
                
        except Exception as e:
            print(f"❌ ERRO: {e}")
            results.append(False)
    
    print("\n" + "=" * 70)
    print("========= RESUMO DOS TESTES =========")
    print("=" * 70)
    
    total_tests = len(results)
    passed_tests = sum(results)
    
    for i, (test, result) in enumerate(zip(test_commands, results)):
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{i+1}. {test['name']}: {status}")
    
    print(f"\n🎯 Total: {passed_tests}/{total_tests} testes passaram")
    
    if all(results):
        print("\n========= TODOS OS TESTES PASSARAM! =========")
        print("\nPróximos passos:")
        print("   1. Execute 'python manage.py migrate' para aplicar migrações")
        print("   2. Execute 'python manage.py runserver' para iniciar o servidor")
        print("   3. Teste os endpoints usando a documentação em API_DOCUMENTATION.md")
    else:
        print("\n⚠️  ALGUNS TESTES FALHARAM")
        print("   Verifique os erros acima e corrija antes de prosseguir")
    
    print("=" * 70)
    
    return all(results)

def run_specific_test(test_name):
    """Run a specific test or test class"""
    print(f"Executando teste específico: {test_name}")
    
    cmd = [sys.executable, '-m', 'pytest', test_name, '-v', '-s']
    
    try:
        result = subprocess.run(cmd, cwd=os.getcwd())
        return result.returncode == 0
    except Exception as e:
        print(f"Erro ao executar teste: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        success = run_specific_test(test_name)
        sys.exit(0 if success else 1)
    else:
        success = run_tests()
        sys.exit(0 if success else 1)