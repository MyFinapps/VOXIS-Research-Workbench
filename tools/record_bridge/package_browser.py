"""Build a small, reproducible standalone Browser candidate from this directory."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

FILES = ["browser.py", "bridge.py", "store.py", "adapters.py", "Start-Record-Browser.cmd",
         "Start-Record-Bridge.cmd", "BROWSER_README.md", "README.md", "VALIDATION.md",
         "test_bridge.py", "test_browser.py", "browser_web/index.html",
         "browser_web/app.js", "browser_web/style.css"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--source-ref", required=True, help="Commit identifying these exact source files")
    args = parser.parse_args()
    root = Path(__file__).parent
    contents = {name: (root / name).read_bytes() for name in FILES}
    contents["BUILD.json"] = (json.dumps({"product":"VOXIS Record Browser", "version":"0.1.0",
        "source_commit":args.source_ref, "bridge_base":"f64ce25b87eb4dd983c3a4d46a382f362fc4c4a5",
        "verification":"Linux automated/API and Chromium UI checks; Forge Browser acceptance pending"}, indent=2)+"\n").encode()
    contents["SHA256SUMS.txt"] = "".join(hashlib.sha256(data).hexdigest()+"  "+name+"\n"
        for name,data in sorted(contents.items())).encode()
    with zipfile.ZipFile(args.output, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for name,data in sorted(contents.items()):
            entry = zipfile.ZipInfo("VOXIS_Record_Browser_C02_v0.1/"+name, (1980,1,1,0,0,0))
            entry.compress_type=zipfile.ZIP_DEFLATED
            entry.external_attr=0o100644 << 16
            archive.writestr(entry,data)
    print(str(args.output.resolve()))


if __name__ == "__main__":
    main()
