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


git clone https://github.com/birukG09/OptimizingCompiler.git
cd OptimizingCompiler
📊 Benchmarks
The system includes four benchmarks:

Translation Speed

Code Size Reduction

Instruction Count Efficiency.

Execution Performance (if testable)

Results are output in tabular and graphical form via CLI or admin dashboard.

👨‍💻 Contributing
Contributions are welcome! Please:

Fork the repo

Create a new branch

Submit a pull request with detailed info

📬 Contact
Created by Biruk Gebre
GitHub: https://github.com/birukG09

