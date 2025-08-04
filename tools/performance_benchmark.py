"""
Performance benchmarking tools for Movie Translate
"""

import time
import psutil
import os
import sys
import tracemalloc
import cProfile
import pstats
import io
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from contextlib import contextmanager
from dataclasses import dataclass
from functools import wraps
import json


@dataclass
class BenchmarkResult:
    """Benchmark result data class"""
    name: str
    execution_time: float
    memory_usage: float
    cpu_usage: float
    peak_memory: float
    call_count: int
    errors: List[str]


class PerformanceBenchmark:
    """Performance benchmarking tool"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.src_dir = project_root / "src"
        self.results = []
        
    def benchmark_function(self, func: Callable, *args, **kwargs) -> BenchmarkResult:
        """Benchmark a single function"""
        name = func.__name__
        errors = []
        call_count = 0
        
        # Start memory tracing
        tracemalloc.start()
        
        # Get initial system metrics
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        initial_cpu = process.cpu_percent()
        
        # Profile the function
        pr = cProfile.Profile()
        pr.enable()
        
        # Execute function with timing
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            call_count = 1
        except Exception as e:
            errors.append(str(e))
            result = None
        end_time = time.time()
        
        pr.disable()
        
        # Get final system metrics
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        final_cpu = process.cpu_percent()
        
        # Get memory usage
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Calculate metrics
        execution_time = end_time - start_time
        memory_usage = final_memory - initial_memory
        cpu_usage = final_cpu - initial_cpu
        peak_memory = peak / 1024 / 1024  # MB
        
        # Get call statistics
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s)
        ps.sort_stats('cumulative')
        ps.print_stats()
        
        return BenchmarkResult(
            name=name,
            execution_time=execution_time,
            memory_usage=memory_usage,
            cpu_usage=cpu_usage,
            peak_memory=peak_memory,
            call_count=call_count,
            errors=errors
        )
    
    @contextmanager
    def benchmark_context(self, name: str):
        """Context manager for benchmarking code blocks"""
        # Start measurements
        tracemalloc.start()
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        initial_cpu = process.cpu_percent()
        start_time = time.time()
        
        try:
            yield
        finally:
            # End measurements
            end_time = time.time()
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            final_cpu = process.cpu_percent()
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            # Calculate metrics
            execution_time = end_time - start_time
            memory_usage = final_memory - initial_memory
            cpu_usage = final_cpu - initial_cpu
            peak_memory = peak / 1024 / 1024  # MB
            
            result = BenchmarkResult(
                name=name,
                execution_time=execution_time,
                memory_usage=memory_usage,
                cpu_usage=cpu_usage,
                peak_memory=peak_memory,
                call_count=1,
                errors=[]
            )
            
            self.results.append(result)
    
    def benchmark_database_operations(self):
        """Benchmark database operations"""
        print("🗄️  Benchmarking database operations...")
        
        try:
            from movie_translate.models.database_models import get_db_manager, Project
            from movie_translate.models.schemas import ProjectCreate
            
            db_manager = get_db_manager()
            db_manager.initialize()
            
            # Benchmark project creation
            def create_test_project():
                project_data = ProjectCreate(
                    name="Benchmark Test Project",
                    video_file_path="/test/video.mp4",
                    video_format="mp4",
                    target_language="en"
                )
                return db_manager.create_project(project_data.dict())
            
            result = self.benchmark_function(create_test_project)
            self.results.append(result)
            
            # Benchmark project retrieval
            project = create_test_project()
            
            def get_project():
                return db_manager.get_project(project.id)
            
            result = self.benchmark_function(get_project)
            self.results.append(result)
            
            # Benchmark project listing
            def list_projects():
                return db_manager.list_projects(limit=100)
            
            result = self.benchmark_function(list_projects)
            self.results.append(result)
            
            # Cleanup
            db_manager.delete_project(project.id)
            
        except Exception as e:
            print(f"Database benchmarking failed: {e}")
    
    def benchmark_cache_operations(self):
        """Benchmark cache operations"""
        print("💾 Benchmarking cache operations...")
        
        try:
            from movie_translate.core.cache_manager import CacheManager
            import tempfile
            
            # Create temporary cache directory
            with tempfile.TemporaryDirectory() as temp_dir:
                cache_manager = CacheManager(cache_dir=Path(temp_dir))
                
                # Benchmark cache set
                def cache_set_operation():
                    for i in range(100):
                        cache_manager.set(f"key_{i}", f"value_{i}")
                
                result = self.benchmark_function(cache_set_operation)
                self.results.append(result)
                
                # Benchmark cache get
                def cache_get_operation():
                    for i in range(100):
                        cache_manager.get(f"key_{i}")
                
                result = self.benchmark_function(cache_get_operation)
                self.results.append(result)
                
                # Benchmark cache delete
                def cache_delete_operation():
                    for i in range(100):
                        cache_manager.delete(f"key_{i}")
                
                result = self.benchmark_function(cache_delete_operation)
                self.results.append(result)
                
        except Exception as e:
            print(f"Cache benchmarking failed: {e}")
    
    def benchmark_file_operations(self):
        """Benchmark file operations"""
        print("📁 Benchmarking file operations...")
        
        try:
            from movie_translate.utils.file_utils import FileProcessor
            import tempfile
            
            # Create temporary test files
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Create test files of different sizes
                small_file = temp_path / "small.txt"
                medium_file = temp_path / "medium.txt"
                large_file = temp_path / "large.txt"
                
                small_file.write_text("x" * 1024)  # 1KB
                medium_file.write_text("x" * 1024 * 1024)  # 1MB
                large_file.write_text("x" * 1024 * 1024 * 10)  # 10MB
                
                file_processor = FileProcessor()
                
                # Benchmark file info extraction
                def get_file_info():
                    return [
                        file_processor.get_file_info(str(small_file)),
                        file_processor.get_file_info(str(medium_file)),
                        file_processor.get_file_info(str(large_file))
                    ]
                
                result = self.benchmark_function(get_file_info)
                self.results.append(result)
                
                # Benchmark file reading
                def read_files():
                    return [
                        small_file.read_text(),
                        medium_file.read_text(),
                        large_file.read_text()
                    ]
                
                result = self.benchmark_function(read_files)
                self.results.append(result)
                
        except Exception as e:
            print(f"File operations benchmarking failed: {e}")
    
    def benchmark_audio_processing(self):
        """Benchmark audio processing operations"""
        print("🎵 Benchmarking audio processing...")
        
        try:
            from movie_translate.services.audio_processing import AudioProcessor
            
            audio_processor = AudioProcessor()
            
            # Benchmark audio analysis (mock)
            def analyze_audio():
                # Mock audio analysis
                return {
                    "duration": 120.0,
                    "sample_rate": 16000,
                    "channels": 1,
                    "format": "wav",
                    "segments": [
                        {
                            "start_time": i * 5.0,
                            "end_time": (i + 1) * 5.0,
                            "text": f"Segment {i}",
                            "confidence": 0.9
                        }
                        for i in range(24)  # 24 segments for 2 minutes
                    ]
                }
            
            result = self.benchmark_function(analyze_audio)
            self.results.append(result)
            
        except Exception as e:
            print(f"Audio processing benchmarking failed: {e}")
    
    def benchmark_translation_operations(self):
        """Benchmark translation operations"""
        print("🌐 Benchmarking translation operations...")
        
        try:
            from movie_translate.services.translation import TranslationService
            
            translation_service = TranslationService()
            
            # Benchmark text translation (mock)
            def translate_text():
                # Mock translation
                return {
                    "translated_text": "Translated text",
                    "confidence": 0.95,
                    "source_language": "en",
                    "target_language": "zh"
                }
            
            result = self.benchmark_function(translate_text)
            self.results.append(result)
            
            # Benchmark batch translation
            def translate_batch():
                # Mock batch translation
                return [
                    {
                        "translated_text": f"Translated text {i}",
                        "confidence": 0.95,
                        "source_language": "en",
                        "target_language": "zh"
                    }
                    for i in range(100)
                ]
            
            result = self.benchmark_function(translate_batch)
            self.results.append(result)
            
        except Exception as e:
            print(f"Translation benchmarking failed: {e}")
    
    def benchmark_ui_operations(self):
        """Benchmark UI operations"""
        print("🖥️  Benchmarking UI operations...")
        
        try:
            # Mock UI operations
            def create_ui_components():
                # Simulate UI component creation
                components = []
                for i in range(100):
                    components.append({
                        "type": "label",
                        "text": f"Label {i}",
                        "position": (i % 10, i // 10)
                    })
                return components
            
            result = self.benchmark_function(create_ui_components)
            self.results.append(result)
            
            # Benchmark UI updates
            def update_ui_components():
                # Simulate UI updates
                updates = []
                for i in range(1000):
                    updates.append({
                        "component_id": f"comp_{i}",
                        "property": "text",
                        "value": f"Updated text {i}"
                    })
                return updates
            
            result = self.benchmark_function(update_ui_components)
            self.results.append(result)
            
        except Exception as e:
            print(f"UI benchmarking failed: {e}")
    
    def run_all_benchmarks(self) -> Dict[str, Any]:
        """Run all performance benchmarks"""
        print("🚀 Running performance benchmarks...")
        print("=" * 50)
        
        # Run individual benchmarks
        self.benchmark_database_operations()
        self.benchmark_cache_operations()
        self.benchmark_file_operations()
        self.benchmark_audio_processing()
        self.benchmark_translation_operations()
        self.benchmark_ui_operations()
        
        # Generate report
        report = self.generate_report()
        
        return report
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive benchmark report"""
        print("📊 Generating benchmark report...")
        
        if not self.results:
            return {"error": "No benchmark results available"}
        
        # Calculate statistics
        total_time = sum(r.execution_time for r in self.results)
        avg_time = total_time / len(self.results)
        max_time = max(r.execution_time for r in self.results)
        min_time = min(r.execution_time for r in self.results)
        
        total_memory = sum(r.memory_usage for r in self.results)
        avg_memory = total_memory / len(self.results)
        max_memory = max(r.memory_usage for r in self.results)
        peak_memory = max(r.peak_memory for r in self.results)
        
        # Group results by category
        categories = {}
        for result in self.results:
            category = result.name.split('_')[0]
            if category not in categories:
                categories[category] = []
            categories[category].append(result)
        
        # Calculate category statistics
        category_stats = {}
        for category, results in categories.items():
            category_time = sum(r.execution_time for r in results)
            category_memory = sum(r.memory_usage for r in results)
            
            category_stats[category] = {
                "total_time": category_time,
                "average_time": category_time / len(results),
                "total_memory": category_memory,
                "average_memory": category_memory / len(results),
                "operation_count": len(results)
            }
        
        # Generate recommendations
        recommendations = self._generate_recommendations()
        
        report = {
            "summary": {
                "total_operations": len(self.results),
                "total_execution_time": total_time,
                "average_execution_time": avg_time,
                "max_execution_time": max_time,
                "min_execution_time": min_time,
                "total_memory_usage": total_memory,
                "average_memory_usage": avg_memory,
                "max_memory_usage": max_memory,
                "peak_memory_usage": peak_memory,
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            },
            "category_statistics": category_stats,
            "detailed_results": [
                {
                    "name": r.name,
                    "execution_time": r.execution_time,
                    "memory_usage": r.memory_usage,
                    "cpu_usage": r.cpu_usage,
                    "peak_memory": r.peak_memory,
                    "call_count": r.call_count,
                    "errors": r.errors
                }
                for r in self.results
            ],
            "recommendations": recommendations
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        if not self.results:
            return recommendations
        
        # Analyze results for recommendations
        slow_operations = [r for r in self.results if r.execution_time > 1.0]
        memory_intensive = [r for r in self.results if r.memory_usage > 10.0]
        high_peak_memory = [r for r in self.results if r.peak_memory > 50.0]
        
        if slow_operations:
            recommendations.append(
                f"Consider optimizing slow operations: {[op.name for op in slow_operations[:3]]}"
            )
        
        if memory_intensive:
            recommendations.append(
                f"Memory-intensive operations detected: {[op.name for op in memory_intensive[:3]]}"
            )
        
        if high_peak_memory:
            recommendations.append(
                f"High peak memory usage in: {[op.name for op in high_peak_memory[:3]]}"
            )
        
        # Category-specific recommendations
        db_operations = [r for r in self.results if 'database' in r.name.lower()]
        if db_operations:
            avg_db_time = sum(r.execution_time for r in db_operations) / len(db_operations)
            if avg_db_time > 0.1:
                recommendations.append("Consider optimizing database queries or adding indexes")
        
        cache_operations = [r for r in self.results if 'cache' in r.name.lower()]
        if cache_operations:
            avg_cache_time = sum(r.execution_time for r in cache_operations) / len(cache_operations)
            if avg_cache_time > 0.01:
                recommendations.append("Consider optimizing cache implementation")
        
        return recommendations


def benchmark_decorator(name: str):
    """Decorator to benchmark functions"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            benchmark = PerformanceBenchmark(Path.cwd())
            
            with benchmark.benchmark_context(name):
                result = func(*args, **kwargs)
            
            return result
        
        return wrapper
    return decorator


def main():
    """Main function to run performance benchmarks"""
    project_root = Path(__file__).parent.parent
    
    print("🏃 Movie Translate Performance Benchmarking")
    print("=" * 60)
    
    # Get system information
    print(f"System Information:")
    print(f"  CPU: {psutil.cpu_count()} cores")
    print(f"  Memory: {psutil.virtual_memory().total / (1024**3):.1f} GB")
    print(f"  Python: {sys.version}")
    print()
    
    # Run benchmarks
    benchmark = PerformanceBenchmark(project_root)
    report = benchmark.run_all_benchmarks()
    
    # Save report
    report_file = project_root / "performance_benchmark_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n📋 Benchmark Summary:")
    summary = report['summary']
    print(f"  Total Operations: {summary['total_operations']}")
    print(f"  Total Execution Time: {summary['total_execution_time']:.3f}s")
    print(f"  Average Execution Time: {summary['average_execution_time']:.3f}s")
    print(f"  Peak Memory Usage: {summary['peak_memory_usage']:.2f} MB")
    print(f"  Report saved to: {report_file}")
    
    # Print slowest operations
    print("\n🐌 Slowest Operations:")
    sorted_results = sorted(report['detailed_results'], key=lambda x: x['execution_time'], reverse=True)
    for i, result in enumerate(sorted_results[:5], 1):
        print(f"  {i}. {result['name']}: {result['execution_time']:.3f}s")
    
    # Print recommendations
    print("\n💡 Performance Recommendations:")
    for i, rec in enumerate(report['recommendations'][:5], 1):
        print(f"  {i}. {rec}")
    
    return report


if __name__ == "__main__":
    main()