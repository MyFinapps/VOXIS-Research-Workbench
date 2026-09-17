#!/usr/bin/env python3
"""VOXIS Home: local configuration and explicit instrument launches."""
import argparse
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import secrets
import sys
import threading
import webbrowser
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'record_bridge'))
from browser import Handler as ProtectedHandler
from launcher import ConfigLock, LaunchRegistry, default_config

WEB = Path(__file__).with_name('web')
ASSETS = {'/': ('index.html', 'text/html'), '/app.js': ('app.js', 'text/javascript'),
          '/style.css': ('style.css', 'text/css')}


class HomeServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = False

    def __init__(self, config, port=0):
        self.config_lock = ConfigLock(Path(config).resolve())
        try:
            self.registry = LaunchRegistry(config)
            self.token = secrets.token_urlsafe(32)
            super().__init__(('127.0.0.1', port), Handler)
            self.origin = f'http://127.0.0.1:{self.server_port}'
        except BaseException:
            self.config_lock.close()
            raise

    @property
    def launch_url(self):
        return self.origin + '/#' + self.token

    def server_close(self):
        super().server_close()
        self.config_lock.close()


class Handler(ProtectedHandler):
    def do_GET(self):
        path = urlsplit(self.path).path
        if not self.authorized(path.startswith('/api/')):
            self.send_payload(403, {'error': 'Home session unavailable. Reopen Home with its launcher.'}); return
        try:
            if path in ASSETS:
                file, mime = ASSETS[path]
                self.send_payload(200, (WEB / file).read_bytes(), mime)
            elif path == '/api/state':
                self.send_payload(200, self.server.registry.snapshot())
            elif path == '/favicon.ico':
                self.send_payload(204, b'', 'image/x-icon')
            else:
                self.send_payload(404, {'error': 'Not found'})
        except (ValueError, OSError, TypeError, KeyError) as e:
            self.send_payload(422, {'error': str(e)})

    def do_POST(self):
        if not self.authorized(True):
            self.send_payload(403, {'error': 'Home session unavailable. Reopen Home with its launcher.'}); return
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if self.headers.get('Content-Type') != 'application/json' or not 0 < size <= 16384:
                raise ValueError('Expected a small JSON request.')
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict):
                raise ValueError('Expected an object.')
            key = data.get('id')
            if not isinstance(key, str) and self.path != '/api/stop':
                raise ValueError('Choose a listed instrument.')
            if self.path == '/api/configure':
                result = self.server.registry.update(key, data.get('entry'))
            elif self.path == '/api/launch':
                result = self.server.registry.launch(key)
                if key == 'stem':
                    opened = webbrowser.open(result.pop('url'))
                    result['message'] = 'Sent Stem Lab to the default browser.' if opened else 'Automatic opening failed. Open the configured HTML file directly.'
            elif self.path == '/api/clear':
                self.server.registry.clear_reminder(key, data.get('confirmed'))
                result = {'message': 'Launch reminder cleared. No process was stopped.'}
            elif self.path == '/api/stop':
                result = {'message': 'Home closed. Stop each instrument in its own window.'}
                self.send_payload(200, result)
                threading.Thread(target=self.server.shutdown, daemon=True).start(); return
            else:
                self.send_payload(404, {'error': 'Not found'}); return
            self.send_payload(200, result)
        except (ValueError, OSError, TypeError, KeyError, RecursionError) as e:
            self.send_payload(422, {'error': str(e)})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=default_config())
    parser.add_argument('--port', type=int, default=0)
    parser.add_argument('--no-open', action='store_true')
    args = parser.parse_args()
    try:
        with HomeServer(args.config, args.port) as server:
            print('VOXIS Workbench Home 0.1.0', flush=True)
            print('Open this local session: ' + server.launch_url, flush=True)
            if not args.no_open:
                webbrowser.open(server.launch_url)
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass
    except (ValueError, OSError) as e:
        print('Home could not start: ' + str(e), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
