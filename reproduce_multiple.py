#!/usr/bin/env python3
"""
FTEC5660 Reproducibility - Multiple ticker/date reproduction runs
Runs TradingAgents for multiple tickers and dates to build a small comparison table.
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.graph.trading_graph import TradingAgentsGraph

config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "deepseek"
config["deep_think_llm"] = "deepseek-reasoner"
config["quick_think_llm"] = "deepseek-chat"
config["max_debate_rounds"] = 1
config["max_risk_discuss_rounds"] = 1
config["temperature"] = 0.0
config["output_language"] = "English"

# Multiple tickers and dates for reproduction
# Paper Table 1 used AAPL, GOOGL, AMZN over Jan-Mar 2024
# We reproduce with NVDA and AAPL on a few dates
RUNS = [
    ("NVDA", "2024-01-10"),
    ("AAPL", "2024-01-11"),
    ("NVDA", "2024-01-25"),
    ("AAPL", "2024-01-25"),
]

ta = TradingAgentsGraph(debug=False, config=config)

results = []
results_dir = Path("reproduction_results")
if not results_dir.exists():
    results_dir.mkdir(parents=True)

for ticker, date in RUNS:
    print(f"\n{'='*60}")
    print(f"Running {ticker} on {date}...")
    print(f"{'='*60}")
    
    start_time = time.time()
    try:
        final_state, decision = ta.propagate(ticker, date)
        elapsed = time.time() - start_time
        
        # Extract key reports
        market_report = final_state.get("market_report", "")
        sentiment_report = final_state.get("sentiment_report", "")
        news_report = final_state.get("news_report", "")
        fundamentals_report = final_state.get("fundamentals_report", "")
        trader_plan = final_state.get("trader_investment_plan", "")
        final_decision = final_state.get("final_trade_decision", "")
        
        # Check if data was available
        has_market_data = "DATA_UNAVAILABLE" not in market_report and len(market_report) > 100
        has_sentiment_data = "UNAVAILABLE" not in sentiment_report[:200]
        has_news_data = "UNAVAILABLE" not in news_report[:200]
        has_fundamentals = len(fundamentals_report) > 100
        
        result = {
            "ticker": ticker,
            "trade_date": date,
            "decision": decision,
            "elapsed_seconds": round(elapsed, 1),
            "has_market_data": has_market_data,
            "has_sentiment_data": has_sentiment_data,
            "has_news_data": has_news_data,
            "has_fundamentals_data": has_fundamentals,
            "market_report": market_report,
            "sentiment_report": sentiment_report,
            "news_report": news_report,
            "fundamentals_report": fundamentals_report,
            "trader_investment_plan": trader_plan,
            "final_trade_decision": final_decision,
            "timestamp": datetime.now().isoformat(),
        }
        results.append(result)
        
        print(f"Decision: {decision}")
        print(f"Elapsed: {elapsed:.1f}s")
        print(f"Market data: {'YES' if has_market_data else 'NO (rate limited)'}")
        print(f"Fundamentals: {'YES' if has_fundamentals else 'NO'}")
        
        # Save individual result
        output_file = results_dir / f"reproduction_{ticker}_{date}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Saved to: {output_file}")
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"ERROR after {elapsed:.1f}s: {type(e).__name__}: {e}")
        results.append({
            "ticker": ticker,
            "trade_date": date,
            "error": str(e),
            "error_type": type(e).__name__,
            "elapsed_seconds": round(elapsed, 1),
        })
    
    # Wait between runs to avoid rate limiting
    if ticker != RUNS[-1][0] or date != RUNS[-1][1]:
        print("Waiting 15s to avoid rate limiting...")
        time.sleep(15)

# Save summary
summary_file = results_dir / "reproduction_summary.json"
with open(summary_file, "w", encoding="utf-8") as f:
    json.dump({
        "total_runs": len(results),
        "runs": [{k: v for k, v in r.items() if k not in 
                  ["market_report", "sentiment_report", "news_report", 
                   "fundamentals_report", "trader_investment_plan", "final_trade_decision"]}
                 for r in results],
        "timestamp": datetime.now().isoformat(),
    }, f, indent=2, ensure_ascii=False)

print(f"\n\n{'='*60}")
print(f"SUMMARY: {len(results)} runs completed")
print(f"{'='*60}")
for r in results:
    if "error" in r:
        print(f"  {r['ticker']} {r['trade_date']}: ERROR - {r['error_type']}")
    else:
        print(f"  {r['ticker']} {r['trade_date']}: {r['decision']} ({r['elapsed_seconds']}s)")
print(f"\nSummary saved to: {summary_file}")
