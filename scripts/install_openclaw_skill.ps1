<#
.SYNOPSIS
  Install pressure-skill to OpenClaw workspace skills (~/.openclaw/workspace/skills).

.NOTES
  Run from repository root. Creates parent directories if missing.
#>
$ErrorActionPreference = "Stop"
& "$PSScriptRoot\install_pressure_skill.ps1" -Targets OpenClaw
