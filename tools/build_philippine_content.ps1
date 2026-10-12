$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
function Write-Mod($path, $value, $bom = $false) {
 $full = Join-Path $root $path
 [IO.Directory]::CreateDirectory((Split-Path $full -Parent)) | Out-Null
 [IO.File]::WriteAllText($full, $value, [Text.UTF8Encoding]::new($bom))
}
$regions = @(
 @(624,'PVI','Висайская республика','Visayan Republic'),
 @(625,'PSM','Республика Самар','Samar Republic'),
 @(627,'PMD','Республика Минданао','Mindanao Republic'),
 @(1026,'PNM','Северный Минданао','North Mindanao'),
 @(628,'PCB','Республика Себу','Cebu Republic'),
 @(1085,'PPN','Конфедерация Панай','Panay Confederation'),
 @(623,'PNL','Республика Северного Лусона','North Luzon Republic'),
 @(327,'PML','Республика Манила','Manila Republic'),
 @(1027,'PBT','Республика Батаан','Bataan Republic')
)
$tags = ''; $ru = @('l_russian:'); $en = @('l_english:')
function Loc($key,$r,$e) { $script:ru += " ${key}:0 `"$r`""; $script:en += " ${key}:0 `"$e`"" }
foreach ($r in $regions) {
 $id,$tag,$name,$english = $r
 $state = Get-ChildItem "$root/history/states" | Where-Object { $_.Name -match "^$id(?:\D)" } | Select-Object -First 1
 $s = [IO.File]::ReadAllText($state.FullName)
 $s = $s -replace 'add_core_of = A10', "add_core_of = $tag"
 if ($id -eq 623) { $s = $s -replace 'owner = PLS','owner = A03' -replace 'add_core_of = PLS',"add_core_of = $tag" }
 if ($id -in @(628,1085)) { $s = $s -replace "owner = $tag",'owner = A10' }
 [IO.File]::WriteAllText($state.FullName,$s,[Text.UTF8Encoding]::new($false))
 if ($tag -notin @('PCB','PPN')) {
  $tags += "$tag = `"countries/$tag.txt`"`n"
  Write-Mod "common/countries/$tag.txt" "graphical_culture = asian_gfx`ngraphical_culture_2d = western_european_2d`ncolor = rgb { $((60 + $id % 120)) $((90 + $id % 100)) $((80 + $id % 140)) }`n"
  Write-Mod "history/countries/$tag - Philippine Republic.txt" "capital = $id`nset_politics = { ruling_party = neutrality elections_allowed = no }`nset_popularities = { neutrality = 100 }`nset_research_slots = 2`nset_stability = 0.45`nset_war_support = 0.35`nset_convoys = 5`nset_technology = { infantry_weapons = 1 }`nadd_ideas = volunteer_only`nadd_ideas = civilian_economy`nadd_ideas = limited_exports`n"
  foreach ($suffix in @('', '_DEF','_neutrality','_neutrality_DEF')) { Loc "$tag$suffix" $name $english }
  Loc "${tag}_ADJ" 'Филиппинск.' 'Philippine'
  foreach ($dir in @('','/medium','/small')) {
   $dest = "$root/gfx/flags$dir/$tag.tga"
   Copy-Item "$root/gfx/flags$dir/A10.tga" $dest -Force
  }
 }
}
Write-Mod 'common/country_tags/02_philippine_republics.txt' $tags
# The former Catholic Republic has no territory, cores, or bookmark entry.
$book = 'common/bookmarks/the_gathering_storm.txt'
$s = [IO.File]::ReadAllText("$root/$book") -replace '(?m)^.*"PLS" = .*\r?\n',''
Write-Mod $book $s
Write-Mod 'common/autonomous_states/A10_confederate_member.txt' @'
autonomy_state = {
 id = A10_confederate_member
 is_puppet = yes
 use_overlord_color = yes
 min_freedom_level = 0.5
 manpower_influence = 1.0
 rule = {
  desc = "A10_confederate_member_desc"
  can_not_declare_war = yes
  can_decline_call_to_war = no
  units_deployed_to_overlord = yes
  can_create_collaboration_government = no
 }
 modifier = { autonomy_manpower_share = 1.0 can_master_build_for_us = 1 autonomy_gain = -1.0 }
 allowed = { OVERLORD = { tag = A10 has_country_flag = A10_confederal_path } }
 can_take_level = { always = no }
 can_lose_level = { always = no }
 ai_subject_wants_higher = { factor = 0 }
 ai_overlord_wants_lower = { factor = 0 }
 ai_overlord_wants_garrison = { always = yes }
}
'@
$effects = @'
A10_ensure_confederation_faction = {
 if = { limit = { NOT = { is_in_faction = yes } }
  create_faction_from_template = A10_confederation_template
 }
}

'@
foreach ($r in $regions) {
 $id,$tag = $r[0..1]
 $effects += @"
A10_release_$tag = {
 A10_ensure_confederation_faction = yes
 if = { limit = { owns_state = $id controls_state = $id NOT = { country_exists = $tag } }
  $tag = { transfer_state = $id }
  set_autonomy = { target = $tag autonomy_state = A10_confederate_member freedom_level = 0.5 }
  if = { limit = { is_faction_leader = yes } add_to_faction = $tag }
 }
}

"@
}
$effects += "A10_federal_progress = {`n"
foreach ($r in $regions) { $id = $r[0]; $effects += " $id = { if = { limit = { is_owned_by = A10 is_controlled_by = A10 NOT = { is_core_of = A10 } } add_compliance = 10 add_resistance = -10 } }`n" }
$effects += "}`n"
Write-Mod 'common/scripted_effects/A10_philippines.txt' $effects
Write-Mod 'common/on_actions/A10_philippines.txt' @'
on_actions = {
 on_startup = { effect = { A10 = {
  A10_ensure_confederation_faction = yes
  if = { limit = { NOT = { has_country_flag = A10_initialized } }
   set_country_flag = A10_initialized
   every_owned_state = { limit = { NOT = { is_core_of = A10 } } set_compliance = 10 set_resistance = 30 }
  }
 } } }
 on_war_relation_added = { effect = {
  if = {
   limit = { OR = {
    AND = { ROOT = { tag = A03 } FROM = { tag = A01 } }
    AND = { ROOT = { tag = A01 } FROM = { tag = A03 } }
   } }
   A10 = { if = { limit = { NOT = { has_country_flag = A10_borneo_event_scheduled } }
    set_country_flag = A10_borneo_event_scheduled
    country_event = { id = A10_philippines.1 days = 7 }
   } }
  }
 } }
}
'@
Write-Mod 'common/ideas/A10_philippines.txt' @'
ideas = { country = {
 A10_separatism = { picture = generic_political_discourse removal_cost = -1 modifier = { stability_factor = -0.10 resistance_target = 0.15 } }
 A10_federal_administration = { picture = generic_political_discourse removal_cost = -1 modifier = { resistance_target = -0.20 compliance_growth = 0.15 } }
 A10_common_army = { picture = generic_army_support removal_cost = -1 modifier = { army_org_factor = 0.05 training_time_army_factor = -0.10 } }
} }
'@
$history = 'history/countries/A10 - Placeholder.txt'
$s = [IO.File]::ReadAllText("$root/$history")
if ($s -notmatch 'add_ideas = A10_separatism') { $s += "`nadd_ideas = A10_separatism`n" }
Write-Mod $history $s
$tree = "focus_tree = {`n id = A10_philippines`n country = { factor = 0 modifier = { add = 100 tag = A10 } }`n default = no`n continuous_focus_position = { x = 1200 y = 1100 }`n"
function Focus($id,$x,$y,$pre,$reward,$r,$e,$extra='',$icon='GFX_goal_generic_political_reform') {
 $script:tree += " focus = { id = $id icon = $icon x = $x y = $y cost = 5 ai_will_do = { factor = 1 } $extra`n"
 foreach ($p in $pre) { $script:tree += " prerequisite = { focus = $p }`n" }
 $script:tree += " completion_reward = { $reward }`n }`n"
 Loc $id $r $e
}
Focus A10_island_congress 5 0 @() 'add_political_power = 100' 'Конгресс островов' 'Congress of the Islands'
Focus A10_confederation 2 1 @('A10_island_congress') 'set_country_flag = A10_confederal_path remove_ideas = A10_separatism A10_release_PVI = yes A10_release_PSM = yes' 'Договор конфедерации' 'Confederal Compact' 'mutually_exclusive = { focus = A10_federation }'
Focus A10_visayan_compact 2 2 @('A10_confederation') 'A10_release_PCB = yes A10_release_PPN = yes add_stability = 0.05' 'Хартии Себу и Паная' 'Charters of Cebu and Panay'
Focus A10_mindanao_compact 2 3 @('A10_visayan_compact') 'A10_release_PMD = yes A10_release_PNM = yes add_political_power = 50' 'Соглашение Минданао' 'Mindanao Compact'
Focus A10_united_command 2 4 @('A10_mindanao_compact') 'add_ideas = A10_common_army add_war_support = 0.10' 'Много стран — одна армия' 'Many States, One Army'
Focus A10_federation 8 1 @('A10_island_congress') 'set_country_flag = A10_federal_path set_cosmetic_tag = A10_FED remove_ideas = A10_separatism add_ideas = A10_federal_administration' 'Единая федерация' 'A United Federation' 'mutually_exclusive = { focus = A10_confederation }'
Focus A10_gendarmerie 8 2 @('A10_federation') 'A10_federal_progress = yes add_manpower = 5000' 'Островная жандармерия' 'Island Gendarmerie'
Focus A10_local_administration 8 3 @('A10_gendarmerie') 'A10_federal_progress = yes add_stability = 0.05' 'Подчинение местных советов' 'Subordinate the Local Councils'
Focus A10_equal_citizenship 8 4 @('A10_local_administration') 'A10_federal_progress = yes add_political_power = 75' 'Общее гражданство' 'Common Citizenship'
Focus A10_coastal_arsenals 5 2 @('A10_island_congress') '1084 = { add_extra_state_shared_building_slots = 2 add_building_construction = { type = arms_factory level = 1 instant_build = yes } } add_equipment_to_stockpile = { type = infantry_equipment_0 amount = 1500 producer = A10 }' 'Арсеналы Кавите' 'Cavite Arsenals' '' 'GFX_goal_generic_construct_mil_factory'
Focus A10_landing_plans 5 3 @('A10_coastal_arsenals') 'add_command_power = 25 add_war_support = 0.10' 'План возвращения Лусона' 'Plan the Return to Luzon' '' 'GFX_goal_generic_prepare_for_war'
Focus A10_strike_japan 5 5 @('A10_landing_plans') 'declare_war_on = { target = A03 type = annex_everything }' 'Ударить, пока Япония связана войной' 'Strike While Japan Is Distracted' 'available = { A03 = { has_war_with = A01 } NOT = { has_war_with = A03 } OR = { has_completed_focus = A10_united_command has_completed_focus = A10_equal_citizenship } } bypass = { has_war_with = A03 }' 'GFX_goal_generic_major_war'
Focus A10_luzon_charter 2 6 @('A10_strike_japan','A10_united_command') 'A10_release_PNL = yes' 'Хартия свободного Лусона' 'Free Luzon Charter' 'available = { owns_state = 623 controls_state = 623 }'
Focus A10_capital_charters 2 7 @('A10_luzon_charter') 'A10_release_PML = yes A10_release_PBT = yes add_stability = 0.05' 'Манила и Батаан в союзе' 'Manila and Bataan Join the Union' 'available = { owns_state = 327 controls_state = 327 owns_state = 1027 controls_state = 1027 }'
Focus A10_federal_reconstruction 8 6 @('A10_strike_japan','A10_equal_citizenship') 'A10_federal_progress = yes 1084 = { add_extra_state_shared_building_slots = 1 add_building_construction = { type = industrial_complex level = 1 instant_build = yes } }' 'Федеральное восстановление' 'Federal Reconstruction' 'available = { owns_state = 327 controls_state = 327 }'
$tree += "}`n"
Write-Mod 'common/national_focus/a10_focus.txt' $tree
Write-Mod 'common/decisions/categories/A10_philippines.txt' 'A10_integration = { icon = generic_political_discourse allowed = { tag = A10 } visible = { has_country_flag = A10_federal_path } }'
$dec = "A10_integration = {`n"
foreach ($r in $regions) {
 $id = $r[0]
 $guard = "owns_state = $id controls_state = $id $id = { NOT = { is_core_of = A10 } }"
 $dec += @"
 A10_pacify_$id = {
  icon = generic_political_discourse cost = 35 days_remove = 30 days_re_enable = 30
  visible = { $guard }
  available = { $guard }
  remove_effect = { if = { limit = { $guard } $id = { add_compliance = 10 add_resistance = -10 } } }
  ai_will_do = { factor = 2 }
 }
 A10_integrate_$id = {
  icon = generic_political_discourse cost = 50 fire_only_once = yes
  visible = { $guard }
  available = { $guard $id = { NOT = { compliance < 80 } } }
  complete_effect = { $id = { add_core_of = A10 } }
  ai_will_do = { factor = 5 }
 }
"@
 Loc "A10_pacify_$id" "Умиротворение: [${id}.GetName]" "Pacification: [${id}.GetName]"
 Loc "A10_pacify_${id}_desc" 'За 30 дней подчинение вырастет на 10 пунктов, сопротивление снизится на 10. Требуются контроль и владение областью.' 'Over 30 days, gain 10 compliance and reduce resistance by 10. Requires ownership and control.'
 Loc "A10_integrate_$id" "Национализация: [${id}.GetName]" "Integration: [${id}.GetName]"
 Loc "A10_integrate_${id}_desc" 'При 80% подчинения область становится национальной территорией Федерации.' 'At 80% compliance, this state becomes a federal core.'
}
$dec += "}`n"
Write-Mod 'common/decisions/A10_philippines.txt' $dec
Loc A10_integration 'Федеральное подчинение и интеграция' 'Federal Pacification and Integration'
Loc A10_integration_desc 'Подавляйте сопротивление и повышайте подчинение. При 80% подчинения можно национализировать область.' 'Suppress resistance and build compliance. At 80% compliance a state can become a core.'
Loc A10_confederate_member 'Участник Филиппинской конфедерации' 'Philippine Confederate Member'
Loc A10_confederate_member_desc 'Самоуправление при едином военном командовании: войска передаются Конфедерации, участник обязан вступать в её войны.' 'Self-government under a common military command: units deploy to the Confederation and members must answer calls to war.'
Loc A10_separatism 'Островной сепаратизм' 'Island Separatism'
Loc A10_separatism_desc 'Островные правительства требуют самостоятельности. Только Кавите признаёт центральную власть безоговорочно.' 'Island governments demand self-rule. Only Cavite accepts central authority unconditionally.'
Loc A10_federal_administration 'Федеральная администрация' 'Federal Administration'
Loc A10_common_army 'Общая армия островов' 'Common Army of the Islands'
foreach ($suffix in @('','_DEF','_neutrality','_neutrality_DEF')) { Loc "A10_FED$suffix" 'Федерация Филиппинских Островов' 'Federation of the Philippine Islands' }
Loc A10_FED_ADJ 'Филиппинск.' 'Philippine'
$descriptions = @(
 @('island_congress','Кавите удерживает острова лишь хрупким соглашением. Конгресс должен выбрать между союзом самостоятельных республик и единой федерацией.','Cavite holds the islands together through a fragile agreement. Congress must choose between self-governing republics and a united federation.'),
 @('confederation','Признать самостоятельность центральных Висайев и Самара. Их правительства получат особый статус участников Конфедерации с общей армией и обязательным участием в войнах.','Recognise self-rule in the central Visayas and Samar. Both become confederate members under a common army, obliged to answer calls to war.'),
 @('visayan_compact','Передать Себу и Панаю собственное управление в обмен на подчинение общему военному командованию.','Give Cebu and Panay their own governments under the common military command.'),
 @('mindanao_compact','Юг островов получит две республики: Минданао и Северный Минданао. Их войска останутся частью общей обороны.','Establish Mindanao and North Mindanao as two republics whose troops serve the common defence.'),
 @('united_command','Островные республики сохранят советы и законы, но подготовку войск и оборону будет вести единый штаб в Кавите.','Island republics retain their councils and laws while a joint staff in Cavite directs training and defence.'),
 @('federation','Отказаться от отделения островов. Федеральная администрация снизит сопротивление и ускорит рост подчинения. При 80% область можно национализировать через решение.','Reject secession. Federal administration reduces resistance and improves compliance growth. At 80%, a decision makes a state a core.'),
 @('gendarmerie','Создать постоянную жандармерию. В подконтрольных ненaциональных областях подчинение вырастет на 10 пунктов, сопротивление снизится на 10.','Establish a permanent gendarmerie. Controlled non-core states gain 10 compliance and lose 10 resistance.'),
 @('local_administration','Заменить соперничающие советы единой системой местного управления. Подчинение подконтрольных областей вырастет на 10 пунктов, сопротивление снизится на 10.','Replace competing councils with a common local administration. Controlled non-core states gain 10 compliance and lose 10 resistance.'),
 @('equal_citizenship','Общие права свяжут острова прочнее гарнизонов. Подчинение вырастет ещё на 10 пунктов. Дальнейшую интеграцию продолжат региональные решения.','Common rights bind the islands together. Gain another 10 compliance; regional decisions continue the integration effort.'),
 @('coastal_arsenals','Расширить оружейные мастерские Кавите и вооружить защитников островов до начала наступления.','Expand Cavite workshops and equip the defenders before the offensive.'),
 @('landing_plans','Подготовить штаб и маршруты возвращения на оккупированный Лусон.','Prepare the staff and routes for a return to occupied Luzon.'),
 @('strike_japan','Пока японские силы заняты войной с Нидерландами, нанести превентивный удар. Фокус объявляет войну Японии напрямую и требует завершения выбранной политической ветки.','Launch a preventive strike while Japan is fighting the Dutch. This focus directly declares war and requires completion of the chosen political branch.'),
 @('luzon_charter','После освобождения северного Лусона учредить светскую республику — нового участника Конфедерации с общей армией.','After liberating northern Luzon, establish a secular republic as a new confederate member.'),
 @('capital_charters','Освобождённые Манила и Батаан получат собственные республики и войдут в общее военное командование.','Liberated Manila and Bataan become separate republics under the common military command.'),
 @('federal_reconstruction','Возвращение Манилы позволяет начать восстановление. Повысить подчинение подконтрольных областей на 10 пунктов и расширить промышленность Кавите.','The return of Manila opens reconstruction. Gain 10 compliance in controlled non-core states and expand Cavite industry.')
)
foreach ($d in $descriptions) { Loc "A10_$($d[0])_desc" $d[1] $d[2] }
Write-Mod 'localisation/russian/A10_philippines_l_russian.yml' ($ru -join "`n") $true
Write-Mod 'localisation/english/A10_philippines_l_english.yml' ($en -join "`n") $true
