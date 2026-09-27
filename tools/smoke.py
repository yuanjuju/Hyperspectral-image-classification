"""CPU functional smoke: synthetic MAT -> training CLI -> artifact -> real HTTP.

The synthetic labels are arbitrary. Accuracy is not a scientific result.
"""
import argparse
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import platform
import subprocess
import sys
import threading
import urllib.request

import numpy as np
import scipy.io as sio
import torch
from werkzeug.serving import make_server

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'HybridSN卷积模型（flask）'
sys.path.insert(0, str(SOURCE))
from predict import create_app
from src.pipeline import sha256


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    cube = np.random.default_rng(7).normal(size=(8, 8, 16)).astype(np.float32)
    labels = (np.arange(64).reshape(8, 8) % 3 + 1).astype(np.int64)
    sio.savemat(output / 'cube.mat', {'indian_pines_corrected': cube})
    sio.savemat(output / 'labels.mat', {'indian_pines_gt': labels})
    # Limit CPU threading in this smoke process only; training CLI accepts the environment unchanged.
    import os
    env = dict(os.environ, OMP_NUM_THREADS='2', OPENBLAS_NUM_THREADS='2', VECLIB_MAXIMUM_THREADS='2')
    command = [sys.executable, str(SOURCE / 'main.py'), '--cube', str(output / 'cube.mat'),
               '--labels', str(output / 'labels.mat'), '--output', str(output / 'model'),
               '--components', '13', '--window', '9', '--classes', '3', '--epochs', '2',
               '--batch-size', '16', '--test-ratio', '0.25', '--seed', '7', '--device', 'cpu']
    completed = subprocess.run(command, env=env, capture_output=True, text=True, timeout=180)
    (output / 'training.log').write_text(completed.stdout + completed.stderr)
    completed.check_returncode()
    torch.set_num_threads(2)
    server = make_server('127.0.0.1', 0, create_app(output / 'model', batch_size=19))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base = f'http://127.0.0.1:{server.server_port}'
        with urllib.request.urlopen(base + '/health', timeout=10) as response:
            health = json.load(response)
        boundary = 'hyperspectral-smoke-boundary'
        body = (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="cube.mat"\r\n'
                'Content-Type: application/octet-stream\r\n\r\n').encode()
        body += (output / 'cube.mat').read_bytes() + f'\r\n--{boundary}--\r\n'.encode()
        request = urllib.request.Request(base + '/api/upload', data=body,
                                         headers={'Content-Type': f'multipart/form-data; boundary={boundary}'})
        with urllib.request.urlopen(request, timeout=60) as response:
            status, predictions = response.status, json.load(response)
        assert status == 200 and health['status'] == 'ready'
        assert predictions['shape'] == [8, 8] and len(predictions['class_ids']) == 64
        assert set(predictions['class_ids']) <= {1, 2, 3}
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()
    (output / 'predictions.json').write_text(json.dumps(predictions, indent=2) + '\n')
    files = [SOURCE / 'main.py', SOURCE / 'predict.py', SOURCE / 'src/model.py',
             SOURCE / 'src/pipeline.py', ROOT / 'tools/smoke.py', ROOT / 'tests/test_pipeline.py',
             ROOT / 'requirements.txt', ROOT / 'requirements-dev.txt']
    result = {'verified_at_utc': datetime.now(timezone.utc).isoformat(),
              'scope': 'synthetic CPU functional verification; not an accuracy or throughput benchmark',
              'python': platform.python_version(), 'platform': platform.platform(),
              'torch': torch.__version__, 'numpy': np.__version__,
              'training_cli': 'passed', 'http_status': status, 'health': health,
              'prediction_shape': predictions['shape'], 'prediction_count': len(predictions['class_ids']),
              'source_sha256': {str(file.relative_to(ROOT)): sha256(file) for file in files}}
    (output / 'result.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
