param([string]$PythonPath = '')
$ErrorActionPreference = 'Stop'
$modRoot = Split-Path $PSScriptRoot -Parent
if (-not $PythonPath) {
 $bundledPython = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
 if (Test-Path -LiteralPath $bundledPython) { $PythonPath = $bundledPython }
 else { $PythonPath = (Get-Command python -ErrorAction Stop).Source }
}
foreach ($script in @('build_philippines_republics.py','build_philippines_rework.py','integrate_philippines_rework.py')) {
 & $PythonPath (Join-Path $PSScriptRoot $script)
 if ($LASTEXITCODE -ne 0) { throw "Philippine build failed: $script" }
}
