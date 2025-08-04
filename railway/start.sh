#!/bin/bash
echo "Starting L'ÎLE DE RÊVE API..."
gunicorn --bind 0.0.0.0:$PORT app:app 