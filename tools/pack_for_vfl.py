"""Pack src/risk_weave into a single-line Python statement for SAS Studio.

SAS Studio's Monaco editor auto-indents typed text, so multi-line code cannot be
typed reliably. This script compresses the package (plus a small driver) into
one line that decodes and executes it in the PROC PYTHON session, where the
``SAS`` object is available. The payload is only an encoding of repo code.

usage: python tools/pack_for_vfl.py "<driver python code>" > payload.txt
"""
import base64
import json
import sys
import zlib
from pathlib import Path

# SAS wraps very long source lines, so the blob sits in a triple-quoted string
# (newlines are ignored by b64decode).
ORDER = ["__init__", "config", "data", "features", "models", "metrics", "cv",
         "policy", "submission", "experiment_log", "run", "final", "extra", "blend"]
BOOT = '''
import sys, types
_mods = json.loads(_SRC)
_pkg = types.ModuleType("risk_weave"); _pkg.__path__ = []; sys.modules["risk_weave"] = _pkg
for _n in _ORDER:
    _m = types.ModuleType("risk_weave." + _n); _m.__package__ = "risk_weave"
    sys.modules["risk_weave." + _n] = _m; setattr(_pkg, _n, _m)
    exec(compile(_mods[_n], _n + ".py", "exec"), _m.__dict__)
'''


def pack(driver):
    root = Path(__file__).resolve().parents[1] / "src" / "risk_weave"
    mods = {n: (root / f"{n}.py").read_text(encoding="utf-8") for n in ORDER}
    code = ("import json\n_SRC = " + repr(json.dumps(mods)) + "\n_ORDER = " + repr(ORDER)
            + "\n" + BOOT + "\n" + driver + "\n")
    blob = base64.b64encode(zlib.compress(code.encode("utf-8"), 9)).decode()
    return f"import zlib,base64;exec(zlib.decompress(base64.b64decode('''{blob}''')).decode())"


def pack_install(dest="~/rw", chunk=1500, only=None):
    """Statements that write the package to ``dest`` on the compute server.

    Returned as several short lines (one string variable per chunk): SAS wraps
    very long source lines and Monaco auto-closes quotes, so a single long
    literal cannot be typed reliably. Later runs need only a short sys.path line.
    """
    root = Path(__file__).resolve().parents[1] / "src" / "risk_weave"
    mods = {f"{n}.py": (root / f"{n}.py").read_text(encoding="utf-8")
            for n in ORDER if only is None or n in only}
    blob = base64.b64encode(zlib.compress(json.dumps(mods).encode("utf-8"), 9)).decode()
    parts = [blob[i:i + chunk] for i in range(0, len(blob), chunk)]
    lines = [f"b{k}='{part}'" for k, part in enumerate(parts)]
    joined = "+".join(f"b{k}" for k in range(len(parts)))
    lines.append(
        "import zlib,base64,json,os;d=os.path.join(os.path.expanduser('" + dest + "'),'risk_weave');"
        "os.makedirs(d,exist_ok=True);"
        "[open(os.path.join(d,k),'w',encoding='utf-8').write(v) for k,v in "
        f"json.loads(zlib.decompress(base64.b64decode({joined})).decode()).items()];"
        "print('INSTALLED',d,sorted(os.listdir(d)))"
    )
    return "\n".join(lines)


if __name__ == "__main__":
    if sys.argv[1] == "--install":
        # optional second argument: comma-separated module names to refresh only
        print(pack_install(only=sys.argv[2].split(",") if len(sys.argv) > 2 else None))
    else:
        print(pack(sys.argv[1]))
