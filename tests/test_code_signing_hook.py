"""The release build's optional Authenticode hook (tools/sign_windows.py).

Builds a tiny Windows PE with Go, then checks that: signing is skipped when not
configured, YGO_REQUIRE_SIGNING=1 refuses an unconfigured build, a configured
command runs on the file, and a command that leaves no certificate table fails.
"""
import os, struct, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import sign_windows as sw

FAKE_SIGNER = r'''
import struct, sys
p = sys.argv[1]; d = bytearray(open(p, 'rb').read())
pe = struct.unpack_from('<I', d, 0x3C)[0]; opt = pe + 24
dirs = opt + (112 if struct.unpack_from('<H', d, opt)[0] == 0x20B else 96)
while len(d) % 8: d.append(0)
table = struct.pack('<IHH', 16, 0x200, 2) + b'\0' * 8
struct.pack_into('<II', d, dirs + 32, len(d), len(table)); d += table
open(p, 'wb').write(d)
'''

def env(**extra):
    e = {k: v for k, v in os.environ.items() if k not in ('YGO_SIGN_COMMAND', 'YGO_REQUIRE_SIGNING')}
    e.update(extra); return e

def main():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / 'go.mod').write_text('module signtest\n\ngo 1.21\n')
        (tmp / 'main.go').write_text('package main\n\nfunc main() {}\n')
        exe = tmp / 'app.exe'
        subprocess.run(['go', 'build', '-o', str(exe), '.'], cwd=tmp, check=True,
                       env={**os.environ, 'GOOS': 'windows', 'GOARCH': 'amd64', 'CGO_ENABLED': '0'})
        assert not sw.has_authenticode(exe)
        signer = tmp / 'fake_signer.py'; signer.write_text(FAKE_SIGNER)
        noop = tmp / 'noop.py'; noop.write_text('')
        hook = [sys.executable, str(ROOT / 'tools/sign_windows.py'), str(exe)]

        r = subprocess.run(hook, env=env(), capture_output=True, text=True)
        assert r.returncode == 0 and 'stays unsigned' in r.stdout, r
        r = subprocess.run(hook, env=env(YGO_REQUIRE_SIGNING='1'), capture_output=True, text=True)
        assert r.returncode != 0 and 'YGO_SIGN_COMMAND is not set' in r.stderr, r
        r = subprocess.run(hook, env=env(YGO_SIGN_COMMAND=f'"{sys.executable}" "{noop}" {{file}}'), capture_output=True, text=True)
        assert r.returncode != 0 and 'no Authenticode signature' in r.stderr, r
        r = subprocess.run(hook, env=env(YGO_SIGN_COMMAND=f'"{sys.executable}" "{signer}" {{file}}'), capture_output=True, text=True)
        assert r.returncode == 0 and 'Signed app.exe' in r.stdout, r
        assert sys.executable not in r.stdout, 'the signing command must not be echoed'
        assert sw.has_authenticode(exe)
    print('code signing hook OK')

if __name__ == '__main__':
    main()
