// Modern 3D Compiler Studio JavaScript
class CompilerStudio {
    constructor() {
        this.editor = null;
        this.currentTab = 'ast';
        this.isCompiling = false;
        this.init();
    }

    init() {
        this.initializeEditor();
        this.bindEvents();
        this.loadExampleCode();
    }

    initializeEditor() {
        const textarea = document.getElementById('codeEditor');
        this.editor = CodeMirror.fromTextArea(textarea, {
            mode: 'text/x-csrc',
            theme: 'dracula',
            lineNumbers: true,
            autoCloseBrackets: true,
            matchBrackets: true,
            indentUnit: 4,
            lineWrapping: true,
            extraKeys: {
                'Ctrl-Enter': () => this.compile(),
                'Cmd-Enter': () => this.compile()
            }
        });

        // Add syntax highlighting for our mini language
        this.addCustomSyntaxHighlighting();
    }

    addCustomSyntaxHighlighting() {
        // Custom highlighting for our language keywords
        const keywords = ['let', 'print'];
        const operators = ['+', '-', '*', '/', '='];
        
        this.editor.on('change', () => {
            const content = this.editor.getValue();
            // Simple syntax validation could go here
        });
    }

    bindEvents() {
        // Compile button
        document.getElementById('compileBtn').addEventListener('click', () => this.compile());

        // Benchmark button
        document.getElementById('benchmarkBtn').addEventListener('click', () => this.runBenchmark());

        // Tab switching
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => {
                const tab = e.target.closest('.tab-button').dataset.tab;
                this.switchTab(tab);
            });
        });

        // Copy buttons
        document.querySelectorAll('.copy-button').forEach(button => {
            button.addEventListener('click', (e) => {
                const target = e.target.closest('.copy-button').dataset.target;
                this.copyToClipboard(target);
            });
        });

        // Download assembly button
        document.getElementById('downloadAssembly').addEventListener('click', () => {
            this.downloadAssembly();
        });

        // Load example button
        document.getElementById('loadExample').addEventListener('click', () => {
            this.loadExampleCode();
        });

        // Clear code button
        document.getElementById('clearCode').addEventListener('click', () => {
            this.clearCode();
        });

        // Dark mode toggle
        document.getElementById('darkModeToggle').addEventListener('click', () => {
            this.toggleDarkMode();
        });
    }

    async compile() {
        if (this.isCompiling) return;

        const code = this.editor.getValue().trim();
        if (!code) {
            this.showError('Please enter some code to compile.');
            return;
        }

        this.isCompiling = true;
        this.showCompiling();

        try {
            const optimizationLevel = document.getElementById('optimizationLevel').value;
            const verbose = document.getElementById('verboseOutput').checked;

            const response = await fetch('/compile', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    code: code,
                    optimization_level: parseInt(optimizationLevel),
                    verbose: verbose
                })
            });

            const result = await response.json();

            if (response.ok) {
                this.showResults(result);
                this.animateSuccess();
            } else {
                this.showError(result.error || 'Compilation failed');
            }

        } catch (error) {
            console.error('Compilation error:', error);
            this.showError('Failed to connect to the compiler backend. Please ensure the Flask server is running.');
        } finally {
            this.isCompiling = false;
            this.hideCompiling();
        }
    }

    showCompiling() {
        const btn = document.getElementById('compileBtn');
        const status = document.getElementById('compilationStatus');
        const text = document.getElementById('compileText');
        
        btn.disabled = true;
        btn.classList.add('opacity-50', 'cursor-not-allowed');
        text.textContent = 'Compiling...';
        status.classList.remove('hidden');
        
        // Hide previous results/errors
        document.getElementById('resultsSection').classList.add('hidden');
        document.getElementById('errorSection').classList.add('hidden');
    }

    hideCompiling() {
        const btn = document.getElementById('compileBtn');
        const status = document.getElementById('compilationStatus');
        const text = document.getElementById('compileText');
        
        btn.disabled = false;
        btn.classList.remove('opacity-50', 'cursor-not-allowed');
        text.textContent = 'Compile & Optimize';
        status.classList.add('hidden');
    }

    showResults(result) {
        // Populate result tabs
        document.getElementById('ast-output').textContent = result.ast || 'No AST data available';
        document.getElementById('ir-output').textContent = result.ir || 'No IR data available';
        document.getElementById('optimized-output').textContent = result.optimized || 'No optimized IR available';
        document.getElementById('assembly-output').textContent = result.assembly || 'No assembly code generated';

        // Show results section
        document.getElementById('resultsSection').classList.remove('hidden');
        document.getElementById('errorSection').classList.add('hidden');

        // Animate into view
        this.animateResults();
    }

    showError(message) {
        document.getElementById('errorOutput').textContent = message;
        document.getElementById('errorSection').classList.remove('hidden');
        document.getElementById('resultsSection').classList.add('hidden');
        
        // Animate error section
        const errorSection = document.getElementById('errorSection');
        errorSection.classList.add('error-glow');
        setTimeout(() => errorSection.classList.remove('error-glow'), 2000);
    }

    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-content`).classList.add('active');

        this.currentTab = tabName;
    }

    async copyToClipboard(targetId) {
        const element = document.getElementById(targetId);
        const text = element.textContent;

        try {
            await navigator.clipboard.writeText(text);
            this.showCopySuccess();
        } catch (err) {
            // Fallback for older browsers
            this.fallbackCopyToClipboard(text);
        }
    }

    fallbackCopyToClipboard(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            this.showCopySuccess();
        } catch (err) {
            console.error('Failed to copy text: ', err);
        }
        
        document.body.removeChild(textArea);
    }

    showCopySuccess() {
        // Create temporary success message
        const message = document.createElement('div');
        message.textContent = 'Copied to clipboard!';
        message.className = 'fixed top-4 right-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg z-50 transition-all duration-300';
        document.body.appendChild(message);

        // Animate out after 2 seconds
        setTimeout(() => {
            message.style.opacity = '0';
            message.style.transform = 'translateY(-20px)';
            setTimeout(() => document.body.removeChild(message), 300);
        }, 2000);
    }

    downloadAssembly() {
        const assemblyCode = document.getElementById('assembly-output').textContent;
        if (!assemblyCode || assemblyCode === 'No assembly code generated') {
            this.showError('No assembly code available to download.');
            return;
        }

        const blob = new Blob([assemblyCode], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'compiled_program.asm';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        this.showDownloadSuccess();
    }

    showDownloadSuccess() {
        const message = document.createElement('div');
        message.textContent = 'Assembly file downloaded!';
        message.className = 'fixed top-4 right-4 bg-blue-500 text-white px-4 py-2 rounded-lg shadow-lg z-50 transition-all duration-300';
        document.body.appendChild(message);

        setTimeout(() => {
            message.style.opacity = '0';
            message.style.transform = 'translateY(-20px)';
            setTimeout(() => document.body.removeChild(message), 300);
        }, 2000);
    }

    loadExampleCode() {
        const exampleCode = `# Educational Compiler Example
