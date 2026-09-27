import io
import json
from unittest.mock import patch

import numpy as np
import pytest
import scipy.io as sio
from sklearn.decomposition import PCA
import torch

from main import train_model
from predict import create_app
from src.pipeline import ModelConfig, Predictor, SpectralTransform, validate_cube


torch.set_num_threads(2)


@pytest.fixture(scope='module')
def trained(tmp_path_factory):
    cube = np.random.default_rng(7).normal(size=(8, 8, 16)).astype(np.float32)
    labels = (np.arange(64).reshape(8, 8) % 3 + 1).astype(np.int64)
    directory = tmp_path_factory.mktemp('run') / 'bundle'
    modes = []
    original = torch.nn.Dropout.forward
    def observe(module, inputs):
        modes.append(module.training)
        return original(module, inputs)
    with patch.object(torch.nn.Dropout, 'forward', observe):
        manifest = train_model(cube, labels, directory,
                               config=ModelConfig(16, 13, 9, 3), epochs=2,
                               batch_size=16, test_ratio=0.25, seed=7)
    return directory, cube, manifest, modes


def mat(cube, key='indian_pines_corrected'):
    stream = io.BytesIO()
    sio.savemat(stream, {key: cube})
    stream.seek(0)
    return stream


def test_training_restores_dropout_each_epoch(trained):
    _, _, manifest, modes = trained
    train_segments = sum(value and (index == 0 or not modes[index-1]) for index, value in enumerate(modes))
    assert train_segments == 2
    assert len(manifest['training']['history']) == 2
    assert manifest['training']['train_samples'] == 48
    assert manifest['training']['test_samples'] == 16
    assert manifest['training']['pca_fit_scope'] == 'training pixel centers only'


def test_frozen_pca_matches_reference_and_roundtrips(tmp_path):
    rng = np.random.default_rng(17)
    training, unseen = rng.normal(size=(48, 16)), rng.normal(size=(4, 5, 16)) + 3
    frozen = SpectralTransform.fit(training, 13)
    reference = PCA(n_components=13, whiten=True, svd_solver='full').fit(training)
    expected = reference.transform(unseen.reshape(-1, 16)).reshape(4, 5, 13)
    np.testing.assert_allclose(frozen.transform(unseen), expected, atol=2e-5)
    frozen.save(tmp_path/'pca.npz')
    np.testing.assert_array_equal(SpectralTransform.load(tmp_path/'pca.npz').transform(unseen), frozen.transform(unseen))


def test_batch_inference_matches_single_patch_without_labels(trained):
    directory, cube, _, _ = trained
    one = Predictor(directory, batch_size=1).predict(cube)
    many = Predictor(directory, batch_size=19).predict(cube)
    assert one == many
    assert len(one['class_ids']) == 64 and one['shape'] == [8, 8]
    assert set(one['class_ids']) <= {1, 2, 3}


def test_artifact_rejects_tampered_weights(trained, tmp_path):
    import shutil
    directory, *_ = trained
    target = tmp_path/'corrupt'
    shutil.copytree(directory, target)
    with (target/'weights.pt').open('ab') as f:
        f.write(b'corrupt')
    with pytest.raises(ValueError, match='checksum'):
        Predictor(target)


def test_existing_artifact_is_not_overwritten(trained):
    directory, cube, *_ = trained
    from src.pipeline import save_artifact
    predictor = Predictor(directory)
    before = (directory/'manifest.json').read_bytes()
    with pytest.raises(FileExistsError):
        save_artifact(directory, predictor.model, predictor.transform, predictor.config, {})
    assert (directory/'manifest.json').read_bytes() == before


@pytest.mark.parametrize('kwargs', [{'components':12}, {'components':17}, {'window':8}, {'window':10}, {'attention_ratio':0}, {'classes':1}])
def test_invalid_configuration_fails_early(kwargs):
    with pytest.raises(ValueError):
        ModelConfig(bands=16, **({'components':13} | kwargs))


