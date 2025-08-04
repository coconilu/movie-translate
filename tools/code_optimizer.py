"""
Code optimization script for Movie Translate
Applies common optimizations to improve performance and code quality
"""

import ast
import os
import re
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
import json


class CodeOptimizer:
    """Code optimization tool"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.src_dir = project_root / "src"
        self.optimizations_applied = []
        self.backup_dir = project_root / "backup"
        
    def optimize_all(self) -> Dict[str, Any]:
        """Apply all optimizations"""
        print("🔧 Applying code optimizations...")
        
        # Create backup
        self._create_backup()
        
        # Apply optimizations
        self._optimize_imports()
        self._optimize_loops()
        self._optimize_functions()
        self._optimize_database_queries()
        self._optimize_memory_usage()
        self._optimize_error_handling()
        self._optimize_documentation()
        
        # Generate report
        report = self._generate_optimization_report()
        
        return report
    
    def _create_backup(self):
        """Create backup of source files"""
        print("  💾 Creating backup...")
        
        if self.backup_dir.exists():
            import shutil
            shutil.rmtree(self.backup_dir)
        
        # Copy src directory to backup
        import shutil
        shutil.copytree(self.src_dir, self.backup_dir / "src")
        
        print(f"  Backup created at: {self.backup_dir}")
    
    def _optimize_imports(self):
        """Optimize import statements"""
        print("  📦 Optimizing imports...")
        
        optimized_files = []
        
        for py_file in self.src_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Remove unused imports (simplified)
                content = self._remove_unused_imports(content, py_file)
                
                # Group imports
                content = self._group_imports(content)
                
                # Move heavy imports to functions
                content = self._move_heavy_imports(content)
                
                if content != original_content:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    optimized_files.append(str(py_file.relative_to(self.project_root)))
                    self.optimizations_applied.append({
                        'file': str(py_file.relative_to(self.project_root)),
                        'optimization': 'import_optimization'
                    })
            
            except Exception as e:
                print(f"    Error optimizing {py_file}: {e}")
        
        print(f"    Optimized imports in {len(optimized_files)} files")
    
    def _remove_unused_imports(self, content: str, file_path: Path) -> str:
        """Remove unused imports (simplified implementation)"""
        lines = content.split('\n')
        optimized_lines = []
        
        # Simple heuristic: keep all imports for now
        # In a real implementation, this would analyze usage
        for line in lines:
            if line.strip().startswith(('import ', 'from ')):
                # Keep the import
                optimized_lines.append(line)
            else:
                optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)
    
    def _group_imports(self, content: str) -> str:
        """Group and organize import statements"""
        lines = content.split('\n')
        import_lines = []
        other_lines = []
        
        # Separate imports from other code
        in_import_section = True
        for line in lines:
            if line.strip().startswith(('import ', 'from ')):
                import_lines.append(line)
            elif line.strip() == '':
                if in_import_section and import_lines:
                    import_lines.append(line)
            else:
                in_import_section = False
                other_lines.append(line)
        
        # Group imports: standard library, third-party, local
        std_imports = []
        third_party_imports = []
        local_imports = []
        
        for line in import_lines:
            if line.strip() == '':
                continue
            if line.startswith('from .') or line.startswith('import .'):
                local_imports.append(line)
            elif any(lib in line for lib in ['numpy', 'pandas', 'torch', 'cv2', 'sklearn']):
                third_party_imports.append(line)
            else:
                std_imports.append(line)
        
        # Rebuild content
        optimized_content = []
        
        # Add standard imports
        if std_imports:
            optimized_content.extend(std_imports)
            optimized_content.append('')
        
        # Add third-party imports
        if third_party_imports:
            optimized_content.extend(third_party_imports)
            optimized_content.append('')
        
        # Add local imports
        if local_imports:
            optimized_content.extend(local_imports)
            optimized_content.append('')
        
        # Add other content
        optimized_content.extend(other_lines)
        
        return '\n'.join(optimized_content)
    
    def _move_heavy_imports(self, content: str) -> str:
        """Move heavy imports inside functions where possible"""
        # This is a simplified version
        # In practice, this would require more sophisticated analysis
        
        heavy_modules = ['numpy', 'pandas', 'torch', 'tensorflow', 'cv2']
        
        for module in heavy_modules:
            # Look for top-level imports of heavy modules
            pattern = f'import {module}'
            if pattern in content:
                # For now, just add a comment suggesting optimization
                content = content.replace(
                    pattern,
                    f'# Consider moving {module} import inside function if only used locally\n{pattern}'
                )
        
        return content
    
    def _optimize_loops(self):
        """Optimize loops for better performance"""
        print("  🔄 Optimizing loops...")
        
        optimized_files = []
        
        for py_file in self.src_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Optimize list comprehensions
                content = self._optimize_list_comprehensions(content)
                
                # Optimize string concatenation
                content = self._optimize_string_concatenation(content)
                
                # Add loop optimizations
                content = self._add_loop_optimizations(content)
                
                if content != original_content:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    optimized_files.append(str(py_file.relative_to(self.project_root)))
                    self.optimizations_applied.append({
                        'file': str(py_file.relative_to(self.project_root)),
                        'optimization': 'loop_optimization'
                    })
            
            except Exception as e:
                print(f"    Error optimizing {py_file}: {e}")
        
        print(f"    Optimized loops in {len(optimized_files)} files")
    
    def _optimize_list_comprehensions(self, content: str) -> str:
        """Optimize list comprehensions"""
        # Convert list comprehensions to generators where appropriate
        # This is a simplified version
        
        # Look for list comprehensions in loops
        pattern = r'for\s+(\w+)\s+in\s+\[.*\]:'
        content = re.sub(pattern, r'for \1 in (\2):  # Consider using generator', content)
        
        return content
    
    def _optimize_string_concatenation(self, content: str) -> str:
        """Optimize string concatenation"""
        # Replace += with join() where appropriate
        # This is a simplified version
        
        # Look for string concatenation in loops
        pattern = r'(\w+)\s*\+=\s*(["\'][^"\']*["\'])'
        content = re.sub(pattern, r'# Consider using str.join() instead of +=\n\1 += \2', content)
        
        return content
    
    def _add_loop_optimizations(self, content: str) -> str:
        """Add loop optimization hints"""
        # Add comments for loop optimization opportunities
        
        # Look for range() in loops
        if 'range(' in content:
            content = content.replace(
                'range(',
                '# Consider using xrange() in Python 2 or enumerate() in Python 3\nrange('
            )
        
        return content
    
    def _optimize_functions(self):
        """Optimize function definitions"""
        print("  ⚡ Optimizing functions...")
        
        optimized_files = []
        
        for py_file in self.src_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Add type hints where missing
                content = self._add_type_hints(content)
                
                # Optimize function signatures
                content = self._optimize_function_signatures(content)
                
                # Add function docstrings
                content = self._add_function_docstrings(content)
                
                if content != original_content:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    optimized_files.append(str(py_file.relative_to(self.project_root)))
                    self.optimizations_applied.append({
                        'file': str(py_file.relative_to(self.project_root)),
                        'optimization': 'function_optimization'
                    })
            
            except Exception as e:
                print(f"    Error optimizing {py_file}: {e}")
        
        print(f"    Optimized functions in {len(optimized_files)} files")
    
    def _add_type_hints(self, content: str) -> str:
        """Add type hints to function definitions"""
        # This is a simplified version
        # In practice, this would require AST analysis
        
        # Add type hints to simple functions
        pattern = r'def\s+(\w+)\s*\(\s*([^)]*)\s*\):'
        
        def add_type_hint(match):
            func_name = match.group(1)
            params = match.group(2)
            
            # Skip if already has type hints
            if '->' in match.group(0) or any(':' in param for param in params.split(',')):
                return match.group(0)
            
            # Add simple type hints
            if not params:
                return f'def {func_name}() -> None:'
            else:
                return f'def {func_name}({params}) -> None:'
        
        content = re.sub(pattern, add_type_hint, content)
        
        return content
    
    def _optimize_function_signatures(self, content: str) -> str:
        """Optimize function signatures"""
        # Add default values for common parameters
        content = re.sub(
            r'def\s+(\w+)\s*\(\s*self\s*,\s*data\s*\):',
            r'def \1(self, data=None):  # Add default value',
            content
        )
        
        return content
    
    def _add_function_docstrings(self, content: str) -> str:
        """Add docstrings to functions"""
        # Add docstrings to functions without them
        pattern = r'def\s+(\w+)\s*\([^)]*\):\s*\n\s*([^"\']|["\'][^"\']*["\'][^"\n]*\n)'
        
        def add_docstring(match):
            func_name = match.group(1)
            func_body = match.group(2)
            
            # Skip if already has docstring
            if '"""' in func_body or "'''" in func_body:
                return match.group(0)
            
            # Add simple docstring
            return f'def {func_name}():\n    """{func_name} function."""\n    {func_body}'
        
        content = re.sub(pattern, add_docstring, content)
        
        return content
    
    def _optimize_database_queries(self):
        """Optimize database queries"""
        print("  🗄️  Optimizing database queries...")
        
        optimized_files = []
        
        for py_file in self.src_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Optimize SELECT * queries
                content = self._optimize_select_queries(content)
                
                # Add query optimization hints
                content = self._add_query_optimization_hints(content)
                
                if content != original_content:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    optimized_files.append(str(py_file.relative_to(self.project_root)))
                    self.optimizations_applied.append({
                        'file': str(py_file.relative_to(self.project_root)),
                        'optimization': 'database_optimization'
                    })
            
            except Exception as e:
                print(f"    Error optimizing {py_file}: {e}")
        
        print(f"    Optimized database queries in {len(optimized_files)} files")
    
    def _optimize_select_queries(self, content: str) -> str:
        """Optimize SELECT * queries"""
        # Replace SELECT * with specific columns
        content = re.sub(
            r'SELECT \* FROM',
            'SELECT id, name, created_at FROM  # Replace * with specific columns',
            content
        )
        
        return content
    
    def _add_query_optimization_hints(self, content: str) -> str:
        """Add query optimization hints"""
        # Add hints for common query optimizations
        if 'SELECT' in content:
            content += "\n\n# Query optimization hints:\n"
            content += "# - Use specific columns instead of SELECT *\n"
            content += "# - Add indexes for frequently queried columns\n"
            content += "# - Use LIMIT for large result sets\n"
            content += "# - Consider using EXISTS instead of IN for subqueries\n"
        
        return content
    
    def _optimize_memory_usage(self):
        """Optimize memory usage patterns"""
        print("  💾 Optimizing memory usage...")
        
        optimized_files = []
        
        for py_file in self.src_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Optimize list usage
                content = self._optimize_list_usage(content)
                
                # Add generator optimizations
                content = self._add_generator_optimizations(content)
                
                # Add memory cleanup hints
                content = self._add_memory_cleanup_hints(content)
                
                if content != original_content:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    optimized_files.append(str(py_file.relative_to(self.project_root)))
                    self.optimizations_applied.append({
                        'file': str(py_file.relative_to(self.project_root)),
                        'optimization': 'memory_optimization'
                    })
            
            except Exception as e:
                print(f"    Error optimizing {py_file}: {e}")
        
        print(f"    Optimized memory usage in {len(optimized_files)} files")
    
    def _optimize_list_usage(self, content: str) -> str:
        """Optimize list usage"""
        # Replace large lists with generators where appropriate
        content = re.sub(
            r'\[(.+)\s+for\s+.+\s+in\s+.+\]',
            r'(\1 for  in )  # Consider using generator expression',
            content
        )
        
        return content
    
    def _add_generator_optimizations(self, content: str) -> str:
        """Add generator optimization hints"""
        # Add hints for using generators
        if '[x for x in' in content:
            content += "\n\n# Memory optimization hint:\n"
            content += "# Consider using generator expressions (x for x in iterable) for large datasets\n"
        
        return content
    
    def _add_memory_cleanup_hints(self, content: str) -> str:
        """Add memory cleanup hints"""
        # Add hints for memory cleanup
        if 'global ' in content:
            content += "\n\n# Memory cleanup hint:\n"
            content += "# Consider using local variables instead of global variables\n"
            content += "# Add explicit cleanup for large objects\n"
        
        return content
    
    def _optimize_error_handling(self):
        """Optimize error handling"""
        print("  ⚠️  Optimizing error handling...")
        
        optimized_files = []
        
        for py_file in self.src_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Replace bare except clauses
                content = self._optimize_bare_excepts(content)
                
                # Add specific exception handling
                content = self._add_specific_exceptions(content)
                
                # Add error handling best practices
                content = self._add_error_handling_best_practices(content)
                
                if content != original_content:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    optimized_files.append(str(py_file.relative_to(self.project_root)))
                    self.optimizations_applied.append({
                        'file': str(py_file.relative_to(self.project_root)),
                        'optimization': 'error_handling_optimization'
                    })
            
            except Exception as e:
                print(f"    Error optimizing {py_file}: {e}")
        
        print(f"    Optimized error handling in {len(optimized_files)} files")
    
    def _optimize_bare_excepts(self, content: str) -> str:
        """Optimize bare except clauses"""
        # Replace bare except with specific exceptions
        content = re.sub(
            r'except:',
            'except Exception:  # Be specific about exceptions',
            content
        )
        
        return content
    
    def _add_specific_exceptions(self, content: str) -> str:
        """Add specific exception handling"""
        # Add hints for specific exceptions
        if 'open(' in content:
            content += "\n\n# Error handling hint:\n"
            content += "# Consider specific exceptions like FileNotFoundError, PermissionError\n"
        
        return content
    
    def _add_error_handling_best_practices(self, content: str) -> str:
        """Add error handling best practices"""
        # Add best practices for error handling
        if 'try:' in content:
            content += "\n\n# Error handling best practices:\n"
            content += "# - Log errors with context\n"
            content += "# - Provide user-friendly error messages\n"
            content += "# - Consider retry mechanisms for transient errors\n"
            content += "# - Clean up resources in finally blocks\n"
        
        return content
    
    def _optimize_documentation(self):
        """Optimize documentation"""
        print("  📚 Optimizing documentation...")
        
        optimized_files = []
        
        for py_file in self.src_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Add module docstring
                content = self._add_module_docstring(content, py_file)
                
                # Optimize existing docstrings
                content = self._optimize_docstrings(content)
                
                # Add documentation hints
                content = self._add_documentation_hints(content)
                
                if content != original_content:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    optimized_files.append(str(py_file.relative_to(self.project_root)))
                    self.optimizations_applied.append({
                        'file': str(py_file.relative_to(self.project_root)),
                        'optimization': 'documentation_optimization'
                    })
            
            except Exception as e:
                print(f"    Error optimizing {py_file}: {e}")
        
        print(f"    Optimized documentation in {len(optimized_files)} files")
    
    def _add_module_docstring(self, content: str, file_path: Path) -> str:
        """Add module docstring"""
        # Add docstring if missing
        if not content.strip().startswith('"""'):
            module_name = file_path.stem
            docstring = f'"""\n{module_name} module for Movie Translate\n"""\n\n'
            return docstring + content
        
        return content
    
    def _optimize_docstrings(self, content: str) -> str:
        """Optimize existing docstrings"""
        # Improve docstring format
        content = re.sub(
            r'"""([^"]*)"""',
            lambda m: f'"""\n{m.group(1).strip()}\n"""',
            content
        )
        
        return content
    
    def _add_documentation_hints(self, content: str) -> str:
        """Add documentation hints"""
        # Add hints for better documentation
        if 'def ' in content:
            content += "\n\n# Documentation hint:\n"
            content += "# - Include parameter types in docstrings\n"
            content += "# - Document return values\n"
            content += "# - Add examples for complex functions\n"
            content += "# - Document exceptions that may be raised\n"
        
        return content
    
    def _generate_optimization_report(self) -> Dict[str, Any]:
        """Generate optimization report"""
        print("📊 Generating optimization report...")
        
        # Count optimizations by type
        optimization_counts = {}
        for opt in self.optimizations_applied:
            opt_type = opt['optimization']
            optimization_counts[opt_type] = optimization_counts.get(opt_type, 0) + 1
        
        # Calculate files affected
        files_affected = set(opt['file'] for opt in self.optimizations_applied)
        
        report = {
            "summary": {
                "total_optimizations": len(self.optimizations_applied),
                "files_affected": len(files_affected),
                "optimization_types": list(optimization_counts.keys()),
                "backup_location": str(self.backup_dir),
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            },
            "optimization_counts": optimization_counts,
            "detailed_optimizations": self.optimizations_applied,
            "recommendations": [
                "Review and test all optimized code",
                "Consider using static analysis tools for further optimization",
                "Profile performance-critical sections",
                "Monitor memory usage after optimizations",
                "Keep backup until optimizations are verified"
            ]
        }
        
        return report


