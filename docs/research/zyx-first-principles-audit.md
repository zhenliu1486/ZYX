# ZYX 第一性原理审计（2026-11-25）

> 不看“功能列表”，只看四类状态迁移：安装、路由、上下文、验收。任何一步失败，系统必须回到旧状态或明确报错，不能留下半完成状态。

## 1. 审计发现与修复

| # | 问题（现象） | 根因 | 修复 | 原理 |
|---|---|---|---|---|
| 1 | `install.sh` 先 `rm -rf` 目标目录再复制；复制失败会留下空目录，用户手改也会丢 | 把“安装”当成覆盖写，没当成状态迁移 | stage 复制 → 旧目录备份 → rename 替换；失败自动恢复；备份到 `~/.zyx-backups/` | 安装必须满足“要么旧版完整，要么新版完整”，不能有半安装 |
| 2 | `route.sh` 找不到目标 Skill 时仍返回 0，只打印“未检测到” | 把“提示”当成“成功”，调用方无法区分 | 缺失时退出码 2；新增 `route-selftest.py` 覆盖七类路由 | 路由器不能把“未解析”伪装成“已解析” |
| 3 | Context Card 只检查 `zyx-context/SKILL.md` 是否存在；同名目录/文件可能被写入 | 只校验文件，不校验“目录归谁所有” | 同名目录、同名文件、非托管卡一律拒绝；刷新旧卡失败只警告 | 用户空间不可被静默占用；辅助状态失败不能回滚主操作 |
| 4 | macOS 上 `env-registry.sh` 先选 cron；cron 受 TCC/省电策略影响可能不执行 | 按“命令存在”选调度器，不按“系统保证执行”选 | Darwin 优先 launchd；systemd 路径加引号 | 调度器要选平台真正会执行的路径，不是命令名最熟悉的路径 |
| 5 | `doctor.sh` 只查 `chromium`/`soffice` 命令名，Playwright/libreoffice 可用时仍报缺 | 检查实现细节，不检查能力 | 改为检查 `chromium` 或 Playwright、`libreoffice` 或 `soffice` | 验收要检查“能不能做”，不是“某个二进制叫什么” |
| 6 | `sync-hosts.sh --list-hosts` 仍进入安装循环 | 参数没有在入口分流 | `--list-hosts` 直接交给 `install.sh --list-hosts` 后退出 | 管理命令的语义要唯一，不能“名义列目录，实际跑安装” |

## 2. 验收

- `wiki-selftest.py` 43/43（含 Context 同名目录/文件冲突）
- `route-selftest.py` 8/8（七类映射 + 未知类型拒绝）
- `look-selftest.py` 6/6
- `doctor --full` 全部就绪
- 原子安装实测：旧目录中的自定义文件被完整备份，新版本正常落位
- launchd 分支用 fake `uname`/`launchctl` 模拟注册，plist 与 state 均生成

## 3. 仍未闭环

- macOS 真机当前 `SANDBOX_UNAVAILABLE`，Bash 3.2 与 launchd 未在真机复跑；接入后应执行 `bash scripts/sync-hosts.sh` 和 `bash skills/zyx/scripts/doctor.sh --full`。
- Skill Contract（v2.0 的 entry/state/acceptance/rollback/migration）仍未做；本审计只把现有七类路由的“安装/路由/上下文/验收”四个状态迁移补齐。
