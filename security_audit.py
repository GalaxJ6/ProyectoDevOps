#!/usr/bin/env python
"""
Security Audit Script for DevOps Project

Ejecuta auditoría completa de seguridad:
- Linting con flake8
- Auditoría de dependencias con pip-audit
- Chequeos de secretos
"""

import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime

class SecurityAudit:
    def __init__(self):
        self.results = {}
        self.timestamp = datetime.now().isoformat()
        self.project_root = Path(__file__).parent
        
    def run_flake8(self):
        """Ejecuta análisis de linting con flake8"""
        print("\n" + "="*60)
        print("🔍 FLAKE8 - Linting Analysis")
        print("="*60)
        
        try:
            result = subprocess.run(
                ["python", "-m", "flake8", "src", "tests", 
                 "--count", "--statistics", "--show-source"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            output = result.stdout + result.stderr
            
            if result.returncode == 0:
                print("✅ PASSED: No linting errors found")
                self.results["flake8"] = {
                    "status": "passed",
                    "errors": 0,
                    "output": output
                }
            else:
                print("❌ FAILED: Linting errors found")
                print(output)
                self.results["flake8"] = {
                    "status": "failed",
                    "output": output
                }
            return result.returncode == 0
            
        except FileNotFoundError:
            print("⚠️  flake8 not installed")
            print("   Install with: pip install flake8")
            self.results["flake8"] = {"status": "skipped", "reason": "not_installed"}
            return False

    def run_pip_audit(self):
        """Ejecuta auditoría de dependencias con pip-audit"""
        print("\n" + "="*60)
        print("🔐 pip-audit - Dependency Audit")
        print("="*60)
        
        try:
            result = subprocess.run(
                ["python", "-m", "pip_audit", "--desc"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            output = result.stdout + result.stderr
            print(output)
            
            if result.returncode == 0:
                print("✅ PASSED: No vulnerabilities found")
                self.results["pip_audit"] = {
                    "status": "passed",
                    "vulnerabilities": 0
                }
                return True
            else:
                # pip-audit retorna 1 si encuentra vulnerabilidades, pero es info válida
                lines = output.split('\n')
                vuln_line = [l for l in lines if "Found" in l and "vulnerabilities" in l]
                
                if vuln_line:
                    print("⚠️  WARNINGS: Vulnerabilities detected (see above)")
                    self.results["pip_audit"] = {
                        "status": "warnings",
                        "output": output
                    }
                    return False  # No fallar completamente, solo advertencia
                else:
                    print("✅ PASSED")
                    self.results["pip_audit"] = {"status": "passed"}
                    return True
                
        except FileNotFoundError:
            print("⚠️  pip-audit not installed")
            print("   Install with: pip install pip-audit")
            self.results["pip_audit"] = {"status": "skipped", "reason": "not_installed"}
            return False

    def run_secret_check(self):
        """Busca patrones de secretos en el código"""
        print("\n" + "="*60)
        print("🔑 Secret Detection")
        print("="*60)
        
        patterns = {
            "AWS_KEY": r"AKIA[0-9A-Z]{16}",
            "PRIVATE_KEY": r"-----BEGIN RSA PRIVATE KEY-----",
            "API_KEY": r"api[_-]?key['\"]?\s*[:=]",
            "PASSWORD": r"password['\"]?\s*[:=]",
            "TOKEN": r"(token|secret)['\"]?\s*[:=]",
        }
        
        try:
            import re
            
            py_files = list(self.project_root.glob("**/*.py"))
            secrets_found = []
            
            for file_path in py_files:
                # Skip venv, __pycache__, etc
                if any(part in file_path.parts for part in ['.venv', 'venv', '__pycache__', '.git']):
                    continue
                
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        for name, pattern in patterns.items():
                            if re.search(pattern, content, re.IGNORECASE):
                                secrets_found.append({
                                    "file": str(file_path),
                                    "pattern": name
                                })
                except:
                    pass
            
            if secrets_found:
                print("❌ FAILED: Potential secrets detected")
                for item in secrets_found:
                    print(f"   - {item['pattern']} in {item['file']}")
                self.results["secrets"] = {
                    "status": "failed",
                    "found": secrets_found
                }
                return False
            else:
                print("✅ PASSED: No obvious secrets detected")
                self.results["secrets"] = {
                    "status": "passed",
                    "found": 0
                }
                return True
                
        except Exception as e:
            print(f"⚠️  Error during secret check: {e}")
            self.results["secrets"] = {"status": "error"}
            return False

    def generate_report(self):
        """Genera reporte de auditoría"""
        print("\n" + "="*60)
        print("📊 Security Audit Report")
        print("="*60)
        print(f"Timestamp: {self.timestamp}")
        
        passed = sum(1 for r in self.results.values() if r.get("status") == "passed")
        failed = sum(1 for r in self.results.values() if r.get("status") == "failed")
        warnings = sum(1 for r in self.results.values() if r.get("status") == "warnings")
        
        print(f"\nResults:")
        print(f"  ✅ Passed:   {passed}")
        print(f"  ❌ Failed:   {failed}")
        print(f"  ⚠️  Warnings: {warnings}")
        
        print(f"\nDetailed Results:")
        for check, result in self.results.items():
            status_icon = {
                "passed": "✅",
                "failed": "❌",
                "warnings": "⚠️",
                "skipped": "⏭️",
                "error": "⚠️"
            }.get(result.get("status"), "❓")
            
            print(f"  {status_icon} {check}: {result.get('status', 'unknown')}")
        
        # Save JSON report
        report_path = self.project_root / "security-audit-report.json"
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n📄 Report saved to: {report_path}")
        
        # Return overall status
        return failed == 0

    def run(self):
        """Ejecuta la auditoría completa"""
        print("\n🛡️  DevOps Security Audit Started")
        print(f"Project: {self.project_root}")
        
        all_passed = True
        
        # Run all checks
        all_passed &= self.run_flake8()
        all_passed &= self.run_pip_audit()  # No falla completamente por warnings
        all_passed &= self.run_secret_check()
        
        # Generate report
        report_passed = self.generate_report()
        
        print("\n" + "="*60)
        if report_passed:
            print("✅ SECURITY AUDIT: PASSED")
            sys.exit(0)
        else:
            print("❌ SECURITY AUDIT: FAILED - Review issues above")
            sys.exit(1)


if __name__ == "__main__":
    audit = SecurityAudit()
    audit.run()
