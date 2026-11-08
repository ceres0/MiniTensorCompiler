"""Export reproducible models with frozen shapes and parameter initializers."""

import argparse
from pathlib import Path

import torch

from models.workloads import CNN, MLP, QKV


WORKLOADS = {
    "mlp": (MLP, (128,), ("output",)),
    "cnn": (CNN, (3, 32, 32), ("output",)),
    "qkv": (QKV, (256,), ("q", "k", "v")),
}


def export_model(name: str, output: Path, batch: int = 1, seed: int = 0) -> Path:
    if batch < 1:
        raise ValueError("batch must be a positive integer")
    model_type, shape, outputs = WORKLOADS[name]
    torch.manual_seed(seed)
    model = model_type().eval()
    sample = torch.randn((batch, *shape), dtype=torch.float32)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with torch.no_grad():
        torch.onnx.export(
            model, (sample,), str(output), input_names=["input"],
            output_names=list(outputs), opset_version=17,
            do_constant_folding=True, dynamo=False,
        )
    return output


def main(name: str) -> None:
    parser = argparse.ArgumentParser(description=f"Export static FP32 {name} ONNX")
    parser.add_argument("--output", type=Path, default=Path(f"models/{name}.onnx"))
    parser.add_argument("--batch", type=int, default=1)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    if args.batch < 1:
        parser.error("--batch must be positive")
    print(export_model(name, args.output, args.batch, args.seed))
