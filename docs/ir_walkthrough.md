# 同一模型的 CPU 证据链

以静态 FP32 MLP 为例，先生成 ONNX，然后分别导出调度路径的 IR 证据和可执行工件：

```bash
uv run --locked python -m models.generate_mlp --output runs/models/trace-mlp.onnx
uv run --locked python -m minicompiler evidence --model runs/models/trace-mlp.onnx --pass-mode scheduled --output-dir runs/trace-mlp/evidence
uv run --locked python -m minicompiler compile --model runs/models/trace-mlp.onnx --mode scheduled --output runs/trace-mlp/artifact
uv run --locked python -c 'import numpy as np; np.savez("runs/trace-mlp/input.npz", input=np.random.default_rng(0).standard_normal((1, 128), dtype=np.float32))'
uv run --locked python -m minicompiler run --artifact runs/trace-mlp/artifact --inputs runs/trace-mlp/input.npz --output runs/trace-mlp/output.npz
```

所有输出目录必须不存在，输出 NPZ 不会覆盖现有文件。`input.npz` 的键必须与 ONNX 输入名一致，形状和 dtype 精确匹配 manifest；结果 NPZ 的键对应 ONNX 输出名。

证据目录中的 `manifest.json` 将文件、版本、模型哈希、Pass 结果和数据来源关联起来：

1. `00_onnx_summary.json`：ONNX shape 推断、输入类型及节点分布。
2. `01_relax_imported.py`：TVM ONNX frontend 导入的 Relax。
3. `02_relax_after_pass.py`：项目 reshape Pass 及调度接入后的 Relax；`scheduled` 路径只对可证明安全的静态二维 FP32 MatMul 插入 `call_tir`。`07_scheduled_tir.py` 包含实际交给编译器的调度后模块（同时包含 Relax 与 PrimFunc），匹配数为 0 时明确标记不可用。
4. `03_legalized_inspection.py`：单独对 Pass 后 IR 执行 `LegalizeOps` 的检查结果，用于观察 `call_tir`；它不是传回编译器的输入。编译从 Pass 后高层模块开始，避免重复运行默认 lowering。
5. `04_vm.txt`：实际编译得到的 VM 可读指令。`05_llvm.ll` 和 `06_assembly.s` 来自同一次编译产物包含的 LLVM 模块；如果运行环境无法提供完整源码，manifest 标记不可用并记录原因，而不是生成占位内容。

证据导出与 `compile` 是**两次独立编译**：相同模型和选项产生相同的项目 Pass 顺序及 TVM 默认 pipeline，但不把两次原生二进制视作字节相同。`linear` 证据对应 `compile --mode custom`；`scheduled` 先运行 reshape Pass，再在满足条件的 MatMul 处接入第 5 周的 `vectorize` 调度，随后由 TVM 默认 pipeline 编译。两种模式是独立实验，并非同时融合和调度。

导出工件包含 CPU 原生库和 manifest，ONNX 权重已嵌入。加载时核对库 hash/大小、TVM 版本、系统和架构，再由 TVM VM 调用；hash 检测误配，**不能证明原生代码来源可信**。只加载可信来源的工件；这些检查也不证明跨 CPU、ABI 或不同构建环境兼容，当前仅在实际执行的主机验证。

TVM 提供 ONNX importer、标准 lowering、LLVM codegen 和 VM；本项目实现 Pass、调度接入、工件管理、证据收集及校验。CUDA 需要真实 NVIDIA 环境及独立计时和测试，本阶段未验证，不将可选后端视为已支持。
