@echo off
set BASE_DIR=%~dp0
python "%BASE_DIR%.agent\skills\obsidian-llm-brain\builder.py" %*
