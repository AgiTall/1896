from pathlib import Path
import urllib.request, urllib.parse,json
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'gfx/leaders/period_sources';out.mkdir(parents=True,exist_ok=True)
files={'meiji':'Emperor Meiji in 1873.jpg','casembroot':'Frans Frederik de Casembroot.jpg','fabius':'Fabius, G.jpg'}
records={}
for key,title in files.items():
 url='https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode({'action':'query','titles':'File:'+title,'prop':'imageinfo','iiprop':'url|extmetadata','format':'json'})
 req=urllib.request.Request(url,headers={'User-Agent':'1896ModAssetBuilder/1.0'})
 data=json.load(urllib.request.urlopen(req,timeout=25));info=next(iter(data['query']['pages'].values()))['imageinfo'][0]
 original=info['url'].split('?')[0];ext=Path(urllib.parse.unquote(urllib.parse.urlparse(original).path)).suffix
 path=out/(key+ext)
 if not path.exists():path.write_bytes(urllib.request.urlopen(urllib.request.Request(original,headers={'User-Agent':'1896ModAssetBuilder/1.0'}),timeout=25).read())
 records[key]={'file':str(path.relative_to(ROOT)),'description':info['descriptionurl'],'original':original,'metadata':info.get('extmetadata',{})}
 (out/'sources.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
 print(key,path.name,records[key]['metadata'].get('LicenseShortName',{}).get('value'))
(out/'sources.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
