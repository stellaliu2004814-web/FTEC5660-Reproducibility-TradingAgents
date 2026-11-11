# FTEC5660 Reproducibility Report: TradingAgents

## Multi-Agents LLM Financial Trading Framework

**Course**: FTEC5660 Agentic AI for Business and FinTech  
**Assignment**: Reproducibility Work  
**Student**: Liu Yutong | **Student ID**: 1155269999  
**Date**: November 2026

---

## 1. Project Summary

### 1.1 Paper Overview

TradingAgents (Xiao et al., 2024) is a multi-agent LLM framework for financial trading that simulates a real-world trading firm. The system employs multiple specialized LLM-based agents:

- **4 Analysts**: Market Analyst (technical indicators), Sentiment Analyst (StockTwits/Reddit/news), News Analyst (macro news), Fundamentals Analyst (SEC filings)
- **2 Researchers**: Bull Researcher and Bear Researcher debate based on analyst reports
- **1 Research Manager**: Synthesizes the debate into an investment recommendation
- **1 Trader**: Converts the recommendation into a trade action (Buy/Sell/Hold)
- **3 Risk Debaters**: Aggressive, Conservative, and Neutral analysts debate risk
- **1 Portfolio Manager**: Makes the final decision

The paper reports (Table 1) that TradingAgents achieved 26.62% cumulative return on AAPL, 24.36% on GOOGL, and 23.21% on AMZN over Jan-Mar 2024, significantly outperforming Buy & Hold and technical indicator baselines (MACD, KDJ&RSI, ZMR, SMA).

### 1.2 What We Tried to Reproduce

We targeted reproducing the core multi-agent decision pipeline: given a stock ticker and date, the system should produce a trading decision (Buy/Overweight/Hold/Underweight/Sell) through its full agent chain.

**Specific reproduction target**: Run TradingAgents for NVDA and AAPL on 2 dates each in January 2024, verify the pipeline executes end-to-end, and record decisions.

---

## 2. Setup Notes

### 2.1 Environment

| Component | Specification |
|-----------|--------------|
| OS | macOS (Darwin) |
| Python | 3.13.12 |
| Virtual Env | venv (isolated) |
| LLM Provider | DeepSeek (replacing OpenAI) |
| Deep Think Model | deepseek-reasoner (replacing o1-preview) |
| Quick Think Model | deepseek-chat (replacing gpt-4o) |
| Temperature | 0.0 (for reproducibility) |
| Debate Rounds | 1 (bull-bear) |
| Risk Debate Rounds | 1 (aggressive-conservative-neutral) |

### 2.2 Data Sources

| Source | Status | Notes |
|--------|--------|-------|
| SEC EDGAR | ✅ Working | Free, fundamental data (as-filed) |
| Yahoo Finance | ⚠️ Rate limited | OHLCV, indicators, news — heavily throttled |
| StockTwits | ❌ 403 Forbidden | Blocked access |
| Reddit RSS | ❌ Timeout | Connection issues |
| FRED | ❌ Not configured | FRED_API_KEY not set (macro data unavailable) |
| Polymarket | ✅ Working | Prediction market odds (live only) |

### 2.3 Model Swap Justification (Edge Case A)

The original paper uses OpenAI's o1-preview and gpt-4o. We replaced these with DeepSeek's deepseek-reasoner and deepseek-chat respectively, as explicitly allowed by the assignment (Section 4, Edge Case A). 

**Documentation of changes**:
- Model name: `o1-preview` → `deepseek-reasoner`, `gpt-4o` → `deepseek-chat`
- Provider: `openai` → `deepseek`
- Base URL: Automatically configured by TradingAgents (DeepSeek API is OpenAI-compatible)
- Decoding params: temperature=0.0 (same for both)
- No prompt/template changes needed
- **Results are not directly comparable to the paper because the underlying LLM differs**

### 2.4 API Keys

- DeepSeek API key configured in `.env` (not committed to git)
- No other paid API keys required

