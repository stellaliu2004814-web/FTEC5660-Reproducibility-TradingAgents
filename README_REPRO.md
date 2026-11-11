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
| Ticker | Date | Decision | Elapsed |
|--------|------|----------|---------|
| NVDA | 2024-01-10 | Overweight | 166s |
| AAPL | 2024-01-11 | Hold | 197s |
| NVDA | 2024-01-25 | Overweight | 163s |
| AAPL | 2024-01-25 | Hold | 170s |

### Ablation (without risk debate)
See `reproduction_results/ablation_summary.json` after running the ablation script.

## Key Findings
1. The multi-agent pipeline (4 analysts, 2 researchers, debate, trader, 3 risk debaters, portfolio manager) runs end-to-end with DeepSeek
2. SEC EDGAR fundamental data works reliably; Yahoo Finance was rate-limited during our runs
3. NVDA consistently received "Overweight" (bullish on AI growth fundamentals)
4. AAPL consistently received "Hold" (conservative on valuation)
5. Model swap from OpenAI to DeepSeek required only config changes (no code modification)

## File Structure
```
TradingAgents/               # Original repo (cloned)
├── reproduce.py             # Single-run reproduction script
├── reproduce_multiple.py    # Multi-ticker/date reproduction
├── ablation_experiment.py   # Ablation: no risk debate
├── reproduction_results/    # JSON results from all runs
├── .env                     # API keys (NOT in git)
└── tradingagents/           # Original framework code
```

## Notes
- No API keys are committed (`.env` is in `.gitignore`)
- DeepSeek API costs are significantly lower than OpenAI (~$0.01-0.05 per run)
- Yahoo Finance rate limiting is the primary external blocker
- LLM outputs are non-deterministic even at temperature=0; results may vary across runs
