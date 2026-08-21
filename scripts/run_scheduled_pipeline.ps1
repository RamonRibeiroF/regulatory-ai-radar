$ErrorActionPreference = "Stop"

# Step 1: locate the project from the scripts directory.
$projectDirectory = Split-Path -Parent $PSScriptRoot

# Step 2: define the virtual-environment Python executable.
$pythonExecutable = Join-Path `
    $projectDirectory `
    ".venv\Scripts\python.exe"

# Step 3: define the automated pipeline entry point.
$pipelineScript = Join-Path `
    $PSScriptRoot `
    "run_pipeline.py"

# Step 4: create the local log directory when necessary.
$logDirectory = Join-Path `
    $projectDirectory `
    "logs"

New-Item `
    -Path $logDirectory `
    -ItemType Directory `
    -Force | Out-Null

$logFile = Join-Path `
    $logDirectory `
    "scheduled_pipeline.log"

# Step 5: verify the required local files.
if (-not (Test-Path -LiteralPath $pythonExecutable)) {
    throw "Virtual-environment Python was not found: $pythonExecutable"
}

if (-not (Test-Path -LiteralPath $pipelineScript)) {
    throw "Pipeline script was not found: $pipelineScript"
}

# Step 6: execute the pipeline from the project root.
Set-Location -LiteralPath $projectDirectory

$startedAt = Get-Date

Add-Content `
    -LiteralPath $logFile `
    -Value (
        "`n============================================================`n" +
        "Scheduled pipeline started at: " +
        $startedAt.ToString("yyyy-MM-dd HH:mm:ss")
    )

try {
    & $pythonExecutable $pipelineScript *>> $logFile

    $pipelineExitCode = $LASTEXITCODE

    if ($pipelineExitCode -ne 0) {
        throw "Pipeline finished with exit code $pipelineExitCode."
    }

    # Step 7: record a successful scheduled execution.
    $finishedAt = Get-Date

    Add-Content `
        -LiteralPath $logFile `
        -Value (
            "Scheduled pipeline completed at: " +
            $finishedAt.ToString("yyyy-MM-dd HH:mm:ss")
        )

    exit 0
}
catch {
    # Step 8: record the failure and return an error exit code.
    $failedAt = Get-Date

    Add-Content `
        -LiteralPath $logFile `
        -Value (
            "Scheduled pipeline failed at: " +
            $failedAt.ToString("yyyy-MM-dd HH:mm:ss") +
            "`nError: " +
            $_.Exception.Message
        )

    exit 1
}