# water-reashercher

A CLI tool for searching water research data from multiple sources.

## Install

From the project root:

```bash
pip install -e .
```

## .env

Create a `.env` file with API keys in root folder (same location as `.env.example`):

```
OPENROUTER_API_KEY=your_openrouter_key
GROQ_API_KEY=your_groq_key
```

## Run without install

From the project root:

```bash
python3 -m cli test gpt
python3 -m cli search "Plant in Mexicali, Mexico"
```

## Run after install

```bash
water-researcher test gpt
water-researcher search "Plant in Mexicali, Mexico"
```

## Providers

Use the `--source` option to specify a provider:

```bash
water-researcher search "Plant in Mexicali, Mexico" --source gpt
# This is also the default source, a bit slow but more reliable

water-researcher search "Plant in Mexicali, Mexico" --source gemma
# Get rate-limited very quickly

water-researcher search "Plant in Mexicali, Mexico" --source groq
# Quicker but contains many parsing errors, should build a more robust parser for this to work properly
```
