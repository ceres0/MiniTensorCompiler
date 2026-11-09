# 深挖实验原始证据：2026-11-09

在用户提供的 Linux x86_64 服务器上运行，CPU 为 AMD EPYC 7B12、GPU 为 RTX 3090（驱动 580.105.08，容器内单卡编号 0），镜像 `minitensorcompiler:gpu-validation`，TVM 0.27.0.post1、Python 3.11.15。源码以只读目录挂载，未包含 `.git`；因此 JSON 内的 git 字段是 null，而不是伪造的 commit。按实验构建的本地归档及 SHA-256：

- `cpu/`、`gpu/`、`fused/`、`qkv.json`：commit `d901b0b`，源码归档 SHA-256 `21700a2b49d6c7b9e1c3332f4fb2d4a006935f212a76e6b4ed506d5fb730f6ce`。
- `cpu-v2/`、`gpu-v2/`、`gpu-holdout/`、`qkv-holdout.json`：commit `8a192f3`，源码归档 SHA-256 `80a104de0018fc40d6c1783fc9d94b4e2ac30a5e18d0494aa54e7fd318e36886`。两次 commit 中 QKV 测试代码相同。

各容器启动时限制在逻辑 CPU 0、1（不同物理核心），CPU 实验使用 TVM 两线程；其中 fused 脚本自身未记录亲和性，绑定信息来自实际启动命令。绑定不是独占核心，电源、频率和其他负载未控制。GPU 选择宿主 GPU 1，其他工作负载仍在服务器上运行。CPU/GPU 实验串行，不能假定无噪声。默认 CPU 对照为固定版本 TVM 原生未调优默认路径，不是最佳 BLAS 或 autotuned 结果。实际时间边界和每次样本见各 JSON；不能把结果推广为跨设备的稳定加速。

## CPU MatMul

`cpu/report.json` 保留首次失败：`[32,256,256]` 上全部版本（含 TVM Default）与 NumPy FP32 在初始 `rtol=1e-4, atol=1e-5` 下未通过；最大绝对误差 3.433e-5，混合容差是否通过还取决于每个参考值。故该形状没有性能结果。

`cpu-v2/report.json` 使用明确记录的 `rtol=1e-4, atol=5e-5`，所有版本均与 NumPy FP32 和 FP64 累加参考通过；该形状 TVM Default 对 FP64 的最大绝对误差约 5.045e-5、RMSE 4.663e-6，混合容差允许项包含相对误差。不能据此声称所有模型都适用此容差。按轮随机交错，30 次预热、6 轮每轮 100 次；保留各版本 TIR 和实际 LLVM 汇编。`cpu-v2/m32_k256_n256/vectorize.s` 可观察 `mulps`、`addps` 指令，但尚未用 profiler 或硬件计数证明缓存命中或实际访存量。服务器 `perf` 对当前内核不可用，`perf_event_paranoid=4`，未修改系统配置。

## CUDA MatMul

`gpu/report.json` 保留原始失败：部分自定义 kernel 被默认 DLight 重复调度。修复后 `gpu-v2/report.json` 对四种形状均与 NumPy 对照通过；`gpu-holdout/report.json` 使用不同 seed 再次通过。输出映射仅将输出轴映射到 block/thread，K 仍串行，没有 shared-memory 优化。每次 VM 调用后同步，时间包含 Python、输出分配和同步，不是 kernel-only 延迟。30 次预热、6 轮每轮 100 次、交替顺序；未采集 Nsight kernel launch、带宽或 occupancy。小形状存在退化。

## 线性融合和 QKV

`fused/` 包含 Default、已有 graph-fused 和手写 scalar-fused TIR 的数值及性能对照。手写源 TIR 无完整 M×N 中间 tensor，但没有证明实际寄存器驻留或内存流量；三个样本中 scalar-fused 相对 graph-fused 未见加速。它尚未接入 ONNX 编译主线。

`qkv.json` 拆分记录编译期 NumPy 拼接、slice-only 诊断、逻辑张量容量及各轮执行样本。逻辑容量不是峰值内存；阈值筛选不是统计置信区间或生产成本模型。首轮 `[8,512,512]` 达到实验候选筛选，但换 seed 的 `qkv-holdout.json` 未通过筛选；不自动启用，也不声称稳定收益。
