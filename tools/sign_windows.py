#!/usr/bin/env python3
"""Optional Authenticode signing hook for the release build.

scripts/build_release.py calls sign() on the launcher right after `go build`,
before the icon check, the updater candidate tests, the SHA-256/size manifest
and the portable ZIP, so every published copy carries the same signed bytes.

Configuration is by environment only; no certificate, token or password is
ever stored in the repository:

  YGO_SIGN_COMMAND    Command that signs one file in place. {file} is replaced
                      by the executable path, e.g.
                      java -jar jsign.jar --storetype TRUSTEDSIGNING ... {file}
  YGO_REQUIRE_SIGNING Set to 1 to fail the build when signing is not configured
                      (the release workflow sets it once signing secrets exist).

Without YGO_SIGN_COMMAND the build stays unsigned, exactly as before.
"""
from __future__ import annotations
import os, shlex, struct, subprocess, sys
from pathlib import Path

def has_authenticode(path: Path) -> bool:
    """True when the PE security data directory points at a certificate table."""
    data = path.read_bytes()
    if data[:2] != b'MZ':
        raise SystemExit(f'{path} is not a PE file')
    pe = struct.unpack_from('<I', data, 0x3C)[0]
    if data[pe:pe + 4] != b'PE\0\0':
        raise SystemExit(f'{path} has no PE header')
    opt = pe + 24
    magic = struct.unpack_from('<H', data, opt)[0]
    dirs = opt + (112 if magic == 0x20B else 96)
    offset, size = struct.unpack_from('<II', data, dirs + 4 * 8)
    return size > 0 and offset + size <= len(data)

def sign(path: Path) -> bool:
    command = os.environ.get('YGO_SIGN_COMMAND', '').strip()
    if not command:
        if os.environ.get('YGO_REQUIRE_SIGNING') == '1':
            raise SystemExit('YGO_REQUIRE_SIGNING=1 but YGO_SIGN_COMMAND is not set')
        print(f'Code signing not configured; {path.name} stays unsigned.', flush=True)
        return False
    args = [a.replace('{file}', str(path)) for a in shlex.split(command)]
    if str(path) not in args:
        raise SystemExit('YGO_SIGN_COMMAND must contain {file}')
    print(f'+ signing {path.name}', flush=True)  # the command may hold secrets; never echo it
    result = subprocess.run(args)
    if result.returncode:
        # CalledProcessError would print the arguments, which may hold an access token.
        raise SystemExit(f'Signing {path.name} failed with exit code {result.returncode}')
    if not has_authenticode(path):
        raise SystemExit(f'Signing finished but {path.name} has no Authenticode signature')
    print(f'Signed {path.name}.', flush=True)
    return True

if __name__ == '__main__':
    for name in sys.argv[1:]:
        sign(Path(name))
