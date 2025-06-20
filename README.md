# ⚙️ OptimizingCompiler

**OptimizingCompiler** is a web-based compiler that translates **x86 (32-bit)** assembly code into optimized **x86_64 (64-bit)** machine code.  
Built with a **Flask backend** and a frontend using **HTML, CSS, and JavaScript**, the project is designed for **experimentation, benchmarking**, and **educational use** in low-level compiler design.

It supports multiple optimization levels and includes benchmark modules to measure performance, size, and transformation accuracy.



## 🚀 Features

- 🔁 **Architecture Translation**: x86 (32-bit) → x86_64 (64-bit)
- 🧠 **Multiple Optimization Levels**:
  - ❌ No Optimization
  - 🧩 Basic Optimization
  - ⚙️ Standard Optimization
  - 🔥 Aggressive Optimization
- 📊 **Benchmark System**: Measure
  - Code size
  - Compile time
  - Runtime performance
  - Optimization effectiveness
- 🌐 **Web Interface**:
  - Built with HTML, CSS, JS
  - Input form for raw assembly code
  - Real-time optimized output
- 🐍 **Python Flask Backend**:
  - Handles compilation and optimization
  - Manages benchmarking logic
- 🛠️ **Modular Codebase**:
  - Easy to extend
  - Pluggable optimization passes

---

## 🧪 Optimization Levels Explained

| Level         | Description                                                                 |
|---------------|-----------------------------------------------------------------------------|
| ❌ No Opt      | Raw translation without any transformation (useful for debugging)          |
| 🧩 Basic Opt   | Removes redundant instructions, basic refactoring                          |
| 🛠️ Standard Opt | Constant folding, register reuse, control flow simplification             |
| 🔥 Aggressive  | Loop unrolling, instruction reordering, advanced architecture-specific tweaks |

---

## 🧱 Technology Stack

| Layer     | Tech Used                                |
|-----------|-------------------------------------------|
| Backend   | Python, Flask                             |
| Frontend  | HTML, CSS, JavaScript                     |
| Compiler  | Custom x86 → x86_64 engine + optimizers   |
| Benchmarks| Python-based testing & reporting framework|




