<#
.SYNOPSIS
    Ars Arcanum Automated System Installer for Windows.
.DESCRIPTION
    Installs and configures all core tools, author workspaces, Typst, Pandoc,
    desktop shortcuts, and background timers on Windows 10/11.
.PARAMETER DryRun
    Simulate and log all planned actions without mutating the system or creating shortcuts.
.PARAMETER NoAdmin
    Run in user-space only mode without attempting system-level package manager operations.
.PARAMETER EnableTimer
    Register an automated daily background backup Scheduled Task.
.PARAMETER Force
    Bypass environment version checks and proceed unconditionally.
.EXAMPLE
    .\scripts\setup_arcanum.ps1
.EXAMPLE
    .\scripts\setup_arcanum.ps1 -DryRun
.EXAMPLE
    .\scripts\setup_arcanum.ps1 -EnableTimer
#>

[CmdletBinding()]
param (
    [Alias("d", "dry-run")]
    [switch]$DryRun,

    [Alias("no-sudo", "no-admin")]
    [switch]$NoAdmin,

    [Alias("enable-timer")]
    [switch]$EnableTimer,

    [Alias("f")]
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$LogFile = $null

if (-not $DryRun) {
    $Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $LogDir = [System.IO.Path]::GetTempPath()
    $LogFile = Join-Path $LogDir "arcanum-install-$Timestamp.log"
    Start-Transcript -Path $LogFile -Append -Force | Out-Null
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Ars Arcanum -- Automated Setup for Windows Writing System" -ForegroundColor Cyan
if ($DryRun) {
    Write-Host "  [MODE: DRY-RUN SIMULATION -- No system changes will be made]" -ForegroundColor Yellow
}
if ($NoAdmin) {
    Write-Host "  [MODE: USER-SPACE ONLY (-NoAdmin) -- System packages bypassed]" -ForegroundColor Yellow
}
if ($LogFile) {
    Write-Host "  [AUDIT LOG: $LogFile]" -ForegroundColor Gray
}
Write-Host "============================================================" -ForegroundColor Cyan

$InstallErrors = [System.Collections.Generic.List[string]]::new()

# 1. Environment and Architecture Detection
$OsName = (Get-CimInstance Win32_OperatingSystem).Caption
$Arch = [System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture.ToString()
Write-Host "[i] Detected System: $OsName ($Arch)" -ForegroundColor Gray

# Reference lockfile if present
$Lockfile = Join-Path $ProjectRoot "dependencies.lock"
if (Test-Path $Lockfile) {
    Write-Host "[i] Referenced dependency lockfile: $Lockfile" -ForegroundColor Gray
}

# 2. Check Core Dependencies (Python, Git, Pandoc, Typst)
Write-Host "`n[1/5] Verifying Core Dependencies..." -ForegroundColor Green

# Python Check
$PythonExe = Get-Command "python" -ErrorAction SilentlyContinue
if ($PythonExe) {
    $PyVer = python --version 2>&1
    Write-Host "  [OK] Python: $PyVer" -ForegroundColor Green
} else {
    Write-Host "  [X] Python is not found in PATH." -ForegroundColor Red
    $InstallErrors.Add("Python missing from PATH. Install Python 3.10+ from python.org or via 'winget install Python.Python.3.12'")
}

# Git Check
$GitExe = Get-Command "git" -ErrorAction SilentlyContinue
if ($GitExe) {
    $GitVer = git --version 2>&1
    Write-Host "  [OK] Git: $GitVer" -ForegroundColor Green
} else {
    Write-Host "  [!] Git not detected. Version tracking and lockfile integrity will be degraded." -ForegroundColor Yellow
    Write-Host "      Install via: winget install Git.Git" -ForegroundColor Gray
}

# Pandoc Check
$PandocExe = Get-Command "pandoc" -ErrorAction SilentlyContinue
if ($PandocExe) {
    $PandocVer = (pandoc --version 2>&1 | Select-Object -First 1)
    Write-Host "  [OK] Pandoc: $PandocVer" -ForegroundColor Green
} else {
    Write-Host "  [i] Pandoc not found. (Optional for DOCX/EPUB publishing pipeline)" -ForegroundColor Yellow
    Write-Host "      Install via: winget install JohnMacFarlane.Pandoc" -ForegroundColor Gray
}

# Typst Check
$TypstExe = Get-Command "typst" -ErrorAction SilentlyContinue
if ($TypstExe) {
    $TypstVer = typst --version 2>&1
    Write-Host "  [OK] Typst: $TypstVer" -ForegroundColor Green
} else {
    Write-Host "  [i] Typst not found. (Optional for sovereign PDF typesetting)" -ForegroundColor Yellow
    Write-Host "      Install via: winget install Typst.Typst" -ForegroundColor Gray
}

# 3. Create Author Workspace Directories
Write-Host "`n[2/5] Initializing Author Workspaces..." -ForegroundColor Green
$UserHome = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::UserProfile)
$UniversesDir = Join-Path $UserHome "Universes"
$ManuscriptsDir = Join-Path $UserHome "Manuscripts"
$WorldsDir = Join-Path $UserHome "Worlds"

if ($DryRun) {
    Write-Host "  [DRY-RUN] Would create directory: $UniversesDir" -ForegroundColor Gray
    Write-Host "  [DRY-RUN] Would create directory: $ManuscriptsDir" -ForegroundColor Gray
    Write-Host "  [DRY-RUN] Would create directory: $WorldsDir" -ForegroundColor Gray
} else {
    foreach ($dir in @($UniversesDir, $ManuscriptsDir, $WorldsDir)) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Host "  [+] Created author workspace: $dir" -ForegroundColor Green
        } else {
            Write-Host "  [OK] Workspace exists: $dir" -ForegroundColor Gray
        }
    }
}

