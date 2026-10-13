"""Download, extract, restore and start the tested Odoo Docker environment.

Requires Python 3.8+ and an installed, running Docker Engine with Compose.

For protected links, SHAREPOINT_ACCESS_TOKEN must be a token issued for this
SharePoint tenant (not a Microsoft Graph token). A file sharing/download URL
can also be supplied with --url.
"""
import argparse
import hashlib
import http.cookiejar
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tarfile
import time
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import Request, build_opener, HTTPCookieProcessor

NAME = 'portable-olist6-20261009-tested.tar'
SHA256 = '118f5a82e29fc6a595350b7f1c299e1c95a69f36f60596b4dbf93476f9ddd284'
DEFAULT = ('https://gopalakrishnan-my.sharepoint.com/:u:/g/personal/gs_training_sh/'
           'IQBQvGC6WY2nSoJ7bp9JF2G4AdiqATei758LPec0GyReHJ0?e=FDc6xU&download=1')

def file_sha256(path):
    """Stream checksums without requiring Python 3.11's hashlib.file_digest."""
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()

def inside_directory(path, root):
    """Python 3.8-compatible equivalent of Path.is_relative_to."""
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False

def download(args):
    if args.output.exists():
        if file_sha256(args.output) != SHA256:
            raise RuntimeError(f'Existing archive does not match the backup: {args.output}')
        print('Using existing verified backup:', args.output)
        return
    partial = args.output.with_name(args.output.name + '.part')
    if partial.exists():
        raise RuntimeError(f'Partial download already exists: {partial}; choose another --output')
    headers = {'User-Agent': 'Mozilla/5.0'}
    token = os.environ.get('SHAREPOINT_ACCESS_TOKEN')
    if token:
        headers['Authorization'] = 'Bearer ' + token
    request = Request(args.url, headers=headers)
    opener = build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
    try:
        # Establish SharePoint's sharing-link cookies before requesting the file.
        if '.sharepoint.com' in (urlparse(args.url).hostname or '') and '/:u:/' in args.url:
            sharing_url = args.url.replace('&download=1', '')
            with opener.open(Request(sharing_url, headers=headers), timeout=120):
                pass
        response = opener.open(request, timeout=120)
    except HTTPError as error:
        raise RuntimeError(f'SharePoint returned HTTP {error.code}. If the file requires sign-in, '
                           'provide a permitted file download link or set SHAREPOINT_ACCESS_TOKEN. '
                           'A folder URL alone does not grant download access.') from None
    with response:
        content_type = response.headers.get('Content-Type', '').lower()
        first = response.read(1024 * 1024)
        if 'text/html' in content_type or first.lstrip().lower().startswith((b'<!doctype html', b'<html')):
            raise RuntimeError('SharePoint returned a web/sign-in page, not the backup. '
                               'Use a file download link with --url or an authorized SharePoint token.')
        total = int(response.headers.get('Content-Length', '0'))
        digest = hashlib.sha256()
        downloaded = 0
        with partial.open('xb') as target:
            chunk = first
            while chunk:
                target.write(chunk)
                digest.update(chunk)
                downloaded += len(chunk)
                suffix = f' / {total / 1048576:.1f} MiB' if total else ''
                print(f'\rDownloaded {downloaded / 1048576:.1f} MiB{suffix}', end='', flush=True)
                chunk = response.read(1024 * 1024)
    print()
    if digest.hexdigest() != SHA256:
        raise RuntimeError(f'SHA-256 mismatch. Kept unverified download at {partial}; '
                           'check the file URL and confirm this is the tested bundle.')
    partial.rename(args.output)
    print(f'Verified backup saved to {args.output.resolve()}')

def verify_files(root):
    manifest = json.loads((root/'bundle-manifest.json').read_text())
    for item in manifest['files']:
        # Network bindings and passwords may be changed for this destination.
        if item['path'] == '.env':
            continue
        if file_sha256(root/item['path']) != item['sha256']:
            raise RuntimeError('Bundle file checksum mismatch: ' + item['path'])

def extract(archive, root):
    root.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive) as bundle:
        files = []
        for member in bundle.getmembers():
            parts = PurePosixPath(member.name).parts
            if not parts or parts[0] != 'odoo-olist6-baseline' or '..' in parts:
                raise RuntimeError('Unexpected archive path: ' + member.name)
            if len(parts) == 1:
                continue
            if not (member.isfile() or member.isdir()):
                raise RuntimeError('Unsupported archive entry: ' + member.name)
            destination = root.joinpath(*parts[1:])
            if not inside_directory(destination, root):
                raise RuntimeError('Unsafe extraction path: ' + member.name)
            if destination.exists():
                raise RuntimeError(f'Refusing to overwrite {destination}. Use a fresh directory.')
            if member.isfile():
                files.append((member, destination))
        # Check every destination before creating any extracted file.
        for member, destination in files:
            destination.parent.mkdir(parents=True, exist_ok=True)
            with bundle.extractfile(member) as source, destination.open('xb') as target:
                while chunk := source.read(1024 * 1024):
                    target.write(chunk)
    verify_files(root)
    print('Extracted and verified Compose files in', root)

