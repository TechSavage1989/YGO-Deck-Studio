import os
import subprocess
import sys
import tempfile
from pathlib import Path

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'tools'))
import patch_embedded_web as pw  # noqa: E402

assert "duelcore.1-rc248" in (root/'web/js/duel-core.js').read_text(encoding='utf-8')
assert 'web/duel-core.css' in pw.PATCH_FILES
LIMITS={'web/js/duel-core.js':798551,'web/js/app.js':463846,'web/styles.css':586884,'web/duel-core.css':361955,'web/index.html':97860}

def check(path):
    with tempfile.NamedTemporaryFile('wb',suffix='.mjs',delete=False) as handle:
        handle.write(path);name=handle.name
    try: subprocess.run(['node','--check',name],check=True)
    finally: os.unlink(name)

for name,limit in LIMITS.items():
    out=pw.replacement_bytes(root/name,name)
    assert len(out)<=limit,(name,len(out),limit)

if pw.terser_command() is None:
    print('rc244 minified embed: SKIPPED terser assertions (npx unavailable)')
else:
    for name in ('web/js/duel-core.js','web/js/app.js'):
        source=(root/name).read_bytes();out=pw.minify_js(source)
        assert out is not None,name
        assert len(out)<len(source)*0.85,(name,len(out))
        assert LIMITS[name]-len(out)>50000,(name,len(out))  # real headroom, not a near miss
        check(out)
    core=pw.minify_js((root/'web/js/duel-core.js').read_bytes()).decode('utf-8')
    # Class and method names are part of the app and test contract and must survive.
    assert 'class IntegratedDuelController' in core and 'export' in core
    for method in ('dummyResponse(','processLoop(','mapCoreMessageValue(','smartOptionalChainResponse(','playSound('):
        assert method in core,method
    assert 'triggering_controller' in core and "duelcore.1-rc248" in core

# The whitespace fallback still yields valid JavaScript when terser is disabled.
os.environ['YGO_NO_TERSER']='1'
try:
    for name in ('web/js/duel-core.js','web/js/app.js'):
        check(pw.replacement_bytes(root/name,name))
finally:
    del os.environ['YGO_NO_TERSER']
print('rc244 minified embed regression passed')
