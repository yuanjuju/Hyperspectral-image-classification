"""Serve a versioned HybridSN artifact through the existing upload endpoint."""
import argparse
import io
import json
from pathlib import Path
import threading

from flask import Flask, Response, jsonify, request
from flask_cors import CORS
import scipy.io as sio
from werkzeug.exceptions import RequestEntityTooLarge
from src.pipeline import Predictor


def create_app(artifact_dir, *, data_key='indian_pines_corrected', batch_size=128,
               max_upload_mb=10, max_pixels=250_000):
    if max_upload_mb < 1:
        raise ValueError('Upload limit must be positive')
    predictor = Predictor(artifact_dir, batch_size=batch_size, max_pixels=max_pixels)
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = max_upload_mb * 1024 * 1024
    CORS(app)
    inference_lock = threading.Lock()  # Keep memory bounded to one inference request per process.

    @app.get('/health')
    def health():
        return jsonify(status='ready', architecture=predictor.manifest['architecture'],
                       schema_version=predictor.manifest['schema_version'])

    @app.errorhandler(RequestEntityTooLarge)
    def upload_too_large(_error):
        return jsonify(error='Upload exceeds configured size limit'), 413

    @app.post('/api/upload')
    def predict_api():
        file = request.files.get('file')
        if file is None or not file.filename:
            return jsonify(error='Provide a non-empty multipart file field'), 400
        if not inference_lock.acquire(blocking=False):
            return jsonify(error='Inference is busy; retry after the current request'), 503
        try:
            try:
                data = sio.loadmat(io.BytesIO(file.read()))
            except (ValueError, TypeError, OSError, IndexError, NotImplementedError):
                return jsonify(error='Expected a readable MAT file (v7.3/HDF5 is not supported)'), 400
            if data_key not in data:
                return jsonify(error=f'MAT key is missing: {data_key}'), 400
            result = predictor.predict(data[data_key])
            return Response(json.dumps(result, ensure_ascii=False), mimetype='application/json')
        except ValueError as error:
            return jsonify(error=str(error)), 400
        finally:
            inference_lock.release()

    return app


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifact', type=Path, required=True)
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=5000)
    parser.add_argument('--data-key', default='indian_pines_corrected')
    parser.add_argument('--batch-size', type=int, default=128)
    parser.add_argument('--max-upload-mb', type=int, default=10)
    parser.add_argument('--max-pixels', type=int, default=250_000)
    args = parser.parse_args()
    app = create_app(args.artifact, data_key=args.data_key, batch_size=args.batch_size,
                     max_upload_mb=args.max_upload_mb, max_pixels=args.max_pixels)
    app.run(host=args.host, port=args.port)


if __name__ == '__main__':
    main()
