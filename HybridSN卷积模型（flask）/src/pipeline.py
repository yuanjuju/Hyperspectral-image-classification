"""Shared preprocessing, bounded patch batches and versioned model artifacts."""
from dataclasses import asdict, dataclass
from pathlib import Path
import hashlib
import json

import numpy as np
import torch
from sklearn.decomposition import PCA
from .model import HybridSN


@dataclass(frozen=True)
class ModelConfig:
    bands: int
    components: int = 30
    window: int = 25
    classes: int = 16
    attention_ratio: int = 16

    def __post_init__(self):
        if any(type(x) is not int for x in asdict(self).values()):
            raise ValueError('Model configuration values must be integers')
        if not 13 <= self.components <= self.bands:
            raise ValueError('PCA components must be between 13 and the input band count')
        if self.window < 9 or self.window % 2 != 1:
            raise ValueError('Patch window must be odd and at least 9')
        if not 1 <= self.attention_ratio <= 64 or self.classes < 2:
            raise ValueError('Invalid attention ratio or class count')

    def model(self):
        return HybridSN(self.window, self.components, self.attention_ratio, self.classes)


class SpectralTransform:
    """A fitted PCA whitening transform; serving never fits on request data."""
    def __init__(self, mean, components, scale):
        self.mean = np.asarray(mean, dtype=np.float32)
        self.components = np.asarray(components, dtype=np.float32)
        self.scale = np.asarray(scale, dtype=np.float32)
        if self.mean.ndim != 1 or self.components.ndim != 2 or self.scale.ndim != 1:
            raise ValueError('Invalid PCA artifact dimensions')
        if self.components.shape != (self.scale.size, self.mean.size):
            raise ValueError('Inconsistent PCA artifact shapes')
        if not all(np.isfinite(x).all() for x in (self.mean, self.components, self.scale)) or np.any(self.scale <= 0):
            raise ValueError('Invalid PCA artifact values')

    @classmethod
    def fit(cls, training_spectra, components):
        if training_spectra.shape[0] < components:
            raise ValueError('Training split has fewer spectra than PCA components')
        pca = PCA(n_components=components, whiten=True, svd_solver='full')
        pca.fit(training_spectra)
        return cls(pca.mean_, pca.components_, np.sqrt(np.maximum(pca.explained_variance_, np.finfo(np.float32).eps)))

    def transform(self, cube):
        if cube.shape[-1] != self.mean.size:
            raise ValueError('Input spectral bands do not match the trained preprocessing artifact')
        flat = cube.reshape(-1, cube.shape[-1]).astype(np.float32)
        reduced = ((flat - self.mean) @ self.components.T) / self.scale
        if not np.isfinite(reduced).all():
            raise ValueError('Spectral transform produced non-finite values')
        return reduced.reshape(*cube.shape[:-1], self.scale.size).astype(np.float32)

    def save(self, path):
        np.savez_compressed(path, mean=self.mean, components=self.components, scale=self.scale)

    @classmethod
    def load(cls, path):
        with np.load(path, allow_pickle=False) as arrays:
            return cls(arrays['mean'], arrays['components'], arrays['scale'])


def validate_cube(cube, bands=None, max_pixels=250_000):
    cube = np.asarray(cube)
    if cube.ndim != 3 or any(size == 0 for size in cube.shape):
        raise ValueError('Expected a non-empty H x W x bands cube')
    if cube.shape[0] * cube.shape[1] > max_pixels:
        raise ValueError('Input exceeds configured pixel limit')
    if bands is not None and cube.shape[-1] != bands:
        raise ValueError('Input spectral bands do not match model configuration')
    if not np.issubdtype(cube.dtype, np.number) or np.iscomplexobj(cube) or not np.isfinite(cube).all():
        raise ValueError('Input cube must contain finite real numeric values')
    cube = cube.astype(np.float32)
    if not np.isfinite(cube).all():
        raise ValueError('Input values exceed float32 range')
    return cube


class PatchDataset(torch.utils.data.Dataset):
    def __init__(self, cube, positions, window, labels=None):
        self.width = cube.shape[1]
        self.window = window
        self.positions = np.asarray(positions)
        self.labels = labels
        margin = window // 2
        self.padded = np.pad(cube, ((margin, margin), (margin, margin), (0, 0)))

    def __len__(self):
        return len(self.positions)

    def __getitem__(self, index):
        position = int(self.positions[index])
        row, col = divmod(position, self.width)
        patch = self.padded[row:row+self.window, col:col+self.window]
        tensor = torch.from_numpy(np.ascontiguousarray(patch.transpose(2, 0, 1)[None]))
        if self.labels is None:
            return tensor
        return tensor, int(self.labels.reshape(-1)[position]) - 1


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save_artifact(directory, model, transform, config, training):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    torch.save({key: value.detach().cpu() for key, value in model.state_dict().items()}, directory / 'weights.pt')
    transform.save(directory / 'preprocessor.npz')
    manifest = {'schema_version': 1, 'architecture': 'HybridSN-channel-attention',
                'config': asdict(config), 'label_offset': 1, 'training': training,
                'files': {name: sha256(directory / name) for name in ('weights.pt', 'preprocessor.npz')}}
    (directory / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


class Predictor:
    def __init__(self, artifact_dir, batch_size=128, max_pixels=250_000):
        if batch_size < 1 or max_pixels < 1:
            raise ValueError('Batch size and pixel limit must be positive')
        directory = Path(artifact_dir)
        self.manifest = json.loads((directory / 'manifest.json').read_text())
        if (self.manifest.get('schema_version') != 1 or self.manifest.get('label_offset') != 1
                or self.manifest.get('architecture') != 'HybridSN-channel-attention'):
            raise ValueError('Unsupported artifact schema')
        for name in ('weights.pt', 'preprocessor.npz'):
            if sha256(directory / name) != self.manifest['files'].get(name):
                raise ValueError(f'Artifact checksum mismatch: {name}')
        self.config = ModelConfig(**self.manifest['config'])
        self.transform = SpectralTransform.load(directory / 'preprocessor.npz')
        if self.transform.components.shape != (self.config.components, self.config.bands):
            raise ValueError('Preprocessor and model configuration disagree')
        self.model = self.config.model().cpu().eval()
        state = torch.load(directory / 'weights.pt', map_location='cpu', weights_only=True)
        self.model.load_state_dict(state, strict=True)
        self.batch_size = batch_size
        self.max_pixels = max_pixels

    def predict(self, cube):
        cube = validate_cube(cube, bands=self.config.bands, max_pixels=self.max_pixels)
        reduced = self.transform.transform(cube)
        dataset = PatchDataset(reduced, np.arange(cube.shape[0] * cube.shape[1]), self.config.window)
        loader = torch.utils.data.DataLoader(dataset, batch_size=self.batch_size, shuffle=False)
        classes = []
        with torch.inference_mode():
            for batch in loader:
                classes.extend((self.model(batch).argmax(dim=1) + 1).tolist())
        return {'predictions': [f'class_{value}' for value in classes],
                'class_ids': classes, 'shape': list(cube.shape[:2]), 'label_offset': 1,
                'order': 'row-major', 'model': self.manifest['architecture']}
