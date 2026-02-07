# llama.cpp Integration Guide

## Overview

TradingAgents supports running local LLM models via llama.cpp, providing:
- **Complete Privacy**: All inference runs locally - your trading data never leaves your machine
- **Cost Savings**: No API fees - completely free after model download
- **Custom Models**: Use fine-tuned models trained on your own trading data
- **Offline Operation**: Works without internet connection

## Quick Start

### 1. Install llama-cpp-python with GPU Support

Choose the installation method based on your hardware:

#### For NVIDIA GPU (CUDA):
```bash
CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python[server]
```

#### For Apple Silicon (M1/M2/M3/M4):
```bash
CMAKE_ARGS="-DGGML_METAL=on" pip install llama-cpp-python[server]
```

#### For AMD GPUs (ROCm):
```bash
CMAKE_ARGS="-DGGML_HIPBLAS=on" pip install llama-cpp-python[server]
```

#### For CPU Only:
```bash
pip install llama-cpp-python[server]
```

### 2. Download Models

Use the helper script to download recommended models:

```bash
# List available models
python scripts/download_models.py --list

# Download DeepSeek R1 Distill 8B (fast reasoning, ~5.5GB)
python scripts/download_models.py deepseek-r1-distill-llama-8b

# Download DeepSeek R1 Distill 70B (best reasoning, ~42GB)
python scripts/download_models.py deepseek-r1-distill-llama-70b

# Download Llama 3.3 70B (comprehensive capabilities, ~42GB)
python scripts/download_models.py llama-3.3-70b-instruct

# Optional: Download embedding model for memory system
python scripts/download_models.py nomic-embed-text
```

### 3. Configure Server

Edit `configs/llamacpp_server.json` to specify which models to load:

```json
{
  "host": "0.0.0.0",
  "port": 8000,
  "models": [
    {
      "model": "./models/deepseek-r1-distill-llama-8b/DeepSeek-R1-Distill-Llama-8B-Q5_K_M.gguf",
      "model_alias": "deepseek-r1-distill-llama-8b",
      "n_ctx": 4096,
      "n_gpu_layers": -1,
      "chat_format": "chatml"
    }
  ]
}
```

**Note:** Only load models you have downloaded. Comment out or remove entries for models you don't have.

### 4. Start llama.cpp Server

```bash
./scripts/start_llamacpp_server.sh
```

The server will start and display:
```
========================================
Starting llama.cpp server
========================================
Config: configs/llamacpp_server.json

Server will be available at: http://localhost:8000
Press Ctrl+C to stop the server
========================================
```

### 5. Run TradingAgents

In a new terminal:

```bash
python main.py
```

Or use the CLI:

```bash
python -m cli.main
```

When prompted:
1. Select **"LlamaCpp (Local)"** as your provider
2. Choose your downloaded models for quick and deep thinking

## Model Recommendations

### For Trading Analysis:

| Model | Size | Use Case | Memory Required | Speed |
|-------|------|----------|-----------------|-------|
| **DeepSeek-R1-Distill-Llama-8B** | 5.5GB | Quick thinking (fast) | 8GB VRAM | ⚡⚡⚡ |
| **DeepSeek-R1-Distill-Llama-70B** | 42GB | Deep thinking (best) | 48GB VRAM | ⚡ |
| **DeepSeek-R1-Distill-Qwen-32B** | 22GB | Balanced reasoning | 24GB VRAM | ⚡⚡ |
| **Llama-3.3-70B-Instruct** | 42GB | Comprehensive capabilities | 48GB VRAM | ⚡ |
| **Qwen2.5-7B-Instruct** | 5.5GB | Lightweight option | 8GB VRAM | ⚡⚡⚡ |

### For Embeddings (Memory System):

- **sentence-transformers (all-MiniLM-L6-v2)** - 22MB, automatically downloaded, works out of the box ✅ **Recommended**
- **nomic-embed-text-v1.5** - 280MB, best for financial text (optional)

## Configuration Options

### Server Mode (Default - Recommended)

Server mode uses llama-cpp-python's OpenAI-compatible server:

**Advantages:**
- Multiple models loaded simultaneously
- Better resource management
- Automatic request queuing
- Hot-swappable models

