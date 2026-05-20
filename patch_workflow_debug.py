"""Patch workflow to add debug patch that prints all version types from server."""
with open(r'D:\GitHub Repositories\sync\.github\workflows\jp-loadingbg.yml', 'r', encoding='utf-8') as f:
    content = f.read()

old = (
    '          # 让 azl 按 CLI 方式运行 download JP\n'
    '          sys.argv = ["azl", "download", "JP", "--force-refresh"]\n'
    '          azl.main()'
)

new = (
    '          # Patch 3: debug - intercept all version types server returns\n'
    '          import azlassets.downloadmgr as dlmgr\n'
    '          _orig_run = dlmgr.DownloadManager.run if hasattr(dlmgr, "DownloadManager") else None\n'
    '          # Patch versioncontrol.parse_version_string to log all types\n'
    '          import azlassets.versioncontrol as vc\n'
    '          _orig_parse = vc.parse_version_string\n'
    '          def _patched_parse(version_string):\n'
    '              results = _orig_parse(version_string)\n'
    '              for r in results:\n'
    '                  print(f"[debug] parse_version_string: type={r.version_type.name}, version={r.version}")\n'
    '              return results\n'
    '          vc.parse_version_string = _patched_parse\n'
    '          print("[patch] Patched versioncontrol.parse_version_string to log all version types")\n'
    '          # Also patch updater.update to log what gets processed\n'
    '          import asyncio\n'
    '          _orig_update = updater.update\n'
    '          async def _patched_update(version_result, *args, **kwargs):\n'
    '              print(f"[debug] updater.update() called: type={version_result.version_type.name}, version={version_result.version}")\n'
    '              result = await _orig_update(version_result, *args, **kwargs)\n'
    '              print(f"[debug] updater.update() result for {version_result.version_type.name}: {len(result) if result else None} items")\n'
    '              return result\n'
    '          updater.update = _patched_update\n'
    '          print("[patch] Patched updater.update to log results")\n'
    '\n'
    '          # 让 azl 按 CLI 方式运行 download JP\n'
    '          sys.argv = ["azl", "download", "JP", "--force-refresh"]\n'
    '          azl.main()'
)

if old in content:
    content = content.replace(old, new)
    with open(r'D:\GitHub Repositories\sync\.github\workflows\jp-loadingbg.yml', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched successfully")
else:
    print("ERROR: old text not found")
    idx = content.find('让 azl')
    if idx >= 0:
        print("Found similar text at", idx)
        print(repr(content[idx-30:idx+150]))
