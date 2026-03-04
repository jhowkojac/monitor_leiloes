#!/usr/bin/env python3
"""
Script para executar suíte completa de testes
"""
import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description):
    """Executa um comando e retorna o resultado"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    print(f"Comando: {cmd}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd="c:\\cursor\\monitor_leiloes")
    
    print(f"Exit code: {result.returncode}")
    if result.stdout:
        print(f"STDOUT:\n{result.stdout}")
    if result.stderr:
        print(f"STDERR:\n{result.stderr}")
    
    return result.returncode == 0


def main():
    """Função principal"""
    print("🚀 EXECUTANDO SUÍTE COMPLETA DE TESTES")
    print("=" * 60)
    
    # Verifica se o servidor está rodando
    print("\n🔍 Verificando se o servidor está rodando...")
    try:
        import requests
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor está rodando")
        else:
            print("❌ Servidor não está respondendo corretamente")
            sys.exit(1)
    except:
        print("❌ Servidor não está rodando. Inicie o servidor com:")
        print("   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        sys.exit(1)
    
    # Lista de testes para executar
    test_suites = [
        {
            "cmd": "venv\\Scripts\\pytest.exe tests/test_detran_mg.py -v",
            "desc": "Testes Unitários - Detran MG"
        },
        {
            "cmd": "venv\\Scripts\\pytest.exe tests/test_integration.py -v",
            "desc": "Testes de Integração - APIs"
        },
        {
            "cmd": "venv\\Scripts\\pytest.exe tests/test_templates.py -v",
            "desc": "Testes de Templates - HTML"
        },
        {
            "cmd": "venv\\Scripts\\pytest.exe tests/test_performance.py -v --tb=short",
            "desc": "Testes de Performance"
        },
        {
            "cmd": "venv\\Scripts\\pytest.exe tests/ -v --cov=app --cov-report=term-missing --cov-report=html:htmlcov --tb=short",
            "desc": "Todos os Testes com Coverage"
        }
    ]
    
    # Executa cada suíte
    results = {}
    for suite in test_suites:
        success = run_command(suite["cmd"], suite["desc"])
        results[suite["desc"]] = success
        
        if not success:
            print(f"❌ {suite['desc']} FALHOU")
        else:
            print(f"✅ {suite['desc']} SUCESSO")
    
    # Testes E2E (separados, pois precisam de WebDriver)
    print(f"\n{'='*60}")
    print("🌐 Testes E2E (Selenium)")
    print(f"{'='*60}")
    print("Para executar testes E2E, use:")
    print("   venv\\Scripts\\pytest.exe tests/test_e2e.py -v --tb=short")
    print("   (Requer Chrome WebDriver instalado)")
    
    # Resumo final
    print(f"\n{'='*60}")
    print("📊 RESUMO FINAL")
    print(f"{'='*60}")
    
    total = len(results)
    passed = sum(results.values())
    failed = total - passed
    
    print(f"Total de suítes: {total}")
    print(f"✅ Sucesso: {passed}")
    print(f"❌ Falha: {failed}")
    
    if failed > 0:
        print(f"\n⚠️  {failed} suítes falharam:")
        for desc, success in results.items():
            if not success:
                print(f"   - {desc}")
        sys.exit(1)
    else:
        print(f"\n🎉 TODAS AS SUÍTES PASSARAM!")
        
        # Mostra informações de coverage se disponível
        coverage_file = Path("c:\\cursor\\monitor_leiloes\\htmlcov\\index.html")
        if coverage_file.exists():
            print(f"\n📈 Coverage report disponível em:")
            print(f"   file:///{coverage_file}")
    
    print(f"\n🏁 Testes concluídos em {len(test_suites)} suítes!")


if __name__ == "__main__":
    main()
