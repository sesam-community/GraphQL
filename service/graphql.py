from flask import Flask, request, Response, jsonify
from sesamutils import sesam_logger, VariablesConfig
from sesamutils.flask import serve
from data_access import DataAccess
from utils import stream_json
import sys
import os

app = Flask(__name__)

required_env_vars = ["baseurl",  "client_id", "client_secret", "grant_type", "resource", "token_url"]
optional_env_vars = ["LOG_LEVEL"]
config = VariablesConfig(required_env_vars, optional_env_vars=optional_env_vars)
if not config.validate():
    sys.exit(1)

if hasattr(config, "LOG_LEVEL") and config.LOG_LEVEL == "DEBUG":
    logger = sesam_logger("GraphQL", app=app)
else:
    logger = sesam_logger("GraphQL")

data_access_layer = DataAccess(config)


@app.route("/<path:path>", methods=["GET"])
def get(path):

    url = path
    query = request.args["query"]
    logger.debug("url from path: " + str(url))
    logger.debug("query from request.args: " + str(query))

    entities = stream_json(data_access_layer.get_entities(url, query))
    return Response(entities, mimetype='application/json')


if __name__ == '__main__':
    serve(app)
