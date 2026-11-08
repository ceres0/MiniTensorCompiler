# MiniTensorCompiler

基于 Apache TVM Relax / TensorIR 的模型编译实验项目。当前阶段聚焦环境锁定、LLVM CPU 上的最小执行与工件导出；图优化、模型导入和性能结果尚未完成。Relax、LLVM codegen 和 VM 来自 TVM。

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

## 参考资料

TVM 源码和教程参考固定在 [v0.27.0 tag](https://github.com/apache/tvm/tree/v0.27.0)（release commit `4d0ac16`）。PyPI 的 wheel 版本固定为 `0.27.0.post1`；不能仅凭 tag 假定 post-release wheel 与源码完全一致。后续 API 以安装的 wheel 和其对应源码为准。
