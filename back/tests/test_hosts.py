def test_hosts_auth(client):
    "Ensure we cannot make calls if not authenticated."
    r = client.get('/api/hosts/')
    assert r.status_code == 401, 'Invalid status code'

def test_hosts_port_scan(authenticated):
    "Ensure we can do a port scan."
    ports = [80, 443]
    r = authenticated.post('/api/hosts/port_scan/', json={'host': '127.0.0.1', 'ports': ports})
    assert r.status_code == 200, 'Invalid status code'
    assert r.json.get('host') == '127.0.0.1', 'Host missing from reply'
    assert 'ports' in r.json, 'Ports missing from reply'
    for port in ports:
        assert str(port) in r.json['ports'], f'Port {port} missing from reply'
