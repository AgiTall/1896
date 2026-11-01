"""Record the targeted diagnostics from the explicit Japanese-content debug load."""
from pathlib import Path
import json,re
R=Path(__file__).resolve().parents[1]
logs=R.parents[1]/'logs'
error=(logs/'error.log').read_text(encoding='utf-8-sig',errors='replace')
system=(logs/'system.log').read_text(encoding='utf-8-sig',errors='replace')
target=re.compile(r'JPC|japan_canon|a03_focus|A03_borneo_triggers|A01_canonical|A03_southern_preparations|A03_japanese_expansion')
findings=[line for line in error.splitlines() if target.search(line)]
report={
 'date':'2026-10-12',
 'mode':'Explicit -debug game launch with the user’s configured mod list unchanged',
 'active_mods':[line for line in system.splitlines() if 'Active Mod:' in line],
 'targeted_diagnostics':findings,
 'targeted_diagnostic_count':len(findings),
 'load_exception':[line for line in error.splitlines() if 'Failed allocate data buffer' in line],
 'limitations':['No full campaign or combat balance playthrough','Global load exception previously documented in docs/LOAD_ISOLATION_RESULTS.md','Other base-content diagnostics remain outside this task','Final province-list refresh is statically checked; this report records the prior debug load'],
}
(R/'tools/japan_engine_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8',newline='\n')
print(f'Targeted diagnostics: {len(findings)}; global load exception: {bool(report["load_exception"])}')
