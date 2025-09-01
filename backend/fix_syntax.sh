#!/bin/bash
# Quick syntax fix for the double brace error
cd /Users/hiufungmak/grace-papers-gen/backend
cp main_with_agent.py main_with_agent_broken.py
sed 's/}}$/}/' main_with_agent_broken.py > main_with_agent.py
echo "Fixed syntax error - replaced '}}' with '}'"