---

## 3. Reproduction Target & Metric

### 3.1 Target

**Target claim**: "TradingAgents produces multi-step trading decisions through its agent pipeline, with analysts providing reports, researchers debating, and a portfolio manager making a final call."

**Metric**: Final decision rating (Buy/Overweight/Hold/Underweight/Sell) and pipeline execution success (all agents producing reports).

### 3.2 Evaluation

We evaluate:
1. Whether the full pipeline executes end-to-end (all 11+ agent steps complete)
2. Whether each analyst produces a report
3. Whether a final decision is produced
4. Whether decisions are directionally reasonable (e.g., NVDA bullish in Jan 2024 during AI boom)

---

## 4. Results: Our Numbers vs Reported

### 4.1 Baseline Reproduction Results

| Ticker | Date | Decision | Has Fundamentals | Has Market Data | Time (s) |
|--------|------|----------|-------------------|-----------------|----------|
| NVDA | 2024-01-10 | **Overweight** | ✅ | ❌ (rate limited) | 166 |
| AAPL | 2024-01-11 | **Hold** | ✅ | ❌ (rate limited) | 197 |
| NVDA | 2024-01-25 | **Overweight** | ✅ | ❌ (rate limited) | 163 |
| AAPL | 2024-01-25 | **Hold** | ✅ | ❌ (rate limited) | 170 |

### 4.2 Comparison with Paper

| Aspect | Paper | Our Reproduction |
|--------|-------|-----------------|
| LLM | OpenAI o1-preview + gpt-4o | DeepSeek reasoner + chat |
| Data source | FinnHub (paid) | Yahoo Finance (free, rate-limited) + SEC EDGAR |
| Stocks tested | AAPL, GOOGL, AMZN | NVDA, AAPL |
| Period | Jan-Mar 2024 (daily) | Jan 2024 (4 dates) |
| Decision for NVDA | N/A (not in paper) | Overweight (consistent across dates) |
| Decision for AAPL | Bullish (26.62% CR) | Hold (more conservative) |
| Full pipeline execution | ✅ | ✅ |
| Multi-agent debate | ✅ | ✅ |

### 4.3 Key Observations

1. **Pipeline integrity**: The full multi-agent pipeline executes correctly with DeepSeek — all 4 analysts, 2 researchers, research manager, trader, 3 risk debaters, and portfolio manager complete their roles.

2. **Fundamental analysis quality**: SEC EDGAR data was retrieved successfully. The Fundamentals Analyst produced detailed, accurate reports (e.g., NVDA Q3 FY2024: revenue $18.12B, +206% YoY, gross margin 74.0%).

3. **Market data gap**: Yahoo Finance rate limiting (HTTP 429) prevented market/technical/sentiment/news data from being retrieved. The agents correctly reported "DATA_UNAVAILABLE" rather than fabricating data — this is a positive reproducibility finding about the system's robustness.

4. **Decision rationale**: Despite missing market data, the system made reasonable decisions based on fundamentals alone:
   - NVDA → Overweight: driven by +206% YoY revenue growth and margin expansion
   - AAPL → Hold: more conservative given slower growth and valuation concerns

5. **Paper's NVDA comparison**: NVDA was not in the paper's Table 1, but our Overweight rating aligns with NVDA's actual ~80% price increase in Q1 2024.

6. **AAPL divergence**: The paper reports strong bullish performance on AAPL (26.62% CR), but our system gave "Hold." This divergence is likely due to:
   - Different LLM (DeepSeek vs OpenAI)
   - Missing market data (no price/technical indicators)
   - Different time period (single dates vs daily compounding)

---

## 5. Modification & Results

### 5.1 Modification: Ablation — Remove Risk Debate

**What changed**: Set `max_risk_discuss_rounds=0`, which skips the Aggressive/Conservative/Neutral risk analysts' debate entirely. The pipeline goes directly from Trader → Portfolio Manager.

