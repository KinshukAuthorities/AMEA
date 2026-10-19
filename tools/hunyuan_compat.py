"""Check/apply the known hierarchical decoder compatibility patch to supplied source."""
import argparse,ast,hashlib,json,re
from pathlib import Path

def patched_text(text):
    if 'class HierarchicalVolumeDecoding' not in text or 'import torch.nn.functional as F' not in text:
        raise ValueError('Unrecognized decoder source; inspect this upstream version before patching')
    changed=text
    for name in ['resolution','bbox_min']:
        changed=re.sub(r'torch\.tensor\('+name+r', dtype=next_points\.dtype, device=device\)',
                       f'torch.tensor({name}, dtype=torch.float32, device=device)',changed)
    start=changed.index('class HierarchicalVolumeDecoding')
    end=changed.find('\nclass ',start+1)
    if end<0:end=len(changed)
    section=changed[start:end]
    if 'next_logits = F.interpolate(grid_logits.unsqueeze(1).float(),' not in section:
        pattern=r'(?m)^(?P<indent>[ \t]+)next_logits\s*=.*(?:nan|NaN).*$'
        matches=list(re.finditer(pattern,section))
        if len(matches)!=1:raise ValueError('Unrecognized coarse-grid initialization; refusing a speculative patch')
        indent=matches[0].group('indent')
        replacement=indent+'next_logits = F.interpolate(grid_logits.unsqueeze(1).float(),\n'+indent+"    size=tuple(grid_size), mode='trilinear', align_corners=True)[0,0].to(dtype)"
        section=re.sub(pattern,lambda _:replacement,section,count=1)
        changed=changed[:start]+section+changed[end:]
    if re.search(r'torch\.tensor\((?:resolution|bbox_min), dtype=next_points\.dtype',changed):
        raise ValueError('Unsafe integer coordinate conversion remains')
    for name in ['resolution','bbox_min']:
        if f'torch.tensor({name}, dtype=torch.float32, device=device)' not in changed:
            raise ValueError('Unrecognized coordinate-conversion source')
    ast.parse(changed)
    if changed!=text:
        changed='# AMEA modification: float32 fractional coordinates and coarse-field preservation in hierarchical decoding.\n'+changed
    return changed

def patch(source,apply=False):
    path=Path(source)/'hy3dgen/shapegen/models/autoencoders/volume_decoders.py'
    before=path.read_text(encoding='utf-8');after=patched_text(before);needed=before!=after
    if needed and apply:
        backup=path.with_suffix(path.suffix+'.amea-original')
        if not backup.exists():backup.write_text(before,encoding='utf-8')
        path.write_text(after,encoding='utf-8')
    return {'file':str(path),'patch_needed':needed,'applied':bool(needed and apply),
        'sha256':hashlib.sha256((after if apply else before).encode()).hexdigest(),
        'note':'Preserve upstream licenses and review real generated geometry; compatibility is not artistic quality.'}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('--apply',action='store_true');a=p.parse_args()
    print(json.dumps(patch(a.source,a.apply),indent=2))
