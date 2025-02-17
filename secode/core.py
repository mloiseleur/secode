import base64

from ruamel.yaml import RoundTripDumper, YAML, dump_all


def encode_file(file_path, decode=False):
    with open(file_path, 'r') as stream:
        payload = _parse_yaml(stream.read())
    return encode_payload(payload, decode)


def encode_stream(stream, decode=False):
    lines = [line for line in stream]
    payload = ''.join(lines)
    payload = _parse_yaml(payload)
    return encode_payload(payload, decode)


def encode_payload(payload, decode=False):
    encoder = base64_decode if decode else base64_encode
    encoded_payload = []
    for document in payload:
        encoded_payload.append(_encode(document, encoder))
    return dump_all(encoded_payload, Dumper=RoundTripDumper)


def _parse_yaml(payload):
    yaml = YAML()
    docs = yaml.load_all(payload)
    return docs


def _encode(payload, encoder):
    if 'items' in payload:
        for i, item in enumerate(payload['items']):
            payload['items'][i] = _encode(item, encoder)
    elif payload.get('kind') == 'Secret':
        if payload.get('stringData'):
            for key in payload.get('stringData'):
                payload['stringData'][key] = encoder(payload['stringData'][key])
        if payload.get('data'):
            for key in payload.get('data'):
                payload['data'][key] = encoder(payload['data'][key])
    else:
        raise ValueError('Invalid K8S Secret file format')
    return payload


# Utils

def base64_encode(value):
    payload = bytes(str(value).encode())
    return base64.b64encode(payload).decode('utf-8')


def base64_decode(payload):
    value = base64.b64decode(payload).decode('utf-8')
    return _downcast(value)


def _downcast(value):
    if value.isnumeric():
        return int(value)
    try:
        return float(value)
    except:
        pass
    return value
