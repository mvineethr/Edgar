#!/usr/bin/env bash
# timeit.sh — run a command N times, report per-run, min, median, mean, max in ms.
# Dependency-free beyond bash + coreutils date + awk (all present in Git Bash).
#
# Usage:   timeit.sh [-n runs] [-w warmup] 'command string'
# Example: timeit.sh -n 5 'git status'
#          timeit.sh -n 3 -w 1 'npm run build'
set -u

runs=5
warmup=0
while getopts "n:w:" opt; do
  case $opt in
    n) runs=$OPTARG ;;
    w) warmup=$OPTARG ;;
    *) echo "usage: timeit.sh [-n runs] [-w warmup] 'command'" >&2; exit 2 ;;
  esac
done
shift $((OPTIND - 1))
if [ $# -lt 1 ]; then
  echo "usage: timeit.sh [-n runs] [-w warmup] 'command'" >&2
  exit 2
fi
cmd="$*"

# GNU date gives nanoseconds via %N; BSD/macOS date prints a literal 'N'.
# Fall back to whole-second resolution there (documented limitation).
if [ "$(date +%N)" = "N" ]; then
  now_ms() { echo $(( $(date +%s) * 1000 )); }
  echo "note: this date lacks %N; resolution limited to 1000 ms" >&2
else
  now_ms() { echo $(( $(date +%s%N) / 1000000 )); }
fi

i=1
while [ "$i" -le "$warmup" ]; do
  bash -c "$cmd" > /dev/null || { echo "warmup $i: command failed" >&2; exit 1; }
  echo "warmup $i: discarded"
  i=$((i + 1))
done

times=""
i=1
while [ "$i" -le "$runs" ]; do
  start=$(now_ms)
  bash -c "$cmd" > /dev/null || { echo "run $i: command failed" >&2; exit 1; }
  end=$(now_ms)
  ms=$((end - start))
  echo "run $i: ${ms} ms"
  times="$times $ms"
  i=$((i + 1))
done

echo "command : $cmd"
echo "$times" | tr ' ' '\n' | sed '/^$/d' | sort -n | awk '
  { a[NR] = $1; sum += $1 }
  END {
    n = NR
    min = a[1]; max = a[n]
    median = (n % 2 == 1) ? a[(n + 1) / 2] : (a[n / 2] + a[n / 2 + 1]) / 2
    mean = sum / n
    printf "runs=%d  min=%d ms  median=%.1f ms  mean=%.1f ms  max=%d ms\n", n, min, median, mean, max
    if (median > 0 && (max - min) / median > 0.2)
      print "WARNING: spread (max-min) exceeds 20% of median - rerun with more runs or on a quieter machine before comparing."
  }'