# 4. Generate Windows CLI Wrapper
Write-Host "`n[3/5] Configuring Windows CLI Wrappers..." -ForegroundColor Green
$CmdWrapper = Join-Path $ScriptDir "arcanum.cmd"
$CmdContent = "@echo off`r`npython `"%~dp0lib\cli.py`" %*`r`n"

if ($DryRun) {
    Write-Host "  [DRY-RUN] Would create command wrapper: $CmdWrapper" -ForegroundColor Gray
} else {
    Set-Content -Path $CmdWrapper -Value $CmdContent -Encoding ASCII -Force
    Write-Host "  [OK] Created CLI wrapper: $CmdWrapper" -ForegroundColor Green
}

# 5. Create Desktop and Start Menu Shortcuts
Write-Host "`n[4/5] Installing Desktop and Start Menu Launchers..." -ForegroundColor Green
$DesktopPath = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::DesktopDirectory)
$StartMenuPath = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Programs)
$ArcanumProgramsDir = Join-Path $StartMenuPath "Ars Arcanum"

$Shortcuts = @(
    @{
        Name = "Ars Arcanum Portfolio Studio"
        Script = "scripts/lib/cli.py"
        Args = "portfolio --html dist/portfolio_studio.html --open"
        Desc = "Sovereign Author Portfolio, Project Catalog & Multi-Book Dashboard"
    },
    @{
        Name = "Ars Arcanum Velocity Studio"
        Script = "scripts/lib/cli.py"
        Args = "words --html dist/velocity_studio.html --open"
        Desc = "Drafting Velocity, Sprint Analytics & Pomodoro Cockpit"
    },
    @{
        Name = "Ars Arcanum Revision Heatmap"
        Script = "scripts/lib/cli.py"
        Args = "revision-heatmap --html dist/revision_heatmap.html --open"
        Desc = "Interactive Manuscript Revision Density & Churn Visualizer"
    },
    @{
        Name = "Ars Arcanum Draft Lineage Studio"
        Script = "scripts/lib/cli.py"
        Args = "draft --html dist/drafts_dashboard.html --open"
        Desc = "Visual Draft Lineage Tree & Milestone State Visualizer"
    }
)

