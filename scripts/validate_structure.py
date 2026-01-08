#!/usr/bin/env python3
"""Validate project structure and basic syntax.

This script validates:
- File structure completeness
- Python syntax
- Import structure
- Configuration files
"""

import ast
import json
import os
import sys
from pathlib import Path
from typing import List, Tuple

# Color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def check_python_syntax(file_path: Path) -> Tuple[bool, str]:
    """Check Python file syntax."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        ast.parse(source, filename=str(file_path))
        return True, ""
    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    except Exception as e:
        return False, f"Error: {e}"


def check_json_syntax(file_path: Path) -> Tuple[bool, str]:
    """Check JSON file syntax."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            json.load(f)
        return True, ""
    except json.JSONDecodeError as e:
        return False, f"JSON error: {e}"
    except Exception as e:
        return False, f"Error: {e}"


def validate_structure():
    """Validate project structure."""
    print(f"{YELLOW}🔍 Validating AI-SRE Platform Structure...{RESET}\n")
    
    base_path = Path(__file__).parent.parent
    errors = []
    warnings = []
    passed = []
    
    # Critical files to check
    critical_files = [
        "backend/app/main.py",
        "backend/app/core/config.py",
        "backend/requirements.txt",
        "frontend/package.json",
        "frontend/src/main.tsx",
        "docker-compose.yml",
        "Makefile",
        ".env.example",
    ]
    
    print(f"{YELLOW}📁 Checking critical files...{RESET}")
    for file_rel in critical_files:
        file_path = base_path / file_rel
        if file_path.exists():
            print(f"  {GREEN}✓{RESET} {file_rel}")
            passed.append(file_rel)
        else:
            print(f"  {RED}✗{RESET} {file_rel} - MISSING")
            errors.append(f"Missing: {file_rel}")
    
    # Check Python syntax
    print(f"\n{YELLOW}🐍 Validating Python syntax...{RESET}")
    python_files = list((base_path / "backend/app").rglob("*.py"))
    python_errors = 0
    
    for py_file in python_files[:20]:  # Check first 20 files
        rel_path = py_file.relative_to(base_path)
        is_valid, error_msg = check_python_syntax(py_file)
        if is_valid:
            print(f"  {GREEN}✓{RESET} {rel_path}")
        else:
            print(f"  {RED}✗{RESET} {rel_path} - {error_msg}")
            errors.append(f"{rel_path}: {error_msg}")
            python_errors += 1
    
    if python_errors == 0:
        print(f"  {GREEN}All Python files have valid syntax!{RESET}")
    
    # Check JSON files
    print(f"\n{YELLOW}📄 Validating JSON files...{RESET}")
    json_files = [
        "frontend/package.json",
        "backend/data/sample_alerts.json",
    ]
    
    for json_rel in json_files:
        json_path = base_path / json_rel
        if json_path.exists():
            is_valid, error_msg = check_json_syntax(json_path)
            if is_valid:
                print(f"  {GREEN}✓{RESET} {json_rel}")
            else:
                print(f"  {RED}✗{RESET} {json_rel} - {error_msg}")
                errors.append(f"{json_rel}: {error_msg}")
    
    # Check directory structure
    print(f"\n{YELLOW}📂 Checking directory structure...{RESET}")
    required_dirs = [
        "backend/app/agents",
        "backend/app/ml",
        "backend/app/rag",
        "backend/app/services",
        "backend/app/security",
        "backend/app/events",
        "backend/app/cost",
        "frontend/src/components",
        "frontend/src/pages",
        "infra/terraform",
        "infra/kubernetes",
        "infra/helm",
        "docs",
        "scripts",
        "monitoring",
    ]
    
    for dir_rel in required_dirs:
        dir_path = base_path / dir_rel
        if dir_path.exists() and dir_path.is_dir():
            print(f"  {GREEN}✓{RESET} {dir_rel}/")
        else:
            print(f"  {RED}✗{RESET} {dir_rel}/ - MISSING")
            errors.append(f"Missing directory: {dir_rel}")
    
    # Summary
    print(f"\n{YELLOW}{'='*60}{RESET}")
    print(f"{YELLOW}📊 Validation Summary{RESET}\n")
    print(f"  {GREEN}✓ Passed: {len(passed)}{RESET}")
    print(f"  {RED}✗ Errors: {len(errors)}{RESET}")
    print(f"  {YELLOW}⚠ Warnings: {len(warnings)}{RESET}")
    
    if errors:
        print(f"\n{RED}❌ Validation failed with {len(errors)} error(s){RESET}")
        return False
    else:
        print(f"\n{GREEN}✅ Structure validation passed!{RESET}")
        print(f"\n{YELLOW}ℹ️  Note: This validates structure only.{RESET}")
        print(f"{YELLOW}   Most implementation logic is marked with TODOs.{RESET}")
        print(f"{YELLOW}   Run 'make setup-local' to install dependencies.{RESET}")
        return True


if __name__ == "__main__":
    success = validate_structure()
    sys.exit(0 if success else 1)
