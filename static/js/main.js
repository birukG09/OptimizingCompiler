/**
 * OptimizingCompiler - Main JavaScript File
 * Handles UI interactions, animations, and dynamic content
 */

// Global variables
let animationObserver = null;
let isAnimationsEnabled = true;

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApplication();
});

/**
 * Initialize the entire application
 */
function initializeApplication() {
    // Initialize animations
    initializeAnimations();
    
    // Initialize navigation
    initializeNavigation();
    
    // Initialize syntax highlighting
    initializeSyntaxHighlighting();
    
    // Initialize tooltips and popovers
    initializeBootstrapComponents();
    
    // Initialize page-specific functionality
    initializePageSpecificFeatures();
    
    // Initialize accessibility features
    initializeAccessibility();
    
    console.log('OptimizingCompiler application initialized successfully');
}

/**
 * Initialize animation system
 */
function initializeAnimations() {
    // Check if user prefers reduced motion
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    
    if (prefersReducedMotion) {
        isAnimationsEnabled = false;
        document.body.classList.add('reduced-motion');
        return;
    }
    
    // Create intersection observer for scroll animations
    animationObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in-view');
                
                // Add staggered animation delays for grouped elements
                const parent = entry.target.closest('.row, .container');
                if (parent) {
                    const siblings = parent.querySelectorAll('.animate-fade-in, .animate-slide-up, .animate-scale-in');
                    siblings.forEach((sibling, index) => {
                        if (sibling === entry.target) {
                            sibling.style.animationDelay = `${index * 0.1}s`;
                        }
                    });
                }
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    // Observe all animation elements
    observeAnimationElements();
    
    // Initialize floating animations
    initializeFloatingAnimations();
}

/**
 * Observe elements for scroll animations
 */
function observeAnimationElements() {
    const animationElements = document.querySelectorAll(
        '.animate-fade-in, .animate-slide-up, .animate-scale-in'
    );
    
    animationElements.forEach(element => {
        if (animationObserver) {
            animationObserver.observe(element);
        }
    });
}

/**
 * Initialize floating animations for hero elements
 */
function initializeFloatingAnimations() {
    const floatingElements = document.querySelectorAll('.animate-float');
    
    floatingElements.forEach((element, index) => {
        if (isAnimationsEnabled) {
            element.style.animationDelay = `${index * 0.5}s`;
            element.classList.add('floating-active');
        }
    });
}

/**
 * Initialize navigation functionality
 */
function initializeNavigation() {
    const navbar = document.querySelector('.navbar');
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    // Add scroll effect to navbar
    if (navbar) {
        window.addEventListener('scroll', throttle(() => {
            if (window.scrollY > 50) {
                navbar.classList.add('navbar-scrolled');
            } else {
                navbar.classList.remove('navbar-scrolled');
            }
        }, 100));
    }
    
    // Handle mobile navigation
    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            const isExpanded = this.getAttribute('aria-expanded') === 'true';
            
            if (isExpanded) {
                navbarCollapse.classList.remove('show');
                this.setAttribute('aria-expanded', 'false');
            } else {
                navbarCollapse.classList.add('show');
                this.setAttribute('aria-expanded', 'true');
            }
        });
        
        // Close mobile menu when clicking on links
        const navLinks = navbarCollapse.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth < 992) {
                    navbarCollapse.classList.remove('show');
                    navbarToggler.setAttribute('aria-expanded', 'false');
                }
            });
        });
    }
    
    // Smooth scrolling for anchor links
    initializeSmoothScrolling();
}

/**
 * Initialize smooth scrolling for anchor links
 */
function initializeSmoothScrolling() {
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                e.preventDefault();
                
                const offsetTop = targetElement.offsetTop - 80; // Account for navbar height
                
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
}

/**
 * Initialize syntax highlighting
 */
