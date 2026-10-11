"""
Zephyr C code review rules.
Each rule returns a list of findings: {"line": int, "severity": str, "rule": str, "message": str}
"""

import re

SEVERITY_CRITICAL = "CRITICAL"
SEVERITY_WARNING  = "WARNING"
SEVERITY_INFO     = "INFO"


def check_malloc_no_free(lines):
    findings = []
    malloc_lines = []
    free_lines = []
    for i, line in enumerate(lines, 1):
        if re.search(r'\bmalloc\s*\(', line):
            malloc_lines.append(i)
        if re.search(r'\bfree\s*\(', line):
            free_lines.append(i)
    if malloc_lines and not free_lines:
        for l in malloc_lines:
            findings.append({
                "line": l,
                "severity": SEVERITY_CRITICAL,
                "rule": "MEMORY_LEAK",
                "message": "malloc() called but no free() found in file — potential memory leak."
            })
    return findings


def check_kmalloc_preferred(lines):
    findings = []
    for i, line in enumerate(lines, 1):
        if re.search(r'\bmalloc\s*\(', line) and not line.strip().startswith("//"):
            findings.append({
                "line": i,
                "severity": SEVERITY_WARNING,
                "rule": "USE_K_MALLOC",
                "message": "Use k_malloc() instead of malloc() in Zephyr kernel context."
            })
    return findings


def check_null_after_alloc(lines):
    findings = []
    for i, line in enumerate(lines, 1):
        if re.search(r'=\s*(k_)?malloc\s*\(', line):
            # Check if next few lines contain a NULL check
            context = "".join(lines[i:min(i+4, len(lines))])
            if "NULL" not in context and "!=" not in context and "if (" not in context:
                findings.append({
                    "line": i,
                    "severity": SEVERITY_CRITICAL,
                    "rule": "NO_NULL_CHECK",
                    "message": "No NULL check after malloc/k_malloc — dereference will crash if allocation fails."
                })
    return findings


def check_unchecked_return(lines):
    findings = []
    zephyr_apis = [
        "uart_tx", "uart_rx_enable", "uart_callback_set",
        "gpio_pin_configure", "gpio_pin_interrupt_configure",
        "i2c_write", "i2c_read", "spi_write", "spi_read",
        "k_sem_take", "k_mutex_lock"
    ]
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        for api in zephyr_apis:
            pattern = r'^\s*' + re.escape(api) + r'\s*\('
            if re.match(pattern, line) and not stripped.startswith("//"):
                findings.append({
                    "line": i,
                    "severity": SEVERITY_WARNING,
                    "rule": "UNCHECKED_RETURN",
                    "message": f"Return value of {api}() not checked — errors will be silently ignored."
                })
    return findings


def check_device_get_binding(lines):
    findings = []
    for i, line in enumerate(lines, 1):
        if re.search(r'device_get_binding\s*\(', line):
            context = "".join(lines[i:min(i+4, len(lines))])
            if "NULL" not in context and "!=" not in context:
                findings.append({
                    "line": i,
                    "severity": SEVERITY_CRITICAL,
                    "rule": "DEVICE_NULL_CHECK",
                    "message": "device_get_binding() result not checked for NULL — will crash if device not found."
                })
    return findings


def check_isr_heavy_processing(lines):
    findings = []
    in_callback = False
    brace_depth = 0
    callback_start = 0
    loop_count = 0

    for i, line in enumerate(lines, 1):
        if re.search(r'(callback|_handler|_isr)\s*\(', line) and '{' in line:
            in_callback = True
            brace_depth = 1
            callback_start = i
            loop_count = 0
            continue
        if in_callback:
            brace_depth += line.count('{') - line.count('}')
            if re.search(r'\bfor\b|\bwhile\b', line):
                loop_count += 1
            if brace_depth <= 0:
                if loop_count > 0:
                    findings.append({
                        "line": callback_start,
                        "severity": SEVERITY_WARNING,
                        "rule": "ISR_HEAVY_PROCESSING",
                        "message": f"Heavy processing (loop) detected inside callback/ISR starting at line {callback_start} — use a work queue instead."
                    })
                in_callback = False
    return findings


def check_magic_numbers(lines):
    findings = []
    allowed = {"0", "1", "-1", "0x00", "0xFF", "NULL"}
    for i, line in enumerate(lines, 1):
        if line.strip().startswith("//") or line.strip().startswith("*"):
            continue
        # Find hex or decimal literals not in #define lines
        if line.strip().startswith("#define"):
            continue
        matches = re.findall(r'\b(0x[0-9A-Fa-f]{2,}|\b[2-9][0-9]+)\b', line)
        for m in matches:
            if m not in allowed:
                findings.append({
                    "line": i,
                    "severity": SEVERITY_INFO,
                    "rule": "MAGIC_NUMBER",
                    "message": f"Magic number '{m}' — consider using a named #define constant."
                })
                break  # one finding per line
    return findings


def check_uninitialized_variable(lines):
    findings = []
    for i, line in enumerate(lines, 1):
        # int/uint declared without init
        m = re.match(r'\s+(int|uint8_t|uint16_t|uint32_t|size_t)\s+(\w+)\s*;', line)
        if m:
            findings.append({
                "line": i,
                "severity": SEVERITY_WARNING,
                "rule": "UNINITIALIZED_VAR",
                "message": f"Variable '{m.group(2)}' declared but not initialized — may hold garbage value."
            })
    return findings


ALL_RULES = [
    check_malloc_no_free,
    check_kmalloc_preferred,
    check_null_after_alloc,
    check_unchecked_return,
    check_device_get_binding,
    check_isr_heavy_processing,
    check_magic_numbers,
    check_uninitialized_variable,
]
