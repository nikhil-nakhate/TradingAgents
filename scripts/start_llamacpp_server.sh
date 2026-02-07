#!/bin/bash
# Start llama.cpp server with multi-model support
#
# Usage:
#   ./scripts/start_llamacpp_server.sh                    # Use default config
#   ./scripts/start_llamacpp_server.sh custom_config.json # Use custom config

set -e

CONFIG_FILE="${1:-configs/llamacpp_server.json}"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Config file not found: $CONFIG_FILE"
    echo ""
    echo "Usage: $0 [config_file]"
    echo ""
    echo "Please create a config file first. Example:"
    echo "  cp configs/llamacpp_server.json.example configs/llamacpp_server.json"
    echo "  # Edit the config to specify your model paths"
    echo "  $0"
    exit 1
fi

echo "========================================"
echo "Starting llama.cpp server"
echo "========================================"
echo "Config: $CONFIG_FILE"
echo ""
echo "Server will be available at: http://localhost:8000"
echo "Press Ctrl+C to stop the server"
echo "========================================"
echo ""

# Start the server
python -m llama_cpp.server --config_file "$CONFIG_FILE"
