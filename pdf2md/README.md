Sometimes clean, structured Markdown files are not available, so they must be generated from PDFs. Full automation is difficult. The sections below explain how to use the `marker` tool and how to check the results with `prettier`, `markdownlint-cli2` and `cspell`.

## PDF to Markdown conversion

```bash
uv run marker --help

# Using a local Ollama model
ollama pull gemma4:31b-mlx
uv run marker pdf/ \
  --output_dir md/ \
  --output_format markdown \
  --disable_image_extraction \
  --use_llm \
  --llm_service marker.services.ollama.OllamaService \
  --ollama_base_url http://localhost:11434 \
  --ollama_model gemma4:31b-mlx \
  --OllamaService_timeout 600
  # --page_range 0-30

# Using a cloud OpenRouter model
uv run marker_single pdf/example.pdf \
  --output_dir md/ \
  --output_format markdown \
  --disable_image_extraction \
  --use_llm \
  --llm_service marker.services.openai.OpenAIService \
  --openai_base_url https://openrouter.ai/api/v1 \
  --openai_api_key $OPENROUTER_API_KEY \
  --openai_model anthropic/claude-sonnet-4.6
  # --page_range 0-30
```

## Markdown linting

The generated Markdown files under `md/` can be linted manually with the commands below.

```bash
# Check consistent formatting
brew install prettier
prettier --help
prettier --check md/example/example.md
prettier --write md/example/example.md  # Edits in place!

# Check Markdown rules
brew install markdownlint-cli2
markdownlint-cli2 --help
markdownlint-cli2 --fix md/example/example.md  # Edits in place!

# Check spelling
brew install cspell
cspell md/example/example.md
```
