"""
Code quality and performance optimization tools for Movie Translate
"""

import ast
import os
import sys
import time
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import json


class CodeQualityChecker:
    """Code quality checker for Movie Translate project"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.src_dir = project_root / "src"
        self.issues = defaultdict(list)
        self.metrics = {}
        
    def check_all(self) -> Dict[str, Any]:
        """Run all code quality checks"""
        print("🔍 Running code quality checks...")
        
        # Run individual checks
        self.check_python_syntax()
        self.check_imports()
        self.check_naming_conventions()
        self.check_code_complexity()
        self.check_documentation()
        self.check_type_hints()
        self.check_error_handling()
        self.check_security_issues()
        self.check_performance_patterns()
        
        # Generate report
        report = self.generate_report()
        
        return report
    
    def check_python_syntax(self):
        """Check Python syntax errors"""
        print("  📝 Checking Python syntax...")
        
        syntax_errors = []
        
        for py_file in self.src_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    source = f.read()
                
                # Parse AST to check syntax
                ast.parse(source, filename=str(py_file))
                
            except SyntaxError as e:
                syntax_errors.append({
                    'file': str(py_file.relative_to(self.project_root)),
                    'line': e.lineno,
                    'error': str(e),
                    'severity': 'error'
                })
            except Exception as e:
                syntax_errors.append({
                    'file': str(py_file.relative_to(self.project_root)),
                    'error': str(e),
                    'severity': 'warning'
                })
        
        self.issues['syntax'] = syntax_errors
        self.metrics['syntax_errors'] = len(syntax_errors)
    
    def check_imports(self):
        """Check import statements and dependencies"""
        print("  📦 Checking imports...")
        
        import_issues = []
        unused_imports = []
        circular_imports = []
        
        # Check for unused imports
        for py_file in self.src_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find all import statements
                import_statements = re.findall(r'^\s*(?:from\s+(\S+)\s+)?import\s+(.+)', content, re.MULTILINE)
                
                # Check if imported modules are actually used
                for from_module, imports in import_statements:
                    import_list = [imp.strip() for imp in imports.split(',')]
                    
                    for imp in import_list:
                        # Remove aliases
                        imp = re.sub(r'\s+as\s+\w+', '', imp)
                        
                        # Check if the imported name is used in the file
                        if not re.search(r'\b' + re.escape(imp) + r'\b', content):
                            unused_imports.append({
                                'file': str(py_file.relative_to(self.project_root)),
                                'import': imp,
                                'from_module': from_module,
                                'severity': 'warning'
                            })
            
            except Exception:
                continue
        
        # Check for potential circular imports
        # This is a simplified check - a full check would require static analysis
        self.issues['imports'] = import_issues + unused_imports + circular_imports
        self.metrics['unused_imports'] = len(unused_imports)
    
    def check_naming_conventions(self):
        """Check naming conventions (PEP 8)"""
        print("  🔤 Checking naming conventions...")
        
        naming_issues = []
        
        for py_file in self.src_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check function names (should be snake_case)
                func_matches = re.findall(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)', content)
                for func_name in func_matches:
                    if not re.match(r'^[a-z_][a-z0-9_]*$', func_name):
                        naming_issues.append({
                            'file': str(py_file.relative_to(self.project_root)),
                            'type': 'function',
                            'name': func_name,
                            'issue': 'Function name should be snake_case',
                            'severity': 'warning'
                        })
                
                # Check class names (should be CamelCase)
                class_matches = re.findall(r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)', content)
                for class_name in class_matches:
                    if not re.match(r'^[A-Z][a-zA-Z0-9]*$', class_name):
                        naming_issues.append({
                            'file': str(py_file.relative_to(self.project_root)),
                            'type': 'class',
                            'name': class_name,
                            'issue': 'Class name should be CamelCase',
                            'severity': 'warning'
                        })
                
                # Check variable names (should be snake_case)
                var_matches = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=', content)
                for var_name in var_matches:
                    if not re.match(r'^[a-z_][a-z0-9_]*$', var_name) and len(var_name) > 1:
                        # Skip single-letter variables and constants
                        if not (var_name.isupper() or len(var_name) == 1):
                            naming_issues.append({
                                'file': str(py_file.relative_to(self.project_root)),
                                'type': 'variable',
                                'name': var_name,
                                'issue': 'Variable name should be snake_case',
                                'severity': 'info'
                            })
            
            except Exception:
                continue
        
        self.issues['naming'] = naming_issues
        self.metrics['naming_issues'] = len(naming_issues)
    
    def check_code_complexity(self):
        """Check code complexity (cyclomatic complexity)"""
        print("  🔄 Checking code complexity...")
        
        complexity_issues = []
        
        for py_file in self.src_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse AST
                tree = ast.parse(content)
                
                # Calculate complexity for each function
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        complexity = self._calculate_complexity(node)
                        
                        if complexity > 10:
                            complexity_issues.append({
                                'file': str(py_file.relative_to(self.project_root)),
                                'function': node.name,
                                'complexity': complexity,
                                'issue': f'Function complexity ({complexity}) exceeds recommended limit (10)',
                                'severity': 'warning' if complexity <= 15 else 'error'
                            })
            
            except Exception:
                continue
        
        self.issues['complexity'] = complexity_issues
        self.metrics['complexity_issues'] = len(complexity_issues)
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity for a function"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity
    
    def check_documentation(self):
        """Check documentation coverage"""
        print("  📚 Checking documentation...")
        
        doc_issues = []
        
        public_functions_without_docs = 0
        total_public_functions = 0
        
        for py_file in self.src_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Check if function is public (doesn't start with underscore)
                        if not node.name.startswith('_'):
                            total_public_functions += 1
                            
                            # Check if function has docstring
                            has_docstring = (
                                node.body and 
                                isinstance(node.body[0], ast.Expr) and
                                isinstance(node.body[0].value, ast.Str)
                            )
                            
                            if not has_docstring:
                                public_functions_without_docs += 1
                                doc_issues.append({
                                    'file': str(py_file.relative_to(self.project_root)),
                                    'function': node.name,
                                    'issue': 'Public function missing docstring',
                                    'severity': 'info'
                                })
            
            except Exception:
                continue
        
        self.issues['documentation'] = doc_issues
        self.metrics['documentation_coverage'] = (
            (total_public_functions - public_functions_without_docs) / total_public_functions * 100
            if total_public_functions > 0 else 100
        )
    
    def check_type_hints(self):
        """Check type hints usage"""
        print("  🔢 Checking type hints...")
        
        type_hint_issues = []
        
        functions_without_hints = 0
        total_functions = 0
        
        for py_file in self.src_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        total_functions += 1
                        
                        # Check if function has type hints
                        has_return_hint = node.returns is not None
                        has_param_hints = all(arg.annotation is not None for arg in node.args.args)
                        
                        if not has_return_hint or not has_param_hints:
                            functions_without_hints += 1
                            type_hint_issues.append({
                                'file': str(py_file.relative_to(self.project_root)),
                                'function': node.name,
                                'issue': 'Function missing type hints',
                                'severity': 'info'
                            })
            
            except Exception:
                continue
        
        self.issues['type_hints'] = type_hint_issues
        self.metrics['type_hint_coverage'] = (
            (total_functions - functions_without_hints) / total_functions * 100
            if total_functions > 0 else 100
        )
    
    def check_error_handling(self):
        """Check error handling patterns"""
        print("  ⚠️  Checking error handling...")
        
        error_handling_issues = []
        
        for py_file in self.src_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for bare except clauses
                bare_excepts = re.findall(r'except\s*:', content)
                for match in bare_excepts:
                    error_handling_issues.append({
                        'file': str(py_file.relative_to(self.project_root)),
                        'issue': 'Bare except clause found',
                        'severity': 'warning'
                    })
                
                # Check for unhandled exceptions in critical sections
                # This is a simplified check
                if 'open(' in content and 'try:' not in content:
                    error_handling_issues.append({
                        'file': str(py_file.relative_to(self.project_root)),
                        'issue': 'File operations without try-catch',
                        'severity': 'info'
                    })
            
            except Exception:
                continue
        
        self.issues['error_handling'] = error_handling_issues
        self.metrics['error_handling_issues'] = len(error_handling_issues)
    
    def check_security_issues(self):
        """Check for security vulnerabilities"""
        print("  🔒 Checking security issues...")
        
        security_issues = []
        
        for py_file in self.src_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for hardcoded secrets
                secret_patterns = [
                    r'password\s*=\s*[\'"][^\'\"]+[\'"]',
                    r'api_key\s*=\s*[\'"][^\'\"]+[\'"]',
                    r'secret\s*=\s*[\'"][^\'\"]+[\'"]',
                    r'token\s*=\s*[\'"][^\'\"]+[\'"]'
                ]
                
                for pattern in secret_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        security_issues.append({
                            'file': str(py_file.relative_to(self.project_root)),
                            'issue': f'Potential hardcoded secret: {match}',
                            'severity': 'error'
                        })
                
                # Check for SQL injection vulnerabilities
                sql_patterns = [
                    r'execute\s*\(\s*[\'"]\s*SELECT.*\+.*',
                    r'execute\s*\(\s*["\'].*%\s*.*',
                    r'cursor\.execute\s*\(\s*f["\'].*%\s*.*'
                ]
                
                for pattern in sql_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        security_issues.append({
                            'file': str(py_file.relative_to(self.project_root)),
                            'issue': f'Potential SQL injection: {match}',
                            'severity': 'error'
                        })
                
                # Check for eval usage
                if 'eval(' in content:
                    security_issues.append({
                        'file': str(py_file.relative_to(self.project_root)),
                        'issue': 'Use of eval() detected',
                        'severity': 'warning'
                    })
            
            except Exception:
                continue
        
        self.issues['security'] = security_issues
        self.metrics['security_issues'] = len(security_issues)
    
    def check_performance_patterns(self):
        """Check for performance anti-patterns"""
        print("  ⚡ Checking performance patterns...")
        
        performance_issues = []
        
        for py_file in self.src_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for string concatenation in loops
                loop_patterns = [
                    r'for\s+\w+\s+in.*:',
                    r'while\s+.*:'
                ]
                
                for pattern in loop_patterns:
                    loop_matches = re.findall(pattern, content)
                    for loop_match in loop_matches:
                        # Look for string concatenation within loops
                        if '+=' in content and 'str' in content:
                            performance_issues.append({
                                'file': str(py_file.relative_to(self.project_root)),
                                'issue': 'Potential string concatenation in loop',
                                'severity': 'info'
                            })
                
                # Check for list comprehensions that could be generators
                if '[x for x in' in content:
                    performance_issues.append({
                        'file': str(py_file.relative_to(self.project_root)),
                        'issue': 'Consider using generator expression instead of list comprehension',
                        'severity': 'info'
                    })
                
                # Check for inefficient database queries
                if 'SELECT *' in content:
                    performance_issues.append({
                        'file': str(py_file.relative_to(self.project_root)),
                        'issue': 'SELECT * detected - consider specifying columns',
                        'severity': 'info'
                    })
            
            except Exception:
                continue
        
        self.issues['performance'] = performance_issues
        self.metrics['performance_issues'] = len(performance_issues)
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive code quality report"""
        print("📊 Generating code quality report...")
        
        # Calculate overall score
        total_issues = sum(len(issues) for issues in self.issues.values())
        error_count = sum(1 for issues in self.issues.values() for issue in issues if issue.get('severity') == 'error')
        warning_count = sum(1 for issues in self.issues.values() for issue in issues if issue.get('severity') == 'warning')
        
        # Calculate quality score (0-100)
        quality_score = max(0, 100 - (total_issues * 2) - (error_count * 10) - (warning_count * 5))
        
        report = {
            'summary': {
                'total_files': len(list(self.src_dir.rglob("*.py"))),
                'total_issues': total_issues,
                'error_count': error_count,
                'warning_count': warning_count,
                'quality_score': quality_score,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            },
            'metrics': dict(self.metrics),
            'issues': dict(self.issues),
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on issues found"""
        recommendations = []
        
        if self.metrics.get('syntax_errors', 0) > 0:
            recommendations.append("Fix syntax errors before proceeding")
        
        if self.metrics.get('unused_imports', 0) > 0:
            recommendations.append("Remove unused imports to improve code clarity")
        
        if self.metrics.get('complexity_issues', 0) > 0:
            recommendations.append("Refactor complex functions to improve maintainability")
        
        if self.metrics.get('documentation_coverage', 100) < 80:
            recommendations.append("Add docstrings to public functions")
        
        if self.metrics.get('type_hint_coverage', 100) < 80:
            recommendations.append("Add type hints to improve code reliability")
        
        if self.metrics.get('security_issues', 0) > 0:
            recommendations.append("Address security issues immediately")
        
        if self.metrics.get('performance_issues', 0) > 0:
            recommendations.append("Optimize performance-critical sections")
        
        return recommendations


class PerformanceOptimizer:
    """Performance optimization tools"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.src_dir = project_root / "src"
        self.optimizations = []
    
    def analyze_performance(self) -> Dict[str, Any]:
        """Analyze performance bottlenecks"""
        print("🚀 Analyzing performance...")
        
        analysis = {
            'file_sizes': self._analyze_file_sizes(),
            'import_patterns': self._analyze_import_patterns(),
            'function_complexity': self._analyze_function_complexity(),
            'memory_usage': self._analyze_memory_patterns(),
            'database_queries': self._analyze_database_patterns(),
            'recommendations': []
        }
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_performance_recommendations(analysis)
        
        return analysis
    
    def _analyze_file_sizes(self) -> Dict[str, Any]:
        """Analyze file sizes and identify large files"""
        file_analysis = {
            'total_files': 0,
            'total_size': 0,
            'large_files': [],
            'average_size': 0
        }
        
        for py_file in self.src_dir.rglob("*.py"):
            file_size = py_file.stat().st_size
            file_analysis['total_files'] += 1
            file_analysis['total_size'] += file_size
            
            if file_size > 50 * 1024:  # > 50KB
                file_analysis['large_files'].append({
                    'file': str(py_file.relative_to(self.project_root)),
                    'size': file_size
                })
        
        if file_analysis['total_files'] > 0:
            file_analysis['average_size'] = file_analysis['total_size'] / file_analysis['total_files']
        
        return file_analysis
    
    def _analyze_import_patterns(self) -> Dict[str, Any]:
        """Analyze import patterns for optimization opportunities"""
        import_analysis = {
            'heavy_imports': [],
            'circular_imports': [],
            'unused_imports': []
        }
        
        # Check for heavy imports (modules that take time to load)
        heavy_modules = ['numpy', 'pandas', 'torch', 'tensorflow', 'cv2']
        
        for py_file in self.src_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for module in heavy_modules:
                    if f'import {module}' in content or f'from {module}' in content:
                        import_analysis['heavy_imports'].append({
                            'file': str(py_file.relative_to(self.project_root)),
                            'module': module
                        })
            
            except Exception:
                continue
        
        return import_analysis
    
    def _analyze_function_complexity(self) -> Dict[str, Any]:
        """Analyze function complexity for optimization"""
        complexity_analysis = {
            'complex_functions': [],
            'large_functions': [],
            'functions_per_file': {}
        }
        
        for py_file in self.src_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                functions = []
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Calculate function size (lines of code)
                        func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                        
                        # Calculate complexity
                        complexity = self._calculate_complexity(node)
                        
                        func_info = {
                            'name': node.name,
                            'lines': func_lines,
                            'complexity': complexity
                        }
                        
                        functions.append(func_info)
                        
                        # Flag complex functions
                        if complexity > 15:
                            complexity_analysis['complex_functions'].append({
                                'file': str(py_file.relative_to(self.project_root)),
                                'function': node.name,
                                'complexity': complexity
                            })
                        
                        # Flag large functions
                        if func_lines > 50:
                            complexity_analysis['large_functions'].append({
                                'file': str(py_file.relative_to(self.project_root)),
                                'function': node.name,
                                'lines': func_lines
                            })
                
                complexity_analysis['functions_per_file'][str(py_file.relative_to(self.project_root))] = len(functions)
            
            except Exception:
                continue
        
        return complexity_analysis
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity
    
    def _analyze_memory_patterns(self) -> Dict[str, Any]:
        """Analyze memory usage patterns"""
        memory_analysis = {
            'memory_intensive_operations': [],
            'potential_leaks': []
        }
        
        for py_file in self.src_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for memory-intensive patterns
                if 'np.array(' in content or 'pd.DataFrame(' in content:
                    memory_analysis['memory_intensive_operations'].append({
                        'file': str(py_file.relative_to(self.project_root)),
                        'operation': 'Large data structure creation'
                    })
                
                # Check for potential memory leaks
                if 'global ' in content and re.search(r'\w+\s*=\s*\[\]', content):
                    memory_analysis['potential_leaks'].append({
                        'file': str(py_file.relative_to(self.project_root)),
                        'issue': 'Global variable with empty list'
                    })
            
            except Exception:
                continue
        
        return memory_analysis
    
    def _analyze_database_patterns(self) -> Dict[str, Any]:
        """Analyze database query patterns"""
        db_analysis = {
            'n_plus_1_queries': [],
            'inefficient_queries': [],
            'missing_indexes': []
        }
        
        # Look for common database anti-patterns
        for py_file in self.src_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for N+1 query patterns
                if re.search(r'for.*in.*:\s*.*\.get\(', content):
                    db_analysis['n_plus_1_queries'].append({
                        'file': str(py_file.relative_to(self.project_root)),
                        'pattern': 'Potential N+1 query in loop'
                    })
                
                # Check for SELECT *
                if 'SELECT *' in content:
                    db_analysis['inefficient_queries'].append({
                        'file': str(py_file.relative_to(self.project_root)),
                        'query': 'SELECT * detected'
                    })
            
            except Exception:
                continue
        
        return db_analysis
    
    def _generate_performance_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        # File size recommendations
        if analysis['file_sizes']['large_files']:
            recommendations.append("Consider splitting large files into smaller modules")
        
        # Import recommendations
        if analysis['import_patterns']['heavy_imports']:
            recommendations.append("Consider lazy loading heavy imports")
        
        # Function complexity recommendations
        if analysis['function_complexity']['complex_functions']:
            recommendations.append("Refactor complex functions to improve performance")
        
        # Database recommendations
        if analysis['database_queries']['n_plus_1_queries']:
            recommendations.append("Optimize database queries to avoid N+1 problem")
        
        # Memory recommendations
        if analysis['memory_patterns']['memory_intensive_operations']:
            recommendations.append("Consider using generators or pagination for large datasets")
        
        return recommendations


def main():
    """Main function to run code quality and performance analysis"""
    project_root = Path(__file__).parent.parent
    
    print("🔧 Movie Translate Code Quality & Performance Analysis")
    print("=" * 60)
    
    # Run code quality checks
    quality_checker = CodeQualityChecker(project_root)
    quality_report = quality_checker.check_all()
    
    # Run performance analysis
    performance_optimizer = PerformanceOptimizer(project_root)
    performance_report = performance_optimizer.analyze_performance()
    
    # Generate combined report
    combined_report = {
        'code_quality': quality_report,
        'performance': performance_report,
        'summary': {
            'quality_score': quality_report['summary']['quality_score'],
            'total_issues': quality_report['summary']['total_issues'],
            'performance_score': max(0, 100 - len(performance_report['recommendations']) * 10)
        }
    }
    
    # Save report
    report_file = project_root / "code_quality_report.json"
    with open(report_file, 'w') as f:
        json.dump(combined_report, f, indent=2)
    
    # Print summary
    print("\n📋 Analysis Summary:")
    print(f"  Code Quality Score: {quality_report['summary']['quality_score']:.1f}/100")
    print(f"  Total Issues: {quality_report['summary']['total_issues']}")
    print(f"  Performance Score: {combined_report['summary']['performance_score']:.1f}/100")
    print(f"  Report saved to: {report_file}")
    
    # Print recommendations
    print("\n💡 Recommendations:")
    all_recommendations = (
        quality_report['recommendations'] + 
        performance_report['recommendations']
    )
    
    for i, rec in enumerate(all_recommendations[:10], 1):  # Show top 10
        print(f"  {i}. {rec}")
    
    return combined_report


if __name__ == "__main__":
    main()