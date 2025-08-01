#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(__file__))

from app import app

# Для Passenger требуется application
application = app

if __name__ == "__main__":
    app.run() 