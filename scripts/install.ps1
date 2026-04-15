# Hypothesis Tracker Install Script (Windows PowerShell)
# Usage: .\scripts\install.ps1 -TargetDir .\hypothesis-tracker [-Force]
#
# 如果 PowerShell 阻止运行脚本，请先执行：
#   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

param(
    [string]$TargetDir = ".\hypothesis-tracker",
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoDir = Split-Path -Parent $ScriptDir

$ProtocolHeading = "## Hypothesis Tracker"
$ProtocolLines = @(
    "## Hypothesis Tracker",
    "",
    "For hypothesis tracking, prefer /ht-trade, /ht-status, and /ht-new.",
    "",
    "Read these first:",
    "- ./.claude/skills/hypothesis-tracker-trade.md",
    "- ./.claude/skills/hypothesis-tracker-status.md",
    "- ./.claude/skills/hypothesis-tracker-new.md",
    "- ./config/hypothesis-tracker.yaml",
    "- ./config/hypothesis-tracker-rules.md",
    "",
    "Hypotheses live in ./hypothesis/H*.md.",
    "Trades are recorded in ./portfolio/trades.csv."
)
$RootClaudeLines = @(
    "# Workspace Instructions",
    ""
) + $ProtocolLines

function Copy-IfNeeded {
    param(
        [string]$Source,
        [string]$Destination
    )
    if ((-not (Test-Path $Destination)) -or $Force) {
        Copy-Item $Source $Destination -Force
    }
}

Write-Host "=== Hypothesis Tracker Installer ==="
Write-Host "Target: $TargetDir"

# --- Check Python ---
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
    Write-Host ""
    Write-Host "X Python not found. Please install Python >= 3.10:" -ForegroundColor Red
    Write-Host "  https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "After installing, re-run this script."
    exit 1
}

$pyVersion = & python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
$pyOk = & python -c "import sys; print(1 if sys.version_info >= (3, 10) else 0)"
if ($pyOk -ne "1") {
    Write-Host ""
    Write-Host "X Python version too old (current: $pyVersion, required: >= 3.10)" -ForegroundColor Red
    Write-Host "  https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}
Write-Host "OK Python $pyVersion" -ForegroundColor Green

# --- Check target directory ---
if (Test-Path $TargetDir) {
    $existingItem = Get-Item -LiteralPath $TargetDir
    if (-not $existingItem.PSIsContainer) {
        Write-Host "ERROR: $TargetDir exists and is not a directory." -ForegroundColor Red
        exit 1
    }
    Write-Host "Target directory already exists. Installing into existing workspace."
}

# --- Create directory structure ---
$dirs = @(
    "config",
    "scripts",
    "templates",
    "examples",
    "hypothesis",
    "portfolio",
    "portfolio\journal",
    ".claude",
    ".claude\skills"
)
foreach ($d in $dirs) {
    $path = Join-Path $TargetDir $d
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
    }
}

# --- Copy script files ---
$scripts = @(
    "check_setup.py",
    "workspace_paths.py",
    "sync_hypothesis.py",
    "trade_stats.py"
)
foreach ($s in $scripts) {
    Copy-Item (Join-Path $RepoDir "scripts\$s") (Join-Path $TargetDir "scripts\$s") -Force
}

# --- Copy templates ---
$templates = @(
    "hypothesis-tracker-hypothesis-template.md",
    "hypothesis-tracker-journal-template.md",
    "hypothesis-tracker-report-template.md"
)
foreach ($t in $templates) {
    Copy-Item (Join-Path $RepoDir "templates\$t") (Join-Path $TargetDir "templates\$t") -Force
}

# --- Copy skills ---
$skills = @(
    "hypothesis-tracker-trade.md",
    "hypothesis-tracker-status.md",
    "hypothesis-tracker-new.md"
)
foreach ($s in $skills) {
    Copy-Item (Join-Path $RepoDir "skills\$s") (Join-Path $TargetDir ".claude\skills\$s") -Force
}

# --- Copy examples ---
Copy-Item (Join-Path $RepoDir "examples\H1-example-thesis.md") (Join-Path $TargetDir "examples\H1-example-thesis.md") -Force
Copy-Item (Join-Path $RepoDir "examples\hypothesis-tracker.base") (Join-Path $TargetDir "examples\hypothesis-tracker.base") -Force

# --- Copy config files (working copies only, no .example duplicates) ---
Copy-IfNeeded (Join-Path $RepoDir "config\hypothesis-tracker.env.example") (Join-Path $TargetDir "config\hypothesis-tracker.env")
Copy-IfNeeded (Join-Path $RepoDir "config\hypothesis-tracker.example.yaml") (Join-Path $TargetDir "config\hypothesis-tracker.yaml")
Copy-IfNeeded (Join-Path $RepoDir "config\hypothesis-tracker.rules.example.md") (Join-Path $TargetDir "config\hypothesis-tracker-rules.md")

# --- Initialize CSV files ---
$tradesPath = Join-Path $TargetDir "portfolio\trades.csv"
if (-not (Test-Path $tradesPath)) {
    Set-Content -Path $tradesPath -Value "date,ticker,market,action,shares,price,currency,reasoning,kill_thesis,outcome_note" -Encoding utf8
}

$holdingsPath = Join-Path $TargetDir "portfolio\holdings.csv"
if (-not (Test-Path $holdingsPath)) {
    Set-Content -Path $holdingsPath -Value "ticker,market,name,shares,avg_cost,currency,date_opened,hypothesis,stop_loss,status" -Encoding utf8
}

# --- CLAUDE.md integration ---
$targetClaude = Join-Path $TargetDir "CLAUDE.md"
if (-not (Test-Path $targetClaude)) {
    Set-Content -Path $targetClaude -Value ($RootClaudeLines -join "`r`n") -Encoding utf8
} else {
    $existingClaude = Get-Content $targetClaude -Raw
    if ($existingClaude -notmatch [regex]::Escape($ProtocolHeading)) {
        $content = $existingClaude.TrimEnd()
        if ($content) {
            $content += "`r`n`r`n"
        }
        $content += ($ProtocolLines -join "`r`n")
        Set-Content -Path $targetClaude -Value $content -Encoding utf8
    }
}

# --- Install Python dependencies ---
Write-Host ""
Write-Host "Installing Python dependencies..."
try {
    & python -m pip install -r (Join-Path $RepoDir "requirements.txt") --quiet
    Write-Host "OK Python dependencies installed" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "WARNING: Dependency install failed. Please run manually:" -ForegroundColor Yellow
    Write-Host "  python -m pip install -r requirements.txt"
    Write-Host ""
}

# --- Run setup check ---
Write-Host ""
Write-Host "Running setup check..."
& python (Join-Path $TargetDir "scripts\check_setup.py")
$setupExitCode = $LASTEXITCODE
if ($setupExitCode -eq 0) {
    Write-Host ""
    Write-Host "OK Installation complete! All checks passed." -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "WARNING: Installation complete, but setup check found issues. Please fix them above." -ForegroundColor Yellow
    $global:LASTEXITCODE = 0
}

Write-Host ""
Write-Host "Installed to $TargetDir"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Review config:       $TargetDir\config\hypothesis-tracker.yaml"
Write-Host "  2. Review rules:        $TargetDir\config\hypothesis-tracker-rules.md"
Write-Host "  3. Read the example:    $TargetDir\examples\H1-example-thesis.md"
Write-Host "  4. Create a hypothesis: Run /ht-new in Claude Code"
Write-Host "  5. Record a trade:      Run /ht-trade in Claude Code"
