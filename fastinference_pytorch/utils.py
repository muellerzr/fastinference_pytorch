# AUTOGENERATED! DO NOT EDIT! File to edit: 00_utils.ipynb (unless otherwise specified).

__all__ = ['noop', 'apply', 'retain_type', 'retain_meta', 'to_device', 'tensor', 'to_numpy']

# Cell
import torch
import numpy as np
from torch import Tensor
from fastcore.utils import is_listy, is_iter

# Cell
def noop(x=None, *args,**kwargs):
    "Do nothing"
    return x

# Cell
def apply(func, x, *args, **kwargs):
    "Apply `func` recursively to `x`, passing on args"
    if is_listy(x): return type(x)([apply(func, o, *args, **kwargs) for o in x])
    if isinstance(x,dict):  return {k: apply(func, v, *args, **kwargs) for k,v in x.items()}
    res = func(x, *args, **kwargs)
    return res if x is None else retain_type(res, x)

# Cell
def retain_type(new, old=None, typ=None, copy_meta=False):
    "Cast `new` to type of `old` or `typ` if it's a superclass"
    # e.g. old is TensorImage, new is Tensor - if not subclass then do nothing
    if new is None: return
    assert old is not None or typ is not None
    if typ is None:
        if not isinstance(old, type(new)): return new
        typ = old if isinstance(old,type) else type(old)
    # Do nothing the new type is already an instance of requested type (i.e. same type)
    if typ==type(None) or isinstance(new, typ): return new
    return retain_meta(old, cast(new, typ), copy_meta=copy_meta)

# Cell
def retain_meta(x, res, copy_meta=False):
    "Call `res.set_meta(x)`, if it exists"
    if hasattr(res,'set_meta'): res.set_meta(x, copy_meta=copy_meta)
    return res

# Cell
def to_device(b, device='cpu'):
    "Recursively put `b` on `device`."
    def _inner(o): return o.to(device, non_blocking=True) if isinstance(o,Tensor) else o.to_device(device) if hasattr(o, "to_device") else o
    return apply(_inner, b)

# Cell
def tensor(x, *rest, **kwargs):
    "Like `torch.as_tensor`, but handle lists too, and can pass multiple vector elements directly."
    if len(rest): x = (x,)+rest
    res = (x if isinstance(x, Tensor)
           else torch.tensor(x, **kwargs) if isinstance(x, (tuple,list))
           else _array2tensor(x) if isinstance(x, np.ndarray)
           else torch.as_tensor(x, **kwargs) if hasattr(x, '__array__') or is_iter(x)
           else _array2tensor(np.array(x), **kwargs))
    if res.dtype is torch.float64: return res.float()
    return res

# Cell
def _array2tensor(x):
    if x.dtype==np.uint16: x.astype(np.float32)
    return torch.from_numpy(x)

# Cell
def to_numpy(self, t:tensor):
    try: return t.cpu().numpy()
    except: return t.detach().cpu().numpy()