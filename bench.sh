#!/usr/bin/env bash
  set -euo pipefail

  pattern="${1:?usage: ./bench.sh <pattern> <file> [runs] }"
  file="${2:?usage: ./bench.sh <pattern> <file> [runs] }"
  runs="${3:-7}"

  if [[ ! -f "$file" ]]; then
    echo "File not found: $file" >&2
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
      (( min_ns == 0 || elapsed_ns < min_ns )) && min_ns=$elapsed_ns
      (( elapsed_ns > max_ns )) && max_ns=$elapsed_ns

      awk -v l="$label" -v i="$i" -v ns="$elapsed_ns" \
        'BEGIN { printf "%s run %d: %.6f sec\n", l, i, ns/1e9 }'
    done

    awk -v l="$label" -v t="$total_ns" -v n="$runs" -v mn="$min_ns" -v mx="$max_ns" \
      'BEGIN { printf "%s avg: %.6f sec | min: %.6f | max: %.6f\n", l, (t/n)/1e9, mn/1e9, mx/1e9 }'
    awk -v t="$total_ns" -v n="$runs" 'BEGIN { printf "%.0f\n", t/n }'
  }

  echo "Pattern: $pattern"
  echo "File:    $file"
  echo "Runs:    $runs"
  echo

  # Warmup
  cargo run --release -- "$pattern" "$file" > /dev/null 2>&1 || true
  grep -aF "$pattern" "$file" > /dev/null 2>&1 || true

  rust_avg_ns=$(bench "rust(cargo run --release)" cargo run --release -- "$pattern" "$file" | tee /dev/stderr | tail -n1)
  grep_avg_ns=$(bench "grep(-aF)" grep -aF "$pattern" "$file" | tee /dev/stderr | tail -n1)

  awk -v r="$rust_avg_ns" -v g="$grep_avg_ns" '
  BEGIN {
    print ""
    printf "Comparison: grep/rust = %.2fx\n", g/r
  }'
