"""Train the material segmentation model on the cleaned OpenSurfaces manifest."""
import argparse, csv, json, random
from pathlib import Path
import numpy as np
from PIL import Image
import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
from torchvision.models.segmentation import deeplabv3_mobilenet_v3_large
from torchvision.transforms.functional import to_tensor, normalize


class OpenSurfacePairs(Dataset):
    def __init__(self, rows, size):
        self.rows, self.size = rows, size
    def __len__(self): return len(self.rows)
    def __getitem__(self, index):
        row = self.rows[index]
        with Image.open(row['image_path']) as image, Image.open(row['label_path']) as mask:
            image = image.convert('RGB').resize((self.size, self.size), Image.Resampling.BILINEAR)
            mask = np.asarray(mask.resize((self.size, self.size), Image.Resampling.NEAREST)).astype(np.int64)
        target = torch.from_numpy(mask).long()
        target[(target < 0) | (target >= 46)] = 255
        return normalize(to_tensor(image), [0.485, .456, .406], [.229, .224, .225]), target


def epoch(model, loader, device, optimizer=None):
    model.train(optimizer is not None)
    for module in model.modules():
        if isinstance(module, nn.modules.batchnorm._BatchNorm): module.eval()
    total, count = 0.0, 0
    confusion = torch.zeros(46, 46, dtype=torch.int64)
    with torch.set_grad_enabled(optimizer is not None):
        for images, target in loader:
            images, target = images.to(device), target.to(device)
            if not (target != 255).any():
                continue
            if optimizer is not None: optimizer.zero_grad()
            output = model(images)
            loss = nn.functional.cross_entropy(output['out'], target, ignore_index=255)
            if optimizer is not None and 'aux' in output:
                loss = loss + .4 * nn.functional.cross_entropy(output['aux'], target, ignore_index=255)
                loss.backward(); optimizer.step()
            total += float(loss.detach()); count += 1
            prediction = output['out'].detach().argmax(1)
            valid = target != 255
            codes = (target[valid] * 46 + prediction[valid]).cpu()
            confusion += torch.bincount(codes, minlength=46 * 46).reshape(46, 46)
    cm = confusion.numpy(); union = cm.sum(0) + cm.sum(1) - np.diag(cm)
    iou = np.divide(np.diag(cm), union, out=np.full(46, np.nan), where=union > 0)
    return total / max(count, 1), float(np.nanmean(iou)), cm


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', type=Path, default=Path(r'E:/Fitwell-OpenSurfaces/prepared/manifest.csv'))
    parser.add_argument('--output', type=Path, default=Path('training/runs/opensurfaces-research'))
    parser.add_argument('--epochs', type=int, default=3)
    parser.add_argument('--size', type=int, default=256)
    parser.add_argument('--batch-size', type=int, default=2)
    args = parser.parse_args()
    random.seed(42); np.random.seed(42); torch.manual_seed(42)
    with args.manifest.open(newline='', encoding='utf-8-sig') as handle:
        rows = [row for row in csv.DictReader(handle) if row['status'] == 'accepted']
    groups = {name: [row for row in rows if row['split'] == name] for name in ('train', 'validation')}
    if not groups['train'] or not groups['validation']: raise ValueError('The manifest needs train and validation rows')
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    args.output.mkdir(parents=True, exist_ok=True)
    print('Device:', device, '| Pairs:', {key: len(value) for key, value in groups.items()}, flush=True)
    model = deeplabv3_mobilenet_v3_large(weights=None, weights_backbone=None, num_classes=46, aux_loss=True)
    model.to(device)
    loaders = {key: DataLoader(OpenSurfacePairs(value, args.size), batch_size=args.batch_size, shuffle=(key == 'train'), num_workers=0) for key, value in groups.items()}
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)
    history, best = [], -1.0
    for number in range(1, args.epochs + 1):
        train_loss, _, _ = epoch(model, loaders['train'], device, optimizer)
        validation_loss, score, matrix = epoch(model, loaders['validation'], device)
        record = {'epoch': number, 'train_loss': train_loss, 'validation_loss': validation_loss, 'validation_mean_iou': score}
        history.append(record); print(record, flush=True)
        if score > best:
            best = score
            torch.save({'state_dict': model.state_dict(), 'size': args.size, 'epoch': number, 'validation_mean_iou': score}, args.output / 'best.pt')
            np.savetxt(args.output / 'validation_confusion_matrix.csv', matrix, delimiter=',', fmt='%d')
        with (args.output / 'history.csv').open('w', newline='', encoding='utf-8') as handle:
            writer = csv.DictWriter(handle, fieldnames=history[0].keys()); writer.writeheader(); writer.writerows(history)
    print('Saved:', (args.output / 'best.pt').resolve())


if __name__ == '__main__': main()
