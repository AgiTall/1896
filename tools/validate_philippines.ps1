$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
function Assert($ok,$message) { if (-not $ok) { throw $message } }
$files = @('common/national_focus/a10_focus.txt','common/scripted_effects/A10_philippines.txt','common/decisions/A10_philippines.txt','common/autonomous_states/A10_confederate_member.txt','common/ideas/A10_philippines.txt','common/on_actions/A10_philippines.txt','events/A10_philippines.txt','common/factions/templates/A10_philippines.txt','interface/A10_faction.gfx')
foreach ($f in $files) {
 $s = [IO.File]::ReadAllText("$root/$f") -replace '"[^"]*"','' -replace '(?m)#.*$',''
 $depth = 0
 foreach ($c in $s.ToCharArray()) { if ($c -eq '{') { $depth++ }; if ($c -eq '}') { $depth-- }; Assert ($depth -ge 0) "Unbalanced braces: $f" }
 Assert ($depth -eq 0) "Unbalanced braces: $f"
}
$tree = [IO.File]::ReadAllText("$root/common/national_focus/a10_focus.txt")
$ids = @([regex]::Matches($tree,'focus = \{ id = (\w+)') | ForEach-Object { $_.Groups[1].Value })
Assert ($ids.Count -eq 15) 'Expected 15 focuses'
Assert (($ids | Select-Object -Unique).Count -eq $ids.Count) 'Duplicate focus IDs'
foreach ($m in [regex]::Matches($tree,'(?:prerequisite|mutually_exclusive) = \{ focus = (\w+)')) { Assert ($m.Groups[1].Value -in $ids) "Missing focus: $m" }
foreach ($lang in @('russian','english')) {
 $f = "$root/localisation/$lang/A10_philippines_l_$lang.yml"
 $s = [IO.File]::ReadAllText($f)
 foreach ($id in $ids) { Assert ($s.Contains(" ${id}:0")) "Missing $lang name $id"; Assert ($s.Contains(" ${id}_desc:0")) "Missing $lang description $id" }
 $bytes = [IO.File]::ReadAllBytes($f)
 Assert ($bytes[0] -eq 239 -and $bytes[1] -eq 187 -and $bytes[2] -eq 191) "Missing localisation BOM: $f"
}
$coreStates = @()
foreach ($f in Get-ChildItem "$root/history/states/*.txt") {
 $s = [IO.File]::ReadAllText($f.FullName)
 if ($s -match 'add_core_of = A10\b') { $coreStates += $f.Name }
 Assert ($s -notmatch '(?:owner|add_core_of) = PLS\b') "PLS still on map: $($f.Name)"
}
Assert ($coreStates.Count -eq 1 -and $coreStates[0] -match '^1084 ') 'A10 must only have core 1084'
$d = [IO.File]::ReadAllText("$root/common/decisions/A10_philippines.txt")
Assert ([regex]::Matches($d,'NOT = \{ compliance < 80 \}').Count -eq 9) 'Expected 9 integration gates at exactly 80% using supported syntax'
foreach ($tag in @('PVI','PSM','PMD','PNM','PNL','PML','PBT')) {
 Assert (Test-Path "$root/common/countries/$tag.txt") "Missing country $tag"
 Assert ((Get-ChildItem "$root/history/countries/$tag*.txt").Count -eq 1) "Missing history $tag"
 foreach ($size in @('','/small','/medium')) { Assert (Test-Path "$root/gfx/flags$size/$tag.tga") "Missing flag $tag $size" }
}
$autonomy = [IO.File]::ReadAllText("$root/common/autonomous_states/A10_confederate_member.txt")
Assert ($autonomy.Contains('use_overlord_color = yes')) 'Members must inherit overlord color'
$effects = [IO.File]::ReadAllText("$root/common/scripted_effects/A10_philippines.txt")
Assert ([regex]::Matches($effects,'add_to_faction = P\w+').Count -eq 9) 'All nine release effects must join faction'
Assert ($effects.Contains('create_faction_from_template = A10_confederation_template')) 'Missing faction creation'
$actions = [IO.File]::ReadAllText("$root/common/on_actions/A10_philippines.txt")
Assert ($actions.Contains('country_event = { id = A10_philippines.1 days = 7 }')) 'Event must be scheduled exactly seven days later'
Assert ($actions.Contains('set_country_flag = A10_borneo_event_scheduled')) 'Missing duplicate event protection'
$event = [IO.File]::ReadAllText("$root/events/A10_philippines.txt")
Assert ($event.Contains('declare_war_on = { target = A03 type = annex_everything }')) 'Chance option must declare war'
foreach ($lang in @('russian','english')) {
 $loc = [IO.File]::ReadAllText("$root/localisation/$lang/A10_philippines_events_l_$lang.yml")
 foreach ($key in @('A10_confederation_faction','A10_philippines.1.t','A10_philippines.1.d','A10_philippines.1.a','A10_philippines.1.b')) { Assert ($loc.Contains(" ${key}:0")) "Missing event/faction $lang localisation $key" }
}
'PASS: script braces, 15 focus links, bilingual localisation/BOM, sole A10 core, 80% integration, country assets, faction creation/membership, inherited color, seven-day event and war option.'