function initializeSyntaxHighlighting() {
    // Initialize Prism.js if available
    if (typeof Prism !== 'undefined') {
        // Configure Prism for assembly language
        Prism.languages.asm = Prism.languages.extend('clike', {
            'comment': [
                /;.*/,
                /\/\*[\s\S]*?(?:\*\/|$)/
            ],
            'string': {
                pattern: /(["'])(?:\\(?:\r\n|[\s\S])|(?!\1)[^\\\r\n])*\1/,
                greedy: true
            },
            'label': {
                pattern: /^\s*[A-Z_a-z]\w*:/m,
                alias: 'function'
            },
            'keyword': [
                /\b(?:mov|add|sub|mul|div|push|pop|call|ret|jmp|je|jne|jl|jle|jg|jge|cmp|test|and|or|xor|not|shl|shr|lea|nop)\b/i,
                /\b(?:eax|ebx|ecx|edx|esi|edi|esp|ebp|rax|rbx|rcx|rdx|rsi|rdi|rsp|rbp|r[8-9]|r1[0-5])\b/i
            ],
            'number': /(?:\b0x[\da-f]+|\b\d+)/i,
            'operator': /[+\-*\/=<>!&|^~]/
        });
        
        // Highlight all code blocks
        Prism.highlightAll();
        
        // Re-highlight when new content is added
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.addedNodes.length > 0) {
                    const codeBlocks = document.querySelectorAll('pre[class*="language-"], code[class*="language-"]');
                    if (codeBlocks.length > 0) {
                        Prism.highlightAll();
                    }
                }
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
}

/**
 * Initialize Bootstrap components
 */
function initializeBootstrapComponents() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

/**
 * Initialize page-specific features
 */
function initializePageSpecificFeatures() {
    const currentPage = getCurrentPage();
    
    switch (currentPage) {
        case 'home':
            initializeHomePage();
            break;
        case 'compiler':
            initializeCompilerPage();
            break;
        case 'about':
            initializeAboutPage();
            break;
        default:
            console.log('No specific initialization for current page');
    }
}

/**
 * Get current page identifier
 */
function getCurrentPage() {
    const path = window.location.pathname;
    
    if (path === '/' || path === '/home') {
        return 'home';
    } else if (path === '/compiler') {
        return 'compiler';
    } else if (path === '/about') {
        return 'about';
    }
    
    return 'unknown';
}

/**
 * Initialize home page specific features
 */
function initializeHomePage() {
    // Initialize typing animation for hero text
    initializeTypingAnimation();
    
    // Initialize feature card hover effects
    initializeFeatureCardEffects();
    
    // Initialize optimization level cards
    initializeOptimizationCards();
    
    // Initialize tech stack animations
    initializeTechStackAnimations();
}

/**
 * Initialize typing animation effect
 */
function initializeTypingAnimation() {
    const heroTitle = document.querySelector('.hero-title');
    const heroSubtitle = document.querySelector('.hero-subtitle');
    
    if (heroTitle && isAnimationsEnabled) {
        // Add typing cursor effect
        const titleText = heroTitle.textContent;
        heroTitle.innerHTML = titleText + '<span class="typing-cursor">|</span>';
        
        // Animate cursor blinking
        const cursor = heroTitle.querySelector('.typing-cursor');
        if (cursor) {
            setInterval(() => {
                cursor.style.opacity = cursor.style.opacity === '0' ? '1' : '0';
            }, 530);
        }
    }
}

/**
 * Initialize feature card hover effects
 */
function initializeFeatureCardEffects() {
    const featureItems = document.querySelectorAll('.feature-item');
    
    featureItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            if (isAnimationsEnabled) {
                this.style.transform = 'translateX(10px) scale(1.02)';
                this.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
            }
        });
        
        item.addEventListener('mouseleave', function() {
            if (isAnimationsEnabled) {
                this.style.transform = 'translateX(0) scale(1)';
            }
        });
    });
}

/**
 * Initialize optimization level cards
 */
