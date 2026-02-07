#!/usr/bin/env python3
"""
Download GGUF models for llama.cpp from Hugging Face.

Usage:
    python scripts/download_models.py deepseek-r1-distill-llama-8b
    python scripts/download_models.py deepseek-r1-distill-llama-70b
    python scripts/download_models.py nomic-embed-text
"""
import os
import sys
from pathlib import Path

try:
    from huggingface_hub import hf_hub_download
    from rich.console import Console
    from rich.progress import Progress
except ImportError:
    print("Error: Required packages not installed.")
    print("Please install: pip install huggingface-hub rich")
    sys.exit(1)

console = Console()

MODELS = {
    "deepseek-r1-distill-llama-8b": {
        "repo": "unsloth/DeepSeek-R1-Distill-Llama-8B-GGUF",
        "files": ["DeepSeek-R1-Distill-Llama-8B-Q5_K_M.gguf"],
        "size": "~5.5GB",
        "description": "Fast reasoning model, good for quick thinking tasks"
    },
    "deepseek-r1-distill-llama-70b": {
        "repo": "unsloth/DeepSeek-R1-Distill-Llama-70B-GGUF",
        "files": ["DeepSeek-R1-Distill-Llama-70B-Q4_K_M.gguf"],
        "size": "~42GB",
        "description": "Best reasoning model for deep thinking tasks"
    },
    "deepseek-r1-distill-qwen-32b": {
        "repo": "unsloth/DeepSeek-R1-Distill-Qwen-32B-GGUF",
        "files": ["DeepSeek-R1-Distill-Qwen-32B-Q5_K_M.gguf"],
        "size": "~22GB",
        "description": "Strong reasoning with balanced size"
    },
    "llama-3.3-70b-instruct": {
        "repo": "bartowski/Llama-3.3-70B-Instruct-GGUF",
        "files": ["Llama-3.3-70B-Instruct-Q4_K_M.gguf"],
        "size": "~42GB",
        "description": "Comprehensive capabilities, high quality responses"
    },
    "qwen2.5-7b-instruct": {
        "repo": "Qwen/Qwen2.5-7B-Instruct-GGUF",
        "files": ["qwen2.5-7b-instruct-q5_k_m.gguf"],
        "size": "~5.5GB",
        "description": "Balanced performance for general tasks"
    },
    # Embedding models
    "nomic-embed-text": {
        "repo": "nomic-ai/nomic-embed-text-v1.5-GGUF",
        "files": ["nomic-embed-text-v1.5.Q8_0.gguf"],
        "size": "~280MB",
        "description": "Embedding model for memory system (optional)"
    },
}


def list_models():
    """List all available models."""
    console.print("\n[bold cyan]Available Models:[/bold cyan]\n")
    for model_name, info in MODELS.items():
        console.print(f"[green]{model_name}[/green]")
        console.print(f"  Description: {info['description']}")
        console.print(f"  Size: {info['size']}")
        console.print(f"  Repo: {info['repo']}")
        console.print()


def download_model(model_name: str, output_dir: Path = None):
    """Download a GGUF model for llama.cpp."""
    if model_name not in MODELS:
        console.print(f"[red]Error: Unknown model '{model_name}'[/red]\n")
        console.print("[yellow]Available models:[/yellow]")
        for name in MODELS.keys():
            console.print(f"  - {name}")
        return False

    if output_dir is None:
        output_dir = Path("./models")

    model_info = MODELS[model_name]
    output_dir.mkdir(parents=True, exist_ok=True)
    model_dir = output_dir / model_name

    console.print(f"\n[bold]Downloading {model_name}[/bold]")
    console.print(f"Size: {model_info['size']}")
    console.print(f"Destination: {model_dir}\n")

    for filename in model_info["files"]:
        try:
            console.print(f"[cyan]Downloading {filename}...[/cyan]")
            file_path = hf_hub_download(
                repo_id=model_info["repo"],
                filename=filename,
                local_dir=model_dir,
                local_dir_use_symlinks=False,
            )
            console.print(f"[green]✓ Downloaded: {file_path}[/green]")
        except Exception as e:
            console.print(f"[red]✗ Error downloading {filename}: {e}[/red]")
            return False

    console.print(f"\n[bold green]✓ Model downloaded successfully![/bold green]")
    console.print(f"Location: {model_dir}\n")
    return True


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Download GGUF models for llama.cpp",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/download_models.py deepseek-r1-distill-llama-8b
  python scripts/download_models.py --list
  python scripts/download_models.py deepseek-r1-distill-llama-70b --output ./my_models
        """
    )
    parser.add_argument(
        "model",
        nargs="?",
        help="Model name to download"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all available models"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("./models"),
        help="Output directory (default: ./models)"
    )

    args = parser.parse_args()

    if args.list or not args.model:
        list_models()
        if not args.model:
            sys.exit(0)

    success = download_model(args.model, args.output)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
