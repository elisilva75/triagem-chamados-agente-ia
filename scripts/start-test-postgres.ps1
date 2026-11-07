param([string]$PgBin = 'C:\Program Files\PostgreSQL\16\bin', [int]$Port = 55432)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$testRoot = Join-Path $projectRoot '.local'
$pgData = Join-Path $testRoot 'pgdata'
$pwFile = Join-Path $testRoot 'pg-password.txt'
New-Item -ItemType Directory -Force $testRoot | Out-Null
if (-not (Test-Path (Join-Path $pgData 'PG_VERSION'))) {
    Set-Content -LiteralPath $pwFile -Value 'senha_ficticia_teste' -Encoding ascii
    & (Join-Path $PgBin 'initdb.exe') -D $pgData -U portfolio_test --auth-host=scram-sha-256 --auth-local=scram-sha-256 "--pwfile=$pwFile" --encoding=UTF8 --locale=C
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao inicializar cluster de teste.' }
}
& (Join-Path $PgBin 'pg_ctl.exe') -D $pgData status
if ($LASTEXITCODE -ne 0) {
    & (Join-Path $PgBin 'pg_ctl.exe') -D $pgData -l (Join-Path $testRoot 'postgres.log') -o "-h 127.0.0.1 -p $Port" -w start
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao iniciar cluster de teste.' }
}
$env:PGPASSWORD = 'senha_ficticia_teste'
try {
    $exists = & (Join-Path $PgBin 'psql.exe') -h 127.0.0.1 -p $Port -U portfolio_test -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='portfolio_test'"
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao consultar banco administrativo de teste.' }
    if ($exists -ne '1') {
        & (Join-Path $PgBin 'createdb.exe') -h 127.0.0.1 -p $Port -U portfolio_test portfolio_test
        if ($LASTEXITCODE -ne 0) { throw 'Falha ao criar banco administrativo de teste.' }
    }
} finally {
    Remove-Item Env:PGPASSWORD
}
$env:TEST_DATABASE_URL = "postgresql+psycopg://portfolio_test:senha_ficticia_teste@127.0.0.1:$Port/portfolio_test"
Write-Output 'Cluster de teste disponível em loopback. TEST_DATABASE_URL definida nesta sessão.'
