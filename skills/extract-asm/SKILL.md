---
name: extract-asm
description: Extract the assembly of a specific function from an object file or assembly file
argument-hint: "<file> <function-name>"
---

# Extract Assembly for a Function

Extract the assembly of a specific function from an object file or assembly file.

## Prerequisites
The input must be a compiled object file (`.o` or `.obj`) or assembly file (`.s` or `.asm`). If you have source code, compile it first (e.g. via CMake build or standalone `clang -S`).

## Usage
Invoke with: the input file and function name.

Arguments:
- `$1` = input file (`.o`, `.obj`, `.s`, or `.asm`)
- `$2` = function name

Examples:
- `build/CMakeFiles/zlib-ng.dir/trees.c.o compress_block`
- `/tmp/output.s my_function`
- `build/CMakeFiles/zlib-ng.dir/Release/trees.obj compress_block`

## Steps

1. Extract assembly for the function from the input:

   **If `.o` object file (Mach-O / ELF):**
   - On macOS, use `llvm-objdump` (ships with Xcode). Mach-O symbols have a `_` prefix:
     ```
     llvm-objdump --disassemble-symbols=_<function_name> --no-show-raw-insn <file>.o
     ```
   - On Linux, use GNU objdump (binutils 2.32+):
     ```
     objdump --disassemble=<function_name> --no-show-raw-insn <file>.o
     ```

   **If `.obj` object file (PE/COFF — Windows):**
   - Prefer `llvm-objdump` (ships with VS LLVM/clang workload or standalone LLVM install):
     ```
     llvm-objdump --disassemble-symbols=<function_name> --no-show-raw-insn <file>.obj
     ```
   - Fallback to `dumpbin` if `llvm-objdump` is not available. `dumpbin` requires the MSVC environment:
     ```
     VSPATH=$(vswhere -latest -property installationPath)
     cmd.exe /c "call \"${VSPATH}\VC\Auxiliary\Build\vcvarsall.bat\" amd64 >nul 2>&1 && dumpbin /disasm <file>.obj"
     ```
     Then extract the named function: find `<function_name>:` label, collect until the next label or summary line.

   **If `.s` or `.asm` assembly file:**
   - Read the file and extract the named function manually:
     - **Mach-O:** Find `_<function_name>:`, collect until next `^_[a-zA-Z]` label (excluding `_Ltmp`, `_LCFI`, `_LBB` prefixes).
     - **ELF/other:** Find `<function_name>:`, collect until the next function label.

2. From the extracted output:
   - Filter out assembler directives (`.` prefix), comments (`#`, `;`, `//`, `@`), and blank lines
   - Keep only instruction lines

3. Output the extracted assembly to stdout. Print a summary line with the instruction count.

## Architecture Notes

### x86-64
- `leaq` instructions with `(%rip)` are PC-relative address computations, not memory loads.
- Memory operands use `offset(%reg)` syntax (e.g. `168(%rdi)` loads from rdi+168).

### AArch64
- Memory operands use `[reg, #offset]` syntax (e.g. `[x0, #168]` loads from x0+168).
- Load instructions: `ldr`, `ldur`, `ldp`, `ldrb`, `ldrh`, `ldrsw`. Store: `str`, `stur`, `stp`, `strb`, `strh`.
- On Apple Silicon this compiles natively — no cross-compilation needed.

### x86-64 (Windows/MSVC)
- Uses Intel syntax by default (destination first): `mov rax, [rcx+168]`.
- Calling convention: first four args in `rcx`, `rdx`, `r8`, `r9` (not `rdi`, `rsi` like SysV).
- Function names may be decorated (e.g. `?name@@...` for C++). C functions are undecorated.

## General
- Object files from CMake builds are typically at:
  - Unix: `build/CMakeFiles/<target>.dir/<source>.o`
  - Windows (Ninja): `build/CMakeFiles/<target>.dir/<source>.obj`
  - Windows (VS generator): `build/CMakeFiles/<target>.dir/<config>/<source>.obj`
