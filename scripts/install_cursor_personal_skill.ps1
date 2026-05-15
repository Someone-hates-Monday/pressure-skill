<#
.SYNOPSIS
  Install pressure-skill to Cursor + user .agents skills dirs only (backward compatible).

.NOTES
  Run from repository root:  .\scripts\install_cursor_personal_skill.ps1
  For Claude Code / OpenClaw as well, use: .\scripts\install_pressure_skill.ps1
#>
$ErrorActionPreference = "Stop"
& "$PSScriptRoot\install_pressure_skill.ps1" -Targets Cursor, Agents
