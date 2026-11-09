# NVIDIA GPU Docker 运行

本镜像基于固定 digest 的 NVIDIA CUDA 13.0.2 base Ubuntu 24.04，安装固定版本的 CUDA 编译器和 runtime 开发包、Python 3.11.15 及 `uv.lock` 中的基础、测试与 GPU 依赖。默认不安装 PyTorch；完整模型导出依赖可用构建参数启用，Linux PyTorch 包含 CUDA 依赖，首次下载和磁盘开销较大。构建不需要 GPU，运行 CUDA 需要 NVIDIA GPU、宿主驱动以及为 Docker 配置的 NVIDIA Container Toolkit；宿主不需要另外安装 CUDA Toolkit。CUDA 13.0 GA 对 Linux x86_64 的标准驱动要求参见 [NVIDIA 发布说明](https://docs.nvidia.com/cuda/archive/13.0.0/cuda-toolkit-release-notes/)；Docker 配置见 [NVIDIA Container Toolkit 文档](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)。

```bash
docker build -t minitensorcompiler:cuda .
docker run --rm --gpus all minitensorcompiler:cuda nvidia-smi
docker run --rm --gpus all minitensorcompiler:cuda python examples/cuda_add.py
docker run --rm --gpus all minitensorcompiler:cuda python examples/cuda_mlp.py
```

Add 示例编译带 GPU 线程绑定的 TIR，由 Relax VM 在 CUDA 设备运行，显式同步并与 NumPy 对照。MLP 示例默认使用 NumPy 和 ONNX 生成独立的静态 FP32 示例模型，使用 TVM 的 CUDA 专用默认 pipeline 编译，在 GPU 上运行并与同输入的 ONNX Runtime CPU 参考值比较。无 CUDA runtime、不可见 GPU、编译失败或数值不一致时返回非零，不退回 CPU。`nvidia-smi` 只能证明设备透传，不能代替后两项测试。

服务器有多张卡时可以选择设备；容器内该设备通常作为设备 0 出现：

```bash
docker run --rm --gpus '"device=1"' minitensorcompiler:cuda python examples/cuda_mlp.py
```

使用自己的静态 FP32 ONNX 模型：

```bash
docker run --rm --gpus all -v "$PWD/models:/input:ro" minitensorcompiler:cuda python examples/cuda_mlp.py --model /input/mlp.onnx
```

默认命令是 CPU 环境报告 `python -m minicompiler doctor`。若需要 PyTorch 模型导出与完整 CPU suite，先构建完整镜像，再将结果写入宿主目录：

```bash
mkdir -p runs
docker build --build-arg INCLUDE_MODELS=1 -t minitensorcompiler:cuda-full .
docker run --rm --gpus all -v "$PWD/runs:/output" minitensorcompiler:cuda-full python -m benchmarks.run_suite --output-dir /output/docker-suite --threads 1
```

上述 suite、`minicompiler compile` 和 `bench` 仍然是 LLVM CPU 流程，并不会因为容器拥有 GPU 而自动变为 CUDA。CUDA 示例采用独立的 TVM CUDA pipeline；它们是数值和设备验证，不是同步计时的 GPU benchmark。镜像内未复制 `.git`，因此容器内报告中的 Git commit 可能为 null；需要可追溯数据时另行记录构建上下文版本。Docker 容器对宿主文件的写入使用容器用户权限，挂载输出目录时请留意文件所有权。

## 已执行的验证

2026-11-09 在 Linux x86_64 服务器的 RTX 3090（驱动 580.105.08）上，默认轻量镜像成功构建；使用 GPU 1 的容器内 CUDA Add 和默认 MLP 数值对照均通过，MLP 相对 ORT 的最大绝对误差为 4.1723e-7。GPU 相关测试为 9 项通过。完整的 `INCLUDE_MODELS=1` 镜像及其他显卡/驱动版本尚未验证；该运行不是性能基准。
