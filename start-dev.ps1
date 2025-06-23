# This script starts the development servers for both the backend and frontend.
# It opens two new PowerShell windows.

Write-Host "Starting Flask backend server on port 5000..."
Start-Process pwsh -ArgumentList '-NoExit', '-Command', '$env:LOL_PICKBAN_PORT="5000"; python -m backend.app'

Write-Host "Starting React frontend server on port 3000..."
Start-Process pwsh -ArgumentList '-NoExit', '-Command', 'cd frontend; $env:PORT="3000"; npm start'

Write-Host "Development servers are starting in new windows." 