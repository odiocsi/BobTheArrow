from flask import Flask, request, abort, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per minute"]
)
limiter.init_app(app)

servers = {}

@app.route("/gameserver/update", methods=['POST'])
@limiter.limit("10 per minute")
def set_count():
    server_id = request.args.get('server_id')
    server_name = request.args.get('server_name')
    max_players = request.args.get('max_players')
    current_players = request.args.get('current_players')
    image = request.args.get('image')

    if server_id is None:
        return "Missing server id", 400

    if max_players is None:
        return "Missing max players", 400

    if current_players is None:
        return "Missing current players", 400

    if image is None:
        return "Missing image link", 400

    if server_id not in servers:
        servers[server_id] = {"name": "n/a", "max": 0, "current": 0, "img": "n/a"}

    try:
        servers[server_id]["name"] = server_name
        servers[server_id]["max"] = int(max_players)
        servers[server_id]["current"] = int(current_players)
    except (TypeError, ValueError):
        servers[server_id] = {"name": "n/a", "max": 0, "current": 0, "img": "n/a"}
        return "Max players and current players must be numbers", 400

    servers[server_id]["img"] = image

    return "success"

@app.route("/gameserver/get", methods=['GET'])
def get_servers():
    if request.remote_addr != '127.0.0.1':
        abort(403)

    server_id = request.args.get('server_id')
    if server_id is None:
        return "Missing server id", 400

    return jsonify(servers[str(server_id)])

if __name__ == "__main__":
    app.run(debug=False)