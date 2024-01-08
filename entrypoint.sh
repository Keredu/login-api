#!/bin/bash
. /tmp/load_env.sh
rm -rf /tmp/*
exec "$@"
