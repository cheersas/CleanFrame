"""Build and sign with the installed Tizen Studio and its Certificate Manager profile (macOS)."""
from pathlib import Path
import os
import subprocess
import zipfile
from font_assets import write_widget_archive

ROOT = Path(__file__).resolve().parents[1]
SDK = Path(os.environ.get('TIZEN_STUDIO', Path.home() / 'tizen-studio'))
PROFILE = os.environ.get('TIZEN_PROFILE', 'cleanframe')
CLI = SDK / 'tools/ide/bin/tizen'
if not CLI.exists():
    raise SystemExit('Tizen Studio CLI missing at ' + str(CLI) + '. Set TIZEN_STUDIO or see docs/development.md.')
dist = ROOT / 'dist'
dist.mkdir(exist_ok=True)
unsigned = dist / 'CleanFrame-unsigned.wgt'
write_widget_archive(unsigned)
signed_dir = dist / 'signed'
signed_dir.mkdir(exist_ok=True)
# Certificate Manager stores the profile passwords, so signing needs no prompt.
result = subprocess.run([str(CLI), 'package', '-t', 'wgt', '-s', PROFILE, '-o', str(signed_dir), '--', str(unsigned)],
                        stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=120)
if 'is created successfully' not in result.stdout:
    print(result.stdout + result.stderr)
    raise SystemExit('SDK did not confirm a signed package. Check the "' + PROFILE + '" profile in Certificate Manager.')
signed = signed_dir / unsigned.name
with zipfile.ZipFile(signed) as package:
    if not {'author-signature.xml', 'signature1.xml'}.issubset(package.namelist()):
        raise SystemExit('Package is missing its signing files.')
target = dist / 'CleanFrame.wgt'
target.write_bytes(signed.read_bytes())
print('Signed widget created: ' + str(target))
