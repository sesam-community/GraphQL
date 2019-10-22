import json


def stream_json(entities):
    first = True
    yield '['
    for i, row in enumerate(entities):
        if not first:
            yield ','
        else:
            first = False
        yield json.dumps(row)
    yield ']'
