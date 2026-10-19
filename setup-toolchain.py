from pathlib import Path
import os
import re
import subprocess

root = Path.home() / '.local/arm64-toolchain'
cache = root / 'debs'
cache.mkdir(parents=True, exist_ok=True)
os.environ['LC_ALL'] = 'C'
plan = subprocess.check_output(['apt-get', '-s', '-o', 'Debug::NoLocking=1', 'install', '--no-install-recommends',
    'gcc-aarch64-linux-gnu', 'libc6-dev-arm64-cross', 'qemu-user', 'gdb-multiarch'], text=True)
packages = re.findall(r'^Inst (\S+) \((\S+)', plan, re.M)
(root / 'package-plan.txt').write_text(plan)
subprocess.run(['apt-get', 'download'] + [p + '=' + v for p, v in packages], cwd=cache, check=True)
for deb in sorted(cache.glob('*.deb')):
    subprocess.run(['dpkg-deb', '-x', str(deb), str(root)], check=True)
(root / 'env.sh').write_text('''export ARM64_TOOLCHAIN="$HOME/.local/arm64-toolchain"
export PATH="$ARM64_TOOLCHAIN/usr/bin:$PATH"
export LD_LIBRARY_PATH="$ARM64_TOOLCHAIN/usr/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export LC_ALL=C
''')
print('USER_LOCAL_TOOLCHAIN_READY', flush=True)
