# Azur Lane Asset Downloader 项目理解

## 两个仓库概览

### 1. AzurLane-AssetDownloader（上游）
- **地址**: `nobbyfix/AzurLane-AssetDownloader`
- **性质**: Python CLI 工具包 (`pip install azlassets`)
- **核心模块**: `azl download [CLIENT]`、`azl extract [CLIENT]`、`azl import [FILE]`
- **支持客户端**: EN, JP, CN, KR, TW
- **关键类**: `VersionType` 枚举 (AZL, CV, L2D, PIC, BGM, CIPHER, MANGA, PAINTING, DORM, MAP)
- **已知问题**: `VersionType` 的 `__hash__ = None`，导致 set/dict 操作报错

### 2. sync（用户定制）
- **地址**: `stephensund/sync`
- **性质**: GitHub Actions 自动化仓库，定时/手动拉取日服 loadingbg
- **工作流文件**: `.github/workflows/jp-loadingbg.yml`
- **触发方式**: `workflow_dispatch`（手动触发）

## sync 工作流程详解

```
1. Checkout 仓库
2. 安装 azlassets v4.0.0
3. 恢复 azlassets state cache（jp-client-state.tar）
   → 从上一个 Release (jp-loadingbg-latest) 的 assets 下载
4. 执行 azl download JP
   → 包含 runtime patch：VT.__hash__ = lambda self: hash(str(self))
5. 恢复上次的 loadingbg_full.zip → last_loadingbg/
6. 运行 collect_loadingbg.py
   → 从 ClientAssets/JP/AssetBundles/loadingbg 复制到 current_loadingbg/
7. 运行 diff_and_zip.sh
   → 对比 last_loadingbg 和 current_loadingbg
   → 生成 loadingbg_full.zip 和 loadingbg_diff.zip
8. 打包 state cache（jp-client-state.tar，仅 ClientAssets/JP 逻辑状态，去除 AssetBundles）
9. 发布 Release (tag: jp-loadingbg-latest)
   → 上传: jp-client-state.tar, loadingbg_full.zip, meta.txt, loadingbg_diff.zip(若有更新)
```

## 关键文件

| 文件 | 作用 |
|------|------|
| `scripts/collect_loadingbg.py` | 把 `ClientAssets/JP/AssetBundles/loadingbg/*` 复制到 `current_loadingbg/` |
| `scripts/diff_and_zip.sh` | 对比新旧 loadingbg，生成 full 和 diff 两个 zip |
| `.github/workflows/jp-loadingbg.yml` | 完整 Actions 流程 |

## 潜在维护关注点

1. **`VersionType.__hash__` 问题** — 上游代码 Bug，已在 Actions 中用 runtime patch 绕过
2. **state cache** — 仅保留逻辑状态（不含 AssetBundles），用于增量更新
3. **Release tag 固定** — 始终用 `jp-loadingbg-latest`，不递增版本号
4. **若无更新** — `diff_and_zip.sh` 会生成空的 `loadingbg_full.zip`（以 last_loadingbg 为准）

## 状态
- ✅ 两个仓库已 clone 到 `D:\GitHub Repositories\`
- ✅ 工作流程已理解
- ⏳ 待用户进一步指示
