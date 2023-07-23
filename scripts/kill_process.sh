#!/bin/bash

# 查找进程ID
process_id=$(pgrep -f "accelerate launch")

if [ -n "$process_id" ]; then
  echo "Found process ID: $process_id"
  # 终止进程
  kill "$process_id"
  echo "Process terminated."
else
  echo "No process found."
fi
