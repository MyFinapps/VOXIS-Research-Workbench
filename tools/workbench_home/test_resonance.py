"""Real loopback HTTP fixtures; no installed Engine or research data is used."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading
import unittest
from resonance import check_session


class ProbeTests(unittest.TestCase):
    def setUp(self):
        self.model = {'manifest': {'version': '0.2.0', 'philosophy':
            'Adaptive resonance laboratory: folio models are provisional modules, not locked doctrine.'},
            'defaultStates': [{'id': s} for s in 'ABCDEF'],
            'folioLayers': [{'id': s} for s in ('2r', '2v', '3r')],
            'presets': {}, 'memory': {s: 0.123 for s in 'ABCDEF'}}
        self.body = json.dumps(self.model).encode(); self.status = 200
        self.content_type = 'application/json'; self.requests = []
        fixture = self
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                fixture.requests.append((self.command, self.path))
                self.send_response(fixture.status)
                self.send_header('Content-Type', fixture.content_type)
                self.send_header('Location', '/must-not-follow')
                self.send_header('Content-Length', str(len(fixture.body)))
                self.end_headers(); self.wfile.write(fixture.body)
            def log_message(self, *args): pass
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start(); self.addCleanup(self.close)
    def close(self):
        self.server.shutdown(); self.server.server_close(); self.thread.join()
    def probe(self): return check_session(self.server.server_port)
    def test_compatible_read_only(self):
        before = self.body
        self.assertTrue(self.probe()['compatible'])
        self.assertEqual(self.requests, [('GET', '/api/model')])
        self.assertEqual(before, self.body)
    def test_unrelated_or_malformed_response(self):
        for body in (b'{}', b'not json', b'[]', b'null'):
            self.body = body
            with self.assertRaises(ValueError): self.probe()
    def test_redirect_not_followed(self):
        self.status = 302
        with self.assertRaises(ValueError): self.probe()
        self.assertEqual(self.requests, [('GET', '/api/model')])
    def test_response_bound_and_content_type(self):
        self.body = b' ' * 65537
        with self.assertRaisesRegex(ValueError, 'large'): self.probe()
        self.body = b'{}'; self.content_type = 'text/html'
        with self.assertRaisesRegex(ValueError, 'JSON'): self.probe()
    def test_malformed_memory_rejected(self):
        for memory in (list('ABCDEF'), {s: float('nan') for s in 'ABCDEF'}):
            self.model['memory'] = memory; self.body = json.dumps(self.model).encode()
            with self.assertRaises(ValueError): self.probe()
    def test_invalid_ports_make_no_request(self):
        for port in (True, 0, 65536, '3030', None):
            with self.assertRaises(ValueError): check_session(port)
        self.assertEqual(self.requests, [])


if __name__ == '__main__': unittest.main()