**Why**: The paper claims risk management (Section 3.4) as a key component. We test whether removing it changes decisions.

**Isolation**: Only one parameter changed (`max_risk_discuss_rounds: 1 → 0`); all other settings identical.

### 5.2 Ablation Results

| Ticker | Date | Baseline Decision | Ablation Decision | Changed? | Baseline Time | Ablation Time |
|--------|------|-------------------|-------------------|----------|---------------|---------------|
| NVDA | 2024-01-10 | Overweight | Overweight | ❌ No | 166s | 170s |
| AAPL | 2024-01-11 | Hold | Hold | ❌ No | 197s | 146s |

### 5.3 Modification Impact Analysis

**Finding: The risk debate has no effect on the final decision rating.**

Both NVDA and AAPL received identical ratings with and without the risk debate component. This suggests that in the current architecture, the Portfolio Manager largely follows the Research Manager's recommendation regardless of the risk analysts' input.

However, examining the ablation run's internal state reveals important nuances:

1. **Risk debate still partially executes**: Even with `max_risk_discuss_rounds=0`, the Aggressive Analyst still produces one statement (visible in `risk_debate_state.aggressive_history`). The conditional logic (`should_continue_risk_analysis`) checks if `count >= 3 * max_risk_discuss_rounds` (= 0), which is immediately true, so it routes to Portfolio Manager after the first speaker. The Aggressive Analyst gets exactly one turn but the Conservative and Neutral analysts get zero turns.

2. **Reasoning depth differs**: In the baseline run, the Portfolio Manager's final decision references "the conservative is right that..." and "the aggressive's bounded downside does not hold," indicating it incorporated all three risk perspectives. In the ablation run, the Portfolio Manager's reasoning references only the Aggressive Analyst's points.

3. **Speed improvement for AAPL**: The ablation run was ~26% faster for AAPL (146s vs 197s), as expected from skipping most of the risk debate.

4. **Decision stability**: The identical decisions suggest the system's core signal comes from the fundamental analysis + bull/bear debate, not the risk debate. The risk debate appears to be a "sanity check" layer that, in these cases, did not override the fundamental signal.

**Implications for the paper's architecture claim**: The paper positions risk management as a key component (Section 3.4), but our ablation suggests it may be ceremonial rather than decision-changing for these test cases. This could be because:
- The missing market data already makes the system conservative (no Buy → only Overweight)
- DeepSeek may be less influenced by additional debate context than OpenAI's models
- The test cases (NVDA strong fundamentals, AAPL stable) had clear directional signals

---

## 6. Debug Diary

### Blocker 1: Yahoo Finance Rate Limiting
- **Problem**: HTTP 429 "Too Many Requests" on all Yahoo Finance endpoints (stock data, indicators, news, global news)
- **Impact**: Market Analyst, Sentiment Analyst, and News Analyst received no data
- **Resolution**: Could not resolve within session. SEC EDGAR (fundamentals) worked reliably. The system's error handling correctly propagated "DATA_UNAVAILABLE" to agents rather than crashing.
- **Workaround**: Relied on fundamentals-only analysis for decision-making

### Blocker 2: StockTwits 403 Forbidden
- **Problem**: StockTwits API returns HTTP 403
- **Impact**: Sentiment Analyst gets no retail sentiment data
- **Resolution**: No resolution; StockTwits appears to have changed access policy. System handles gracefully.

### Blocker 3: Reddit RSS Timeout
- **Problem**: Reddit RSS feed requests timeout
- **Impact**: No Reddit sentiment data
- **Resolution**: System handles gracefully; no crash

### Blocker 4: FRED API Key Not Set
- **Problem**: FRED_API_KEY not configured
- **Impact**: No macro economic data (CPI, PCE, unemployment, Fed funds rate)
- **Resolution**: Free key available at https://fred.stlouisfed.org; not critical for reproduction as fundamentals worked

