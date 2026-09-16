# 任务胶囊：ATOM-CLEAN-001

## 身份与状态

- 状态：ACCEPTED
- Owner：当前 Codex 会话
- 写入租约：已释放（范围为本项目目录）
- 所属模块：MOD-CLEAN, MOD-CI
- 所属原型：PROTO-CLEAN-001, PROTO-CI-001
- Atom Goal：GOAL-ATM-001

## 模型路由与预算

- 原子模式：单模型热循环
- budget class：balanced
- Planner / Executor / Verifier：当前 Codex 会话（普通低风险原子，允许自验）
- reasoning effort：当前会话配置
- 费用与额度：UNKNOWN

## 需求映射

| 需求 ID | 关系 | 版本 | 验收条件 |
|---|---|---|---|
| REQ-CLEAN-001 | OWNER | IN-0001/v1 | 发现外层真实 `node_modules`，不跟随链接 |
| REQ-CLEAN-002 | OWNER | IN-0001/v1 | 30 天活动阈值行为可回放 |
| REQ-SAFE-001 | OWNER | IN-0001/v1 | audit/apply、marker、排除、边界与报告齐备 |
| REQ-CI-001 | OWNER | IN-0001/v1 | Jenkins 周期调度、测试门禁、报告归档 |

## Goal 与参考

- 目标状态：交付可独立运行、可 Jenkins 调度的安全清理工作流。
- 行为权威：IN-0001 与已冻结 DEC-0001/0002。
- 实现参考：Python 3.9 标准库、Jenkins Declarative Pipeline 常规结构。
- 目标复刻度：≥90%。
- 非目标：本轮不安装/配置 Jenkins 服务，不立即扫描或删除用户的 Documents 内容。

## 写入范围与硬约束

- 允许修改：`node-modules-cleaner/**`。
- 禁止修改：其他工作流与 Documents 中的用户项目。
- 硬约束：默认 dry-run；真删除前复核边界；不跟随符号链接；清理前测试通过；有审计报告。

## 冻结评分与验证器

| 维度 | 权重 | 验证器 | 证据 |
|---|---:|---|---|
| 核心行为 | 45% | `python3 -m unittest discover -s tests -v` | EVD-0001 |
| 安全边界 | 35% | 同上，涉及 marker/链接/根目录 | EVD-0001 |
| Jenkins 与工程完整性 | 20% | 语法编译、CLI help、Jenkinsfile 结构检查 | EVD-0001 |

## 执行记录

- 设计：以可观察文件活动做保守判定；命令行与 Jenkins 分别采用 audit/apply 安全默认。
- 计划：先实现 CLI 与报告，再接 Jenkins，最后回放安全场景。
- 尝试 1：测试暴露 Python 3.9 `Path.stat` 兼容性及 macOS `/var` 规范化差异。
- 尝试 2：改用 `lstat()` 并在测试中比较规范路径，8 项测试全部通过。

## 输出

- 验收报告：`.agent-native/reports/ATOM-CLEAN-001.md`
- 当前证据：EVD-0001
- 结论：ACCEPTED
