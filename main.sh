#!/bin/bash

python banner.py

# Remove old logs
if [ -f 'ai-demo-lab-logs.txt' ]; then
  rm 'ai-demo-lab-logs.txt'
fi


python personal_assistant.py 2> /dataset/ai-demo-lab-logs.txt &
python website_summarizer.py 2> /dataset/ai-demo-lab-logs.txt &

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?