"""Home contract checks. All configuration and captures are disposable fixtures."""
import http.client
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

import home
from launcher import LaunchRegistry, ConfigLock, validate_entry, command_for

BRIDGE = Path(__file__).resolve().parents[1] / 'record_bridge'
sys.path.insert(0, str(BRIDGE))
import store
from test_bridge import wxr_fixture, stem_fixture, raw


class HomeTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name); self.config = self.root / 'private' / 'home.json'
        self.registry = LaunchRegistry(self.config)

    def entry(self, key, path):
        return self.registry.update(key, {'target': str(path), 'version': 'fixture'})

    def test_first_visit_creates_no_config_or_index(self):
        self.assertTrue(all(r['state']=='setup' for r in self.registry.snapshot()['instruments']))
        self.assertFalse(self.config.exists())
        self.assertEqual(list(self.root.iterdir()), [])

    def test_persistence_and_entry_identity_change(self):
        p=self.root/'Stem Lab.html'; p.write_text('<h1>synthetic</h1>')
        self.entry('stem',p)
        second=LaunchRegistry(self.config)
        self.assertEqual(second.data,self.registry.data)
        self.assertEqual(second.launch('stem')['url'],p.as_uri())
        p.write_text('changed')
        with self.assertRaisesRegex(ValueError,'changed'):
            second.launch('stem')
        self.assertEqual(second.snapshot()['instruments'][2]['state'],'changed')
        p.unlink()
        self.assertEqual(second.snapshot()['instruments'][2]['state'],'missing')

    def test_url_and_launch_input_validation(self):
        for target in ['http://example.test/','javascript:alert(1)','https://user:secret@example.test/','https://example.test/#secret','https://example.test/a\n']:
            with self.assertRaises(ValueError):
                validate_entry('wxr',{'target':target})
        self.entry('wxr','https://example.test/wxr-003/')
        self.assertEqual(self.registry.launch('wxr')['url'],'https://example.test/wxr-003/')
        for key in ['shell','__import__',None]:
            with self.assertRaises(ValueError):
                self.registry.launch(key)
        with self.assertRaises(ValueError):
            self.entry('stem','relative.html')

    def test_corrupt_config_not_repaired_or_overwritten(self):
        self.config.parent.mkdir(); self.config.write_bytes(b'{broken')
        before=self.config.read_bytes()
        with self.assertRaises(ValueError):LaunchRegistry(self.config)
        self.assertEqual(before,self.config.read_bytes())

    def test_save_failure_leaves_previous_config_and_memory(self):
        self.entry('wxr','https://example.test/one')
        before=self.config.read_bytes(); old=self.registry.data
        with patch('launcher.os.replace',side_effect=PermissionError('denied')):
            with self.assertRaises(PermissionError):self.entry('wxr','https://example.test/two')
        self.assertEqual(before,self.config.read_bytes());self.assertEqual(old,self.registry.data)

    def test_one_home_per_config_and_lock_release(self):
        first=ConfigLock(self.config)
        try:
            with self.assertRaises(ValueError):ConfigLock(self.config)
        finally:first.close()
        ConfigLock(self.config).close()

    def test_restart_requires_explicit_closed_confirmation(self):
        self.entry('resonance',self._script('worker.py','import time; time.sleep(60)'))
        self.registry.launch('resonance');process=self.registry.processes['resonance']
        try:
            second=LaunchRegistry(self.config)
            self.assertEqual(second.snapshot()['instruments'][4]['state'],'unconfirmed')
            with self.assertRaises(ValueError):second.launch('resonance')
            with self.assertRaises(ValueError):self.registry.clear_reminder('resonance',True)
            with self.assertRaises(ValueError):second.clear_reminder('resonance',False)
        finally:process.terminate();process.wait(timeout=5)
        second.clear_reminder('resonance',True)
        self.assertEqual(second.snapshot()['instruments'][4]['state'],'configured')

    def _script(self,name,code):
        p=self.root/name;p.write_text(code);return p

    def test_exited_wrapper_keeps_reminder_and_failure_message(self):
        self.entry('resonance',self._script('failure.py','raise SystemExit(7)'))
        self.registry.launch('resonance')
        self.registry.processes['resonance'].wait(timeout=5)
        row=self.registry.snapshot()['instruments'][4]
        self.assertEqual(row['state'],'unconfirmed')
        self.assertIn('(7)',row['error'])
        with self.assertRaises(ValueError):self.registry.launch('resonance')

    def test_settings_backup_restore_uses_disposable_copy(self):
        self.entry('wxr','https://example.test/original')
        backup=self.root/'backup.json';backup.write_bytes(self.config.read_bytes())
        self.entry('wxr','https://example.test/new')
        preserved=self.root/'before-restore.json';preserved.write_bytes(self.config.read_bytes())
        self.config.write_bytes(backup.read_bytes())
        restored=LaunchRegistry(self.config)
        self.assertEqual(restored.launch('wxr')['url'],'https://example.test/original')
        self.assertEqual(json.loads(preserved.read_text())['entries']['wxr']['target'],'https://example.test/new')

    def test_launch_failure_can_retry_without_silent_pending(self):
        self.entry('resonance',self._script('worker.py','pass'))
        with patch('launcher.subprocess.Popen',side_effect=OSError('no')):
            with self.assertRaises(ValueError):self.registry.launch('resonance')
        self.assertEqual(self.registry.data['pending'],[])

    def test_windows_command_shapes_and_metacharacters(self):
        p=self._script('start engine.cmd','@echo off')
        e=validate_entry('resonance',{'target':str(p)})
        with patch('launcher.os.name','nt'),patch.dict(os.environ,{'SystemRoot':'C:\\Windows'}):
            # Path uses host-native implementation already chosen by pathlib.
            with patch('launcher.Path',type(p)):
                cmd=command_for('resonance',e)
                self.assertIn('/d /s /c',cmd);self.assertIn(str(p),cmd)
        p=self._script('bad&name.cmd','@echo off')
        with self.assertRaisesRegex(ValueError,'metacharacters'):
            validate_entry('resonance',{'target':str(p)})

    def test_browser_launch_real_handoff_export_and_shutdown_preserve_index(self):
        # Copy the unchanged Browser into a path containing spaces; no real user index.
        folder=self.root/'Browser instrument';shutil.copytree(BRIDGE,folder,ignore=shutil.ignore_patterns('__pycache__'))
        appdata=self.root/'profile';index=appdata/'VOXIS'/'RecordBridge'/'index.sqlite'
        ids=[]
        for n,data in enumerate([wxr_fixture(),stem_fixture()]):
            source=self.root/f'capture-{n}.json';source.write_bytes(raw(data));ids.append(store.ingest(index,source)['id'])
        before=index.read_bytes()
        self.entry('browser',folder/'Start-Record-Browser.cmd')
        with patch.dict(os.environ,{'LOCALAPPDATA':str(appdata)}):
            result=self.registry.launch('browser')
        process=self.registry.processes['browser']
        try:
            self.assertEqual(self.registry.launch('browser')['url'],result['url'])
            u=urlsplit(result['url']);base=f'{u.scheme}://{u.netloc}'
            def request(route,body=None):
                headers={'X-VOXIS-Token':u.fragment}
                if body is not None:headers['Content-Type']='application/json'
                req=Request(base+route,headers=headers,data=None if body is None else json.dumps(body).encode())
                with urlopen(req,timeout=5) as r:return json.load(r)
            self.assertEqual(len(request('/api/records')['records']),2)
            for n,rid in enumerate(ids):
                self.assertEqual(request('/api/record?id='+rid)['record']['id'],rid)
                target=self.root/f'export-{n}.json';request('/api/export',{'id':rid,'path':str(target)})
                self.assertEqual(target.read_bytes(),(self.root/f'capture-{n}.json').read_bytes())
            self.assertNotIn(u.fragment,self.config.read_text())
            self.assertEqual(index.read_bytes(),before)
            request('/api/stop',{});process.wait(timeout=5)
            self.registry.poll();self.assertNotIn('browser',self.registry.data['pending'])
        finally:
            if process.poll() is None:process.terminate();process.wait(timeout=5)


