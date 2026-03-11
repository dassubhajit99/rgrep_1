#!/usr/bin/env bash
set -euo pipefail

pattern="${1:?usage: ./bench.sh <pattern> <file> [runs]}"
file="${2:?usage: ./bench.sh <pattern> <file> [runs]}"
runs="${3:-7}"
binary="./target/release/rgrep_1"

if [[ ! -f "$file" ]]; then
  echo "File not found: $file" >&2
  exit 1
fi

echo "Building release binary..."
cargo build --release > /dev/null

if [[ ! -x "$binary" ]]; then
  echo "Binary not found or not executable: $binary" >&2
  exit 1
fi

bench() {
  local label="$1"
  shift

  local total_ns=0
  local min_ns=0
  local max_ns=0

  for i in $(seq 1 "$runs"); do
    local start_ns end_ns elapsed_ns

    start_ns=$(date +%s%N)
    "$@" > /dev/null 2>&1
    end_ns=$(date +%s%N)
    elapsed_ns=$((end_ns - start_ns))

    total_ns=$((total_ns + elapsed_ns))
    ((min_ns == 0 || elapsed_ns < min_ns)) && min_ns=$elapsed_ns
    ((elapsed_ns > max_ns)) && max_ns=$elapsed_ns

    awk -v l="$label" -v i="$i" -v ns="$elapsed_ns" \
      'BEGIN { printf "%s run %d: %.6f sec\n", l, i, ns/1e9 }' >&2
  done

  local avg_ns=$((total_ns / runs))
  awk -v l="$label" -v avg="$avg_ns" -v mn="$min_ns" -v mx="$max_ns" \
    'BEGIN { printf "%s avg: %.6f sec | min: %.6f | max: %.6f\n", l, avg/1e9, mn/1e9, mx/1e9 }' >&2

  echo "$avg_ns"
}

echo "Pattern: $pattern"
echo "File:    $file"
echo "Runs:    $runs"
echo "Rust:    $binary \"$pattern\" \"$file\""
echo "Grep:    grep -aF \"$pattern\" \"$file\""
echo

# Warmup
"$binary" "$pattern" "$file" > /dev/null 2>&1 || true
grep -aF "$pattern" "$file" > /dev/null 2>&1 || true

rust_avg_ns=$(bench "rust(binary)" "$binary" "$pattern" "$file")
grep_avg_ns=$(bench "grep(-aF)" grep -aF "$pattern" "$file")

echo
awk -v r="$rust_avg_ns" -v g="$grep_avg_ns" '
BEGIN {
  printf "rust avg: %.6f sec\n", r/1e9
  printf "grep avg: %.6f sec\n", g/1e9
  if (g > 0) {
    printf "Rust/Grep = %.2fx\n", r/g
    printf "Grep is %.2fx faster\n", r/g
  }
}'
