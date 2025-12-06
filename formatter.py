import json


def format_print(data):
    def convert(o):
        if hasattr(o, "model_dump"):
            return o.model_dump()
        if isinstance(o, list):
            return [convert(i) for i in o]
        if isinstance(o, dict):
            return {k: convert(v) for k, v in o.items()}
        return o

    print(json.dumps(convert(data), indent=4))