class HomeAPITests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup)
        self.root=Path(tmp.name);self.server=home.HomeServer(self.root/'home.json')
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.addCleanup(self.stop)
    def stop(self):
        self.server.shutdown();self.server.server_close();self.thread.join(timeout=3)
    def request(self,path,body=None,headers=None,authenticated=True):
        h={'X-VOXIS-Token':self.server.token} if authenticated else {}
        if body is not None:h['Content-Type']='application/json'
        h.update(headers or {})
        c=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=5)
        try:
            c.request('GET' if body is None else 'POST',path,body=None if body is None else json.dumps(body),headers=h)
            r=c.getresponse();return r.status,r.read()
        finally:c.close()
    def test_protected_routes_and_inert_fixed_assets(self):
        for route in ['/api/state','/api/configure','/api/launch','/api/clear','/api/stop']:
            body=None if route=='/api/state' else {}
            for h,auth in [({},False),({'Origin':'https://foreign.test'},True),({'Host':'foreign.test'},True),({'Sec-Fetch-Site':'cross-site'},True)]:
                self.assertEqual(self.request(route,body,h,auth)[0],403)
        self.assertEqual(self.request('/',authenticated=False)[0],200)
        self.assertEqual(self.request('/../launcher.py')[0],404)
        self.assertEqual(self.request('/api/launch',{'id':['browser']})[0],422)
        self.assertFalse((self.root/'home.json').exists())
    def test_configure_and_reload_state(self):
        self.assertEqual(self.request('/api/configure',{'id':'wxr','entry':{'target':'https://example.test/wxr'}})[0],200)
        code,data=self.request('/api/state');self.assertEqual(code,200)
        self.assertEqual(json.loads(data)['instruments'][3]['state'],'configured')
    def test_port_conflict_is_actionable_and_releases_lock(self):
        with self.assertRaises(OSError):home.HomeServer(self.root/'other.json',self.server.server_port)
        other=home.HomeServer(self.root/'other.json');other.server_close()
    def test_stop_home_does_not_stop_owned_instrument(self):
        p=self.root/'worker.py';p.write_text('import time; time.sleep(60)')
        self.server.registry.update('resonance',{'target':str(p)})
        self.server.registry.launch('resonance');process=self.server.registry.processes['resonance']
        try:
            self.assertEqual(self.request('/api/stop',{})[0],200)
            self.thread.join(timeout=3)
            self.assertIsNone(process.poll())
        finally:process.terminate();process.wait(timeout=5)


if __name__=='__main__':unittest.main()
