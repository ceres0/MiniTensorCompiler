# MiniTensorCompiler

基于 Apache TVM Relax / TensorIR 的模型编译实验项目。当前完成环境锁定、LLVM CPU 最小执行，以及静态 ONNX 模型的检查、Relax 导入和 IR 分析。Relax、ONNX frontend、LLVM codegen 和 VM 来自 TVM；图优化、完整模型编译和性能结果尚未完成。

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

## 参考资料

TVM 源码和教程参考固定在 [v0.27.0 tag](https://github.com/apache/tvm/tree/v0.27.0)（release commit `4d0ac16`）。PyPI 的 wheel 版本固定为 `0.27.0.post1`；不能仅凭 tag 假定 post-release wheel 与源码完全一致。后续 API 以安装的 wheel 和其对应源码为准。