**Configuration:**
```python
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "llamacpp"
config["llamacpp_server_url"] = "http://localhost:8000/v1"  # Default
config["deep_think_llm"] = "deepseek-r1-distill-llama-70b"
config["quick_think_llm"] = "deepseek-r1-distill-llama-8b"
```

### Direct Mode (Advanced)

Direct mode loads models in-process without a server:

**Advantages:**
- Lower latency (no HTTP overhead)
- Simpler for single-model use
- Better for constrained environments

**Configuration:**
```python
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "llamacpp"
config["llamacpp_model_path"] = "./models/deepseek-r1-distill-llama-8b/DeepSeek-R1-Distill-Llama-8B-Q5_K_M.gguf"
config["llamacpp_n_ctx"] = 4096
config["llamacpp_n_gpu_layers"] = -1  # -1 = use all GPU layers
```

## Fine-tuning Workflow

### 1. Prepare Training Data

Create a dataset of trading scenarios and expert decisions:

```json
[
  {
    "instruction": "Analyze this market situation and provide trading recommendation.",
    "input": "NVDA stock shows strong technical momentum with MACD crossover. Fundamentals show 25% revenue growth YoY. News sentiment is positive due to AI chip demand.",
    "output": "RECOMMENDATION: BUY\n\nRATIONALE:\n1. Technical Analysis: MACD bullish crossover indicates upward momentum\n2. Fundamental Strength: 25% YoY revenue growth demonstrates strong business performance\n3. Positive Catalysts: AI chip demand provides sustainable growth driver\n\nRISK FACTORS:\n- Monitor for profit-taking at resistance levels\n- Valuation may be stretched in short term\n\nPOSITION SIZE: Moderate (15-20% of portfolio)"
  }
]
```

### 2. Fine-tune Using Unsloth