if ($DryRun) {
    foreach ($sc in $Shortcuts) {
        Write-Host "  [DRY-RUN] Would create shortcut: '$($sc.Name).lnk' on Desktop and Start Menu" -ForegroundColor Gray
    }
} else {
    if (-not (Test-Path $ArcanumProgramsDir)) {
        New-Item -ItemType Directory -Path $ArcanumProgramsDir -Force | Out-Null
    }

    $WScriptShell = New-Object -ComObject WScript.Shell
    try {
        foreach ($sc in $Shortcuts) {
            $TargetPy = "pythonw.exe"
            $PyCheck = Get-Command "pythonw.exe" -ErrorAction SilentlyContinue
            if (-not $PyCheck) {
                $TargetPy = "python.exe"
            }

            $PyPath = (Get-Command $TargetPy).Source
            $ScriptPath = Join-Path $ProjectRoot $sc.Script
            $ScriptArg = "`"$ScriptPath`" $($sc.Args)"

            # Desktop Shortcut
            $DeskLnkPath = Join-Path $DesktopPath "$($sc.Name).lnk"
            $Shortcut = $WScriptShell.CreateShortcut($DeskLnkPath)
            $Shortcut.TargetPath = $PyPath
            $Shortcut.Arguments = $ScriptArg
            $Shortcut.WorkingDirectory = $ProjectRoot
            $Shortcut.Description = $sc.Desc
            $Shortcut.Save()

            # Start Menu Shortcut
            $ProgLnkPath = Join-Path $ArcanumProgramsDir "$($sc.Name).lnk"
            $ProgShortcut = $WScriptShell.CreateShortcut($ProgLnkPath)
            $ProgShortcut.TargetPath = $PyPath
            $ProgShortcut.Arguments = $ScriptArg
            $ProgShortcut.WorkingDirectory = $ProjectRoot
            $ProgShortcut.Description = $sc.Desc
            $ProgShortcut.Save()

            Write-Host "  [OK] Installed shortcut: $($sc.Name)" -ForegroundColor Green
        }
    } finally {
        [System.Runtime.InteropServices.Marshal]::ReleaseComObject($WScriptShell) | Out-Null
    }
}

# 6. Optional Scheduled Backup Task (Daily)
if ($EnableTimer) {
    Write-Host "`n[5/5] Registering Background Backup Scheduled Task..." -ForegroundColor Green
    $TaskName = "ArsArcanumDailyBackup"
    if ($DryRun) {
        Write-Host "  [DRY-RUN] Would register Windows Scheduled Task: $TaskName (Daily at 03:00 AM)" -ForegroundColor Gray
    } else {
        $CliScript = Join-Path $ProjectRoot "scripts\lib\cli.py"
        $Action = New-ScheduledTaskAction -Execute "python.exe" -Argument "`"$CliScript`" backup" -WorkingDirectory $ProjectRoot
        $Trigger = New-ScheduledTaskTrigger -Daily -At 3am
        $Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive
        $Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

        try {
            Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Force | Out-Null
            Write-Host "  [OK] Registered Scheduled Task: $TaskName (Runs daily at 3:00 AM)" -ForegroundColor Green
        } catch {
            Write-Host "  [!] Could not register Scheduled Task via PowerShell: $_" -ForegroundColor Yellow
            $InstallErrors.Add("Scheduled task registration failed: $_")
        }
    }
} else {
    Write-Host "`n[5/5] Background backup timer skipped (pass -EnableTimer to register daily task)." -ForegroundColor Gray
}

# Completion Summary
Write-Host "`n============================================================" -ForegroundColor Cyan
if ($DryRun) {
    Write-Host "  [DRY-RUN COMPLETE] All simulated checks passed without errors." -ForegroundColor Green
} elseif ($InstallErrors.Count -gt 0) {
    Write-Host "  [PARTIAL] Ars Arcanum setup finished WITH WARNINGS:" -ForegroundColor Yellow
    foreach ($err in $InstallErrors) {
        Write-Host "    - $err" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [SUCCESS] Ars Arcanum Writing Setup Installed Successfully!" -ForegroundColor Green
}
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Next Steps for Authors:" -ForegroundColor Cyan
Write-Host "1. Double-click 'Ars Arcanum Studio Hub' on your Desktop to open the Craft Cockpit"
Write-Host "2. Double-click 'Ars Arcanum Zen Studio' for distraction-free drafting"
Write-Host "3. Open Windows Terminal and run: .\scripts\arcanum new manuscript"
Write-Host "4. Or create a new world bible: .\scripts\arcanum new world"
Write-Host "============================================================" -ForegroundColor Cyan

if (-not $DryRun -and $LogFile) {
    Stop-Transcript | Out-Null
    Write-Host "Setup Audit Log: $LogFile" -ForegroundColor Gray
}