function initializeOptimizationCards() {
    const optimizationCards = document.querySelectorAll('.optimization-card');
    
    optimizationCards.forEach((card, index) => {
        // Add progressive enhancement
        card.addEventListener('mouseenter', function() {
            if (isAnimationsEnabled) {
                this.style.transform = 'translateY(-10px) rotateX(5deg)';
                this.style.boxShadow = '0 20px 40px rgba(0, 122, 204, 0.2)';
                this.style.transition = 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)';
            }
        });
        
        card.addEventListener('mouseleave', function() {
            if (isAnimationsEnabled) {
                this.style.transform = 'translateY(0) rotateX(0)';
                this.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.3)';
            }
        });
        
        // Add click animation
        card.addEventListener('click', function() {
            if (isAnimationsEnabled) {
                this.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    this.style.transform = 'scale(1)';
                }, 150);
            }
        });
    });
}

/**
 * Initialize tech stack animations
 */
function initializeTechStackAnimations() {
    const techCards = document.querySelectorAll('.tech-card');
    
    techCards.forEach((card, index) => {
        // Staggered reveal animation
        if (isAnimationsEnabled) {
            card.style.animationDelay = `${index * 0.2}s`;
        }
        
        // Icon rotation on hover
        const icon = card.querySelector('i');
        if (icon) {
            card.addEventListener('mouseenter', function() {
                if (isAnimationsEnabled) {
                    icon.style.transform = 'rotateY(180deg) scale(1.1)';
                    icon.style.transition = 'transform 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
                }
            });
            
            card.addEventListener('mouseleave', function() {
                if (isAnimationsEnabled) {
                    icon.style.transform = 'rotateY(0) scale(1)';
                }
            });
        }
    });
}

/**
 * Initialize compiler page specific features
 */
function initializeCompilerPage() {
    // Initialize code editor enhancements
    initializeCodeEditor();
    
    // Initialize real-time validation
    initializeCodeValidation();
    
    // Initialize keyboard shortcuts
    initializeKeyboardShortcuts();
    
    // Initialize auto-save functionality
    initializeAutoSave();
}

/**
 * Initialize code editor enhancements
 */
function initializeCodeEditor() {
    const codeEditor = document.getElementById('assemblyInput');
    
    if (codeEditor) {
        // Add line numbers
        addLineNumbers(codeEditor);
        
        // Add syntax highlighting on input
        codeEditor.addEventListener('input', debounce(function() {
            highlightSyntax(this);
        }, 300));
        
        // Add auto-indentation
        codeEditor.addEventListener('keydown', function(e) {
            handleAutoIndentation(e, this);
        });
        
        // Add bracket matching
        codeEditor.addEventListener('input', function() {
            handleBracketMatching(this);
        });
    }
}

/**
 * Add line numbers to code editor
 */
function addLineNumbers(editor) {
    const lineNumbersDiv = document.createElement('div');
    lineNumbersDiv.className = 'line-numbers';
    lineNumbersDiv.style.cssText = `
        position: absolute;
        left: 0;
        top: 0;
        width: 40px;
        height: 100%;
        background: var(--vscode-bg-tertiary);
        border-right: 1px solid var(--vscode-border);
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        font-size: 14px;
        line-height: 1.5;
        color: var(--vscode-text-muted);
        padding: 1.5rem 0.5rem;
        user-select: none;
        overflow: hidden;
    `;
    
    // Wrap editor in container
    const wrapper = document.createElement('div');
    wrapper.style.position = 'relative';
    editor.parentNode.insertBefore(wrapper, editor);
    wrapper.appendChild(lineNumbersDiv);
    wrapper.appendChild(editor);
    
    // Adjust editor padding
    editor.style.paddingLeft = '50px';
    
    // Update line numbers
    function updateLineNumbers() {
        const lines = editor.value.split('\n').length;
        let lineNumbersText = '';
        for (let i = 1; i <= lines; i++) {
            lineNumbersText += i + '\n';
        }
        lineNumbersDiv.textContent = lineNumbersText;
    }
    
    // Initial update and bind to changes
    updateLineNumbers();
    editor.addEventListener('input', updateLineNumbers);
    editor.addEventListener('scroll', function() {
        lineNumbersDiv.scrollTop = editor.scrollTop;
    });
}

