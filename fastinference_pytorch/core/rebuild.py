# AUTOGENERATED! DO NOT EDIT! File to edit: 00d_core.rebuild.ipynb (unless otherwise specified).

__all__ = ['load_data', 'load_model', 'get_tfm', 'generate_pipeline', 'make_pipelines']

# Cell
import io, operator, pickle, torch

# Cell
from pathlib import Path
from numpy import ndarray
from fastcore.utils import _patched

# Cell
from ..utils import to_device, tensor

# Cell
def load_data(path:Path=Path('.'), fn='data'):
    "Opens `pkl` file containing exported `Transform` information"
    if '.pkl' not in fn: fn += '.pkl'
    if not isinstance(path, Path): path = Path(path)
    with open(path/fn, 'rb') as handle:
        tfmd_dict = pickle.load(handle)
    return tfmd_dict

# Cell
def load_model(path:Path='.', fn='model', cpu=True, onnx=False):
    if not onnx:
        if '.pkl' not in fn: fn += '.pkl'
        path = f'{path}/{fn}'
        return torch.load(path, map_location='cpu' if cpu else None)
    else:
        try:
            import onnxruntime as ort
        except ImportError:
            print('to use ONNX you must have `onnxruntime` installed\n\
            Install it with `pip install onnxruntime-gpu`')
        if '.onnx' not in fn: fn += '.onnx'
        path = f'{path}/{fn}'
        ort_session = ort.InferenceSession(path)
        if not cpu:
            try:
                ort_session.set_providers(['CUDAExecutionProvider'])
            except:
                ort_session.set_providers(['CPUExecutionProvider'])
        return ort_session

# Cell
def get_tfm(key, tfms):
    "Makes a transform from `key`. Class or function must be in global memory (imported)"
    args = tfms[key]
    return globals()[key](**args)

# Cell
def generate_pipeline(tfms, order=True) -> dict:
    "Generate `pipe` of transforms from dict and (potentially) sort them"
    pipe = []
    for key in tfms.keys():
        tfm = get_tfm(key, tfms)
        pipe.append(tfm)
    if order: pipe = sorted(pipe, key=operator.attrgetter('order'))
    return pipe

# Cell
def make_pipelines(tfms) -> dict:
    "Make `item` and `batch` transform pipelines"
    pipe, keys = {}, ['after_item', 'after_batch']
    for key in keys:
        pipe[key] = generate_pipeline(tfms[key], True)
    if not any(isinstance(x, ToTensor) for x in pipe['after_item']):
        pipe['after_item'].append(ToTensor(False))
    return pipe