### Blocker 5: DeepSeek Model Warning
- **Problem**: RuntimeWarning "Model 'deepseek-reasoner' is not in the known model list for provider 'deepseek'"
- **Impact**: None — warning only, the model works correctly
- **Resolution**: Ignored; the framework's model list is outdated

### Blocker 6: pip Installation Issues
- **Problem**: First `pip install -e .` appeared to succeed but `import tradingagents` failed; then EEXIST error on rebuild
- **Resolution**: `pip cache purge` + reinstall fixed the issue

### Non-Blocker: Research Manager Structured Output
- **Problem**: "structured output returned no parsed result; retrying once as free text"
- **Impact**: The Research Manager's structured output failed once but the system retried successfully
- **Resolution**: Self-healing; no action needed

---

## 7. Conclusions

### 7.1 What Is Reproducible

1. **Multi-agent pipeline execution**: ✅ Fully reproducible. The complete agent chain (analysts → researchers → debate → trader → risk debate → portfolio manager) runs end-to-end with a different LLM provider (DeepSeek).

2. **Fundamental analysis quality**: ✅ SEC EDGAR data retrieval and the Fundamentals Analyst's report are high quality and accurate. NVDA's Q3 FY2024 financials were correctly extracted and analyzed.

3. **Decision production**: ✅ The system consistently produces a clear 5-tier rating (Buy/Overweight/Hold/Underweight/Sell).

4. **Robustness to data failures**: ✅ The system gracefully handles data source failures, reporting "DATA_UNAVAILABLE" rather than fabricating data or crashing.

### 7.2 What Is Not Reproducible

1. **Full backtest comparison**: ❌ Yahoo Finance rate limiting prevented us from running the full daily backtest needed to compute CR%, ARR%, SR, MDD% as in Table 1.

2. **Market technical analysis**: ❌ No OHLCV, RSI, MACD, or moving average data was available due to rate limiting.

3. **Sentiment analysis**: ❌ StockTwits (403) and Reddit (timeout) both failed.

4. **Exact numerical comparison**: ❌ Since we used DeepSeek instead of OpenAI, and many data sources failed, exact numerical comparison with the paper's Table 1 is not possible.

### 7.3 Why

1. **External API limitations**: Yahoo Finance's free tier has aggressive rate limits that made systematic data retrieval impossible during our testing window. The paper used FinnHub (paid) which likely had higher quotas.

2. **Model differences**: DeepSeek and OpenAI models have different reasoning patterns. DeepSeek produced more conservative decisions (e.g., "Hold" for AAPL vs the paper's bullish results), which could reflect genuine model differences or the impact of missing market data.

3. **Non-determinism**: Even at temperature=0, LLM outputs vary across runs. The paper itself acknowledges this limitation.

4. **Temporal data drift**: News, sentiment, and social media data are inherently non-reproducible for historical dates — the paper acknowledges this as a fundamental challenge.

### 7.4 Recommendations for Future Users

1. **Use Alpha Vantage as a fallback data source**: Configure `ALPHA_VANTAGE_API_KEY` to avoid Yahoo Finance rate limits
2. **Set FRED_API_KEY**: Free and enables macro economic data
3. **Budget for API costs**: Each run requires ~11 LLM calls + 20+ tool calls; DeepSeek is ~10x cheaper than OpenAI
4. **Run multiple trials**: Due to LLM non-determinism, run 3-5 trials per condition and report mean/variance
5. **Pin data versions**: For true reproducibility, cache Yahoo Finance responses locally

---

## References

1. Xiao, Y., Sun, E., Luo, D., & Wang, W. (2024). TradingAgents: Multi-Agents LLM Financial Trading Framework. arXiv:2412.20138.
2. TradingAgents GitHub: https://github.com/TauricResearch/TradingAgents
3. DeepSeek API: https://platform.deepseek.com/
4. SEC EDGAR: https://www.sec.gov/edgar/
5. Yahoo Finance API: https://finance.yahoo.com/

---

*This report is part of FTEC5660 Reproducibility Work, due November 13, midnight.*