[Unsloth](https://github.com/unslothai/unsloth) provides efficient fine-tuning for llama.cpp models:

```python
from unsloth import FastLanguageModel
import torch
from trl import SFTTrainer
from transformers import TrainingArguments

# Load base model
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Meta-Llama-3.3-70B-Instruct",
    max_seq_length=4096,
    dtype=torch.float16,
    load_in_4bit=True,  # Use 4-bit quantization for efficiency
)

# Apply LoRA for parameter-efficient fine-tuning
model = FastLanguageModel.get_peft_model(
    model,
    r=16,  # LoRA rank
    lora_alpha=16,
    lora_dropout=0.05,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    use_gradient_checkpointing=True,
)

# Prepare your dataset
from datasets import load_dataset
dataset = load_dataset("json", data_files="trading_data.json")

# Fine-tune
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset["train"],
    max_seq_length=4096,
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_steps=5,
        max_steps=100,
        learning_rate=2e-4,
        fp16=True,
        logging_steps=1,
        output_dir="outputs",
    ),
)

trainer.train()

# Save the fine-tuned model
model.save_pretrained("trading_model_lora")
tokenizer.save_pretrained("trading_model_lora")
```

### 3. Convert to GGUF Format

```bash
# Merge LoRA adapters with base model
python -m unsloth.convert --model ./trading_model_lora --output ./trading_model_merged

# Convert to GGUF
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
python convert_hf_to_gguf.py ../trading_model_merged \
    --outfile ../models/my_trading_model.gguf \
    --outtype q5_k_m  # Q5_K_M quantization
```

### 4. Use Your Fine-tuned Model

Add to `configs/llamacpp_server.json`:
```json
{
  "model": "./models/my_trading_model.gguf",
  "model_alias": "my-trading-model",
  "n_ctx": 4096,
  "n_gpu_layers": -1
}
```

Restart server and select "my-trading-model" in the CLI.

## Troubleshooting

### Model Not Found Error
```
Error: Model not found: ./models/...
```

**Solution:**
- Verify model was fully downloaded: `ls -lh models/`
- Check path in `configs/llamacpp_server.json` matches downloaded file
- Re-download: `python scripts/download_models.py MODEL_NAME`

### Server Won't Start
```
Error: Address already in use
```

**Solution:**
- Another process is using port 8000
- Kill existing server: `lsof -ti:8000 | xargs kill -9`
- Or change port in `configs/llamacpp_server.json`

### Out of Memory Error
```
llama.cpp: error: failed to load model
```

**Solutions:**
1. **Use smaller quantization:**
   - Q4_K_M instead of Q5_K_M (~20% smaller)
   - Q4_0 for maximum compression

2. **Reduce GPU layers:**
   ```json
   "n_gpu_layers": 32  // Instead of -1 (all layers)
   ```

3. **Use smaller model:**
   - 8B model instead of 70B
   - Qwen 7B instead of Llama 70B

### Slow Inference
```
Response taking 30+ seconds
```

**Solutions:**
1. **Enable GPU acceleration:**
   ```bash
   # Reinstall with CUDA
   pip uninstall llama-cpp-python
   CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python[server]
   ```

2. **Increase GPU layers:**
   ```json
   "n_gpu_layers": -1  // Use all layers on GPU
   ```

3. **Increase batch size:**
   ```json
   "n_batch": 1024  // From 512
   ```

4. **Use faster quantization:**
   - Q4_0 is faster than Q5_K_M (slightly lower quality)

### Connection Refused
```
Error: Connection refused to http://localhost:8000
```

**Solution:**
- Ensure server is running: `./scripts/start_llamacpp_server.sh`
- Check server logs for errors
- Verify port: `netstat -an | grep 8000`

## Performance Tips

### 1. GPU Acceleration
Always install with GPU support if available:
```bash
# Check NVIDIA GPU
nvidia-smi

# Install with CUDA
CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python[server]
```

### 2. Quantization Selection
| Quantization | Quality | Size | Speed | Use Case |
|--------------|---------|------|-------|----------|
| Q4_0 | Good | Small | Fastest | Testing, quick tasks |
| Q4_K_M | Very Good | Medium | Fast | Production, balanced |
| Q5_K_M | Excellent | Large | Moderate | Best quality |
| Q8_0 | Near-perfect | Largest | Slowest | Maximum quality |

**Recommendation:** Q5_K_M for 8B models, Q4_K_M for 70B models

### 3. Context Window
- **4096 tokens** - Good for most trading analysis
- **8192 tokens** - For longer reports and complex debates
- **16384 tokens** - Maximum detail, but slower

```json
"n_ctx": 4096  // Adjust based on needs
```

### 4. Batch Size
- **512** - Default, balanced
- **1024** - Better throughput for multiple requests
- **256** - Lower memory usage

### 5. Thread Count
```python
config["llamacpp_n_threads"] = cpu_count - 1  # Leave one core free
```

## Advanced Configuration

### Multi-Model Setup

Load multiple models for different tasks:

```json
{
  "models": [
    {
      "model": "./models/deepseek-r1-distill-llama-8b/...",
      "model_alias": "quick-thinking",
      "n_ctx": 4096
    },
    {
      "model": "./models/deepseek-r1-distill-llama-70b/...",
      "model_alias": "deep-thinking",
      "n_ctx": 8192
    },
    {
      "model": "./models/my_trading_model.gguf",
      "model_alias": "custom-trading",
      "n_ctx": 4096
    }
  ]
}
```

### Custom Embedding Models

Use llama.cpp for embeddings too:

```python
config["llamacpp_embedding_model_path"] = "./models/nomic-embed-text/nomic-embed-text-v1.5.Q8_0.gguf"
```

## Resources

- [llama.cpp GitHub](https://github.com/ggerganov/llama.cpp) - Core llama.cpp project
- [llama-cpp-python Docs](https://llama-cpp-python.readthedocs.io/) - Python bindings documentation
- [Hugging Face GGUF Models](https://huggingface.co/models?library=gguf) - Browse available models
- [Unsloth](https://github.com/unslothai/unsloth) - Efficient fine-tuning toolkit
- [GGUF Quantization Guide](https://github.com/ggerganov/llama.cpp/blob/master/examples/quantize/README.md) - Quantization details

## Support

For issues and questions:
- TradingAgents Issues: https://github.com/TauricResearch/TradingAgents/issues
- llama.cpp Issues: https://github.com/ggerganov/llama.cpp/issues
- llama-cpp-python Issues: https://github.com/abetlen/llama-cpp-python/issues
