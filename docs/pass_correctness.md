# 冗余 reshape 链归并

本项目实现一个独立的 Relax function pass，使用 DPL 匹配 `reshape(reshape(x, s1), s2)`，在条件成立时将外层改写为对 `x` 的一次 reshape。TVM 自带类似变换；该实验展示规则、保护和验证流程，不宣称性能提升，也不将 TVM 的默认优化归为项目实现。

## 语义条件与边界

- 只匹配两个 Relax `reshape` 调用。输入、中间结果和输出都必须有明确的 tensor 类型、相同的已知 dtype 和完全静态形状。
- 三者的元素总数必须一致。维度必须为正整数；零维标量形状 `()` 允许，含零长度或负维度的形状保守跳过。符号维度、未知形状或 dtype 也跳过并记录原因。
- 外层目标由已验证的最终输出类型重新构造为具体形状，不直接迁移依赖原中间输入的目标表达式；因此不会在新输入上重新解释原目标的 `0`/`-1`。若类型不能证明这些条件则不改写。
- 只替换外层 reshape 的输入；中间结果仍有其他消费者时保留该绑定，无其他消费者时由 DPL 的重写清除无用绑定。对标记为 Primitive 的函数不做处理。
- Pass 保持原 IRModule 不变，返回新模块。禁用时原样返回，未知形状正常跳过；意外异常时回退到原模块并在报告中标记失败，CLI 返回非零，不伪装成成功。

## 使用与验证

`python examples/02_relax_pass.py --output-dir runs/reshape-demo` 生成前后 IR 与报告，并用 LLVM VM 编译执行两版，验证输出相等。对于静态 ONNX 模型，可运行 `python -m minicompiler reshape --model <model.onnx> --output-dir <新目录>`；加 `--disable` 可生成未改写的对照。每次运行需要新的输出路径，以免误读旧结果。文本 IR 仅供检查，不是包含完整权重的独立可执行工件。

报告中 `status`、`matches`、`rewrites`、`skipped` 和 `events` 记录一次调用的状态和 DPL 回调结果；跳过事件附带原因，成功事件附带形状与 dtype。异常回退时，`rewrites` 归零，`attempted_rewrites` 与 `rolled_back` 事件记录已撤销的尝试。这些数值是图改写统计，不是运行时 kernel 调用次数。

测试包含多种静态形状、共享消费者、动态维、零长度、标量、推断维度、禁用与数值对照。TVM 的实际构造和编译能力限制了部分无效形状的构图；对无法证明安全的形状采用不改写策略。无性能基准或加速声明。
