#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("Content-Type: text/html\n")
print("<html><body>")
print("<h1>Python работает на IP Manager!</h1>")
print("<p>Если вы видите это сообщение, Python настроен правильно.</p>")
print("<p>Время сервера:", __import__('datetime').datetime.now(), "</p>")
print("</body></html>") 