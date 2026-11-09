# 线性融合和 QKV 实验

## 线性子图

项目以 DPL 描述 `relu(add(matmul(x, w), bias))` 并提供语义守卫，由 TVM 的 `FuseOpsByPattern` 完成子图提取。只处理 dataflow 内的正整数静态 FP32 `x[M,K]`、`w[K,N]` 和 `bias[N]`；matmul 必须为 add 的左操作数，输出和 bias 广播维度必须严格匹配。权重和偏置可为常量或运行时输入。matmul 或 add 有匹配范围外消费者时保守拒绝；动态形状、未知 dtype 和其他广播同样不改写。DPL 的匹配有交换律，因此规则额外检查实际参数顺序。

`minicompiler linear` 输出原始和分组后的 Relax IR 与报告；`--disable` 禁用，`--keep-params-in-input` 保留 ONNX 权重输入。`matches` 是 TVM 匹配检查回调数，`accepted` 是守卫通过的候选，`rewrites` 是实际新增 Composite 调用数，三者不应混同。失败时回退原图并报告错误。此步骤的 IR dump 用于检查，不是完整含权重的可执行物。

`examples/05_linear_fusion.py` 对前后图分别执行独立的 `LegalizeOps`/`FuseTIR` 用于生成结构性证据，并另从高层图编译数值验证；独立的 IR 演示不用于 benchmark 编译。该示例中的静态 TIR PrimFunc 从 3 个变成 1 个，但融合后的 TIR 仍有中间 buffer 和多个循环。静态函数数不等于运行时调用次数，不能据此宣称已经消除中间写回。

`bench --mode custom` 的正式比较使用同一 ONNX、固定输入、权重和线程：TVM Default 使用固定版本原生流水线；Custom 先执行项目规则，在复刻的固定版本默认 Relax 流水线的 `LegalizeOps` 后插入一次 TVM `FuseTIR`，其余顺序、TIR pipeline、PassContext 和目标一致，避免重复执行 lowering。复刻代码限定 TVM 0.27.0.post1，并有顺序回归测试。两条路径均对 ORT 校验；结果中 `default_over_custom_speedup = median_default / median_custom`，无规则命中时为 null。报告分别记录 Pass 和编译耗时。CPU 亲和性及电源等限制与 [基线方法](benchmark_methodology.md) 相同；性能改善或退化均以实测为准。

## QKV 合并（默认关闭的实验）

`run_merge_qkv` 仅对同一 dataflow block 中相邻的三个 matmul 处理：它们共享同一个输入，输入和三个等形状权重均为静态二维 FP32，且权重为常量。编译期沿输出维拼接权重，替换为一个 matmul 和三个 slice，保留原有输出与消费者；动态权重和不兼容形状均跳过。该路径默认关闭，并要求调用者显式提供 `(M,K,N)` 形状白名单；白名单是人工配置，不是自动成本模型，也不是收益保证。

QKV 形状矩阵使用固定权重和输入，先校验合并前后数值，再对同一 TVM 默认编译路径计时；性能受 shape、切片、缓存、线程数和硬件影响。未在目标环境验证的形状不应被当成已验证获益的生产策略。

```bash
uv run --locked python -m benchmarks.qkv_matrix --threads 1 --output runs/qkv-matrix.json
```

矩阵覆盖 M=1/8/32、K=N=256/512。每个形状在实验中临时加入白名单；脚本按先默认、后合并的顺序分别计时，记录输入和权重哈希、逐次样本及数值误差，不会自动创建生产白名单。输出文件已存在时会拒绝覆盖。
