#!/bin/bash
# Setup llama.cpp models for TradingAgents
#
# This script helps download models for use with llama.cpp server

set -e

PROJECT_ROOT="/home/nikhil/Code/TradingAgents"
MODELS_DIR="$PROJECT_ROOT/models"

echo "========================================="
echo "llama.cpp Model Setup for TradingAgents"
echo "========================================="
echo ""

# Create models directory
mkdir -p "$MODELS_DIR"

echo "Model Options:"
echo "1. DeepSeek-R1-Distill-Llama-8B (Recommended - 5.4GB)"
echo "   - Fast reasoning model, good for screening"
echo ""
echo "2. Qwen2.5-7B-Instruct (Alternative - 4.7GB)"
echo "   - Balanced performance"
echo ""
echo "3. Skip download (models already exist)"
echo ""

read -p "Select option (1-3): " choice

case $choice in
  1)
    echo ""
    echo "Downloading DeepSeek-R1-Distill-Llama-8B..."
    mkdir -p "$MODELS_DIR/deepseek-r1-distill-llama-8b"
    cd "$MODELS_DIR/deepseek-r1-distill-llama-8b"

    MODEL_URL="https://huggingface.co/bartowski/DeepSeek-R1-Distill-Llama-8B-GGUF/resolve/main/DeepSeek-R1-Distill-Llama-8B-Q5_K_M.gguf"
    echo "Downloading from: $MODEL_URL"
    wget -c "$MODEL_URL" -O DeepSeek-R1-Distill-Llama-8B-Q5_K_M.gguf

    echo "✓ Model downloaded successfully!"
    ;;

  2)
    echo ""
    echo "Downloading Qwen2.5-7B-Instruct..."
    mkdir -p "$MODELS_DIR/qwen2.5-7b-instruct"
    cd "$MODELS_DIR/qwen2.5-7b-instruct"

    MODEL_URL="https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF/resolve/main/qwen2.5-7b-instruct-q5_k_m.gguf"
    echo "Downloading from: $MODEL_URL"
    wget -c "$MODEL_URL" -O qwen2.5-7b-instruct-q5_k_m.gguf

    echo "✓ Model downloaded successfully!"

    # Update config for qwen
    sed -i 's/deepseek-r1-distill-llama-8b/qwen2.5-7b-instruct/g' "$PROJECT_ROOT/configs/llamacpp_server.json"
    sed -i 's/DeepSeek-R1-Distill-Llama-8B-Q5_K_M.gguf/qwen2.5-7b-instruct-q5_k_m.gguf/g' "$PROJECT_ROOT/configs/llamacpp_server.json"
    ;;

  3)
    echo "Skipping download..."
    ;;

  *)
    echo "Invalid option"
    exit 1
    ;;
esac

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "To start the llama.cpp server:"
echo "  cd $PROJECT_ROOT"
echo "  conda activate tradingagents"
echo "  ./scripts/start_llamacpp_server.sh"
echo ""
echo "Then in another terminal, run tests:"
echo "  conda activate tradingagents"
echo "  python test_discovery.py"
echo ""