def test_default_model_preserves_historical_classifier_shape():
    model = ModelConfig(bands=200).model()
    assert model.dense1.in_features == 18496
    with torch.inference_mode():
        assert model.eval()(torch.zeros(1, 1, 30, 25, 25)).shape == (1, 16)


@pytest.mark.parametrize('cube', [np.zeros((4,4)), np.full((4,4,16), np.nan), np.zeros((0,4,16)), np.ones((4,4,16),dtype=complex)])
def test_invalid_cube_rejected(cube):
    with pytest.raises(ValueError):
        validate_cube(cube, bands=16)


def test_upload_contract(trained):
    directory, cube, *_ = trained
    client = create_app(directory, batch_size=19).test_client()
    assert client.get('/health').json['status'] == 'ready'
    response = client.post('/api/upload', data={'file':(mat(cube),'cube.mat')})
    assert response.status_code == 200
    assert len(response.json['predictions']) == 64
    assert response.json['class_ids'] == Predictor(directory, batch_size=19).predict(cube)['class_ids']
    assert client.post('/api/upload').status_code == 400
    assert client.post('/api/upload', data={'file':(mat(cube,'other'),'cube.mat')}).status_code == 400
    assert client.post('/api/upload', data={'file':(io.BytesIO(b'not a mat'),'bad.mat')}).status_code == 400
    assert client.post('/api/upload', data={'file':(mat(cube[:,:,:15]),'wrong.mat')}).status_code == 400


def test_upload_size_limit_is_active(trained):
    directory, *_ = trained
    client = create_app(directory, max_upload_mb=1).test_client()
    response = client.post('/api/upload', data={'file':(io.BytesIO(b'x' * 1_100_000),'large.mat')})
    assert response.status_code == 413


def test_pixel_limit_applies_before_patch_materialization(trained):
    directory, cube, *_ = trained
    with pytest.raises(ValueError, match='pixel limit'):
        Predictor(directory, max_pixels=63).predict(cube)


def test_complex_labels_are_rejected(tmp_path):
    cube = np.ones((4, 4, 16), dtype=np.float32)
    with pytest.raises(ValueError, match='real numeric'):
        train_model(cube, np.ones((4, 4), dtype=complex), tmp_path/'model',
                    config=ModelConfig(16, 13, 9, 3), epochs=1)


def test_busy_request_fails_fast_and_lock_recovers(trained):
    from concurrent.futures import ThreadPoolExecutor
    import threading
    directory, cube, *_ = trained
    app = create_app(directory, batch_size=19)
    entered, release = threading.Event(), threading.Event()
    original = Predictor.predict
    def blocked(predictor, data):
        entered.set()
        assert release.wait(timeout=10)
        return original(predictor, data)
    def upload():
        with app.test_client() as client:
            return client.post('/api/upload', data={'file': (mat(cube), 'cube.mat')})
    with patch.object(Predictor, 'predict', blocked), ThreadPoolExecutor(max_workers=1) as pool:
        first = pool.submit(upload)
        try:
            assert entered.wait(timeout=10)
            assert upload().status_code == 503
        finally:
            release.set()
        assert first.result(timeout=20).status_code == 200
    assert upload().status_code == 200


def test_bad_upload_releases_inference_lock(trained):
    directory, cube, *_ = trained
    client = create_app(directory).test_client()
    assert client.post('/api/upload', data={'file': (mat(cube, 'wrong'), 'cube.mat')}).status_code == 400
    assert client.post('/api/upload', data={'file': (mat(cube), 'cube.mat')}).status_code == 200


def test_artifact_rejects_unknown_architecture(trained, tmp_path):
    import shutil
    directory, *_ = trained
    target = tmp_path/'unknown'
    shutil.copytree(directory, target)
    manifest = json.loads((target/'manifest.json').read_text())
    manifest['architecture'] = 'another-model'
    (target/'manifest.json').write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match='schema'):
        Predictor(target)