def restore(root):
    def compose(*args, capture=False):
        return subprocess.run(['docker', 'compose', *args], cwd=root,
                              check=True, text=True, capture_output=capture)
    compose('config', '--quiet')
    compose('up', '-d', 'db')
    for attempt in range(60):
        check = subprocess.run(['docker','compose','exec','-T','db','pg_isready',
                                '-U','team','-d','postgres'], cwd=root,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if check.returncode == 0:
            break
        time.sleep(2)
    else:
        raise RuntimeError('PostgreSQL did not become ready')
    exists = compose('exec','-T','db','psql','-U','team','-d','postgres','-At','-c',
                     "SELECT count(*) FROM pg_database WHERE datname='olist6';",capture=True).stdout.strip()
    if exists != '0':
        raise RuntimeError('olist6 already exists in these Compose volumes; refusing to overwrite it.')
    compose('exec','-T','db','psql','-U','team','-d','postgres','-v','ON_ERROR_STOP=1','-c',
            "DO $$ BEGIN IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='training_reader') "
            "THEN CREATE ROLE training_reader NOLOGIN; END IF; END $$;")
    compose('exec','-T','db','pg_restore','-U','team','-d','postgres','--create',
            '--exit-on-error','/backup/olist6.dump')
    compose('run','--rm','--no-deps','filestore-restore')
    expected = json.loads((root/'expected-state.json').read_text())['counts']
    for table, count in expected.items():
        actual = compose('exec','-T','db','psql','-U','team','-d','olist6','-At','-c',
                         'SELECT count(*) FROM '+table+';',capture=True).stdout.strip()
        if int(actual) != count:
            raise RuntimeError('Restored record count differs: ' + table)
    (root/'.setup-restore-complete.json').write_text(json.dumps(
        {'database':'olist6','backup_sha256':SHA256,'counts_verified':expected},indent=2))
    print('Database and filestore restored; all 13 checked record counts match.')

def start_odoo(root):
    """Start the restored environment and check HTTP inside its Odoo container."""
    subprocess.run(['docker','compose','up','-d','db','odoo'],cwd=root,check=True)
    check_script = """import time, urllib.request
for attempt in range(90):
    try:
        with urllib.request.urlopen('http://127.0.0.1:8069/web/login?db=olist6', timeout=10) as response:
            page = response.read().decode('utf-8', errors='replace')
            if response.status != 200 or 'login' not in page.lower():
                raise RuntimeError('Unexpected Odoo login response')
        print('Odoo login page verified: HTTP 200')
        break
    except Exception:
        if attempt == 89:
            raise
        time.sleep(2)
"""
    subprocess.run(['docker','compose','exec','-T','odoo','python3','-c',check_script],
                   cwd=root,check=True)
    binding = subprocess.run(['docker','compose','port','odoo','8069'],cwd=root,
                             check=True,text=True,capture_output=True).stdout.strip().splitlines()[0]
    host, port = binding.rsplit(':',1)
    if host in ('0.0.0.0','[::]','::'): host='localhost'
    print(f'\nReady: http://{host}:{port}/web/login')
    print('Use your existing Odoo login. No replay or seeding workers were started.')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default=DEFAULT, help='Actual file sharing or download URL')
    parser.add_argument('--output', type=Path, default=Path(NAME))
    parser.add_argument('--directory', type=Path, default=Path.cwd(), help='Fresh destination; defaults to current directory')
    parser.add_argument('--download-only', action='store_true', help='Download without extracting or restoring')
    parser.add_argument('--prepare-only', action='store_true', help='Download and extract without restoring')
    args = parser.parse_args()
    if sys.version_info < (3, 8):
        raise RuntimeError('Python 3.8 or newer is required (including 3.10, 3.11 and 3.12).')
    root = args.directory.resolve()
    if (root/'.setup-restore-complete.json').exists():
        print('Setup already completed; database was not restored again.')
        if not (args.download_only or args.prepare_only):
            start_odoo(root)
        return
    if not (args.download_only or args.prepare_only):
        subprocess.run(['docker','compose','version'],check=True,stdout=subprocess.DEVNULL)
        subprocess.run(['docker','info'],check=True,stdout=subprocess.DEVNULL)
    download(args)
    if args.download_only:
        return
    extract(args.output.resolve(), root)
    if args.prepare_only:
        print('Files prepared only; database has not been restored.')
        return
    restore(root)
    start_odoo(root)

if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError, subprocess.CalledProcessError) as error:
        print(f'Error: {error}', file=sys.stderr)
        sys.exit(1)
