<#
.SYNOPSIS
  Copy canonical pressure-skill folder (.cursor/skills/pressure-skill) to user-level agent skill dirs.

.DESCRIPTION
  Source of truth: repo .cursor/skills/pressure-skill (includes references/).
  Targets: Cursor + legacy .agents scan paths, Claude Code (.claude/skills), OpenClaw (.openclaw/workspace/skills).

.PARAMETER Targets
  Which install roots to write. Default All.

.EXAMPLE
  .\scripts\install_pressure_skill.ps1
  .\scripts\install_pressure_skill.ps1 -Targets ClaudeCode
  .\scripts\install_pressure_skill.ps1 -Targets Cursor,Agents
#>
param(
  [ValidateSet('Cursor', 'Agents', 'ClaudeCode', 'OpenClaw', 'All')]
  [string[]]$Targets = @('All')
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$src = Join-Path $repoRoot ".cursor\skills\pressure-skill"
$skillName = "pressure-skill"

if (-not (Test-Path -LiteralPath $src)) {
  Write-Error "Source skill folder not found: $src"
}

$resolved = [System.Collections.Generic.List[string]]::new()
foreach ($t in $Targets) {
  if ($t -eq 'All') {
    @('Cursor', 'Agents', 'ClaudeCode', 'OpenClaw') | ForEach-Object { [void]$resolved.Add($_) }
    break
  }
  if (-not $resolved.Contains($t)) { [void]$resolved.Add($t) }
}

$roots = @{
  'Cursor'     = (Join-Path $env:USERPROFILE ".cursor\skills")
  'Agents'     = (Join-Path $env:USERPROFILE ".agents\skills")
  'ClaudeCode' = (Join-Path $env:USERPROFILE ".claude\skills")
  'OpenClaw'   = (Join-Path $env:USERPROFILE ".openclaw\workspace\skills")
}

foreach ($key in $resolved) {
  $dstRoot = $roots[$key]
  $dst = Join-Path $dstRoot $skillName
  New-Item -ItemType Directory -Force -Path $dstRoot | Out-Null
  if (Test-Path -LiteralPath $dst) {
    Remove-Item -LiteralPath $dst -Recurse -Force
  }
  Copy-Item -LiteralPath $src -Destination $dst -Recurse -Force
  Write-Host "[$key] -> $dst"
}

Write-Host ""
Write-Host "Skill files installed. Notes:"
Write-Host "  - Cursor / Agents: reload window; try /pressure-skill"
Write-Host "  - Claude Code: use your product's skill / command discovery (often skill name pressure-skill)"
Write-Host "  - OpenClaw: same; path follows OpenClaw workspace skills layout"
Write-Host "  - Running bundle_local.py / uvicorn: still from THIS repo root (scripts/ live here), not only ~/.skill copy"
