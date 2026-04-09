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
