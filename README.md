# rgrep_1

A simple Rust-based grep-like CLI that searches for a pattern in a text file and prints matching lines.

## Prerequisites

- Rust toolchain (Cargo)
- Python 3 (for test file generation)
- Linux `grep` (for benchmark comparison)

## Generate Test Files (Python)

This project includes `generate_random_txt.py` to create large text files.

### Basic examples

```bash
# Create 3 GB file (default unit is GB if no suffix)
python3 generate_random_txt.py 3

# Create 3 GB file explicitly named
python3 generate_random_txt.py 3gb -o 3gb.txt

# Create 500 MB file
python3 generate_random_txt.py 500mb -o 500mb.txt
```

### Useful options

```bash
# Gibberish mode instead of meaningful words
python3 generate_random_txt.py 1gb --mode gibberish -o gibberish_1gb.txt

# Change write chunk size (MB)
python3 generate_random_txt.py 1gb --chunk-mb 8 -o test_1gb.txt

# Use a custom word list (one word per line)
python3 generate_random_txt.py 1gb --word-list ./words.txt -o custom_1gb.txt
```

## Run with Cargo

```bash
# Debug mode
cargo run -- person 3gb.txt

# Release mode (faster)
cargo run --release -- person 3gb.txt
```

## Run Using Binary

```bash
# Build release binary once
cargo build --release

# Run binary directly
./target/debug/rgrep_1 person 3gb.txt
```

## Run Benchmark Script

`bench.sh` compares your Rust binary against Linux `grep`.

```bash
# If needed, make executable once
chmod +x bench.sh

# Usage: ./bench.sh <pattern> <file> [runs]
./bench.sh person 3gb.txt 7
```

What `bench.sh` does:

- Builds release binary (`cargo build --release`)
- Runs warmup
- Benchmarks:
  - `./target/debug/rgrep_1 <pattern> <file>`
  - `grep -aF <pattern> <file>`
- Prints run-wise timings, averages, and speed ratio