/**
 * Highlight syntax in real-time
 */
function highlightSyntax(editor) {
    // Basic syntax highlighting for assembly
    const keywords = ['mov', 'add', 'sub', 'mul', 'div', 'push', 'pop', 'call', 'ret', 'jmp'];
    const registers = ['eax', 'ebx', 'ecx', 'edx', 'esi', 'edi', 'esp', 'ebp', 'rax', 'rbx', 'rcx', 'rdx', 'rsi', 'rdi', 'rsp', 'rbp'];
    
    // This is a simplified version - in a full implementation, you'd use a proper syntax highlighter
    console.log('Syntax highlighting triggered for:', editor.value.substring(0, 50));
}

/**
 * Handle auto-indentation
 */
function handleAutoIndentation(event, editor) {
    if (event.key === 'Enter') {
        const cursorPosition = editor.selectionStart;
        const textBeforeCursor = editor.value.substring(0, cursorPosition);
        const lines = textBeforeCursor.split('\n');
        const currentLine = lines[lines.length - 1];
        
        // Get indentation of current line
        const indentMatch = currentLine.match(/^\s*/);
        const indent = indentMatch ? indentMatch[0] : '';
        
        // Add same indentation to next line
        setTimeout(() => {
            const newCursorPosition = editor.selectionStart;
            editor.value = editor.value.substring(0, newCursorPosition) + 
                          indent + 
                          editor.value.substring(newCursorPosition);
            editor.selectionStart = editor.selectionEnd = newCursorPosition + indent.length;
        }, 0);
    }
}

/**
 * Handle bracket matching
 */
function handleBracketMatching(editor) {
    // Simple bracket matching implementation
    const brackets = {'(': ')', '[': ']', '{': '}'};
    const text = editor.value;
    const cursor = editor.selectionStart;
    
    if (cursor > 0) {
        const charBefore = text[cursor - 1];
        const charAfter = text[cursor];
        
        if (brackets[charBefore] && charAfter !== brackets[charBefore]) {
            // Auto-close bracket
            editor.value = text.substring(0, cursor) + brackets[charBefore] + text.substring(cursor);
            editor.selectionStart = editor.selectionEnd = cursor;
        }
    }
}

/**
 * Initialize real-time code validation
 */
function initializeCodeValidation() {
    const codeEditor = document.getElementById('assemblyInput');
    
    if (codeEditor) {
        codeEditor.addEventListener('input', debounce(function() {
            validateAssemblyCode(this.value);
        }, 500));
    }
}

/**
 * Validate assembly code
 */
function validateAssemblyCode(code) {
    const lines = code.split('\n');
    const errors = [];
    
    lines.forEach((line, index) => {
        const trimmedLine = line.trim();
        if (trimmedLine && !trimmedLine.startsWith(';')) {
            // Basic validation - check for valid instruction format
            const parts = trimmedLine.split(/\s+/);
            if (parts.length > 0) {
                const instruction = parts[0].toLowerCase();
                const validInstructions = ['mov', 'add', 'sub', 'mul', 'div', 'push', 'pop', 'call', 'ret', 'jmp', 'je', 'jne', 'cmp', 'test'];
                
                if (!validInstructions.includes(instruction)) {
                    errors.push({
                        line: index + 1,
                        message: `Unknown instruction: ${instruction}`
                    });
                }
            }
        }
    });
    
    displayValidationErrors(errors);
}

/**
 * Display validation errors
 */
function displayValidationErrors(errors) {
    let errorContainer = document.getElementById('validationErrors');
    
    if (!errorContainer) {
        errorContainer = document.createElement('div');
        errorContainer.id = 'validationErrors';
        errorContainer.className = 'validation-errors mt-2';
        
        const editor = document.getElementById('assemblyInput');
        if (editor && editor.parentNode) {
            editor.parentNode.insertBefore(errorContainer, editor.nextSibling);
        }
    }
    
    if (errors.length > 0) {
        const errorHtml = errors.map(error => 
            `<div class="alert alert-warning alert-sm py-1">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Line ${error.line}: ${error.message}
            </div>`
        ).join('');
        
        errorContainer.innerHTML = errorHtml;
        errorContainer.style.display = 'block';
    } else {
        errorContainer.style.display = 'none';
    }
}

