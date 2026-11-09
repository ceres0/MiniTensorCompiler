"""Compare a scalar fused epilogue kernel with the existing graph fusion path.

Both are compiled using the same custom TVM pipeline and invoked via Relax VM.
A fixed-order single run is diagnostic, not proof of stable speedup.
"""
import argparse
import hashlib
from pathlib import Path
import json
import os
import time


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir', type=Path, required=True)
    p.add_argument('--shape', action='append', help='M,K,N; can be repeated')
    p.add_argument('--threads', type=int, default=1)
    p.add_argument('--warmup', type=int, default=30)
    p.add_argument('--repeat', type=int, default=100)
    p.add_argument('--rounds', type=int, default=3)
    p.add_argument('--seed', type=int, default=13)
    a = p.parse_args(argv)
    try:
        shapes = [tuple(map(int, v.split(','))) for v in (a.shape or ['1,128,256', '8,128,256', '32,128,256'])]
        if any(len(s) != 3 or min(s) <= 0 for s in shapes) or len(set(shapes)) != len(shapes):
            raise ValueError()
    except ValueError:
        p.error('shapes must be unique positive M,K,N triples')
    if a.output_dir.exists(): p.error('output directory exists')
    if a.threads < 1 or a.warmup < 0 or a.repeat < 1 or a.rounds < 1 or a.seed < 0:
        p.error('invalid thread, seed, or repetition count')
    os.environ.update(TVM_NUM_THREADS=str(a.threads), OMP_NUM_THREADS=str(a.threads), OPENBLAS_NUM_THREADS=str(a.threads))
    import numpy as np
    import tvm
    from tvm import relax
    from minicompiler.compiler.linear_pipeline import linear_fused_pipeline
    from minicompiler.doctor import collect_report
    from minicompiler.passes.linear_bias_relu import run_linear_bias_relu
    from minicompiler.profiling.benchmark import measure
    from minicompiler.profiling.report import _git_info
    from minicompiler.runtime.correctness import compare_outputs
    from minicompiler.schedules.fused_linear_cpu import make_fused_linear
    if tvm.runtime.num_threads() != a.threads:
        raise RuntimeError('TVM thread count differs from requested count')
    a.output_dir.mkdir(parents=True)
    records = []
    for m, k, n in shapes:
        path = a.output_dir / f'm{m}_k{k}_n{n}'
        path.mkdir()
        x = relax.Var('x', relax.TensorType((m, k), 'float32'))
        w = relax.Var('w', relax.TensorType((k, n), 'float32'))
        b = relax.Var('bias', relax.TensorType((n,), 'float32'))
        bb = relax.BlockBuilder()
        with bb.function('main', [x, w, b]):
            with bb.dataflow():
                mul = bb.emit(relax.op.matmul(x, w))
                add = bb.emit(relax.op.add(mul, b))
                y = bb.emit_output(relax.op.nn.relu(add))
            bb.emit_func_output(y)
        original = bb.get()
        graph, info = run_linear_bias_relu(original)
        if info['status'] != 'ok' or info['rewrites'] != 1:
            raise RuntimeError(f'graph fusion failed: {info}')
        graph_tir = relax.transform.FuseTIR()(relax.transform.LegalizeOps()(graph))
        kernel = make_fused_linear(m, k, n)
        (path / 'graph_fused_tir.py').write_text(graph_tir.script() + '\n')
        (path / 'scalar_fused_tir.py').write_text(kernel.script() + '\n')
        bb = relax.BlockBuilder()
        gv = bb.add_func(kernel['main'].without_attr('global_symbol'), 'scalar_linear')
        with bb.function('main', [x, w, b]):
            with bb.dataflow():
                y = bb.emit_output(relax.op.call_tir(gv, (x, w, b), out_ty=relax.TensorType((m, n), 'float32')))
            bb.emit_func_output(y)
        mods = {'tvm_default': original, 'graph_fused': graph, 'scalar_fused': bb.get()}
        rng = np.random.default_rng(a.seed)
        inputs = [rng.standard_normal(s, dtype=np.float32) for s in ((m,k),(k,n),(n,))]
        ref = np.maximum(inputs[0] @ inputs[1] + inputs[2], 0)
        tensors = [tvm.runtime.tensor(tvm_input) for tvm_input in inputs]
        stages = {}
        for name, mod in mods.items():
            start = time.perf_counter_ns()
            with tvm.transform.PassContext(opt_level=2):
                pipeline = 'default' if name == 'tvm_default' else linear_fused_pipeline()
                exe = tvm.compile(mod, target='llvm', relax_pipeline=pipeline, tir_pipeline='default')
            compile_ms = (time.perf_counter_ns() - start) / 1e6
            vm = relax.VirtualMachine(exe, tvm.cpu())
            fn = vm['main']
            correctness = compare_outputs([fn(*tensors).numpy()], [ref])
            entry = {'compile_ms': compile_ms, 'correctness': correctness}
            if correctness['passed']:
                entry['inference'] = measure(lambda: fn(*tensors), a.warmup, a.repeat, a.rounds)
            stages[name] = entry
        if all(v['correctness']['passed'] for v in stages.values()):
            speedup = stages['graph_fused']['inference']['median_ms'] / stages['scalar_fused']['inference']['median_ms']
        else:
            speedup = None
        records.append({'shape': [m,k,n],
                        'inputs_sha256': hashlib.sha256(b''.join(value.tobytes() for value in inputs)).hexdigest(),
                        'stages': stages, 'graph_over_scalar_speedup': speedup})
    report = {'git': _git_info(), 'environment': collect_report(), 'threads': a.threads, 'seed': a.seed,
              'method': 'Fixed order TVM Default then graph then scalar. All Relax VM and same target, pre-created inputs, output allocation included. Graph and scalar use same custom pipeline; TVM Default uses its native pipeline. CPU affinity/power uncontrolled.',
              'warning': 'Single local scalar accumulator avoids full intermediate tensors in authored TIR; register allocation and hardware traffic not measured.',
              'results': records}
    (a.output_dir / 'report.json').write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
    print(a.output_dir / 'report.json')
    return 0 if all(v['graph_over_scalar_speedup'] is not None for v in records) else 1

if __name__ == '__main__':
    raise SystemExit(main())
