@echo off

REM Load environment variables from .env file
for /f "usebackq tokens=1,2 delims==" %%A in (.env) do set %%A=%%B

REM Run setup_database.sql using environment variables
docker-compose exec -T postgres psql -U %POSTGRES_USER% -d %POSTGRES_DB% -f /app/setup_database.sql

echo Database setup completed!
pause
