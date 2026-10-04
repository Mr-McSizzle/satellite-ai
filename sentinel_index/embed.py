"""
RemoteCLIP Embedder. Loads ViT-B/32 locally.
Used for both indexing (image -> vec) and searching (text -> vec).
"""
import numpy as np
import torch
import open_clip
from PIL import Image

from . import config

_model = None
_preprocess = None
_tokenizer = None
_device = "cuda" if torch.cuda.is_available() else "cpu"

def load():
    global _model, _preprocess, _tokenizer
    if _model is not None:
        return
        
    print(f"[embed] Loading RemoteCLIP {config.CLIP_ARCH} on {_device}...")
    _model, _, _preprocess = open_clip.create_model_and_transforms(
        config.CLIP_ARCH,
        pretrained=str(config.CLIP_WEIGHTS),
        device=_device
    )
    _model.eval()
    _tokenizer = open_clip.get_tokenizer(config.CLIP_ARCH)

@torch.no_grad()
def embed_images(images: list[Image.Image]) -> np.ndarray:
    load()
    if not images:
        return np.zeros((0, config.EMBED_DIM), dtype=np.float32)
        
    tensors = torch.stack([_preprocess(img) for img in images]).to(_device)
    features = _model.encode_image(tensors)
    features /= features.norm(dim=-1, keepdim=True)
    return features.cpu().numpy().astype(np.float32)

@torch.no_grad()
def embed_text(texts: list[str]) -> np.ndarray:
    load()
    tokens = _tokenizer(texts).to(_device)
    features = _model.encode_text(tokens)
    features /= features.norm(dim=-1, keepdim=True)
    return features.cpu().numpy().astype(np.float32)
