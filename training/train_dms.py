"""Fine-tune a torchvision segmentation model on checked DMS image/mask pairs."""
import argparse
import csv
import json
import random
from pathlib import Path
import numpy as np
from PIL import Image
import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
from torchvision.models.segmentation import deeplabv3_mobilenet_v3_large, DeepLabV3_MobileNet_V3_Large_Weights
from torchvision.transforms.functional import to_tensor, normalize


class Pairs(Dataset):
    def __init__(self, root, rows, classes, size):
        self.root, self.rows, self.size = root.resolve(), rows, size
        self.lookup = np.full(256, 255, dtype=np.int64)
        for row in classes:
            self.lookup[int(row['label_id'])] = int(row['model_channel'])
    def __len__(self):
        return len(self.rows)
    def __getitem__(self, index):
        row = self.rows[index]
        ip = (self.root / row['image_path']).resolve(); mp = (self.root / row['label_path']).resolve()
        if not ip.is_relative_to(self.root) or not mp.is_relative_to(self.root):
            raise ValueError('Manifest path escapes data root')
        with Image.open(ip) as im, Image.open(mp) as mask:
            if im.size != mask.size:
                raise ValueError('Image/mask mismatch')
            im = im.convert('RGB').resize((self.size, self.size), Image.Resampling.BILINEAR)
            mask = np.asarray(mask.resize((self.size, self.size), Image.Resampling.NEAREST)).astype(np.int64)
        if mask.ndim != 2 or mask.min() < 0 or mask.max() >= 256:
            raise ValueError('Invalid mask values')
        target = torch.from_numpy(self.lookup[mask].copy()).long()
        image = normalize(to_tensor(im), [0.485, .456, .406], [.229, .224, .225])
        return image, target


def run_epoch(model, loader, device, optimizer=None):
    model.train(optimizer is not None)
    # Freeze batch-norm statistics for this small-batch pilot.
    for module in model.modules():
        if isinstance(module, nn.modules.batchnorm._BatchNorm): module.eval()
    total_loss = 0.; batches = 0
    confusion = torch.zeros(46, 46, dtype=torch.int64)
    with torch.set_grad_enabled(optimizer is not None):
        for images, target in loader:
            if not (target != 255).any(): continue
            images, target = images.to(device), target.to(device)
            if optimizer is not None: optimizer.zero_grad()
            output = model(images)
            loss = nn.functional.cross_entropy(output['out'], target, ignore_index=255)
            if optimizer is not None and 'aux' in output:
                loss += .4 * nn.functional.cross_entropy(output['aux'], target, ignore_index=255)
            if optimizer is not None:
                loss.backward(); optimizer.step()
            total_loss += float(loss.detach()); batches += 1
            prediction = output['out'].detach().argmax(1)
            valid = target != 255
            codes = (target[valid] * 46 + prediction[valid]).cpu()
            confusion += torch.bincount(codes, minlength=46 * 46).reshape(46, 46)
    if not batches: raise RuntimeError('No labelled pixels available in this split')
    cm = confusion.numpy(); union = cm.sum(0) + cm.sum(1) - np.diag(cm)
    iou = np.divide(np.diag(cm), union, out=np.full(46, np.nan), where=union > 0)
    return total_loss / batches, float(np.nanmean(iou)), cm, iou


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data', type=Path, required=True)
    p.add_argument('--epochs', type=int, default=3)
    p.add_argument('--size', type=int, default=256)
    p.add_argument('--batch-size', type=int, default=2)
    p.add_argument('--output', type=Path, default=Path('training/runs/dms-pilot'))
    p.add_argument('--evaluate-test', action='store_true', help='Evaluate a frozen checkpoint once on the held-out test set')
    a = p.parse_args()
    if a.epochs < 1 or a.size < 64 or a.batch_size < 1: p.error('Invalid training settings')
    random.seed(42); np.random.seed(42); torch.manual_seed(42)
    repo = Path(__file__).resolve().parents[1]
    with (repo / 'datasets/dms/model_classes.csv').open() as f: classes = list(csv.DictReader(f))
    assert len(classes) == 46
    with (a.data / 'pilot_manifest.csv').open() as f: rows = [r for r in csv.DictReader(f) if r['status'] == 'accepted']
    if len({r['image_id'] for r in rows}) != len(rows): raise ValueError('Duplicate images in manifest')
    groups = {s: [r for r in rows if r['split'] == s] for s in ['train', 'validation', 'test']}
    if not groups['train'] or not groups['validation']: raise ValueError('Need accepted train and validation pairs; inspect pilot_manifest.csv')
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print('Device:', device, '| Pairs:', {s: len(v) for s, v in groups.items()}, flush=True)
    a.output.mkdir(parents=True, exist_ok=True)
    checkpoint = a.output / 'best.pt'
    model = deeplabv3_mobilenet_v3_large(weights=None, weights_backbone=None, num_classes=46, aux_loss=True) if a.evaluate_test else deeplabv3_mobilenet_v3_large(weights=DeepLabV3_MobileNet_V3_Large_Weights.DEFAULT)
    model.classifier[-1] = nn.Conv2d(model.classifier[-1].in_channels, 46, 1)
    # Keep the saved model architecture consistent in train and test modes.
    model.aux_classifier[-1] = nn.Conv2d(model.aux_classifier[-1].in_channels, 46, 1)
    model.to(device)
    loaders = {s: DataLoader(Pairs(a.data, v, classes, a.size), batch_size=a.batch_size, shuffle=(s == 'train' and not a.evaluate_test), num_workers=0) for s, v in groups.items() if v}
    if a.evaluate_test:
        if 'test' not in loaders: raise ValueError('No held-out test pairs')
        saved = torch.load(checkpoint, map_location=device, weights_only=True)
        model.load_state_dict(saved['state_dict'])
        loss, score, cm, iou = run_epoch(model, loaders['test'], device)
        (a.output / 'test_metrics.json').write_text(json.dumps({'loss':loss,'mean_iou':score,'test_pairs':len(groups['test'])}, indent=2))
        np.savetxt(a.output / 'test_confusion_matrix.csv', cm, delimiter=',', fmt='%d')
        print('Held-out test mean IoU:', score); return
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)
    best = -1.; history = []
    for epoch in range(1, a.epochs + 1):
        train_loss, _, _, _ = run_epoch(model, loaders['train'], device, optimizer)
        val_loss, score, cm, iou = run_epoch(model, loaders['validation'], device)
        history.append({'epoch':epoch,'train_loss':train_loss,'validation_loss':val_loss,'validation_mean_iou':score})
        print(history[-1], flush=True)
        if score > best:
            best = score
            torch.save({'state_dict':model.state_dict(),'classes':classes,'size':a.size,'epoch':epoch,'validation_mean_iou':score}, checkpoint)
            np.savetxt(a.output / 'validation_confusion_matrix.csv', cm, delimiter=',', fmt='%d')
            with (a.output / 'validation_per_class.csv').open('w',newline='') as f:
                w=csv.writer(f);w.writerow(['channel','material','iou'])
                for c,v in zip(classes,iou):w.writerow([c['model_channel'],c['material_name'],'' if np.isnan(v) else float(v)])
        with (a.output / 'history.csv').open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(history[0]));w.writeheader();w.writerows(history)
    print('Saved checkpoint:', checkpoint.resolve())
    print('This pilot does not update the browser camera. Validate before deployment.')


if __name__ == '__main__':
    main()
