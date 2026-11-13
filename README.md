# FTEC5660 Reproducibility: TradingAgents

## Project
**Paper**: TradingAgents: Multi-Agents LLM Financial Trading Framework (2024)
**Authors**: Yijia Xiao, Edward Sun, Di Luo, Wei Wang
**arXiv**: https://arxiv.org/abs/2412.20138
**Original Repo**: https://github.com/TauricResearch/TradingAgents

## What This Repository Contains
This is a reproducibility study of the TradingAgents framework, as part of FTEC5660 (Agentic AI for Business and FinTech) at HKUST(GZ).

## Reproduction Target
We reproduce the multi-agent trading decision pipeline for NVDA and AAPL on historical dates in January 2024, comparing the system's decisions (Buy/Hold/Sell/Overweight/Underweight) with the paper's reported behavior.

**Paper Table 1** reports cumulative returns of 26.62% (AAPL), 24.36% (GOOGL), and 23.21% (AMZN) over Jan-Mar 2024, significantly outperforming B&H and technical indicator baselines.

Our reproduction focuses on:
- Verifying the multi-agent pipeline (analysts -> researchers -> debate -> trader -> risk management -> portfolio manager) executes correctly
- Producing trade decisions for NVDA and AAPL on multiple dates
- Comparing decisions with and without the risk debate component (ablation)

## Modification
**Model swap (Edge Case A)**: Replaced OpenAI o1-preview + gpt-4o with DeepSeek deepseek-reasoner + deepseek-chat, as allowed by the assignment. DeepSeek's API is OpenAI-compatible, requiring only config changes (model name + base URL + key).

**Ablation**: Removed the risk debate round (`max_risk_discuss_rounds=0`), skipping the Aggressive/Conservative/Neutral risk analysts' debate. This tests whether the risk management component (paper Section 3.4) actually affects final decisions.

## Setup

### Prerequisites
- Python 3.11+
- DeepSeek API key (or OpenAI API key)

### Installation
```bash
# Clone
git clone https://github.com/TauricResearch/TradingAgents.git
cd TradingAgents

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install
pip install -e .

# Configure API key
cp .env.example .env
# Edit .env and add your API key
```

### .env Configuration (DeepSeek)
```
DEEPSEEK_API_KEY=your_key_here
TRADINGAGENTS_LLM_PROVIDER=deepseek
TRADINGAGENTS_DEEP_THINK_LLM=deepseek-reasoner
TRADINGAGENTS_QUICK_THINK_LLM=deepseek-chat
TRADINGAGENTS_TEMPERATURE=0.0
SEC_EDGAR_USER_AGENT=Your Name your@email.com
```

## Running

### Single reproduction
```bash
python reproduce.py
```
Runs TradingAgents for NVDA on 2024-01-10 with DeepSeek.

### Multiple tickers/dates
```bash
python reproduce_multiple.py
```
Runs for NVDA and AAPL on two dates each (4 runs total).

### Ablation experiment (no risk debate)
```bash
python ablation_experiment.py
```
Same as above but with `max_risk_discuss_rounds=0`.

## Results

### Baseline Reproduction (with risk debate)

| Ticker | Date | Decision | Fundamentals | Market Data | Sentiment | News | Elapsed (s) |
|--------|------|----------|--------------|-------------|-----------|------|-------------|
| NVDA | 2024-01-10 | Overweight | ✅ | ❌ | ⚠️ placeholder† | ⚠️ placeholder† | 165.6 |
| AAPL | 2024-01-11 | Hold | ✅ | ❌ | ⚠️ placeholder† | ⚠️ placeholder† | 197.1 |
| NVDA | 2024-01-25 | Overweight | ✅ | ❌ | ⚠️ placeholder† | ⚠️ placeholder† | 163.0 |
| AAPL | 2024-01-25 | Hold | ✅ | ❌ | ⚠️ placeholder† | ⚠️ placeholder† | 169.8 |

### Ablation (without risk debate)

| Ticker | Date | Baseline | Ablation | Changed? | Baseline (s) | Ablation (s) |
|--------|------|----------|----------|----------|--------------|--------------|
| NVDA | 2024-01-10 | Overweight | Overweight | ❌ No | 165.6 | 169.9 |
| AAPL | 2024-01-11 | Hold | Hold | ❌ No | 197.1 | 145.7 |

> **† Placeholder note**: `has_sentiment_data` / `has_news_data` are `true` in the JSON only because the Sentiment and News Analysts each *generated a text report*. All underlying sources failed (StockTwits 403, Reddit timeout, Yahoo Finance news 429, FRED key not set), so these are "data-unavailable" placeholder reports with a default Neutral score (5.0/10, Low confidence). **No actual sentiment, news, or macro data was retrieved.** Decisions were driven solely by SEC EDGAR fundamentals.

> Elapsed times are exact values from `reproduction_results/*.json`.

## Key Findings
1. The multi-agent pipeline (4 analysts, 2 researchers, debate, trader, 3 risk debaters, portfolio manager) runs end-to-end with DeepSeek
2. SEC EDGAR fundamental data works reliably; Yahoo Finance was rate-limited during our runs
3. NVDA consistently received "Overweight" (bullish on AI growth fundamentals); AAPL consistently received "Hold" (conservative on valuation)
4. Model swap from OpenAI to DeepSeek required only config changes (no code modification)
5. **Ablation finding**: removing the risk debate (`max_risk_discuss_rounds=0`) did **not** change either decision — the risk debate appears to be a "sanity check" layer rather than a decision-changing component in these test cases
6. **Robustness finding**: when data sources failed, agents correctly reported `DATA_UNAVAILABLE` and declined to fabricate data rather than hallucinating figures

## File Structure
```
FTEC5660-Reproducibility-TradingAgents/
├── README.md                 # This file
├── REPORT.pdf                # Final report (9 pages, PDF for submission)
├── REPORT.md                 # Report (Markdown source)
├── REPORT.html               # Report (styled HTML version)
├── reproduce.py              # Single-run reproduction script
├── reproduce_multiple.py     # Multi-ticker/date reproduction (4 runs)
├── ablation_experiment.py    # Ablation: no risk debate (2 runs)
├── reproduction_results/     # JSON results from all 6 runs
├── .env.example              # API key template (copy to .env)
├── .gitignore                # Blocks .env / venv from being committed
├── pyproject.toml            # Package config
├── requirements.txt          # Dependencies
└── main.py                   # Original repo entry point
```

**Note**: The upstream framework source lives at [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents). Clone it and copy this repo's scripts into it, or follow the Installation steps above which set it up from scratch.

## Submission Package
| Component | Location |
|-----------|----------|
| Report (PDF, 9 pages) | `REPORT.pdf` in this repo |
| GitHub repo | https://github.com/stellaliu2004814-web/FTEC5660-Reproducibility-TradingAgents |
| Presentation video | Recorded Zoom presentation (≤15 min), uploaded separately |

## Notes
- No API keys are committed (`.env` is in `.gitignore`)
- DeepSeek API costs are significantly lower than OpenAI (~$0.01-0.05 per run)
- Yahoo Finance rate limiting is the primary external blocker
- LLM outputs are non-deterministic even at temperature=0; results may vary across runs

## Author
Liu Yutong — Student ID: 1155269999
Course: FTEC5660 Agentic AI for Business and FinTech, HKUST(GZ)
