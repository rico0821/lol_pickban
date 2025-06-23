# This script starts the development servers for both the backend and frontend.
# It opens two new PowerShell windows.

# Start the Flask backend server in a new window
Write-Host "Starting Flask backend server..."
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "python -m backend.app"

# Start the React frontend server in another new window
Write-Host "Starting React frontend server..."
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd frontend; npm start"

Write-Host "Development servers are starting in new windows." 