# Wiki-Linux Diagnostic

- generated_utc: 2026-05-07 12:52:41 UTC
- parent_root_exists: yes
- repo_root: /home/sourov/Documents/wiki-linux/wiki-linux
- wiki_root: /home/sourov/wiki
- workspace_branch: main
- workspace_pending_changes: 57
- wiki_branch: HEAD
- wiki_pending_changes: 0

## Services
- wiki-ollama: active
- wiki-openwebui: active
- wiki-monitor: activating
inactive
- wiki-sync.timer: active
- wiki-wallpaper.timer: active
- wiki-screensaver-watch: active

## Ports
- 11434: listening
- 8080: listening

## Open WebUI State
- canonical_db: /home/sourov/.local/share/wiki-linux/openwebui-data/webui.db
- canonical_db_size: 561152
- legacy_db: /home/sourov/.config/open-webui/data/webui.db
- legacy_db_size: 561152
- extra_desktop_instance_detected: yes

## Processes
```
711 /home/sourov/.config/open-webui/python/bin/python /home/sourov/.config/open-webui/python/bin/open-webui serve --host 127.0.0.1 --port 8080
10552 /usr/lib/electron41/electron /usr/lib/open-webui/app.asar --ozone-platform-hint=auto --no-sandbox --enable-features=GlobalShortcutsPortal,WaylandTextInput
10586 /proc/self/exe --type=utility --utility-sub-type=network.mojom.NetworkService --lang=en-US --service-sandbox-type=none --no-sandbox --disable-dev-shm-usage --enable-crash-reporter=4e8f2de7-6d72-4444-9369-76d58427b2f7,no_channel --user-data-dir=/home/sourov/.config/open-webui --shared-files=v8_context_snapshot_data:100 --field-trial-handle=3,i,3834671093311507853,1027076555898867124,262144 --enable-features=GlobalShortcutsPortal,PdfUseShowSaveFilePicker,WaylandTextInput --disable-features=DropInputEventsWhilePaintHolding,LocalNetworkAccessChecks,ScreenAIOCREnabled,SpareRendererForSitePerProcess,TraceSiteInstanceGetProcessCreation --variations-seed-version --pseudonymization-salt-handle=7,i,11917968589197360201,6175511814728290685,4 --trace-process-track-uuid=3190708989122997041
10768 /home/sourov/.config/open-webui/llama.cpp/b9050/llama-b9050/llama-server --host 127.0.0.1 --port 18881 --models-dir /home/sourov/.config/open-webui/models
10861 /proc/self/exe --type=renderer --enable-crash-reporter=4e8f2de7-6d72-4444-9369-76d58427b2f7,no_channel --user-data-dir=/home/sourov/.config/open-webui --app-path=/usr/lib/open-webui/app.asar --no-sandbox --no-zygote --no-sandbox --disable-dev-shm-usage --ozone-platform=x11 --disable-gpu-compositing --lang=en-US --num-raster-threads=4 --enable-main-frame-before-activation --renderer-client-id=4 --time-ticks-at-unix-epoch=-1778156592576575 --launch-time-ticks=459696831 --shared-files=v8_context_snapshot_data:100 --field-trial-handle=3,i,3834671093311507853,1027076555898867124,262144 --enable-features=GlobalShortcutsPortal,PdfUseShowSaveFilePicker,WaylandTextInput --disable-features=DropInputEventsWhilePaintHolding,LocalNetworkAccessChecks,ScreenAIOCREnabled,SpareRendererForSitePerProcess,TraceSiteInstanceGetProcessCreation --variations-seed-version --pseudonymization-salt-handle=7,i,11917968589197360201,6175511814728290685,4 --trace-process-track-uuid=3190708990060038890
10875 /home/sourov/.config/open-webui/python/bin/uv run open-webui serve --host 127.0.0.1 --port 8081
10880 /home/sourov/.config/open-webui/python/bin/python /home/sourov/.config/open-webui/python/bin/open-webui serve --host 127.0.0.1 --port 8081
10895 /proc/self/exe --type=utility --utility-sub-type=audio.mojom.AudioService --lang=en-US --service-sandbox-type=none --no-sandbox --disable-dev-shm-usage --enable-crash-reporter=4e8f2de7-6d72-4444-9369-76d58427b2f7,no_channel --user-data-dir=/home/sourov/.config/open-webui --shared-files=v8_context_snapshot_data:100 --field-trial-handle=3,i,3834671093311507853,1027076555898867124,262144 --enable-features=GlobalShortcutsPortal,PdfUseShowSaveFilePicker,WaylandTextInput --disable-features=DropInputEventsWhilePaintHolding,LocalNetworkAccessChecks,ScreenAIOCREnabled,SpareRendererForSitePerProcess,TraceSiteInstanceGetProcessCreation --variations-seed-version --pseudonymization-salt-handle=7,i,11917968589197360201,6175511814728290685,4 --trace-process-track-uuid=3190708990997080739
```
