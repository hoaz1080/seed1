@echo off
title seed

setlocal

:: Mở terminal tại thư mục hiện tại
cd /d %~dp0

:: Cài đặt các thư viện từ pip.txt trong lần chạy đầu tiên
python -m pip install -r requirement.txt

:: Chạy seed.py
python seed.py

:: pause
pause

endlocal
