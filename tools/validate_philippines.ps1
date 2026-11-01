param([string]$PythonPath = '')
$ErrorActionPreference = 'Stop'
$modRoot = Split-Path $PSScriptRoot -Parent
if (-not $PythonPath) {
 $bundledPython = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
 if (Test-Path -LiteralPath $bundledPython) { $PythonPath = $bundledPython }
 else { $PythonPath = (Get-Command python -ErrorAction Stop).Source }
}
foreach ($script in @('validate_philippines_rework.py','A10D_validate_development.py','A10W_validate.py','test_philippines_republics.py','test_philippines_military.py')) {
 & $PythonPath (Join-Path $PSScriptRoot $script)
 if ($LASTEXITCODE -ne 0) { throw "Philippine validation failed: $script" }
}
