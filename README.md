# Node Modules Cleaner

定期扫描 `Documents` 下的 `node_modules`，清理连续 30 天没有文件系统活动的目录，并为 Jenkins 保留 JSON 审计报告。实现只使用 Python 标准库，无需安装依赖。

## 安全模型

- 只匹配名称精确为 `node_modules` 的真实目录，不跟随符号链接。
- 删除前会再次确认目录仍在扫描根目录内。
- 拒绝扫描文件系统根目录或整个用户主目录。
- 命令行默认是 `audit` 模式，不会删除任何内容。
- 项目根目录或 `node_modules` 内存在 `.node-modules-cleaner-keep` 时永久跳过。
- 每次运行都在 `reports/runtime/` 产生带时间戳的 JSON 报告。

“未使用”按文件系统可观察信号判定：`node_modules` 中文件的 `atime/mtime/ctime`，以及项目根目录、`package.json` 和常见锁文件的时间。只有所有信号都早于阈值时才会进入清理列表。如果磁盘挂载关闭了访问时间更新，纯“只读使用”无法被可靠检测，重要项目应使用 keep marker 或排除规则。

## 本地使用

先做一次预览：

```bash
./bin/cleanup-node-modules --root "$HOME/Documents" --days 30 --mode audit
```

检查 JSON 报告后执行清理：

```bash
./bin/cleanup-node-modules --root "$HOME/Documents" --days 30 --mode apply
```

需要排除的目录写入 `config/excludes.txt`，路径相对于扫描根目录，支持 glob。例如：

```text
archived-project/**
client/important-demo/**
```

## Jenkins 接入

1. 将这个目录放入 Jenkins 能访问的 Git 仓库，新建 **Pipeline from SCM** 任务并指向 `Jenkinsfile`。
2. 让 Jenkins agent 运行用户对 `/Users/artechphy/Documents` 拥有读取和删除权限。不要为此给 Jenkins 整机 root 权限。
3. Jenkinsfile 默认每周日上海时间凌晨 3 点的一个散列时刻运行，阈值 30 天，模式为 `apply`。
4. 首次可手动构建并将 `CLEAN_MODE` 改为 `audit`，确认归档的 JSON 报告后，再使用默认 `apply`。
5. Jenkins 会在每次扫描前执行自动化测试；测试失败时不会进入删除阶段。

Jenkins 参数：

- `CLEAN_ROOT`：扫描根目录，默认 `/Users/artechphy/Documents`。
- `INACTIVE_DAYS`：未活动天数，默认 `30`。
- `CLEAN_MODE`：`apply` 真正删除，`audit` 只预览。

## 验证

```bash
python3 -m unittest discover -s tests -v
PYTHONPYCACHEPREFIX=/tmp/node-modules-cleaner-pycache python3 -m py_compile src/node_modules_cleaner.py
```

运行时返回码为 `0` 表示成功，`1` 表示有个别候选目录处理失败，`2` 表示参数或根目录错误。
