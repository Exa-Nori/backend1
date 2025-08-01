#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

print("Content-Type: text/html; charset=utf-8")
print()
print("<!DOCTYPE html>")
print("<html>")
print("<head>")
print("<title>CGI Python Test</title>")
print("<meta charset='utf-8'>")
print("</head>")
print("<body>")
print("<h1>CGI Python работает!</h1>")
print("<p>Версия Python:", sys.version, "</p>")
print("<p>Путь к Python:", sys.executable, "</p>")
print("<p>Текущая директория:", os.getcwd(), "</p>")
print("<p>Переменные окружения:</p>")
print("<ul>")
for key, value in os.environ.items():
    if key.startswith('HTTP_') or key in ['PATH', 'PYTHONPATH']:
        print(f"<li><strong>{key}:</strong> {value}</li>")
print("</ul>")
print("</body>")
print("</html>") 