/**
 * Initialize keyboard shortcuts
 */
function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl+Enter or Cmd+Enter to compile
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            const compileBtn = document.getElementById('compileBtn');
            if (compileBtn && !compileBtn.disabled) {
                compileBtn.click();
            }
        }
        
        // Ctrl+K or Cmd+K to clear input
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const clearBtn = document.getElementById('clearInput');
            if (clearBtn) {
                clearBtn.click();
            }
        }
        
        // Ctrl+L or Cmd+L to load sample
        if ((e.ctrlKey || e.metaKey) && e.key === 'l') {
            e.preventDefault();
            const sampleBtn = document.getElementById('loadSample');
            if (sampleBtn) {
                sampleBtn.click();
            }
        }
    });
}

/**
 * Initialize auto-save functionality
 */
function initializeAutoSave() {
    const codeEditor = document.getElementById('assemblyInput');
    
    if (codeEditor) {
        // Load saved content on page load
        const savedContent = localStorage.getItem('assemblyCode');
        if (savedContent && !codeEditor.value.trim()) {
            codeEditor.value = savedContent;
        }
        
        // Auto-save on input
        codeEditor.addEventListener('input', debounce(function() {
            localStorage.setItem('assemblyCode', this.value);
            showAutoSaveIndicator();
        }, 1000));
    }
}

/**
 * Show auto-save indicator
 */
function showAutoSaveIndicator() {
    let indicator = document.getElementById('autoSaveIndicator');
    
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.id = 'autoSaveIndicator';
        indicator.className = 'auto-save-indicator';
        indicator.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--vscode-success);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            font-size: 0.8rem;
            z-index: 9999;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;
        indicator.innerHTML = '<i class="fas fa-check me-2"></i>Auto-saved';
        document.body.appendChild(indicator);
    }
    
    indicator.style.opacity = '1';
    setTimeout(() => {
        indicator.style.opacity = '0';
    }, 2000);
}

/**
 * Initialize about page specific features
 */
function initializeAboutPage() {
    // Initialize progress bars for optimization techniques
    initializeProgressBars();
    
    // Initialize interactive process steps
    initializeProcessSteps();
    
    // Initialize benchmark visualizations
    initializeBenchmarkVisualizations();
}

/**
 * Initialize progress bars
 */
function initializeProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    
    progressBars.forEach((bar, index) => {
        if (isAnimationsEnabled) {
            setTimeout(() => {
                const targetWidth = bar.getAttribute('data-width') || '75%';
                bar.style.width = targetWidth;
                bar.style.transition = 'width 1s ease-in-out';
            }, index * 200);
        }
    });
}

/**
 * Initialize interactive process steps
 */
function initializeProcessSteps() {
    const processSteps = document.querySelectorAll('.process-step');
    
    processSteps.forEach((step, index) => {
        step.addEventListener('click', function() {
            // Remove active class from all steps
            processSteps.forEach(s => s.classList.remove('active'));
            
            // Add active class to clicked step
            this.classList.add('active');
            
            // Show step details
            showStepDetails(index);
        });
    });
}

/**
 * Show step details
 */
