---
name: extract-asm
description: Extract the assembly of a specific function from an object file or assembly file
argument-hint: "<file> <function-name>"
---

# Extract Assembly for a Function

Extract the assembly of a specific function from an object file or assembly file.

## Prerequisites
The input must be a compiled object file (`.o` or `.obj`) or assembly file (`.s` or `.asm`). If you have source code, compile it first (e.g. via CMake build or standalone `clang -S`).

## Arguments
- `$1` = input file (`.o`, `.obj`, `.s`, or `.asm`)
- `$2` = function name

Examples:
- `build/CMakeFiles/zlib-ng.dir/trees.c.o compress_block`
- `/tmp/output.s my_function`
- `build/CMakeFiles/zlib-ng.dir/Release/trees.obj compress_block`

## Steps

1. **Extract assembly** for the function based on file type:

   | Platform | File | Command |
   |----------|------|---------|
   | macOS | `.o` | `llvm-objdump --disassemble-symbols=_<name> --no-show-raw-insn <file>` |
   | Linux | `.o` | `objdump --disassemble=<name> --no-show-raw-insn <file>` |
   | Windows | `.obj` | `llvm-objdump --disassemble-symbols=<name> --no-show-raw-insn <file>` |

   Symbol names differ by platform — use this when passing to `--disassemble-symbols` or searching in `.s` files:

   | Platform | C function `foo` | C++ function `foo` |
   |----------|------------------|--------------------|
   | macOS (Mach-O) | `_foo` | `_Z3foov` (Itanium mangled, `_` prefixed) |
   | Linux (ELF) | `foo` | `_Z3foov` (Itanium mangled) |
   | Windows (PE/COFF) | `foo` | `?foo@@YAXXZ` (MSVC decorated) |

   Notes:
   - macOS `llvm-objdump` ships with Xcode.
   - Linux requires GNU binutils 2.32+.
   - Windows: if `llvm-objdump` is not available, fall back to `dumpbin`:
     ```
     VSPATH=$(vswhere -latest -property installationPath)
     cmd.exe /c "call \"${VSPATH}\VC\Auxiliary\Build\vcvarsall.bat\" amd64 >nul 2>&1 && dumpbin /disasm <file>.obj"
     ```
     Then manually extract the function: find `<function_name>:` label, collect until the next label or summary line.

   **For `.s` or `.asm` files:** Read the file and extract manually:
   - **Mach-O:** Find `_<function_name>:`, collect until next `^_[a-zA-Z]` label (excluding `_Ltmp`, `_LCFI`, `_LBB` prefixes).
   - **ELF/other:** Find `<function_name>:`, collect until the next function label.

2. **Clean up** the extracted output:
   - Filter out assembler directives (`.` prefix), comments (`#`, `;`, `//`, `@`), and blank lines
   - Keep only instruction lines

3. **Output** the assembly to stdout with a summary line showing the instruction count.

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
