#!/usr/bin/env python3
"""
FTEC5660 Reproducibility - Modification Experiment (Ablation)

Modification: Remove the risk debate round (max_risk_discuss_rounds=0)
This skips the Aggressive/Conservative/Neutral risk analysts' debate,
going directly from the Trader to the Portfolio Manager.

Compare with baseline (max_risk_discuss_rounds=1):
- Does removing risk debate change the final decision?
- Does it change the reasoning quality?
- Does it speed up the run?

Paper reports risk management as a key component (Section 3.4).
We test whether it actually affects decisions.
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

# --- Common config ---
BASE_CONFIG = {
    "llm_provider": "deepseek",
    "deep_think_llm": "deepseek-reasoner",
    "quick_think_llm": "deepseek-chat",
    "max_debate_rounds": 1,
    "temperature": 0.0,
    "output_language": "English",
}

# Test cases: same as baseline reproduction
TEST_CASES = [
    ("NVDA", "2024-01-10"),
    ("AAPL", "2024-01-11"),
]

# --- Modification: max_risk_discuss_rounds = 0 (ablation: no risk debate) ---
MOD_CONFIG = BASE_CONFIG.copy()
MOD_CONFIG["max_risk_discuss_rounds"] = 0  # ABLATION: skip risk debate

results_dir = Path("reproduction_results")
if not results_dir.exists():
    results_dir.mkdir(parents=True)

results = []

for ticker, date in TEST_CASES:
    print(f"\n{'='*60}")
    print(f"ABLATION RUN: {ticker} on {date} (no risk debate)")
    print(f"{'='*60}")
    
    config = DEFAULT_CONFIG.copy()
    config.update(MOD_CONFIG)
    
    ta = TradingAgentsGraph(debug=False, config=config)
    
    start_time = time.time()
    try:
        final_state, decision = ta.propagate(ticker, date)
        elapsed = time.time() - start_time
        
        result = {
            "ticker": ticker,
            "trade_date": date,
            "decision": decision,
            "elapsed_seconds": round(elapsed, 1),
            "modification": "max_risk_discuss_rounds=0 (no risk debate)",
            "trader_investment_plan": final_state.get("trader_investment_plan", ""),
            "final_trade_decision": final_state.get("final_trade_decision", ""),
            "risk_debate_state": {
                "aggressive_history": final_state.get("risk_debate_state", {}).get("aggressive_history", []),
                "conservative_history": final_state.get("risk_debate_state", {}).get("conservative_history", []),
                "neutral_history": final_state.get("risk_debate_state", {}).get("neutral_history", []),
            },
            "investment_plan": final_state.get("investment_plan", ""),
            "market_report": final_state.get("market_report", ""),
            "fundamentals_report": final_state.get("fundamentals_report", ""),
            "sentiment_report": final_state.get("sentiment_report", ""),
            "news_report": final_state.get("news_report", ""),
            "timestamp": datetime.now().isoformat(),
        }
        results.append(result)
        
        print(f"Decision: {decision}")
        print(f"Elapsed: {elapsed:.1f}s")
        
        # Save individual result
        output_file = results_dir / f"ablation_{ticker}_{date}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"Saved to: {output_file}")
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"ERROR after {elapsed:.1f}s: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        results.append({
            "ticker": ticker,
            "trade_date": date,
            "error": str(e),
            "error_type": type(e).__name__,
            "elapsed_seconds": round(elapsed, 1),
        })
    
    # Wait between runs
    if ticker != TEST_CASES[-1][0] or date != TEST_CASES[-1][1]:
        print("Waiting 15s to avoid rate limiting...")
        time.sleep(15)

# Save summary
summary_file = results_dir / "ablation_summary.json"
with open(summary_file, "w", encoding="utf-8") as f:
    json.dump({
        "modification": "Removed risk debate (max_risk_discuss_rounds=0)",
        "total_runs": len(results),
        "runs": [{k: v for k, v in r.items() if k not in
                  ["market_report", "sentiment_report", "news_report",
                   "fundamentals_report", "trader_investment_plan", "final_trade_decision",
                   "investment_plan", "risk_debate_state"]}
                 for r in results],
        "timestamp": datetime.now().isoformat(),
    }, f, indent=2, ensure_ascii=False)

print(f"\n\n{'='*60}")
print(f"ABLATION SUMMARY: {len(results)} runs completed")
print(f"{'='*60}")
for r in results:
    if "error" in r:
        print(f"  {r['ticker']} {r['trade_date']}: ERROR - {r['error_type']}")
    else:
        print(f"  {r['ticker']} {r['trade_date']}: {r['decision']} ({r['elapsed_seconds']}s)")
print(f"\nSummary saved to: {summary_file}")