function showStepDetails(stepIndex) {
    const stepDetails = [
        {
            title: "Input Processing",
            content: "The compiler parses x86 assembly code, tokenizes instructions, and validates syntax before translation."
        },
        {
            title: "Architecture Translation", 
            content: "32-bit registers are mapped to 64-bit equivalents, and instruction formats are updated for x86_64 compatibility."
        },
        {
            title: "Optimization Passes",
            content: "Multiple optimization techniques are applied based on the selected level, including dead code elimination and instruction reordering."
        },
        {
            title: "Benchmarking",
            content: "Performance metrics are collected across four stages to measure compilation effectiveness and optimization impact."
        }
    ];
    
    // Create or update details modal/panel
    let detailsPanel = document.getElementById('stepDetailsPanel');
    if (!detailsPanel) {
        detailsPanel = document.createElement('div');
        detailsPanel.id = 'stepDetailsPanel';
        detailsPanel.className = 'step-details-panel mt-4 p-4';
        detailsPanel.style.cssText = `
            background: var(--vscode-bg-secondary);
            border: 1px solid var(--vscode-border);
            border-radius: 8px;
            display: none;
        `;
        
        const processSection = document.querySelector('.process-step').closest('.row');
        if (processSection) {
            processSection.appendChild(detailsPanel);
        }
    }
    
    const step = stepDetails[stepIndex];
    detailsPanel.innerHTML = `
        <h5 class="text-primary">${step.title}</h5>
        <p class="text-muted">${step.content}</p>
    `;
    detailsPanel.style.display = 'block';
}

/**
 * Initialize benchmark visualizations
 */
function initializeBenchmarkVisualizations() {
    const benchmarkCards = document.querySelectorAll('.benchmark-card');
    
    benchmarkCards.forEach((card, index) => {
        // Add hover effects with data visualization
        card.addEventListener('mouseenter', function() {
            if (isAnimationsEnabled) {
                this.style.transform = 'translateY(-5px) scale(1.02)';
                this.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
                
                // Show additional metrics on hover
                showBenchmarkDetails(this, index);
            }
        });
        
        card.addEventListener('mouseleave', function() {
            if (isAnimationsEnabled) {
                this.style.transform = 'translateY(0) scale(1)';
                hideBenchmarkDetails(this);
            }
        });
    });
}

/**
 * Show benchmark details on hover
 */
function showBenchmarkDetails(card, index) {
    const details = [
        "Measures instruction count reduction and binary size optimization",
        "Tracks compilation speed across different optimization levels", 
        "Evaluates actual execution speed improvements",
        "Analyzes usage of x86_64 specific features"
    ];
    
    let tooltip = card.querySelector('.benchmark-tooltip');
    if (!tooltip) {
        tooltip = document.createElement('div');
        tooltip.className = 'benchmark-tooltip';
        tooltip.style.cssText = `
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            background: var(--vscode-bg-tertiary);
            color: var(--vscode-text);
            padding: 0.5rem 1rem;
            border-radius: 4px;
            font-size: 0.8rem;
            white-space: nowrap;
            z-index: 1000;
            opacity: 0;
            transition: opacity 0.3s ease;
            margin-bottom: 10px;
        `;
        card.style.position = 'relative';
        card.appendChild(tooltip);
    }
    
    tooltip.textContent = details[index];
    tooltip.style.opacity = '1';
}

/**
 * Hide benchmark details
 */
function hideBenchmarkDetails(card) {
    const tooltip = card.querySelector('.benchmark-tooltip');
    if (tooltip) {
        tooltip.style.opacity = '0';
    }
}

/**
 * Initialize accessibility features
 */
function initializeAccessibility() {
    // Add keyboard navigation for interactive elements
    initializeKeyboardNavigation();
    
    // Add ARIA labels and descriptions
    addARIALabels();
    
    // Initialize focus management
    initializeFocusManagement();
    
    // Add screen reader announcements
    initializeScreenReaderSupport();
}

/**
 * Initialize keyboard navigation
 */
function initializeKeyboardNavigation() {
    // Make interactive elements focusable
    const interactiveElements = document.querySelectorAll(
        '.optimization-card, .tech-card, .process-step, .benchmark-card'
    );
    
    interactiveElements.forEach(element => {
        if (!element.hasAttribute('tabindex')) {
            element.setAttribute('tabindex', '0');
        }
        
        // Add keyboard event listeners
        element.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    });
}

/**
 * Add ARIA labels and descriptions
 */
