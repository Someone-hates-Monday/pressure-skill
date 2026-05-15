<#
.SYNOPSIS
  Install pressure-skill to Claude Code user skills directory (~/.claude/skills).

.NOTES
  Run from repository root. Full multi-target install: .\scripts\install_pressure_skill.ps1
#>
$ErrorActionPreference = "Stop"
& "$PSScriptRoot\install_pressure_skill.ps1" -Targets ClaudeCode
