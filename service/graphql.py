from flask import Flask, request, Response, jsonify
from sesamutils import sesam_logger, VariablesConfig
from sesamutils.flask import serve
from data_access import DataAccess
from utils import stream_json
import sys

app = Flask(__name__)
logger = sesam_logger("GraphQL", app=app)

required_env_vars = ["baseurl",  "client_id", "client_secret", "grant_type", "resource", "token_url"]
optional_env_vars = ["LOG_LEVEL"]
config = VariablesConfig(required_env_vars, optional_env_vars=optional_env_vars)
if not config.validate():
    sys.exit(1)


data_access_layer = DataAccess(config)


@app.route("/<path:path>", methods=["POST"])
def get(path):

    query = request.get_json()
    entities = stream_json(data_access_layer.get_entities(path, query))
    logger.debug(entities)
# evt stream_json(entities) i response. fra utils-modulen til anders
    return Response(entities, mimetype='application/json')


if __name__ == '__main__':
    serve(app)
