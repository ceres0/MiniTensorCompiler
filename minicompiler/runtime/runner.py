"""TVM VM execution with input preparation outside timed inference."""

import numpy as np
import tvm
from tvm import relax

from minicompiler.compiler.pipeline import compile_module


class TVMRunner:
    def __init__(self, executable, input_names, compile_time_ms, pipeline):
        self.executable = executable
        self.device = tvm.cpu(0)
        self.vm = relax.VirtualMachine(executable, self.device)
        self.input_names = tuple(input_names)
        self.compile_time_ms = compile_time_ms
        self.pipeline = pipeline

    def prepare_inputs(self, inputs):
        """Copy named CPU arrays once before timing; return ordered TVM tensors."""
        if set(inputs) != set(self.input_names):
            raise ValueError(f"Expected inputs {self.input_names}, got {tuple(inputs)}")
        def contiguous_preserving_shape(value):
            array = np.asarray(value)
            # ascontiguousarray changes a scalar's rank from zero to one.
            return array if array.flags.c_contiguous else np.ascontiguousarray(array)
        return tuple(tvm.runtime.tensor(contiguous_preserving_shape(inputs[name]), device=self.device)
                     for name in self.input_names)

    def run_prepared(self, prepared):
        """Run a VM invocation using pre-created device inputs."""
        return self.vm["main"](*prepared)

    @staticmethod
    def outputs_to_numpy(result):
        """Copy VM outputs to host outside of the timed region."""
        if isinstance(result, tvm.runtime.Tensor):
            return [result.numpy()]
        return [tensor.numpy() for tensor in result]


def build_runner(mod, *, mode="default", target="llvm", onnx_input_names=None, instruments=None):
    """Compile embedded parameters; map ONNX input names by preserved input order.

    TVM's ONNX importer sanitizes names, so callers should supply the ordered
    original ONNX runtime input names when preparing inputs by ONNX name.
    """
    main = mod["main"]
    names = [str(param.name) for param in main.params]
    attrs = main.attrs
    if attrs is not None and "params" in attrs and len(attrs["params"]):
        raise ValueError("Benchmark runner requires embedded parameters; import with keep_params_in_input=False")
    if onnx_input_names is not None:
        onnx_input_names = tuple(onnx_input_names)
        if len(onnx_input_names) != len(names) or len(set(onnx_input_names)) != len(names):
            raise ValueError("ONNX runtime inputs must uniquely match Relax parameter count")
        names = onnx_input_names
    executable, elapsed, pipeline = compile_module(mod, target=target, mode=mode, instruments=instruments)
    return TVMRunner(executable, names, elapsed, pipeline)
