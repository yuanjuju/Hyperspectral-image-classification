"""Train HybridSN and export one versioned model + preprocessing artifact."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import json
import random
import uuid

import numpy as np
import scipy.io as sio
from sklearn.model_selection import train_test_split
import torch
from torch.utils.data import DataLoader
from src.pipeline import ModelConfig, PatchDataset, SpectralTransform, save_artifact, validate_cube


def train_model(cube, labels, output, *, config, epochs=40, batch_size=128,
                test_ratio=0.9, learning_rate=0.00037, seed=345, device='cpu'):
    if Path(output).exists():
        raise FileExistsError(f'Artifact directory already exists: {output}')
    cube = validate_cube(cube, bands=config.bands)
    labels = np.asarray(labels)
    if labels.shape != cube.shape[:2] or not np.issubdtype(labels.dtype, np.number) or np.iscomplexobj(labels):
        raise ValueError('Labels must be a real numeric H x W array matching the cube')
    if not np.isfinite(labels).all() or np.any(labels != np.floor(labels)) or labels.min() < 0 or labels.max() > config.classes:
        raise ValueError('Labels must be integers: 0 for background, 1..classes for supervised pixels')
    if epochs < 1 or batch_size < 1 or not 0 < test_ratio < 1 or not np.isfinite(learning_rate) or learning_rate <= 0:
        raise ValueError('Invalid training arguments')
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    positions = np.flatnonzero(labels.reshape(-1) > 0)
    train_positions, test_positions = train_test_split(
        positions, test_size=test_ratio, random_state=seed, stratify=labels.reshape(-1)[positions])
    # Fit spectral statistics only on the selected training centers.
    transform = SpectralTransform.fit(cube.reshape(-1, cube.shape[-1])[train_positions], config.components)
    reduced = transform.transform(cube)
    train_set = PatchDataset(reduced, train_positions, config.window, labels)
    test_set = PatchDataset(reduced, test_positions, config.window, labels)
    generator = torch.Generator().manual_seed(seed)
    train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=True, generator=generator)
    test_loader = DataLoader(test_set, batch_size=batch_size, shuffle=False)
    model = config.model().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    loss_fn = torch.nn.CrossEntropyLoss()
    history = []
    for epoch in range(epochs):
        model.train()  # Reset after the previous epoch's evaluation, including Dropout.
        weighted_loss = 0.0
        for inputs, targets in train_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            optimizer.zero_grad(set_to_none=True)
            loss = loss_fn(model(inputs), targets)
            loss.backward(); optimizer.step()
            weighted_loss += loss.item() * targets.size(0)
        model.eval()
        correct = total = 0
        with torch.inference_mode():
            for inputs, targets in test_loader:
                predicted = model(inputs.to(device)).argmax(dim=1).cpu()
                correct += (predicted == targets).sum().item()
                total += targets.numel()
        row = {'epoch': epoch + 1, 'train_loss': weighted_loss / len(train_set),
               'test_accuracy': correct / total, 'test_samples': total}
        history.append(row)
        print(json.dumps(row), flush=True)
    record = {'seed': seed, 'epochs': epochs, 'batch_size': batch_size, 'learning_rate': learning_rate,
              'device': str(device), 'train_samples': len(train_set), 'test_samples': len(test_set),
              'split': 'stratified random labeled pixel centers; spatial patches may overlap',
              'test_ratio': test_ratio, 'pca_fit_scope': 'training pixel centers only',
              'created_at_utc': datetime.now(timezone.utc).isoformat(), 'history': history}
    manifest = save_artifact(output, model, transform, config, record)
    np.savez_compressed(Path(output) / 'split_indices.npz', train=train_positions, test=test_positions)
    from src.pipeline import sha256
    manifest['files']['split_indices.npz'] = sha256(Path(output) / 'split_indices.npz')
    (Path(output) / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cube', type=Path, required=True)
    parser.add_argument('--labels', type=Path, required=True)
    parser.add_argument('--data-key', default='indian_pines_corrected')
    parser.add_argument('--label-key', default='indian_pines_gt')
    parser.add_argument('--output', type=Path, default=Path('artifacts') / (datetime.now().strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:8]))
    parser.add_argument('--components', type=int, default=30)
    parser.add_argument('--window', type=int, default=25)
    parser.add_argument('--classes', type=int, default=16)
    parser.add_argument('--epochs', type=int, default=40)
    parser.add_argument('--batch-size', type=int, default=128)
    parser.add_argument('--test-ratio', type=float, default=0.9)
    parser.add_argument('--learning-rate', type=float, default=0.00037)
    parser.add_argument('--seed', type=int, default=345)
    parser.add_argument('--device', default='cpu', help='Explicit device, e.g. cpu or cuda:0')
    args = parser.parse_args()
    cube_data, label_data = sio.loadmat(args.cube), sio.loadmat(args.labels)
    if args.data_key not in cube_data or args.label_key not in label_data:
        parser.error('Specified MAT data or label key is missing')
    cube = validate_cube(cube_data[args.data_key])
    config = ModelConfig(bands=cube.shape[-1], components=args.components, window=args.window, classes=args.classes)
    train_model(cube, label_data[args.label_key], args.output, config=config, epochs=args.epochs,
                batch_size=args.batch_size, test_ratio=args.test_ratio, learning_rate=args.learning_rate,
                seed=args.seed, device=args.device)
    print(f'Artifact written: {args.output}')


if __name__ == '__main__':
    main()
