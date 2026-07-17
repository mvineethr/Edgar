<#
.SYNOPSIS
  Run a command N times and report per-run, min, median, mean, max in ms.
.DESCRIPTION
  Dependency-free timing harness for PowerShell 5.1+. The command string is
  executed with Invoke-Expression inside Measure-Command; its stdout is
  discarded so output cost does not dominate the measurement. Exits non-zero
  if any run throws.
.EXAMPLE
  .\timeit.ps1 -Command "git status" -Runs 5
.EXAMPLE
  .\timeit.ps1 "npm run build" -Runs 3 -Warmup 1
#>
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Command,
    [int]$Runs = 5,
    [int]$Warmup = 0
)
$ErrorActionPreference = 'Stop'

if ($Runs -lt 1) { Write-Error "-Runs must be >= 1"; exit 2 }

for ($i = 1; $i -le $Warmup; $i++) {
    $null = Measure-Command { Invoke-Expression $Command | Out-Null }
    Write-Host ("warmup {0}: discarded" -f $i)
}

$times = @()
for ($i = 1; $i -le $Runs; $i++) {
    $t = (Measure-Command { Invoke-Expression $Command | Out-Null }).TotalMilliseconds
    $times += $t
    Write-Host ("run {0}: {1:N1} ms" -f $i, $t)
}

$sorted = @($times | Sort-Object)
$n = $sorted.Count
if ($n % 2 -eq 1) {
    $median = $sorted[($n - 1) / 2]
} else {
    $median = ($sorted[$n / 2 - 1] + $sorted[$n / 2]) / 2
}
$mean = ($times | Measure-Object -Average).Average
$min = $sorted[0]
$max = $sorted[$n - 1]

Write-Host ("command : {0}" -f $Command)
Write-Host ("runs={0}  min={1:N1} ms  median={2:N1} ms  mean={3:N1} ms  max={4:N1} ms" -f $n, $min, $median, $mean, $max)

if ($median -gt 0 -and (($max - $min) / $median) -gt 0.2) {
    Write-Host "WARNING: spread (max-min) exceeds 20% of median - rerun with more runs or on a quieter machine before comparing."
}