function addARIALabels() {
    // Add labels to form elements
    const formElements = document.querySelectorAll('input, select, textarea');
    formElements.forEach(element => {
        if (!element.hasAttribute('aria-label') && !element.hasAttribute('aria-labelledby')) {
            const label = element.previousElementSibling;
            if (label && label.tagName === 'LABEL') {
                element.setAttribute('aria-labelledby', label.id || generateId('label'));
                if (!label.id) {
                    label.id = element.getAttribute('aria-labelledby');
                }
            }
        }
    });
    
    // Add descriptions to complex elements
    const codeEditor = document.getElementById('assemblyInput');
    if (codeEditor) {
        codeEditor.setAttribute('aria-label', 'Assembly code editor');
        codeEditor.setAttribute('aria-describedby', 'assemblyInputHelp');
        
        // Create help text if it doesn't exist
        if (!document.getElementById('assemblyInputHelp')) {
            const helpText = document.createElement('div');
            helpText.id = 'assemblyInputHelp';
            helpText.className = 'sr-only';
            helpText.textContent = 'Enter your x86 assembly code. Use Ctrl+Enter to compile, Ctrl+K to clear, Ctrl+L to load sample code.';
            codeEditor.parentNode.appendChild(helpText);
        }
    }
}

/**
 * Initialize focus management
 */
function initializeFocusManagement() {
    // Trap focus in modals and overlays
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Tab') {
            const focusableElements = getFocusableElements();
            const firstElement = focusableElements[0];
            const lastElement = focusableElements[focusableElements.length - 1];
            
            if (e.shiftKey && document.activeElement === firstElement) {
                e.preventDefault();
                lastElement.focus();
            } else if (!e.shiftKey && document.activeElement === lastElement) {
                e.preventDefault();
                firstElement.focus();
            }
        }
    });
}

/**
 * Get focusable elements
 */
function getFocusableElements() {
    const focusableSelectors = [
        'a[href]',
        'button:not([disabled])',
        'input:not([disabled])',
        'select:not([disabled])',
        'textarea:not([disabled])',
        '[tabindex]:not([tabindex="-1"])'
    ];
    
    return Array.from(document.querySelectorAll(focusableSelectors.join(', ')))
        .filter(element => {
            return element.offsetWidth > 0 && element.offsetHeight > 0;
        });
}

/**
 * Initialize screen reader support
 */
function initializeScreenReaderSupport() {
    // Create live region for announcements
    const liveRegion = document.createElement('div');
    liveRegion.id = 'liveRegion';
    liveRegion.setAttribute('aria-live', 'polite');
    liveRegion.setAttribute('aria-atomic', 'true');
    liveRegion.className = 'sr-only';
    document.body.appendChild(liveRegion);
    
    // Announce important events
    window.announceToScreenReader = function(message) {
        const liveRegion = document.getElementById('liveRegion');
        if (liveRegion) {
            liveRegion.textContent = message;
            
            // Clear after announcement
            setTimeout(() => {
                liveRegion.textContent = '';
            }, 1000);
        }
    };
}

/**
 * Utility function: Throttle
 */
function throttle(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Utility function: Debounce
 */
function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            timeout = null;
            if (!immediate) func(...args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func(...args);
    };
}

/**
 * Utility function: Generate unique ID
 */
function generateId(prefix = 'id') {
    return prefix + '_' + Math.random().toString(36).substr(2, 9);
}

/**
 * Utility function: Format file size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Utility function: Copy text to clipboard
 */
function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        return navigator.clipboard.writeText(text);
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        return new Promise((resolve, reject) => {
            if (document.execCommand('copy')) {
                resolve();
            } else {
                reject();
            }
            document.body.removeChild(textArea);
        });
    }
}

/**
 * Utility function: Download text as file
 */
function downloadTextAsFile(text, filename) {
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

/**
 * Export utilities for global use
 */
window.OptimizingCompiler = {
    utils: {
        throttle,
        debounce,
        generateId,
        formatFileSize,
        copyToClipboard,
        downloadTextAsFile
    },
    announceToScreenReader: window.announceToScreenReader
};

// Initialize application
console.log('OptimizingCompiler JavaScript loaded successfully');
