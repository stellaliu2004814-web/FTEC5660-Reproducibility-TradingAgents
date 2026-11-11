#!/usr/bin/env python3
"""
FTEC5660 Reproducibility Assignment - TradingAgents Reproduction Script

Reproduces: TradingAgents multi-agent trading decision for NVDA on a historical date.
Paper: "TradingAgents: Multi-Agents LLM Financial Trading Framework" (2024)
Repo: https://github.com/TauricResearch/TradingAgents

Modification: Uses DeepSeek (deepseek-reasoner + deepseek-chat) instead of the
paper's OpenAI (o1-preview + gpt-4o), as allowed by the assignment (Edge Case A).
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Load .env
from dotenv import load_dotenv
load_dotenv()

from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.graph.trading_graph import TradingAgentsGraph

# --- Configuration ---
# Using DeepSeek as LLM provider (assignment Edge Case A: model swap)
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "deepseek"
config["deep_think_llm"] = "deepseek-reasoner"
config["quick_think_llm"] = "deepseek-chat"
config["max_debate_rounds"] = 1
config["max_risk_discuss_rounds"] = 1
config["temperature"] = 0.0
config["output_language"] = "English"

# --- Reproduction Target ---
# Paper Table 1: Trading decisions for stocks (AAPL, GOOGL, AMZN, NVDA)
# We reproduce: single-day decision for NVDA on 2024-01-10
# Expected behavior: The system should produce a Buy/Hold/Sell decision
# through its multi-agent pipeline (analysts -> researchers -> debate -> trader -> risk management)

TICKER = "NVDA"
TRADE_DATE = "2024-01-10"

print(f"{'='*70}")
print(f"TradingAgents Reproduction")
print(f"{'='*70}")
print(f"Ticker: {TICKER}")
print(f"Trade Date: {TRADE_DATE}")
print(f"LLM Provider: {config['llm_provider']}")
print(f"Deep Think Model: {config['deep_think_llm']}")
print(f"Quick Think Model: {config['quick_think_llm']}")
print(f"Max Debate Rounds: {config['max_debate_rounds']}")
print(f"Max Risk Rounds: {config['max_risk_discuss_rounds']}")
print(f"Temperature: {config['temperature']}")
print(f"{'='*70}")
print()

# Initialize the graph
ta = TradingAgentsGraph(debug=True, config=config)

# Run the propagation
start_time = time.time()
print(f"Starting analysis for {TICKER} on {TRADE_DATE}...")
print()

try:
    final_state, decision = ta.propagate(TICKER, TRADE_DATE)
    elapsed = time.time() - start_time

    print()
    print(f"{'='*70}")
    print(f"RESULT")
    print(f"{'='*70}")
    print(f"Decision: {decision}")
    print(f"Elapsed: {elapsed:.1f}s ({elapsed/60:.1f} min)")
    print(f"{'='*70}")

    # Extract individual agent reports
    print()
    print("--- Market Analyst Report ---")
    print(final_state.get("market_report", "N/A")[:500])
    print()

    print("--- Sentiment Analyst Report ---")
    print(final_state.get("sentiment_report", "N/A")[:500])
    print()

    print("--- News Analyst Report ---")
    print(final_state.get("news_report", "N/A")[:500])
    print()

    print("--- Fundamentals Analyst Report ---")
    print(final_state.get("fundamentals_report", "N/A")[:500])
    print()

    print("--- Trader Investment Plan ---")
    print(final_state.get("trader_investment_plan", "N/A")[:500])
    print()

    print("--- Final Trade Decision ---")
    print(final_state.get("final_trade_decision", "N/A")[:1000])
    print()

    # Save results
    results_dir = Path("reproduction_results")
    results_dir.mkdir(exist_ok=True)

    result_summary = {
        "ticker": TICKER,
        "trade_date": TRADE_DATE,
        "decision": decision,
        "elapsed_seconds": elapsed,
        "config": {
            "llm_provider": config["llm_provider"],
            "deep_think_llm": config["deep_think_llm"],
            "quick_think_llm": config["quick_think_llm"],
            "max_debate_rounds": config["max_debate_rounds"],
            "max_risk_discuss_rounds": config["max_risk_discuss_rounds"],
            "temperature": config["temperature"],
        },
        "market_report": final_state.get("market_report", ""),
        "sentiment_report": final_state.get("sentiment_report", ""),
        "news_report": final_state.get("news_report", ""),
        "fundamentals_report": final_state.get("fundamentals_report", ""),
        "trader_investment_plan": final_state.get("trader_investment_plan", ""),
        "investment_plan": final_state.get("investment_plan", ""),
        "final_trade_decision": final_state.get("final_trade_decision", ""),
        "timestamp": datetime.now().isoformat(),
    }

    output_file = results_dir / f"reproduction_{TICKER}_{TRADE_DATE}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result_summary, f, indent=2, ensure_ascii=False)

    print(f"\nResults saved to: {output_file}")

except Exception as e:
    elapsed = time.time() - start_time
    print(f"\nERROR after {elapsed:.1f}s: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

    # Save error info
    results_dir = Path("reproduction_results")
    results_dir.mkdir(exist_ok=True)
    error_file = results_dir / f"error_{TICKER}_{TRADE_DATE}.json"
    with open(error_file, "w") as f:
        json.dump({
            "ticker": TICKER,
            "trade_date": TRADE_DATE,
            "error": str(e),
            "error_type": type(e).__name__,
            "elapsed_seconds": elapsed,
            "timestamp": datetime.now().isoformat(),
        }, f, indent=2)
    print(f"Error saved to: {error_file}")
