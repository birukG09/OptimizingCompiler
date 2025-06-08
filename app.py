"""
Flask backend for the Optimizing Compiler Studio.
Provides REST API endpoints for the web interface.
"""

from flask import Flask, request, jsonify, render_template_string, send_from_directory
from flask_cors import CORS
import json
import traceback
import io
import sys
from contextlib import redirect_stdout, redirect_stderr

# Import our compiler modules
from lexer import Lexer, LexerError
from parser import Parser, ParseError, print_ast
from semantic import SemanticAnalyzer, SemanticError
from optimizer import IRGenerator, Optimizer
from codegen import CodeGenerator

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

class CompilerAPI:
    """Main compiler API class that handles compilation requests."""
    
    def __init__(self):
        self.reset_components()
    
    def reset_components(self):
        """Reset all compiler components for a fresh compilation."""
        self.lexer = None
        self.parser = None
        self.semantic_analyzer = SemanticAnalyzer()
        self.ir_generator = IRGenerator()
        self.optimizer = Optimizer()
        self.code_generator = CodeGenerator()
    
    def compile_source(self, source_code: str, optimization_level: int = 2, verbose: bool = False) -> dict:
        """
        Compile source code and return all intermediate representations.
        
        Args:
            source_code: Source code to compile
            optimization_level: Optimization level (0-3)
            verbose: Whether to include verbose output
            
        Returns:
            Dictionary containing compilation results
        """
        try:
            self.reset_components()
            results = {
                'success': True,
                'ast': '',
                'ir': '',
                'optimized': '',
                'assembly': '',
                'tokens': '',
                'semantic_info': '',
                'verbose_output': []
            }
            
            if verbose:
                results['verbose_output'].append("=== COMPILATION PIPELINE ===")
            
            # Stage 1: Lexical Analysis
            if verbose:
                results['verbose_output'].append("\n1. LEXICAL ANALYSIS:")
                results['verbose_output'].append("-" * 30)
            
            self.lexer = Lexer(source_code)
            tokens = self.lexer.tokenize()
            
            if verbose:
                # Capture token output
                token_output = io.StringIO()
                with redirect_stdout(token_output):
                    self.lexer.print_tokens()
                results['tokens'] = token_output.getvalue()
                results['verbose_output'].append(f"Generated {len(tokens)} tokens")
            
            # Stage 2: Syntax Analysis
            if verbose:
                results['verbose_output'].append("\n2. SYNTAX ANALYSIS:")
                results['verbose_output'].append("-" * 30)
            
            self.parser = Parser(tokens)
            ast = self.parser.parse()
            
            # Capture AST output
            ast_output = io.StringIO()
            with redirect_stdout(ast_output):
                print_ast(ast)
            results['ast'] = ast_output.getvalue()
            
            if verbose:
                results['verbose_output'].append("AST generated successfully")
            
            # Stage 3: Semantic Analysis
            if verbose:
                results['verbose_output'].append("\n3. SEMANTIC ANALYSIS:")
                results['verbose_output'].append("-" * 30)
            
            success = self.semantic_analyzer.analyze(ast)
            
            if not success:
                error_output = io.StringIO()
                with redirect_stdout(error_output):
                    self.semantic_analyzer.print_errors()
                raise SemanticError(f"Semantic analysis failed:\n{error_output.getvalue()}")
            
            # Capture semantic info
            semantic_output = io.StringIO()
            with redirect_stdout(semantic_output):
                if self.semantic_analyzer.warnings:
                    self.semantic_analyzer.print_errors()
                else:
                    print("No semantic errors or warnings")
                
                # Show symbol table
                symbol_table = self.semantic_analyzer.get_symbol_table()
                print("\nDeclared variables:")
                for var in symbol_table.get_all_variables():
                    print(f"  {var.name}: {var.type}")
            
            results['semantic_info'] = semantic_output.getvalue()
            
            if verbose:
                results['verbose_output'].append("Semantic analysis passed")
                if self.semantic_analyzer.warnings:
                    results['verbose_output'].append(f"Warnings: {len(self.semantic_analyzer.warnings)}")
            
            # Stage 4: IR Generation
            if verbose:
                results['verbose_output'].append("\n4. IR GENERATION:")
                results['verbose_output'].append("-" * 30)
            
            tac_program = self.ir_generator.generate(ast)
            results['ir'] = str(tac_program)
            
            if verbose:
                results['verbose_output'].append(f"Generated {len(tac_program.instructions)} TAC instructions")
            
            # Stage 5: Optimization
            if verbose:
                results['verbose_output'].append("\n5. OPTIMIZATION:")
                results['verbose_output'].append("-" * 30)
            
            if optimization_level > 0:
                optimized_tac = self.optimizer.optimize(tac_program, passes=optimization_level)
                results['optimized'] = str(optimized_tac)
                
                if verbose:
                    original_count = len(tac_program.instructions)
                    optimized_count = len(optimized_tac.instructions)
                    reduction = ((original_count - optimized_count) / original_count * 100) if original_count > 0 else 0
                    results['verbose_output'].append(f"Optimization level: O{optimization_level}")
                    results['verbose_output'].append(f"Instructions: {original_count} → {optimized_count} ({reduction:.1f}% reduction)")
            else:
                optimized_tac = tac_program
                results['optimized'] = "Optimization disabled (O0)"
                if verbose:
                    results['verbose_output'].append("Optimization disabled")
            
            # Stage 6: Code Generation
            if verbose:
                results['verbose_output'].append("\n6. CODE GENERATION:")
                results['verbose_output'].append("-" * 30)
            
            assembly_code = self.code_generator.generate(optimized_tac)
            results['assembly'] = assembly_code
            
            if verbose:
                results['verbose_output'].append("x86-64 assembly generated successfully")
                results['verbose_output'].append("Ready for compilation with NASM + GCC")
            
            if verbose:
                results['verbose_output'].append("\n=== COMPILATION COMPLETE ===")
            
            return results
            
        except (LexerError, ParseError, SemanticError) as e:
            return {
                'success': False,
                'error': str(e),
                'stage': self._get_error_stage(e)
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Internal compiler error: {str(e)}",
                'stage': 'unknown',
                'traceback': traceback.format_exc() if verbose else None
            }
    
    def _get_error_stage(self, error):
        """Determine which compilation stage produced the error."""
        if isinstance(error, LexerError):
            return 'lexical_analysis'
        elif isinstance(error, ParseError):
            return 'syntax_analysis'
        elif isinstance(error, SemanticError):
            return 'semantic_analysis'
        else:
            return 'unknown'

