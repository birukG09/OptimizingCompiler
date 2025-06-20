from flask import render_template, request, jsonify, flash
from app import app
from compiler.x86_compiler import X86Compiler
from compiler.benchmarks import BenchmarkRunner
import logging

logger = logging.getLogger(__name__)

@app.route('/')
def home():
    """Home page with animated introduction"""
    return render_template('index.html')

@app.route('/about')
def about():
    """About page explaining compiler functionality"""
    return render_template('about.html')

@app.route('/compiler')
def compiler():
    """Main compiler interface"""
    return render_template('compiler.html')

@app.route('/compile', methods=['POST'])
def compile_code():
    """Handle assembly compilation requests"""
    try:
        # Get form data
        assembly_code = request.form.get('assembly_code', '').strip()
        optimization_level = request.form.get('optimization_level', 'none')
        
        if not assembly_code:
            return jsonify({
                'success': False,
                'error': 'Please provide assembly code to compile'
            })
        
        # Initialize compiler
        compiler = X86Compiler()
        
        # Compile the code
        result = compiler.compile(assembly_code, optimization_level)
        
        if result['success']:
            # Run benchmarks if compilation successful
            benchmark_runner = BenchmarkRunner()
            benchmarks = benchmark_runner.run_benchmarks(
                result['original_code'],
                result['compiled_code'],
                optimization_level
            )
            result['benchmarks'] = benchmarks
            
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Compilation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Compilation failed: {str(e)}'
        })

@app.route('/contact')
def contact():
    """Contact information"""
    contact_info = {
        'name': 'Biruk Gebre',
        'github': 'birukG09',
        'github_url': 'https://github.com/birukG09'
    }
    return jsonify(contact_info)

@app.errorhandler(404)
def not_found(error):
    return render_template('base.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('base.html', error="Internal server error"), 500
