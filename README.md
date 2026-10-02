# sync

日服（JP）`loadingbg` / `gallerypic` 资源的增量同步仓库。

`.github/workflows/jp-assets.yml` 每天运行一次：用 [azlassets](https://github.com/nobbyfix/AzurLane-AssetDownloader)
下载资源 → 从 `ClientAssets/JP/AssetBundles/` 收集这两个目录 → 与上一次快照 diff → 发布到 Release
[`jp-loadingbg-latest`](https://github.com/stephensund/sync/releases/tag/jp-loadingbg-latest)。

## 产物

| Asset | 说明 |
|---|---|
| `loadingbg_full.zip` | loadingbg 完整快照（`last_*` + `current_*` 合并） |
| `gallerypic_full.zip` | gallerypic 完整快照 |
| `loadingbg_diff.zip` / `gallerypic_diff.zip` | 本次相比上次的增量（仅在有变化时上传） |
| `jp-client-state.tar` | azlassets 逻辑状态（version / hashes / difflog，不含 AssetBundles） |
| `meta.txt` | `trigger` / `mode` / `generated_at` / `has_diff` |

## 为什么需要外部调度器

GitHub 原生 `schedule` 只是 **best-effort**，官方不保证时间。自 **2026-08-26** 起全球范围出现大面积
调度积压（社区讨论 [#206019](https://github.com/orgs/community/discussions/206019)、
[#208924](https://github.com/orgs/community/discussions/208924)），本仓库实测：

| 区间 | 相对 16:00（北京）的延迟 |
|---|---|
| 2026-08-21 ~ 08-26 | 0.26 ~ 0.56 h（正常抖动） |
| 2026-08-27 ~ 10-02 | **3.44 ~ 11.69 h**（平均 4.77 h） |

排除项：`created_at == run_started_at`（不是 runner 排队），cron 表达式正确，也没有整次漏跑——
是**定时事件本身被推迟创建**，属 GitHub 调度器侧问题；把 cron 改到奇数分钟无效（社区已证伪）。

因此本仓库采用双轨：

1. **主路径**：外部调度器定时 POST `workflow_dispatch` 接口 → 走实时事件通道，秒级启动。
2. **兜底**：保留原生 `schedule`（UTC 8:00）。当天若外部调度已成功触发过，`guard` job 会跳过迟到的
   定时运行，避免重复。

## 接入外部调度器

> 需要一把 GitHub PAT：**classic token 需 `repo` + `workflow` scope**（本仓库现用 token 已满足）；
> 若用 fine-grained token，需要 `Actions: read and write`。
> ⚠️ 本仓库是 public，**不要把 token 提交进仓库**，只放在外部调度服务里。

被调用的接口：

```
POST https://api.github.com/repos/stephensund/sync/actions/workflows/jp-assets.yml/dispatches
```

### 方式 A：cron-job.org（免费、最简单）

1. 注册登录 <https://cron-job.org>（免费版即可）。
2. **Create cronjob**：
   - **Title**：`sync jp assets`
   - **URL**：`https://api.github.com/repos/stephensund/sync/actions/workflows/jp-assets.yml/dispatches`
   - **Schedule**：Every day，`16:00`，时区选 `Asia/Shanghai`
   - **Request method**：`POST`
   - **Request body**：`{"ref":"main"}`
   - **Headers**：
     ```
     Accept: application/vnd.github+json
     Authorization: Bearer <你的 PAT>
     X-GitHub-Api-Version: 2022-11-28
     Content-Type: application/json
     ```
   - **成功判定**：填 HTTP `204`（GitHub 成功返回 204 且无 body），失败会邮件告警。
3. 保存后用 **Test run** 验证一次，再去 Actions 页面确认出现一条 `workflow_dispatch` 运行。

### 方式 B：Cloudflare Worker（Cron Triggers）

```js
export default {
  async scheduled(event, env, ctx) {
    ctx.waitUntil(fetch(
      "https://api.github.com/repos/stephensund/sync/actions/workflows/jp-assets.yml/dispatches",
      {
        method: "POST",
        headers: {
          Accept: "application/vnd.github+json",
          Authorization: `Bearer ${env.GH_PAT}`,
          "X-GitHub-Api-Version": "2022-11-28",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ ref: "main" }),
      }
    ));
  },
};
```

`wrangler.toml`：

```toml
name = "sync-jp-assets"
main = "src/index.js"
compatibility_date = "2026-10-01"

[triggers]
crons = ["0 8 * * *"]   # UTC 8:00 = 北京 16:00
```

`GH_PAT` 用 `wrangler secret put GH_PAT` 写入。

## 手动 / 本地触发

```bash
# 用 gh CLI
gh workflow run jp-assets.yml -R stephensund/sync

# 用 curl（等价于外部调度器发的那一发，期望 204）
curl -i -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer $GH_PAT" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/stephensund/sync/actions/workflows/jp-assets.yml/dispatches \
  -d '{"ref":"main"}'

# 强制冷启动（全量重下，约 40 分钟）
# -d '{"ref":"main","inputs":{"cold_start":true}}'
```

## 运行模式

| 模式 | 触发条件 | 行为 |
|---|---|---|
| `cold` | cache 未命中，或手动传 `cold_start=true` | `azl download JP --force-refresh` 全量下载，产出 `*_full.zip` |
| `incremental` | cache 命中 | 只下载 diff，产出 `*_diff.zip` + 合并后的 `*_full.zip` |

缓存（`actions/cache`）保存 `jp-client-state.tar` + `last_loadingbg/` + `last_gallerypic/`；
cache key 每次运行唯一（`jp-assets-v2-<os>-<run_id>`）配合 `restore-keys` 前缀匹配，确保每次都能写入新缓存。

## 已知注意事项

- **public 仓库 60 天无 commit 会自动禁用 `schedule`**：本仓库最后 commit 为 2026-08-20，
  约 **2026-10-19** 起兜底的定时触发可能静默失效（`workflow_dispatch` 主路径不受影响）。
  需要保留兜底时，定期推一个 commit，或把仓库改为 private。
- `delete_asset_safe` 等上游行为依赖 workflow 里的 runtime patch（支持删除目录），
  升级 azlassets **主版本**前先复查这些 patch 是否仍适用。
- `azlassets` 目前未锁版本（裸 `pip install azlassets`），上游曾在一个月内发生 breaking change（4.4 → 5.2）。