# Global compiler API instance
compiler_api = CompilerAPI()

@app.route('/')
def index():
    """Redirect to homepage first, then serve the main web interface."""
    from flask import redirect, request
    
    # Check if user wants to go directly to studio
    if request.args.get('studio') == 'true':
        try:
            with open('index.html', 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return """
            <h1>Compiler Studio</h1>
            <p>Frontend files not found. Please ensure index.html is in the same directory as app.py</p>
            """, 404
    else:
        # Redirect to homepage
        return redirect('/home')

@app.route('/home')
def homepage():
    """Serve the beautiful homepage with 3D animations."""
    try:
        with open('homepage.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Homepage not found", 404

@app.route('/style.css')
def serve_css():
    """Serve the CSS file."""
    try:
        with open('style.css', 'r', encoding='utf-8') as f:
            response = app.response_class(
                f.read(),
                mimetype='text/css'
            )
            return response
    except FileNotFoundError:
        return "CSS file not found", 404

@app.route('/script.js')
def serve_js():
    """Serve the JavaScript file."""
    try:
        with open('script.js', 'r', encoding='utf-8') as f:
            response = app.response_class(
                f.read(),
                mimetype='application/javascript'
            )
            return response
    except FileNotFoundError:
        return "JavaScript file not found", 404

@app.route('/benchmark', methods=['POST'])
def benchmark_code():
    """
    Benchmark compilation across all optimization levels.
    
    Expected JSON payload:
    {
        "code": "source code string"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'code' not in data:
            return jsonify({
                'success': False,
                'error': 'No source code provided'
            }), 400
        
        source_code = data.get('code', '').strip()
        if not source_code:
            return jsonify({
                'success': False,
                'error': 'Source code cannot be empty'
            }), 400
        
        import time
        
        benchmark_results = []
        total_start_time = time.time()
        
        # Test all optimization levels
        for opt_level in [0, 1, 2, 3]:
            start_time = time.time()
            
            # Create fresh compiler instance for each test
            test_compiler = CompilerAPI()
            result = test_compiler.compile_source(source_code, opt_level, verbose=False)
            
            end_time = time.time()
            compilation_time = round((end_time - start_time) * 1000, 2)  # Convert to milliseconds
            
            if result['success']:
                # Count instructions in original and optimized IR
                original_ir_lines = len([line for line in result['ir'].split('\n') if line.strip() and not line.strip().startswith('#')])
                optimized_ir_lines = len([line for line in result['optimized'].split('\n') if line.strip() and not line.strip().startswith('#')])
                
                benchmark_results.append({
                    'optimization_level': opt_level,
                    'compilation_time': compilation_time,
                    'original_instructions': original_ir_lines,
                    'optimized_instructions': optimized_ir_lines,
                    'assembly_lines': len([line for line in result['assembly'].split('\n') if line.strip() and not line.strip().startswith(';')]),
                    'success': True
                })
            else:
                benchmark_results.append({
                    'optimization_level': opt_level,
                    'compilation_time': compilation_time,
                    'error': result.get('error', 'Unknown error'),
                    'success': False
                })
        
        total_time = round((time.time() - total_start_time) * 1000, 2)
        
        # Calculate performance metrics
        successful_benchmarks = [b for b in benchmark_results if b['success']]
        
        if not successful_benchmarks:
            return jsonify({
                'success': False,
                'error': 'All benchmark tests failed'
            }), 400
        
        return jsonify({
            'success': True,
            'benchmarks': benchmark_results,
            'total_time': total_time,
            'summary': {
                'best_optimization': min(successful_benchmarks, key=lambda x: x['optimized_instructions']),
                'fastest_compilation': min(successful_benchmarks, key=lambda x: x['compilation_time']),
                'total_tests': len(benchmark_results),
                'successful_tests': len(successful_benchmarks)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Benchmark error: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@app.route('/compile', methods=['POST'])
def compile_code():
    """
    Compile source code endpoint.
    
    Expected JSON payload:
    {
        "code": "source code string",
        "optimization_level": 0-3,
        "verbose": boolean
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'code' not in data:
            return jsonify({
                'success': False,
                'error': 'No source code provided'
            }), 400
        
        source_code = data.get('code', '').strip()
        if not source_code:
            return jsonify({
                'success': False,
                'error': 'Source code cannot be empty'
            }), 400
        
        optimization_level = data.get('optimization_level', 2)
        verbose = data.get('verbose', False)
        
        # Validate optimization level
        if not isinstance(optimization_level, int) or optimization_level < 0 or optimization_level > 3:
            return jsonify({
                'success': False,
                'error': 'Optimization level must be between 0 and 3'
            }), 400
        
        # Compile the code
        result = compiler_api.compile_source(source_code, optimization_level, verbose)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/examples')
def get_examples():
    """Get example source code snippets."""
    examples = {
        'basic': {
            'name': 'Basic Arithmetic',
            'description': 'Simple variable declarations and arithmetic',
            'code': '''let x = 5 + 3;
let y = x * 2;
print(x);
print(y);'''
        },
        'optimization_demo': {
            'name': 'Optimization Demo',
            'description': 'Demonstrates various optimizations',
            'code': '''# Constant folding demo
let a = 10 + 5;       # Will be folded to 15
let b = a * 1;        # Will be optimized to just 'a'
let c = b + 0;        # Will be optimized away

# Complex expression
let x = 5 + 3;
let y = x * 2;
let result = (x + y) * 2 - 12;

print(result);'''
        },
        'complex': {
            'name': 'Complex Expression',
            'description': 'Nested expressions with parentheses',
            'code': '''let a = (3 + 2) * (4 - 1);
let b = -5 + 10;
let c = a * b / 3;
print(a);
print(b);
print(c);'''
        }
    }
    
    return jsonify(examples)

@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'components': {
            'lexer': 'ok',
            'parser': 'ok', 
            'semantic_analyzer': 'ok',
            'optimizer': 'ok',
            'code_generator': 'ok'
        }
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    print("🚀 Starting Optimizing Compiler Studio Backend...")
    print("📍 Web interface: http://localhost:5000")
    print("🔧 API endpoint: http://localhost:5000/compile")
    print("❤️  Health check: http://localhost:5000/api/health")
    print("-" * 50)
    
    # Run the Flask development server
    app.run(
        host='0.0.0.0',  # Make accessible from all interfaces
        port=5000,
        debug=True,
        threaded=True
    )