def main():
    """Main function to run code optimizations"""
    import time
    
    project_root = Path(__file__).parent.parent
    
    print("🔧 Movie Translate Code Optimization")
    print("=" * 50)
    
    # Run optimizations
    optimizer = CodeOptimizer(project_root)
    start_time = time.time()
    report = optimizer.optimize_all()
    end_time = time.time()
    
    # Save report
    report_file = project_root / "optimization_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n📋 Optimization Summary:")
    summary = report['summary']
    print(f"  Total Optimizations: {summary['total_optimizations']}")
    print(f"  Files Affected: {summary['files_affected']}")
    print(f"  Time Taken: {end_time - start_time:.2f}s")
    print(f"  Backup Location: {summary['backup_location']}")
    print(f"  Report saved to: {report_file}")
    
    # Print optimization counts
    print("\n📈 Optimizations by Type:")
    for opt_type, count in report['optimization_counts'].items():
        print(f"  {opt_type}: {count}")
    
    # Print recommendations
    print("\n💡 Recommendations:")
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"  {i}. {rec}")
    
    print("\n⚠️  Important:")
    print("  - Review all changes before committing")
    print("  - Run tests to ensure optimizations don't break functionality")
    print("  - Profile performance to verify improvements")
    
    return report


if __name__ == "__main__":
    main()