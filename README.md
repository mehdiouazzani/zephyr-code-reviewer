# Zephyr C Code Review Agent

A static analysis agent that automatically reviews C firmware code written for Zephyr RTOS. It detects common bugs and bad practices, and generates a PDF report with findings classified by severity.

## What it detects

| Rule | Severity | Description |
|------|----------|-------------|
| `MEMORY_LEAK` | CRITICAL | `malloc()` called without `free()` |
| `NO_NULL_CHECK` | CRITICAL | No NULL check after memory allocation |
| `DEVICE_NULL_CHECK` | CRITICAL | `device_get_binding()` result not checked |
| `USE_K_MALLOC` | WARNING | `malloc()` used instead of `k_malloc()` in Zephyr context |
| `UNCHECKED_RETURN` | WARNING | Return value of Zephyr API not checked (`uart_tx`, `gpio_pin_configure`, etc.) |
| `ISR_HEAVY_PROCESSING` | WARNING | Heavy loop detected inside ISR/callback — should use work queue |
| `UNINITIALIZED_VAR` | WARNING | Variable declared but not initialized |
| `MAGIC_NUMBER` | INFO | Numeric literal used directly — should be a named `#define` |

## Usage

```bash
pip install -r requirements.txt
python3 reviewer.py sample/main.c
python3 reviewer.py your_file.c --output report.pdf
```

## Project structure

```
zephyr-code-reviewer/
├── reviewer.py       # Main agent — CLI entry point
├── rules.py          # All analysis rules
├── report.py         # PDF report generator
├── requirements.txt
└── sample/
    └── main.c        # Example file with intentional bugs for demo
```

## Example output

Running on `sample/main.c` (which contains intentional bugs):

```
============================================================
  Zephyr Code Review — main.c
============================================================
  CRITICAL : 1
  WARNING  : 5
  INFO     : 9
  TOTAL    : 15
============================================================
```

A PDF report is also generated with the exact line numbers, code snippets and fix suggestions.

## Author

Elmehdi ELOUAZZANI — Embedded Systems & IoT Engineer  
[linkedin.com/in/mehdi-el-ouazzani-06969417a](https://linkedin.com/in/mehdi-el-ouazzani-06969417a)
