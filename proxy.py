# proxy.py (modifié)
from flask import Flask, request, Response
import requests

app = Flask(__name__)
API_BASE = "http://127.0.0.1:40631"

@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def proxy(path):
    if request.method == 'OPTIONS':
        # Répondre directement au preflight
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, PATCH, OPTIONS',
            'Access-Control-Allow-Headers': '*'
        }
        return Response('', 200, headers)

    url = f"{API_BASE}/{path}"

    resp = requests.request(
        method=request.method,
        url=url,
        headers={key: value for key, value in request.headers if key != 'Host'},
        data=request.get_data(),
        params=request.args
    )

    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for name, value in resp.raw.headers.items() if name.lower() not in excluded_headers]
    headers.append(('Access-Control-Allow-Origin', '*'))
    headers.append(('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, PATCH, OPTIONS'))
    headers.append(('Access-Control-Allow-Headers', '*'))

    return Response(resp.content, resp.status_code, headers)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5555, debug=True)