# Demonstrates optimization capabilities

let x = 5 + 3;        # Constant folding: becomes 8
let y = x * 2;        # Will be 16
let z = y - 4;        # Will be 12

# This will be optimized away
let unused = 10 + 5;  # Dead code elimination

# Complex expression
let result = (x + y) * 2 - z;  # Will be computed to 36

# Print results
print(x);       # 8
print(y);       # 16  
print(z);       # 12
print(result);  # 36

# Unary operators
let negative = -5;
let positive = +10;
print(negative);
print(positive);

# Parenthesized expression
let complex = (3 + 2) * (4 - 1);  # 5 * 3 = 15
print(complex);`;

        this.editor.setValue(exampleCode);
        this.animateCodeLoad();
    }

    clearCode() {
        this.editor.setValue('');
        document.getElementById('resultsSection').classList.add('hidden');
        document.getElementById('errorSection').classList.add('hidden');
    }

    toggleDarkMode() {
        document.body.classList.toggle('dark-mode');
        const isDark = document.body.classList.contains('dark-mode');
        localStorage.setItem('darkMode', isDark);
    }

    animateSuccess() {
        const btn = document.getElementById('compileBtn');
        btn.classList.add('success-glow');
        setTimeout(() => btn.classList.remove('success-glow'), 2000);
    }

    animateResults() {
        const resultsSection = document.getElementById('resultsSection');
        resultsSection.style.opacity = '0';
        resultsSection.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            resultsSection.style.opacity = '1';
            resultsSection.style.transform = 'translateY(0)';
        }, 100);
    }

    animateCodeLoad() {
        const editorElement = document.querySelector('.CodeMirror');
        editorElement.style.transform = 'scale(0.98)';
        editorElement.style.opacity = '0.7';
        
        setTimeout(() => {
            editorElement.style.transform = 'scale(1)';
            editorElement.style.opacity = '1';
        }, 200);
    }

    async runBenchmark() {
        const code = this.editor.getValue().trim();
        if (!code) {
            this.showError('Please enter some code to benchmark.');
            return;
        }

        // Show benchmark tab and status
        this.switchTab('benchmark');
        this.showBenchmarkProgress();

        try {
            const response = await fetch('/benchmark', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    code: code
                })
            });

            const result = await response.json();

            if (response.ok) {
                this.displayBenchmarkResults(result);
            } else {
                this.showError(result.error || 'Benchmark failed');
            }

        } catch (error) {
            console.error('Benchmark error:', error);
            this.showError('Failed to connect to the benchmark service.');
        } finally {
            this.hideBenchmarkProgress();
        }
    }

    showBenchmarkProgress() {
        const status = document.getElementById('benchmarkStatus');
        const btn = document.getElementById('benchmarkBtn');
        const text = document.getElementById('benchmarkText');
        
        status.classList.remove('hidden');
        btn.disabled = true;
        btn.classList.add('opacity-50');
        text.textContent = 'RUNNING...';
        
        // Animate progress
        let progress = 0;
        const progressElement = document.getElementById('benchmarkProgress');
        const interval = setInterval(() => {
            progress++;
            progressElement.textContent = `${progress}/4`;
            if (progress >= 4) {
                clearInterval(interval);
            }
        }, 800);
    }

    hideBenchmarkProgress() {
        const status = document.getElementById('benchmarkStatus');
        const btn = document.getElementById('benchmarkBtn');
        const text = document.getElementById('benchmarkText');
        
        status.classList.add('hidden');
        btn.disabled = false;
        btn.classList.remove('opacity-50');
        text.textContent = 'RUN BENCHMARK';
    }

    displayBenchmarkResults(results) {
        const container = document.getElementById('benchmarkResults');
        const chartContainer = document.getElementById('performanceChart');
        const instructionMetrics = document.getElementById('instructionMetrics');
        const timeMetrics = document.getElementById('timeMetrics');

        // Clear previous results
        container.innerHTML = '';
        chartContainer.innerHTML = '';
        instructionMetrics.innerHTML = '';
        timeMetrics.innerHTML = '';

        // Display benchmark results for each optimization level
        results.benchmarks.forEach((benchmark, index) => {
            const card = this.createBenchmarkCard(benchmark, index);
            container.appendChild(card);
        });

        // Create performance chart
        this.createPerformanceChart(results.benchmarks, chartContainer);

        // Display detailed metrics
        this.displayDetailedMetrics(results.benchmarks, instructionMetrics, timeMetrics);

        // Show summary
        const summary = this.createBenchmarkSummary(results);
        container.appendChild(summary);
    }

    createBenchmarkCard(benchmark, index) {
        const card = document.createElement('div');
        card.className = 'benchmark-result-card';
        
        const levelClass = `o${benchmark.optimization_level}`;
        const reductionPercent = ((benchmark.original_instructions - benchmark.optimized_instructions) / benchmark.original_instructions * 100).toFixed(1);
        
        card.innerHTML = `
            <div class="flex justify-between items-start mb-3">
                <div>
                    <span class="optimization-level-badge ${levelClass}">O${benchmark.optimization_level}</span>
                    <h4 class="text-cyan-400 font-semibold mt-2" style="font-family: 'Orbitron', monospace;">
                        ${benchmark.optimization_level === 0 ? 'NO OPTIMIZATION' : 
                          benchmark.optimization_level === 1 ? 'BASIC OPTIMIZATION' :
                          benchmark.optimization_level === 2 ? 'STANDARD OPTIMIZATION' : 'AGGRESSIVE OPTIMIZATION'}
                    </h4>
                </div>
                <div class="text-right">
                    <div class="text-cyan-400 font-semibold">${benchmark.optimized_instructions}</div>
                    <div class="text-xs text-cyan-300">instructions</div>
                </div>
            </div>
            
            <div class="performance-bar">
                <div class="performance-bar-fill" style="width: ${100 - parseFloat(reductionPercent)}%"></div>
            </div>
            
            <div class="grid grid-cols-2 gap-4 mt-3 text-sm">
                <div>
                    <div class="text-cyan-300">Compilation Time</div>
                    <div class="text-cyan-400 font-semibold">${benchmark.compilation_time}ms</div>
                </div>
                <div>
                    <div class="text-cyan-300">Reduction</div>
                    <div class="text-cyan-400 font-semibold">${reductionPercent}%</div>
                </div>
            </div>
        `;
        
        return card;
    }

    createPerformanceChart(benchmarks, container) {
        container.className = 'chart-container';
        
        const maxInstructions = Math.max(...benchmarks.map(b => b.original_instructions));
        
        benchmarks.forEach(benchmark => {
            const barHeight = (benchmark.optimized_instructions / maxInstructions) * 200;
            const bar = document.createElement('div');
            bar.className = 'chart-bar';
            bar.style.height = `${barHeight}px`;
            
            const label = document.createElement('div');
            label.className = 'chart-bar-label';
            label.textContent = `O${benchmark.optimization_level}`;
            
            const value = document.createElement('div');
            value.className = 'chart-bar-value';
            value.textContent = benchmark.optimized_instructions;
            
            bar.appendChild(label);
            bar.appendChild(value);
            container.appendChild(bar);
        });
    }

    displayDetailedMetrics(benchmarks, instructionContainer, timeContainer) {
        const baseline = benchmarks[0]; // O0 as baseline
        
        benchmarks.forEach(benchmark => {
            if (benchmark.optimization_level === 0) return;
            
            const instructionImprovement = ((baseline.optimized_instructions - benchmark.optimized_instructions) / baseline.optimized_instructions * 100).toFixed(1);
            const timeChange = ((benchmark.compilation_time - baseline.compilation_time) / baseline.compilation_time * 100).toFixed(1);
            
            const instructionMetric = document.createElement('div');
            instructionMetric.className = 'metric-item';
            instructionMetric.innerHTML = `
                <span class="metric-label">O${benchmark.optimization_level} vs O0</span>
                <span>
                    <span class="metric-value">${instructionImprovement}%</span>
                    <span class="metric-improvement">↓ ${baseline.optimized_instructions - benchmark.optimized_instructions} instructions</span>
                </span>
            `;
            instructionContainer.appendChild(instructionMetric);
            
            const timeMetric = document.createElement('div');
            timeMetric.className = 'metric-item';
            timeMetric.innerHTML = `
                <span class="metric-label">O${benchmark.optimization_level} Time</span>
                <span>
                    <span class="metric-value">${benchmark.compilation_time}ms</span>
                    <span class="${timeChange > 0 ? 'metric-degradation' : 'metric-improvement'}">
                        ${timeChange > 0 ? '↑' : '↓'} ${Math.abs(timeChange)}%
                    </span>
                </span>
            `;
            timeContainer.appendChild(timeMetric);
        });
    }

    createBenchmarkSummary(results) {
        const bestOptimization = results.benchmarks.reduce((best, current) => 
            current.optimized_instructions < best.optimized_instructions ? current : best
        );
        
        const fastestCompilation = results.benchmarks.reduce((fastest, current) =>
            current.compilation_time < fastest.compilation_time ? current : fastest
        );
        
        const summary = document.createElement('div');
        summary.className = 'benchmark-summary benchmark-winner';
        summary.innerHTML = `
            <h4 class="text-cyan-400 font-semibold mb-3" style="font-family: 'Orbitron', monospace;">BENCHMARK SUMMARY</h4>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <div class="text-green-400 font-semibold">BEST OPTIMIZATION</div>
                    <div class="text-cyan-400">O${bestOptimization.optimization_level} - ${bestOptimization.optimized_instructions} instructions</div>
                    <div class="text-cyan-300 text-sm">
                        ${((results.benchmarks[0].optimized_instructions - bestOptimization.optimized_instructions) / results.benchmarks[0].optimized_instructions * 100).toFixed(1)}% reduction from O0
                    </div>
                </div>
                <div>
                    <div class="text-green-400 font-semibold">FASTEST COMPILATION</div>
                    <div class="text-cyan-400">O${fastestCompilation.optimization_level} - ${fastestCompilation.compilation_time}ms</div>
                    <div class="text-cyan-300 text-sm">
                        ${results.total_time}ms total benchmark time
                    </div>
                </div>
            </div>
        `;
        
        return summary;
    }

    // Pipeline Visualization Methods
    showPipelineVisualization(result) {
        if (!result.success) return;
        
        this.switchTab('pipeline');
        this.resetPipelineSteps();
        
        // Simulate step-by-step compilation
        const steps = [
            { step: 1, output: result.tokens || 'Tokens generated successfully', delay: 500 },
            { step: 2, output: result.ast || 'AST built successfully', delay: 1000 },
            { step: 3, output: result.semantic || 'Semantic analysis passed', delay: 1500 },
            { step: 4, output: result.ir || 'TAC generated', delay: 2000 },
            { step: 5, output: result.optimized || 'Optimization complete', delay: 2500 },
            { step: 6, output: result.assembly || 'Assembly code generated', delay: 3000 }
        ];
        
        steps.forEach(({ step, output, delay }) => {
            setTimeout(() => {
                this.activatePipelineStep(step, output);
            }, delay);
        });
    }
    
    resetPipelineSteps() {
        document.querySelectorAll('.pipeline-step').forEach(step => {
            step.classList.remove('active', 'completed');
            step.querySelector('.step-output').classList.add('hidden');
        });
        document.getElementById('pipelineProgress').style.width = '0%';
        document.getElementById('currentStepText').textContent = 'Ready';
    }
    
    activatePipelineStep(stepNumber, output) {
        const step = document.querySelector(`[data-step="${stepNumber}"]`);
        const allSteps = document.querySelectorAll('.pipeline-step');
        
        // Mark previous steps as completed
        for (let i = 1; i < stepNumber; i++) {
            const prevStep = document.querySelector(`[data-step="${i}"]`);
            prevStep.classList.remove('active');
            prevStep.classList.add('completed');
        }
        
        // Activate current step
        step.classList.add('active');
        step.classList.remove('completed');
        
        // Show output
        const outputElement = step.querySelector('.step-output');
        const outputContent = step.querySelector('pre') || step.querySelector('div');
        outputContent.textContent = output;
        outputElement.classList.remove('hidden');
        
        // Update progress
        const progress = (stepNumber / 6) * 100;
        document.getElementById('pipelineProgress').style.width = `${progress}%`;
        
        const stepNames = ['', 'Lexing', 'Parsing', 'Semantic', 'IR Gen', 'Optimize', 'CodeGen'];
        document.getElementById('currentStepText').textContent = stepNames[stepNumber];
        
        // Complete the step after a delay
        setTimeout(() => {
            step.classList.remove('active');
            step.classList.add('completed');
            
            if (stepNumber === 6) {
                document.getElementById('currentStepText').textContent = 'Complete';
            }
        }, 400);
    }

    // AST Viewer Methods
    displayASTViewer(result) {
        if (!result.success || !result.ast) return;
        
        this.switchTab('ast');
        
        // Parse AST string into structured data
        const astData = this.parseASTString(result.ast);
        
        // Update view based on selected mode
        const viewMode = document.getElementById('astViewMode').value;
        this.renderAST(astData, viewMode);
        
        // Update statistics
        this.updateASTStatistics(astData);
    }
    
    parseASTString(astString) {
        // Simple parser for the AST string format
        const lines = astString.split('\n').filter(line => line.trim());
        const root = { type: 'Program', children: [], depth: 0 };
        const stack = [root];
        
        lines.forEach(line => {
            const depth = (line.match(/^ */)[0].length / 2);
            const content = line.trim();
            
            if (content.includes(':')) {
                const [type, value] = content.split(':').map(s => s.trim());
                const node = {
                    type: type,
                    value: value || null,
                    children: [],
                    depth: depth
                };
                
                // Find correct parent
                while (stack.length > depth + 1) {
                    stack.pop();
                }
                
                const parent = stack[stack.length - 1];
                parent.children.push(node);
                stack.push(node);
            }
        });
        
        return root;
    }
    
    renderAST(astData, viewMode) {
        const container = document.getElementById('astTreeContainer');
        const treeView = document.getElementById('astTree');
        const jsonView = document.getElementById('astJson');
        const placeholder = document.getElementById('astPlaceholder');
        
        // Hide placeholder
        placeholder.classList.add('hidden');
        
        if (viewMode === 'json') {
            treeView.classList.add('hidden');
            jsonView.classList.remove('hidden');
            jsonView.querySelector('pre').textContent = JSON.stringify(astData, null, 2);
        } else {
            jsonView.classList.add('hidden');
            treeView.classList.remove('hidden');
            treeView.innerHTML = this.createASTTreeHTML(astData);
            this.bindASTNodeEvents();
        }
    }
    
    createASTTreeHTML(node, depth = 0) {
        const highlight = document.getElementById('astHighlight').value;
        let className = `ast-node depth-${Math.min(depth, 4)}`;
        
        if (highlight === 'type') {
            if (node.type.includes('Expression')) className += ' type-expression';
            else if (node.type.includes('Statement')) className += ' type-statement';
            else if (node.type.includes('Operation')) className += ' type-operation';
            else if (node.type.includes('Literal')) className += ' type-literal';
        }
        
        const hasChildren = node.children && node.children.length > 0;
        const toggle = hasChildren ? '<span class="ast-node-toggle">−</span>' : '<span class="ast-node-toggle" style="opacity:0.3;">○</span>';
        
        let html = `
            <div class="${className} expanded" data-depth="${depth}">
                <div class="ast-node-header">
                    ${toggle}
                    <span class="ast-node-type">${node.type}</span>
                    ${node.value ? `<span class="ast-node-value">${node.value}</span>` : ''}
                </div>
        `;
        
        if (hasChildren) {
            html += '<div class="ast-children">';
            node.children.forEach(child => {
                html += this.createASTTreeHTML(child, depth + 1);
            });
            html += '</div>';
        }
        
        html += '</div>';
        return html;
    }
    
    bindASTNodeEvents() {
        document.querySelectorAll('.ast-node-toggle').forEach(toggle => {
            toggle.addEventListener('click', (e) => {
                e.stopPropagation();
                const node = e.target.closest('.ast-node');
                const children = node.querySelector('.ast-children');
                
                if (children) {
                    if (node.classList.contains('expanded')) {
                        node.classList.remove('expanded');
                        node.classList.add('collapsed');
                        e.target.textContent = '+';
                    } else {
                        node.classList.remove('collapsed');
                        node.classList.add('expanded');
                        e.target.textContent = '−';
                    }
                }
            });
        });
    }
    
    updateASTStatistics(astData) {
        const stats = this.calculateASTStats(astData);
        
        document.getElementById('totalNodes').textContent = stats.totalNodes;
        document.getElementById('maxDepth').textContent = stats.maxDepth;
        document.getElementById('expressionCount').textContent = stats.expressions;
        document.getElementById('statementCount').textContent = stats.statements;
        document.getElementById('cyclomaticComplexity').textContent = stats.complexity;
        document.getElementById('nestingLevel').textContent = stats.maxDepth;
        document.getElementById('variableCount').textContent = stats.variables;
        
        // Update node types breakdown
        const nodeTypes = document.getElementById('nodeTypes');
        nodeTypes.innerHTML = '';
        Object.entries(stats.nodeTypes).forEach(([type, count]) => {
            const item = document.createElement('div');
            item.className = 'flex justify-between';
            item.innerHTML = `<span>${type}:</span><span>${count}</span>`;
            nodeTypes.appendChild(item);
        });
    }
    
    calculateASTStats(node, stats = {
        totalNodes: 0,
        maxDepth: 0,
        expressions: 0,
        statements: 0,
        variables: 0,
        complexity: 1,
        nodeTypes: {}
    }, depth = 0) {
        stats.totalNodes++;
        stats.maxDepth = Math.max(stats.maxDepth, depth);
        
        // Count node types
        stats.nodeTypes[node.type] = (stats.nodeTypes[node.type] || 0) + 1;
        
        // Count specific types
        if (node.type.includes('Expression')) stats.expressions++;
        if (node.type.includes('Statement')) stats.statements++;
        if (node.type.includes('Declaration')) stats.variables++;
        
        // Calculate complexity (simplified)
        if (node.type.includes('If') || node.type.includes('While') || node.type.includes('For')) {
            stats.complexity++;
        }
        
        // Recurse through children
        if (node.children) {
            node.children.forEach(child => {
                this.calculateASTStats(child, stats, depth + 1);
            });
        }
        
        return stats;
    }
}

// Utility functions for enhanced UX
function addFloatingParticles() {
    const container = document.querySelector('.floating-particles');
    
    for (let i = 0; i < 5; i++) {
        const particle = document.createElement('div');
        particle.className = 'floating-particle';
        particle.style.cssText = `
            position: absolute;
            width: ${Math.random() * 4 + 2}px;
            height: ${Math.random() * 4 + 2}px;
            background: rgba(139, 92, 246, ${Math.random() * 0.5 + 0.2});
            border-radius: 50%;
            top: ${Math.random() * 100}%;
            left: ${Math.random() * 100}%;
            animation: float ${Math.random() * 20 + 10}s ease-in-out infinite;
            animation-delay: ${Math.random() * 5}s;
        `;
        container.appendChild(particle);
    }
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize the main application
    const studio = new CompilerStudio();
    
    // Add floating particles for ambiance
    addFloatingParticles();
    
    // Load dark mode preference
    const isDarkMode = localStorage.getItem('darkMode') === 'true';
    if (isDarkMode) {
        document.body.classList.add('dark-mode');
    }
    
    // Add keyboard shortcuts info
    const helpText = 'Keyboard shortcuts: Ctrl+Enter / Cmd+Enter to compile';
    console.log(helpText);
    
    // Performance monitoring
    const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
            if (entry.entryType === 'navigation') {
                console.log(`Page load time: ${entry.duration}ms`);
            }
        }
    });
    observer.observe({ entryTypes: ['navigation'] });
});

// Export for potential module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CompilerStudio;
}