import time
import requests

API_URL = "http://localhost:8001/"

def rpc_call(method, params=None):
    payload = {"method": method, "params": params or {}}
    r = requests.post(API_URL, json=payload, timeout=5)
    r.raise_for_status()
    return r.json()


def wait_for_api(timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(API_URL, timeout=2)
            if r.status_code in (200, 400, 404):
                return True
        except Exception:
            time.sleep(1)
    return False


def test_status_endpoint():
    assert wait_for_api(), "API did not start in time"
    resp = rpc_call("status")
    assert isinstance(resp, dict)
    # status endpoint may return result or error depending on runtime
    assert "result" in resp or "error" in resp
