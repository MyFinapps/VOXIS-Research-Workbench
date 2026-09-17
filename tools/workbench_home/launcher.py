"""Local launch registry. No record storage, import, migration or replay."""
import copy
import hashlib
import json
import os
from pathlib import Path
import queue
import re
import subprocess
import sys
import tempfile
import threading
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

INSTRUMENTS = {
    'browser': ('Record Browser', 'Browse, inspect and export preserved originals.'),
    'bridge': ('Record Bridge', 'Import native captures and verify the index.'),
    'stem': ('Stem Lab', 'Explore stems, contact and movement.'),
    'wxr': ('WXR-003', 'Open the dual-folio spatial instrument.'),
    'resonance': ('Resonance Engine', 'Return to the local research engine.'),
}


def default_config():
    return Path(os.environ.get('LOCALAPPDATA', Path.home() / '.local' / 'share')) / 'VOXIS' / 'WorkbenchHome' / 'home.json'


def clean(value, limit=4096):
    if not isinstance(value, str) or len(value) > limit or any(ord(c) < 32 for c in value):
        raise ValueError('Use plain text without control characters.')
    return value.strip()


def file_hash(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest() if hasattr(hashlib, 'file_digest') else hashlib.sha256(handle.read()).hexdigest()


def validate_entry(key, data):
    if key not in INSTRUMENTS or not isinstance(data, dict):
        raise ValueError('Choose a listed instrument.')
    target = clean(data.get('target', '')).strip('"')
    version = clean(data.get('version', ''), 160)
    if not target:
        return {'target': '', 'version': version, 'sha256': ''}
    if key == 'wxr':
        u = urlsplit(target)
        if u.scheme != 'https' or not u.hostname or u.username or u.password or u.fragment or any(c.isspace() for c in target):
            raise ValueError('Use an HTTPS instrument URL without credentials or a session fragment.')
        return {'target': target, 'version': version, 'sha256': ''}
    p = Path(target)
    if not p.is_absolute():
        raise ValueError('Choose a full absolute file path.')
    if key in ('browser', 'bridge'):
        expected = 'browser.py' if key == 'browser' else 'bridge.py'
        wrapper = 'Start-Record-Browser.cmd' if key == 'browser' else 'Start-Record-Bridge.cmd'
        if p.name.lower() == wrapper.lower():
            p = p.with_name(expected)
        if p.name != expected:
            raise ValueError('Choose ' + expected + ' or ' + wrapper + ' from the installed instrument folder.')
    allowed = {'.html', '.htm'} if key == 'stem' else {'.py'} if key in ('browser', 'bridge') else {'.py', '.exe', '.cmd', '.bat', '.ps1'}
    if p.suffix.lower() not in allowed or not p.is_file():
        raise ValueError('That instrument file is missing or has an unsupported extension.')
    p = p.resolve()
    if key == 'resonance' and p.suffix.lower() in ('.cmd', '.bat') and re.search(r'[&|<>^%!"\r\n]', str(p)):
        raise ValueError('Batch launcher paths cannot contain shell metacharacters. Use a path without them.')
    return {'target': str(p.resolve()), 'version': version, 'sha256': file_hash(p)}


class ConfigLock:
    """One Home process per configuration, with an OS-released crash-safe lock."""
    def __init__(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = path.with_suffix('.lock').open('a+b')
        self.handle.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(self.handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            if os.fstat(self.handle.fileno()).st_size == 0:
                self.handle.write(b'0'); self.handle.flush()
        except OSError:
            self.handle.close()
            raise ValueError('Home is already open for this configuration. Return to that window or close it first.') from None

    def close(self):
        self.handle.close()


def command_for(key, entry):
    p = Path(entry['target'])
    if key == 'browser':
        return [sys.executable, '-u', str(p), '--no-open']
    if p.suffix.lower() == '.py':
        return [sys.executable, str(p)]
    if os.name != 'nt':
        raise ValueError('This launcher needs Windows. Python, HTML and HTTPS entries can be tested here.')
    if p.suffix.lower() == '.ps1':
        return [str(Path(os.environ['SystemRoot']) / 'System32/WindowsPowerShell/v1.0/powershell.exe'), '-NoProfile', '-File', str(p)]
    if p.suffix.lower() in ('.cmd', '.bat'):
        cmd = str(Path(os.environ['SystemRoot']) / 'System32/cmd.exe')
        return '"' + cmd + '" /d /s /c ""' + str(p) + '""'
    return [str(p)]


class LaunchRegistry:
    def __init__(self, config):
        self.path = Path(config).resolve()
        self.lock = threading.RLock()
        self.processes = {}
        self.urls = {}  # Session URLs never go into configuration or logs.
        self.errors = {}
        self.data = {'schema': 1, 'entries': {}, 'pending': []}
        if self.path.exists():
            if self.path.stat().st_size > 65536:
                raise ValueError('Home configuration is too large. Preserve it and restore a known-good copy.')
            d = json.loads(self.path.read_text('utf-8'))
            if (not isinstance(d, dict) or d.get('schema') != 1 or not isinstance(d.get('entries'), dict)
                    or not isinstance(d.get('pending'), list) or set(d['entries']) - INSTRUMENTS.keys()
                    or any(k not in INSTRUMENTS for k in d['pending'])):
                raise ValueError('Unsupported Home configuration. Preserve it and restore a known-good copy.')
            for e in d['entries'].values():
                if not isinstance(e, dict) or any(not isinstance(e.get(f), str) for f in ('target', 'version', 'sha256')):
                    raise ValueError('Invalid Home configuration; no repair was attempted.')
            self.data = d

    def save(self, data):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, name = tempfile.mkstemp(prefix='.home-', dir=self.path.parent)
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=True, allow_nan=False)
                f.write('\n'); f.flush(); os.fsync(f.fileno())
            os.replace(name, self.path)
            self.data = data
        finally:
            if os.path.exists(name):
                os.unlink(name)

    def update(self, key, values):
        entry = validate_entry(key, values)
        with self.lock:
            if key in self.data['pending']:
                raise ValueError('Close the existing instrument and clear its launch reminder before changing its location.')
            d = copy.deepcopy(self.data); d['entries'][key] = entry
            self.save(d); self.errors.pop(key, None)
        return entry

    def poll(self):
        for key, process in list(self.processes.items()):
            code = process.poll()
            if code is None:
                continue
            del self.processes[key]; self.urls.pop(key, None)
            # Resonance may be a wrapper that leaves child processes running.
            # Bridge is launched directly as bridge.py; Q ends the owned process.
            if key == 'resonance':
                self.errors[key] = f'Launcher exited ({code}). Check the instrument before clearing its reminder.'
                continue
            d = copy.deepcopy(self.data)
            if key in d['pending']:
                d['pending'].remove(key); self.save(d)
            self.errors.pop(key, None)
            if code:
                self.errors[key] = f'{INSTRUMENTS[key][0]} exited ({code}). Check its files and Python installation.'

    def snapshot(self):
        with self.lock:
            self.poll(); rows = []
            for key, (title, purpose) in INSTRUMENTS.items():
                entry = self.data['entries'].get(key, {'target': '', 'version': '', 'sha256': ''})
                state, detail = 'setup', 'Needs setup'
                if entry['target']:
                    state, detail = 'configured', 'Configured'
                    if key != 'wxr':
                        p = Path(entry['target'])
                        try:
                            if not p.is_file():
                                state, detail = 'missing', 'File missing'
                            elif file_hash(p) != entry['sha256']:
                                state, detail = 'changed', 'File changed — configure again'
                        except OSError:
                            state, detail = 'missing', 'File unavailable'
                if key in self.data['pending']:
                    state, detail = ('running', 'Running') if key in self.processes else ('unconfirmed', 'Check existing session')
                rows.append({'id': key, 'title': title, 'purpose': purpose, **entry,
                             'state': state, 'detail': detail, 'error': self.errors.get(key, ''),
                             'can_open': state == 'configured' or key == 'browser' and state == 'running' and key in self.urls,
                             'can_clear': state == 'unconfirmed',
                             'verification': 'Home integration not yet verified on The Forge'})
            return {'version': '0.1.0', 'config_path': str(self.path), 'instruments': rows}

    def clear_reminder(self, key, confirmed):
        with self.lock:
            self.poll()
            if key not in INSTRUMENTS or confirmed is not True:
                raise ValueError('Confirm that you closed the instrument first.')
            if key in self.processes:
                raise ValueError('The launcher is still running. Close the instrument and its launcher first.')
            d = copy.deepcopy(self.data)
            d['pending'] = [k for k in d['pending'] if k != key]
            self.save(d); self.errors.pop(key, None)

    def launch(self, key):
        with self.lock:
            self.poll()
            if key not in INSTRUMENTS:
                raise ValueError('Choose a listed instrument.')
            if key in self.data['pending']:
                if key == 'browser' and key in self.urls and key in self.processes:
                    return {'url': self.urls[key], 'message': 'Returning to the existing Browser session.'}
                raise ValueError('A previous launch may still be open. Close it before clearing its launch reminder.')
            entry = self.data['entries'].get(key, {})
            checked = validate_entry(key, entry)
            if not checked['target']:
                raise ValueError('Configure this instrument first.')
            if checked != entry:
                raise ValueError('The entry file changed. Inspect the new build and save its configuration again.')
            if key == 'wxr':
                return {'url': checked['target'], 'message': 'Opening WXR-003. Use its HTTPS address on Quest; this is not Quest verification.'}
            if key == 'stem':
                return {'url': Path(checked['target']).as_uri(), 'message': 'Opening Stem Lab in the default browser.'}
            cmd = command_for(key, checked)
            d = copy.deepcopy(self.data); d['pending'].append(key); self.save(d)
            kwargs = {'cwd': str(Path(checked['target']).parent), 'shell': False}
            if key == 'browser':
                kwargs.update(stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
                if os.name == 'nt':
                    kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            elif os.name == 'nt':
                kwargs['creationflags'] = subprocess.CREATE_NEW_CONSOLE
            try:
                process = subprocess.Popen(cmd, **kwargs)
            except OSError:
                d['pending'].remove(key); self.save(d)
                raise ValueError('Launch failed. Check the configured file, permissions and required interpreter.') from None
            self.processes[key] = process
            if key != 'browser':
                return {'message': 'Launcher started. Check its window; startup does not establish instrument readiness.'}
            lines = queue.Queue()
            def drain():
                try:
                    while True:
                        line = process.stdout.readline(4096)
                        if not line:
                            break
                        match = re.fullmatch(rb'Open this local session: (http://127\.0\.0\.1:[0-9]+/#[A-Za-z0-9_-]+)\r?\n', line)
                        if match:
                            lines.put(match[1].decode('ascii'))
                finally:
                    process.stdout.close()
            threading.Thread(target=drain, daemon=True).start()
            try:
                url = lines.get(timeout=8)
                u = urlsplit(url)
                request = Request(url.split('#')[0] + 'api/info', headers={'X-VOXIS-Token': u.fragment})
                with urlopen(request, timeout=3) as response:
                    info = json.load(response)
                if not isinstance(info, dict) or info.get('version') != '0.1.0':
                    raise ValueError('Unexpected Browser version.')
                self.urls[key] = url
                return {'url': url, 'message': 'Browser ready. Opening its local session.'}
            except (queue.Empty, OSError, ValueError):
                # Do not kill a process just because its readiness probe failed.
                self.errors[key] = 'Browser readiness was not confirmed. Check the instrument before retrying.'
                raise ValueError(self.errors[key]) from None
