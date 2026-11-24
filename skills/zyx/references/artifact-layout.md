# 产物目录与回传规范

> 与 `../shared/artifacts/convention.md` 对齐；本文件只讲 zyx 收口时的目录落点与回传格式。

## 1. 产物根目录

- 桌面产物根目录：`<桌面>/zyx-output/`。
- **桌面目录跨平台探测与回退顺序**（与 `../scripts/desktop-dir.sh` 一致）：
  1. 系统桌面（macOS `~/Desktop`；Linux `~/Desktop` / `~/桌面`；Windows `%USERPROFILE%/Desktop`）；
  2. 文档目录（`~/Documents`）；
  3. 主目录 `$HOME` 下的 `zyx-output/`。
- 根目录下**按生成产物的 Skill 名分一级子目录**，目录名见下表。

| 来源 Skill | 一级子目录名 | 示例 |
|---|---|---|
| 女娲 nuwa-skill | `nuwa/` | `~/Desktop/zyx-output/nuwa/芒格-perspective/` |
| 大师 master-skill | `master/` | `~/Desktop/zyx-output/master/跨境电商-master/` |
| 仓颉 cangjie-skill | `cangjie/` | `~/Desktop/zyx-output/cangjie/穷查理宝典/` |
| dbs 家族 | `dbs/` | `~/Desktop/zyx-output/dbs/2026-11-23-生意诊断/` |
| 内容生产 video-studio | `video/` | `~/Desktop/zyx-output/video/武侠打斗分镜/` |
| 产物迭代 f2r | `f2r/` | `~/Desktop/zyx-output/f2r/文案v2-20261124/` |

## 2. 目录内部结构

每个产物子目录内部遵循 `../shared/artifacts/convention.md`：
- 产物主体（SKILL.md / 能力卡 / 报告 / 成稿）；
- `sources/`：来源元数据与摘录（不存长段原文，版权安全）；
- `evals/`：Darwin 式压测用例与结果（适用时）；
- `MANIFEST.md`：产物清单、来源 Skill 与版本、校验状态、生成时间。

## 3. 命名规则

- 子目录用小写英文 slug 或中文短名，不含空格；多词用连字符 `-`。
- 同一原料重复蒸馏时，新版本加日期后缀 `YYYYMMDD`，不覆盖旧目录；确需覆盖前先备份。
- 禁止用 agent id、会话 id、临时文件名作为目录名。

## 4. 规范目录生成（脚本）

`../scripts/artifact-dir.sh` 给定「来源 + 产物名 + 可选日期」，返回规范目录并可创建：

```bash
# 只返回路径
bash ../scripts/artifact-dir.sh cangjie "穷查理宝典"
# 创建目录（含 sources/ 与 evals/ 子目录）
bash ../scripts/artifact-dir.sh video "武侠打斗分镜" --create
# 带日期后缀
bash ../scripts/artifact-dir.sh nuwa "芒格视角" --date 20261124
```

- 来源白名单：`nuwa master cangjie dbs video f2r`；非法来源报错退出 1。
- 产物名做 slug 化（去特殊字符、空格转 `-`）；未传日期时不带日期后缀。
- 桌面根目录由 `../scripts/desktop-dir.sh` 按第 1 节回退顺序探测，脚本不写死宿主路径。

## 5. 隐私与脱敏边界（强制）

- 产物落盘前必过脱敏检查：个人手机号、身份证、银行卡、住址、内部账号、未公开客户名、未签保密协议的商业数据一律不写入产物目录；必要时以占位符（如 `<手机号>`、`<客户A>`）替代。
- 上游素材原文归入 `sources/` 时同样先脱敏；含敏感信息的原始素材不进可外发的产物包。
- 脱敏作为发布前必过项，见 `../shared/quality/qa-audit.md`。

## 6. 收口回传格式

全部产物就位后，zyx 向用户回传一张清单，每条包含：

| 字段 | 说明 |
|---|---|
| 产物名称 | 产物标题 / slug |
| 来源 Skill | R1 女娲 / R2 大师 / R3 仓颉 / R4 dbs / R5 video-studio / R6 f2r，及所用版本号 |
| 产物路径 | 桌面产物目录下的绝对路径 |
| 校验状态 | 三重验证 / 质检 / 压测通过情况（未跑的项如实标注「未测」） |
| 边界与限制 | 适用条件、反例、未覆盖部分 |

回传前核对：每个产物都落在对应来源 Skill 的子目录内；`MANIFEST.md` 与实际文件一致；没有遗留临时文件、缓存或本机隐藏配置。

## 7. 远端产物接口（预留，未启用）

- 当前产物**只落本机目录**，不自动 push 到任何远端仓库。
- 预留的远端 `fetch` / `commit` 接口仅为占位设计：后续若要把产物回传到指定仓库，需单独授权、单独指定目标仓库与分支，并在推送前过第 5 节脱敏与 `../shared/quality/qa-audit.md` 清单。
- 未授权前，zyx 不调用任何远端写接口。
