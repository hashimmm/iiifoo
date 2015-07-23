#!/bin/sh

nohup gunicorn start_iiifoo_server:app -c iiifoo_gunicorn_conf.py
