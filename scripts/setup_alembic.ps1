# Function to read user input with a default value
function Read-WithDefault {
    param (
        [string]$prompt,
        [string]$default
    )
    $input = Read-Host -Prompt "$prompt [$default]"
    if (-not $input) {
        $input = $default
    }
    return $input
}

# Get user input
$db_url_default = "localhost"
$db_default_port = "5432"
$db_url = Read-WithDefault "Enter the URL of your database" $db_url_default
$db_port = Read-WithDefault "Enter the port of your database" $db_default_port
$db_user = Read-WithDefault "Enter the PostgreSQL username" "postgres"
$db_password = Read-Host -Prompt "Enter the PostgreSQL password" -AsSecureString
$db_name = Read-WithDefault "Enter the database name" "postgres"

# Convert secure string to plain text for URL construction
$db_password_plain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($db_password))

# Initialize Alembic
alembic init alembic

# Update alembic.ini with the provided database URL
$alembic_ini_path = "alembic.ini"
(Get-Content $alembic_ini_path) | ForEach-Object {
    $_ -replace 'sqlalchemy.url = .*', "sqlalchemy.url = postgresql://${db_user}:${db_password_plain}@${db_url}:${db_port}/${db_name}"
} | Set-Content $alembic_ini_path

# Update env.py to import Base and set target_metadata
(Get-Content "alembic/env.py") | ForEach-Object {
    $_ -replace '# target_metadata = mymodel.Base.metadata', "from services.database.models import Base"
} | Set-Content "alembic/env.py"

(Get-Content "alembic/env.py") | ForEach-Object {
    $_ -replace 'target_metadata = None', 'target_metadata = Base.metadata'
} | Set-Content "alembic/env.py"

Write-Host "Alembic setup complete. You can now run " -ForegroundColor Green -NoNewline
Write-Host "'alembic revision --autogenerate -m `"initial`"' " -ForegroundColor Yellow -NoNewline
Write-Host "to create your first migration." -ForegroundColor Green
