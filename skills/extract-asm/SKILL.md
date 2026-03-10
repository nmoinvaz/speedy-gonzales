---
name: extract-asm
description: Extract assembly from an object file or assembly file, optionally for a specific function
argument-hint: "<file> [function-name]"
---

## Prerequisites
The input must be a compiled object file (`.o` or `.obj`) or assembly file (`.s` or `.asm`). If you have source code, compile it first (e.g. via CMake build or standalone `clang -S`).

## Arguments
- `$1` = input file (`.o`, `.obj`, `.s`, or `.asm`)
- `$2` = function name (optional — if omitted, disassemble the entire file)

Examples:
- `trees.c.o compress_block` — single function
- `trees.c.o` — entire file
- `trees.s my_function`
- `trees.obj compress_block`

## Steps

### 1. Disassemble object files (`.o` / `.obj`)

Use the appropriate tool for the platform:

| Platform | Tool | Notes |
|----------|------|-------|
| macOS | `llvm-objdump` | Ships with Xcode |
| Linux | `objdump` | GNU binutils 2.32+ |
| Windows | `llvm-objdump` | Ships with VS LLVM/clang workload or standalone LLVM |

**Single function** (`$2` provided):

| Platform | Command |
|----------|---------|
| macOS | `llvm-objdump --disassemble-symbols=_<name> --no-show-raw-insn <file>` |
| Linux | `objdump --disassemble=<name> --no-show-raw-insn <file>` |
| Windows | `llvm-objdump --disassemble-symbols=<name> --no-show-raw-insn <file>` |

**Entire file** (`$2` omitted):

| Platform | Command |
|----------|---------|
| macOS | `llvm-objdump -d --no-show-raw-insn <file>` |
| Linux | `objdump -d --no-show-raw-insn <file>` |
| Windows | `llvm-objdump -d --no-show-raw-insn <file>` |

**Windows `dumpbin` fallback** — if `llvm-objdump` is not available:
```
VSPATH=$(vswhere -latest -property installationPath)
cmd.exe /c "call \"${VSPATH}\VC\Auxiliary\Build\vcvarsall.bat\" amd64 >nul 2>&1 && dumpbin /disasm <file>.obj"
```
Then manually extract the function: find `<function_name>:` label, collect until the next label or summary line.

### 2. Extract from assembly files (`.s` / `.asm`)

Read the file directly. If `$2` is provided, extract the named function:
- **Mach-O:** Find `_<function_name>:`, collect until next `^_[a-zA-Z]` label (excluding `_Ltmp`, `_LCFI`, `_LBB` prefixes).
- **ELF/other:** Find `<function_name>:`, collect until the next function label.

### 3. Clean up and output

- Filter out assembler directives (`.` prefix), comments (`#`, `;`, `//`, `@`), and blank lines
- Keep only instruction lines
- Output the assembly to stdout with a summary line showing the instruction count

## Symbol Names

Symbol names differ by platform — use this when passing to `--disassemble-symbols` or searching in `.s` files:

| Platform | C function `foo` | C++ function `foo` |
|----------|------------------|--------------------|
| macOS (Mach-O) | `_foo` | `_Z3foov` (Itanium mangled, `_` prefixed) |
| Linux (ELF) | `foo` | `_Z3foov` (Itanium mangled) |
| Windows (PE/COFF) | `foo` | `?foo@@YAXXZ` (MSVC decorated) |

## Architecture Notes

| Architecture | Key details |
|-------------|-------------|
| **x86-64** | `offset(%reg)` memory syntax. `leaq (%rip)` is PC-relative, not a load. |
| **AArch64** | `[reg, #offset]` memory syntax. Loads: `ldr`, `ldur`, `ldp`, `ldrb`, `ldrh`, `ldrsw`. Stores: `str`, `stur`, `stp`, `strb`, `strh`. Apple Silicon compiles natively. |
| **x86-64 (MSVC)** | Intel syntax (dest first): `mov rax, [rcx+168]`. Args in `rcx`, `rdx`, `r8`, `r9`. C++ names may be decorated (`?name@@...`). |

## CMake Build Paths
- Unix: `build/CMakeFiles/<target>.dir/<source>.o`
- Windows (Ninja): `build/CMakeFiles/<target>.dir/<source>.obj`
- Windows (VS): `build/CMakeFiles/<target>.dir/<config>/<source>.obj`
