#!/bin/sh

nohup gunicorn start_mira_server:app -c iiifoo_gunicorn_conf.py
