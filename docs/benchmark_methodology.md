# CPU 基线方法

基线复用同一 ONNX 模型及其权重，对静态 FP32 输入使用 NumPy `default_rng` 和记录的 seed 生成标准正态样本。ORT 使用 CPUExecutionProvider、顺序执行、配置的 intra-op 线程数及一个 inter-op 线程；TVM 使用内嵌权重的 Relax 模块、LLVM 目标和 VM，启动时设置 `TVM_NUM_THREADS`，并检查运行时报告的线程数。CLI 必须在新进程中设置线程环境；通过 Python API 调用时须在 TVM 初始化前设置。

先逐输出比较形状及数值，FP32 默认 `rtol=1e-4, atol=1e-5`；报告最大绝对误差、最大相对误差（分母下限 1e-12）和 RMSE。非有限值视为失败，且误差指标记为 null。测试还覆盖 MLP batch 1/8/32、CNN batch 1/8 的固定随机、零和 ±100 输入。正确性失败后不进行计时。

每个系统先预热，然后独立测多轮，JSON 保存每次耗时及全部样本的 median、p95。输入准备、ONNX 加载和编译、ORT session 创建以及显式的 TVM 输出到 NumPy 转换均不计入推理时间；计时包括 Python API 调用及运行时输出分配。ORT 接口直接返回 NumPy 数组，TVM 返回 runtime tensor，因此不同系统接口开销并不完全相同。CPU 调用同步完成；这里不适用于异步 GPU 计时。

报告中的 ONNX 加载、检查、形状推断与 Relax 导入是合并计时；TVM 编译单独计时，不包括 Python 启动、VM 初始化、ORT session 创建或推理。主文件 SHA-256 不覆盖外置 ONNX 数据文件；使用外置数据时应另外保存这些文件。报告还记录依赖、目标、模型形状、seed、线程及 Git commit/工作区是否有未提交更改。

报告同时拆分 ONNX 加载检查与 Relax 导入，并在同一次真实编译的 PassContext 内记录 PassInstrument 事件；`inclusive_ms` 包含嵌套 Pass，不能相加，`exclusive_ms` 扣除嵌套 Pass 时间但仍包含回调开销。插桩本身会影响编译耗时；TVM 总 build 时间不是单独的 codegen 时间，无法准确界定的 codegen 和 schedule 时间为 null。Custom 模式先编译 Default 再编译 Custom，因此不能将后者称为严格冷编译；suite 在独立子进程运行每项，但不控制系统缓存。静态 PrimFunc 数来自标注 Pass 后的 IR，不是运行时调用次数；未接 runtime profiler 的 `runtime_kernel_invocations` 为 null。

`default` 是 TVM 0.27.0.post1 的原生 CPU 默认 Relax/TIR 编译流程；`nofusion` 在相同流程中显式禁用 `FuseOps` 和 `FuseTIR`。该版本默认 CPU 流程本身不含这两个 Pass，因此两者可能完全相同，NoFusion 仅供诊断。不要将 ORT 与 TVM 之间的差异称为项目优化收益；后续自定义优化必须与相同配置的 TVM Default 比较。

本项目不自动控制 CPU 亲和性、电源策略或系统负载，报告如实标记为未控制。正式比较需在同一台机器固定这些条件，并确认线程数、模型与输入一致；目前的 macOS 本地运行不代表参考 Linux x86_64 平台已验证。

可选编译缓存尚未实现；报告不包含缓存命中率，也不将热缓存响应时间作为编译加速。
