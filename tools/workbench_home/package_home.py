"""Build a deterministic Home candidate with unchanged Bridge dependencies."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

HOME_FILES = ['home.py','launcher.py','Start-Workbench-Home.cmd','README.md','test_home.py',
              'web/index.html','web/app.js','web/style.css']
BRIDGE_FILES = ['browser.py','bridge.py','store.py','adapters.py','Start-Record-Browser.cmd',
                'Start-Record-Bridge.cmd','BROWSER_README.md','README.md','VALIDATION.md','test_bridge.py',
                'browser_web/index.html','browser_web/app.js','browser_web/style.css']


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('output',type=Path);p.add_argument('--source-ref',required=True);args=p.parse_args()
    root=Path(__file__).resolve().parents[2]
    def git(*argv):return subprocess.check_output(['git','-C',str(root),*argv],stderr=subprocess.PIPE)
    commit=git('rev-parse','--verify','--end-of-options',args.source_ref+'^{commit}').decode().strip()
    files={}
    for folder,names in [('workbench_home',HOME_FILES),('record_bridge',BRIDGE_FILES)]:
        for name in names:
            source='tools/'+folder+'/'+name;data=git('show',commit+':'+source)
            if (root/source).read_bytes()!=data:raise ValueError('Source differs from commit: '+source)
            files[folder+'/'+name]=data
    files['START-HERE.txt']=('VOXIS Workbench Home 0.1 candidate\n\nExtract the whole ZIP into a new folder.\nOpen workbench_home, then double-click Start-Workbench-Home.cmd.\nRead workbench_home/README.md for setup and scoped acceptance.\nDo not move the record_bridge dependency folder away from workbench_home.\n').encode()
    files['BUILD.json']=(json.dumps({'product':'VOXIS Workbench Home','version':'0.1.0','source_commit':commit,
        'verification':'Candidate. See README; Forge integration acceptance pending.',
        'browser_runtime_acceptance':'97bbccb3eec4d15b08205d7a07115fdd14497feb; Home integration is separate.'},indent=2)+'\n').encode()
    files['SHA256SUMS.txt']=''.join(hashlib.sha256(data).hexdigest()+'  '+name+'\n' for name,data in sorted(files.items())).encode()
    with zipfile.ZipFile(args.output,'x',compression=zipfile.ZIP_DEFLATED) as z:
        for name,data in sorted(files.items()):
            entry=zipfile.ZipInfo('VOXIS_Workbench_Home_C03_v0.1/'+name,(1980,1,1,0,0,0));entry.compress_type=zipfile.ZIP_DEFLATED;entry.external_attr=0o100644<<16;z.writestr(entry,data)
    print(args.output.resolve())


if __name__=='__main__':main()
