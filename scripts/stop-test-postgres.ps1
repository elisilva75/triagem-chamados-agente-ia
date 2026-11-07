param([string]$PgBin = 'C:\Program Files\PostgreSQL\16\bin')
$projectRoot = Split-Path $PSScriptRoot -Parent
& (Join-Path $PgBin 'pg_ctl.exe') -D (Join-Path $projectRoot '.local/pgdata') -m fast -w stop
if ($LASTEXITCODE -ne 0) { throw 'Falha ao parar cluster de teste.' }
