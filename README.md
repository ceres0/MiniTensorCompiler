# MiniTensorCompiler

基于 Apache TVM Relax / TensorIR 的模型编译实验项目。当前完成静态 ONNX 导入、LLVM CPU 基线、受语义保护的图改写，以及静态 FP32 MatMul CPU 调度消融。Relax、ONNX frontend、融合基础设施、LLVM codegen 和 VM 来自 TVM。

## 环境和运行

参考环境是 Ubuntu 24.04 x86_64、Python 3.11 和 `apache-tvm==0.27.0.post1`。macOS arm64 的执行结果不代表 Linux 或 CUDA 已验证。安装 [uv](https://docs.astral.sh/uv/) 后：

```bash
uv sync --locked --extra dev
uv run --locked python -m minicompiler doctor
uv run --locked pytest tests/smoke
uv run --locked python examples/00_add.py
uv run --locked python examples/03_call_tir.py
```

`00_add.py` 编译并运行 Relax Add，导出和重新加载工件后再次校验结果。`03_call_tir.py` 展示 Relax 调用 TensorIR、打印 IR 和 VM 字节码，并验证输出。

`doctor` 输出 JSON，包括操作系统、CPU、逻辑核心数、Python 和依赖版本、LLVM 信息及导入状态；缺失必要模块时返回非零。`llvm_config_version` 是主机工具的版本，不一定是 TVM 编译所用的 LLVM；`tvm_build_llvm_major` 是 TVM 暴露的主版本，无法获取时为 null。实际 wheel 提供 `tvm.tirx`，不提供方案中提到的独立 `tvm_tirx` 模块；两项都报告，前者是必要项。

## ONNX 导入和 IR 分析

使用可选的 PyTorch 依赖生成固定随机种子、静态 FP32 的 MLP、CNN 和三分支 QKV 模型（默认 batch 为 1，可用 `--batch`、`--seed` 调整）：

```bash
uv sync --locked --extra dev --extra models
uv run --locked python -m models.generate_mlp --output runs/models/mlp.onnx
uv run --locked python -m models.generate_cnn --output runs/models/cnn.onnx
uv run --locked python -m models.generate_qkv --output runs/models/qkv.onnx
uv run --locked python -m minicompiler import --model runs/models/mlp.onnx --output-dir runs/mlp/embedded
uv run --locked python -m minicompiler import --model runs/models/mlp.onnx --output-dir runs/mlp/params --keep-params-in-input
uv run --locked pytest tests
```

导入命令生成 `00_onnx_summary.json`、`01_relax_imported.py` 和 `02_relax_inspection.json`，分别包含 ONNX 输入、opset 和节点统计，可读的 Relax IR，以及 Relax Call、算子、形状、dtype 和 DFPattern 匹配统计。默认 pattern 统计单个 matmul、add、relu、reshape 调用，不代表融合命中次数。输出目录中已有同名工件时命令会拒绝覆盖，请为每次导入选择新目录。

目前只接受输入为 FP32 tensor 且维度均为已知正整数的 ONNX 模型；自定义 domain 和不能确定的 Relax tensor 形状会明确报错。其他算子是否支持取决于固定版本 TVM 的 ONNX frontend，导入错误会保留原始诊断。默认将权重嵌入 IR；`--keep-params-in-input` 将权重保留为函数参数，TVM 在内存中的 `main.attrs['params']` 保存相应数组。两种模式应分别导入、比较。IR dump 供阅读，不是包含完整权重的独立可加载工件；后续执行应保留原始 ONNX 和参数。生成的模型和 `runs/` 默认不加入 Git。

## CPU 基线

```bash
uv run --locked python -m minicompiler bench --model runs/models/mlp.onnx --target llvm --mode default --threads 1 --output runs/bench/mlp-default.json
uv run --locked python -m minicompiler bench --model runs/models/cnn.onnx --target llvm --mode default --threads 1 --output runs/bench/cnn-default.json
uv run --locked python -m minicompiler bench --model runs/models/mlp.onnx --target llvm --mode nofusion --threads 1 --output runs/bench/mlp-nofusion.json
```

默认固定 seed 0，预热 30 次，再测量 3 轮各 100 次；可通过 `--seed`、`--warmup`、`--repeat`、`--rounds` 调整。每份 JSON 同时包含 ORT CPU 与所选 TVM 模式、每次延迟、median/p95、误差、环境与编译耗时。只有正确性通过才测延迟，失败时命令返回非零并保留错误指标；已有输出文件不会被覆盖。运行方式、计时边界与公平性限制见 [benchmark 方法](docs/benchmark_methodology.md)。

固定版本的 TVM CPU 默认 pipeline 本身不含 `FuseOps`/`FuseTIR`；`nofusion` 显式禁用它们，仅用于诊断，可能与默认路径相同，不代表优化收益。ORT 与 TVM 是不同系统，其延迟差异也不是项目自定义优化收益。

## 冗余 reshape Pass

```bash
uv run --locked python examples/02_relax_pass.py --output-dir runs/reshape-demo
uv run --locked python -m minicompiler reshape --model runs/models/mlp.onnx --output-dir runs/mlp/reshape
uv run --locked python -m minicompiler reshape --model runs/models/mlp.onnx --output-dir runs/mlp/reshape-disabled --disable
```

示例展示两层 reshape 合并，并编译执行前后版本验证数值。CLI 对输入 ONNX 模型分别输出改写前后 IR 和含命中、跳过原因的 JSON；普通 MLP 未必包含匹配模式。该 Pass 对未知、动态或零长度形状保守跳过；更多前提和回归用例见 [Pass 正确性说明](docs/pass_correctness.md)。TVM 自带类似 Pass，此处不宣称性能提升。

## 线性子图融合

```bash
uv run --locked python examples/05_linear_fusion.py --output-dir runs/linear-evidence
uv run --locked python -m minicompiler linear --model runs/models/mlp.onnx --output-dir runs/mlp/linear
uv run --locked python -m minicompiler bench --model runs/models/mlp.onnx --target llvm --mode custom --threads 1 --output runs/bench/mlp-custom.json
```

自定义规则使用 TVM 的融合基础设施将合规的 FP32 `relu(matmul(x, w) + bias)` 分组；实验命令输出融合前后的 Relax 和 TIR。`custom` 基准在同一进程、相同模型和输入下测量 TVM Default 与自定义路径，并分别校验 ORT。完整约束、TIR 证据、QKV 实验与性能限制见 [线性融合说明](docs/linear_fusion.md)。

## MatMul CPU 调度消融

```bash
uv run --locked python -m benchmarks.matmul_schedule --threads 1 --output-dir runs/matmul-ablation
```

实验对比 TVM Default 与手写 TIR 的 naive、分块、重排、并行和向量化版本，输出各形状 IR、正确性及逐次延迟。适用范围、调度前提和测量边界见 [调度说明](docs/schedule_optimization.md)。

## 参考资料

TVM 源码和教程参考固定在 [v0.27.0 tag](https://github.com/apache/tvm/tree/v0.27.0)（release commit `4d0ac16`）。PyPI 的 wheel 版本固定为 `0.27.0.post1`；不能仅凭 tag 假定 post-release wheel 与源码完全一致。后续 API 以安装的 wheel 和其对应源码为准。
