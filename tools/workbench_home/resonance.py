"""Explicit, bounded, read-only compatibility probe for a local Resonance service."""
import http.client
import json
import math


def check_session(port):
    if type(port) is not int or not 1 <= port <= 65535:
        raise ValueError('Enter a port number from 1 to 65535.')
    # Direct loopback only: no proxies, redirects, browser navigation or POSTs.
    for host in ('127.0.0.1', '::1'):
        connection = http.client.HTTPConnection(host, port, timeout=2)
        try:
            connection.request('GET', '/api/model', headers={'Accept': 'application/json'})
            response = connection.getresponse()
            if response.status != 200:
                raise ValueError('A local service answered, but its model response was not compatible. No Engine was started.')
            if response.getheader('Content-Type', '').split(';')[0].strip() != 'application/json':
                raise ValueError('The local service did not return a JSON model. No Engine was started.')
            raw = response.read(65537)
            if len(raw) > 65536:
                raise ValueError('The model response was too large. No Engine was started.')
            try:
                model = json.loads(raw)
                compatible = (
                    model['manifest']['version'] == '0.2.0'
                    and model['manifest']['philosophy'] == 'Adaptive resonance laboratory: folio models are provisional modules, not locked doctrine.'
                    and {s['id'] for s in model['defaultStates']} == set('ABCDEF')
                    and {'2r', '2v', '3r'} <= {s['id'] for s in model['folioLayers']}
                    and isinstance(model['presets'], dict)
                    and isinstance(model['memory'], dict)
                    and set(model['memory']) == set('ABCDEF')
                    and all(type(v) in (int, float) and math.isfinite(v) for v in model['memory'].values())
                )
            except (ValueError, TypeError, KeyError, OverflowError, RecursionError):
                compatible = False
            if not compatible:
                raise ValueError('A local service answered, but it did not match the supported Resonance model. No Engine was started.')
            return {'compatible': True, 'port': port, 'message':
                    f'Compatible Resonance service detected on port {port} (model 0.2.0). '
                    'Switch to its existing tab. No tab was opened or refreshed and no Engine was started. '
                    'This checks compatibility, not a unique session identity. Launch reminders remain unchanged.'}
        except ConnectionRefusedError:
            continue
        except (OSError, http.client.HTTPException):
            raise ValueError('The local service could not be checked. No Engine was started; keep any existing session open.') from None
        finally:
            connection.close()
    raise ValueError('No service answered on that local port. Check the Engine console; no Engine was started.')
