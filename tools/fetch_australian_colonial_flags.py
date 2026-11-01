"""Download public domain historical SVG flags; render with bundled sharp."""
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import quote
import hashlib,json,subprocess,sys,shutil
from PIL import Image
R=Path(__file__).resolve().parents[1]
FILES={'A07':'Flag of New South Wales.svg','AVC':'Flag of Victoria (1877–1901).svg','AQL':'Flag of Queensland (1876–1901).svg','ASA':'Flag of South Australia (1876–1904).svg','AWA':'Flag of Western Australia (1870–1953).svg','ATA':'Flag of Tasmania.svg'}
def main():
    node=sys.argv[1];packages=sys.argv[2]
    folder=R/'gfx/flags/sources/australia_1893';folder.mkdir(parents=True,exist_ok=True)
    report={}
    for tag,name in FILES.items():
        filename=name.replace(' ','_');digest=hashlib.md5(filename.encode()).hexdigest()
        url='https://upload.wikimedia.org/wikipedia/commons/'+digest[0]+'/'+digest[:2]+'/'+quote(filename)
        svg=folder/(tag+'.svg');png=folder/(tag+'.png')
        if not svg.exists():
            with urlopen(Request(url,headers={'User-Agent':'1896ModHistoricalFlags/1.0 (local educational game mod)'}),timeout=30) as response:svg.write_bytes(response.read())
        script="const sharp=require(require.resolve('sharp',{paths:[process.argv[1]]}));sharp(process.argv[2]).resize(820,520,{fit:'fill'}).png().toFile(process.argv[3]).catch(e=>{console.error(e);process.exit(1)});"
        subprocess.run([node,'-e',script,packages,str(svg),str(png)],check=True)
        with Image.open(png) as source:
            for sub,size in [('',(82,52)),('medium',(41,26)),('small',(10,7))]:
                for suffix in ('','_democratic','_neutrality'):
                    p=R/'gfx/flags'/sub/(tag+suffix+'.tga')
                    if p.exists():
                        backup=R/'tools/backups/australia_before_split_1893'/p.relative_to(R);backup.parent.mkdir(parents=True,exist_ok=True)
                        if not backup.exists():shutil.copy2(p,backup)
                    source.convert('RGB').resize(size,Image.Resampling.LANCZOS).save(p)
        report[tag]={'file':name,'source':'https://commons.wikimedia.org/wiki/File:'+quote(filename),'original':url,'license':'Public domain; see source page'}
        print(tag,'OK',flush=True)
    (folder/'sources.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':main()
