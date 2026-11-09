# CPU 参考运行的原始报告

本目录保存 `runs/final-suite` 的原始 JSON 副本；大模型、TIR dump 和运行日志仍保存在本地 `runs/`，可通过 `python -m benchmarks.run_suite --output-dir runs/new-suite --threads 1` 重新生成。`suite.json` 中的绝对路径是当次主机的记录，不是跨机器可用路径。

本次运行针对干净代码 commit `bfe7a2c`，Apple M2、macOS arm64、单线程、seed 13；每项预热 30 次，3 轮各 100 次。系统负载、CPU 亲和性和电源策略未控制；PassInstrument 会增加编译时间。不可将本次结果视为跨硬件或稳定收益。

- `mlp.json` 与 `cnn.json` 分别含 Default、项目线性融合路径及 ORT 的真实逐次样本、数值误差和同次编译的 Pass 事件；CNN 无线性规则命中，其 Default/custom 差异不代表本项目图改写收益。
- `mlp_nofusion.json` 是诊断路径；固定版本的 CPU Default 本身没有 FuseOps/FuseTIR。
- `matmul.json` 为 `[8,128,128]` 的 Default 和五级 TIR 调度消融；六形状实验的说明见 `docs/experiments.md`。
- 静态 PrimFunc 数是特定 Pass 后的 IR 快照，运行时 kernel 次数未测量并保留为 null。codegen 和 schedule 的独立耗时也未测得；TVM build 总耗时不能作为二者的替代。
