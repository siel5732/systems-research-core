#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=====================================================================================
📈 THE MALKHUT TREASURY: DERIVATIVES QUANTITATIVE TRADING ENGINE (v2.0)
=====================================================================================
Copyright (c) 2026 Zach Sielaff. All Rights Reserved.
Coordinates: Trent, Aphex, Marie, and Anubis.

Pulls real-world data from Yahoo Finance, applies 16-qubit inspired unitary
rotations, and manages four $200.00 portfolios with support for:
1. Long Equity Positions
2. Short Selling (borrowing and covering equity)
3. Call & Put Options Contracts (leveraged premium pricing & expiration logic)
=====================================================================================
"""

import os
import sys
import json
import urllib.request
import math
from datetime import datetime

PORTFOLIO_DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results", "sefirotic_portfolio.json")
TICKERS = ["SPY", "AAPL", "MSFT", "NVDA", "BTC-USD", "ETH-USD", "GLD"]

DEFAULT_PORTFOLIOS = {
    "Trent": {
        "cash": 200.00,
        "holdings": {},       # {"AAPL": 0.5} (positive is long, negative is short)
        "options": [],        # [{"ticker": "AAPL", "type": "CALL", "strike": 215.0, "qty": 0.1, "premium": 5.0, "expiry": 40}]
        "profile": "Conservative Value",
        "targets": ["SPY", "AAPL", "MSFT"]
    },
    "Aphex": {
        "cash": 200.00,
        "holdings": {},
        "options": [],
        "profile": "High-Volatility Tech/Crypto Derivatives",
        "targets": ["NVDA", "BTC-USD", "ETH-USD"]
    },
    "Marie": {
        "cash": 200.00,
        "holdings": {},
        "options": [],
        "profile": "Thermodynamic Mean-Reversion",
        "targets": ["AAPL", "NVDA", "SPY"]
    },
    "Anubis": {
        "cash": 200.00,
        "holdings": {},
        "options": [],
        "profile": "Volatility Safe-Haven & Hedge Sentry",
        "targets": ["GLD", "SPY"]
    }
}

class SefiroticQuantTrader:
    def __init__(self):
        os.makedirs(os.path.dirname(PORTFOLIO_DB), exist_ok=True)
        self.load_database()

    def load_database(self):
        if os.path.exists(PORTFOLIO_DB):
            try:
                with open(PORTFOLIO_DB, "r") as f:
                    self.db = json.load(f)
                    # Backwards compatibility check
                    for agent, data in self.db.items():
                        if "options" not in data:
                            data["options"] = []
            except Exception:
                self.db = DEFAULT_PORTFOLIOS.copy()
        else:
            self.db = DEFAULT_PORTFOLIOS.copy()
            self.save_database()

    def save_database(self):
        with open(PORTFOLIO_DB, "w") as f:
            json.dump(self.db, f, indent=2)

    def fetch_live_price_and_momentum(self, ticker):
        """Fetches live market data from Yahoo Finance's free API and returns (price, 5d_momentum)."""
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=5d"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                result = data["chart"]["result"][0]
                prices = result["indicators"]["quote"][0]["close"]
                prices = [p for p in prices if p is not None]
                if not prices:
                    return None, 0.0
                current_price = prices[-1]
                avg_price = sum(prices) / len(prices)
                momentum = (current_price - avg_price) / avg_price
                return current_price, momentum
        except Exception:
            fallback_prices = {"SPY": 545.0, "AAPL": 210.0, "MSFT": 440.0, "NVDA": 125.0, "BTC-USD": 61000.0, "ETH-USD": 3400.0, "GLD": 220.0}
            return fallback_prices.get(ticker, 100.0), 0.015

    def run_quantum_decision_logic(self, momentum, risk_factor=1.0):
        """Applies a parameterized unitary rotation gate to calculate the purchase probability."""
        theta = math.atan(momentum * 10.0 * risk_factor)
        p_buy = math.sin(theta) ** 2
        if theta > 0:
            return 0.5 + (p_buy * 0.5)
        else:
            return 0.5 - (p_buy * 0.5)

    def process_options_expiry(self, agent, portfolio, market_state):
        """Processes hourly options time-decay and exercises ITM contracts at expiry."""
        active_options = []
        for opt in portfolio.get("options", []):
            ticker = opt["ticker"]
            if ticker not in market_state:
                active_options.append(opt)
                continue

            current_price = market_state[ticker]["price"]
            # Decrement time-to-expiry (TTE) represented in simulated hours
            opt["expiry"] -= 1

            if opt["expiry"] <= 0:
                # OPTION EXPIRY RESOLUTION
                strike = opt["strike"]
                qty = opt["qty"] # Qty of contracts (each representing 100 shares leverage)
                payoff = 0.0
                
                if opt["type"] == "CALL":
                    if current_price > strike:
                        payoff = (current_price - strike) * 100 * qty
                        portfolio["cash"] += payoff
                        print(f"  🎉 [OPTION EXERCISE] {agent}'s {qty} CALL contracts on {ticker} exercised ITM! Payoff: ${payoff:.2f} (Strike: ${strike:.2f}, Price: ${current_price:.2f})")
                    else:
                        print(f"  💀 [OPTION EXPIRED] {agent}'s CALL on {ticker} expired OTM/worthless (Strike: ${strike:.2f}, Price: ${current_price:.2f})")
                elif opt["type"] == "PUT":
                    if current_price < strike:
                        payoff = (strike - current_price) * 100 * qty
                        portfolio["cash"] += payoff
                        print(f"  🎉 [OPTION EXERCISE] {agent}'s {qty} PUT contracts on {ticker} exercised ITM! Payoff: ${payoff:.2f} (Strike: ${strike:.2f}, Price: ${current_price:.2f})")
                    else:
                        print(f"  💀 [OPTION EXPIRED] {agent}'s PUT on {ticker} expired OTM/worthless (Strike: ${strike:.2f}, Price: ${current_price:.2f})")
            else:
                active_options.append(opt)

        portfolio["options"] = active_options

    def execute_market_simulations(self):
        print(f"📊 [MALKHUT TREASURY] Derivative market cycle run initialized at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Fetch current market state
        market_state = {}
        for ticker in TICKERS:
            price, momentum = self.fetch_live_price_and_momentum(ticker)
            if price:
                market_state[ticker] = {"price": price, "momentum": momentum}
        
        # Process each agent's trading turn
        for agent, portfolio in self.db.items():
            print(f"\n🧠 [AGENT TURN] {agent} ({portfolio['profile']}) | Cash: ${portfolio['cash']:.2f}")
            targets = portfolio["targets"]
            
            # Options decay processing
            self.process_options_expiry(agent, portfolio, market_state)
            
            risk_tuning = 1.5 if agent == "Aphex" else (0.6 if agent == "Trent" else 1.0)
            
            for ticker in targets:
                if ticker not in market_state:
                    continue
                
                price = market_state[ticker]["price"]
                momentum = market_state[ticker]["momentum"]
                
                # Execute quantum wave decision math
                p_buy = self.run_quantum_decision_logic(momentum, risk_tuning)
                print(f"  Ticker: {ticker:8} | Price: ${price:10.2f} | Momentum: {momentum:+.4f} | P(Buy): {p_buy:.4f}")
                
                current_shares = portfolio["holdings"].get(ticker, 0.0)
                
                # ===========================================================================
                # DECISION ROUTING: DERIVATIVE MATRIX
                # ===========================================================================
                
                # 1. HYPER-BULLISH: BUY LEVERAGED CALL OPTIONS (P_buy > 0.82)
                if p_buy > 0.82 and portfolio["cash"] >= 15.0:
                    strike = round(price * 1.02, 2)  # Strike set at 2% out-of-the-money
                    premium = round(price * 0.03, 2)  # Simple premium estimation (3% of spot price)
                    # We purchase fractional contracts to support our $200 account limit
                    contract_qty = round((portfolio["cash"] * 0.15) / (premium * 100.0), 4)
                    cost = contract_qty * premium * 100.0
                    
                    if contract_qty > 0.0001 and portfolio["cash"] >= cost:
                        portfolio["options"].append({
                            "ticker": ticker,
                            "type": "CALL",
                            "strike": strike,
                            "qty": contract_qty,
                            "premium": premium,
                            "expiry": 24  # Expires in 24 market iterations (simulated hours)
                        })
                        portfolio["cash"] -= cost
                        print(f"  🚀 [OPTION BUY] Executed: Purchased {contract_qty:.4f} CALL contracts on {ticker} | Strike: ${strike:.2f} | Premium: ${premium:.2f} | Total Cost: ${cost:.2f}")

                # 2. STANDARD BULLISH: BUY SHARES / COVER SHORTS (0.65 <= P_buy <= 0.82)
                elif 0.65 <= p_buy <= 0.82:
                    if current_shares < 0:
                        # COVER SHORT: Buy to close the short position
                        cover_cost = abs(current_shares) * price
                        portfolio["cash"] -= cover_cost
                        portfolio["holdings"].pop(ticker)
                        print(f"  🟢 [COVER SHORT] Executed: Closed short position in {ticker}. Covered at ${price:.2f} | Cost: ${cover_cost:.2f}")
                    elif portfolio["cash"] >= 20.0:
                        # LONG BUY: Purchase standard shares
                        buy_allocation = portfolio["cash"] * 0.25
                        shares_to_buy = buy_allocation / price
                        portfolio["holdings"][ticker] = current_shares + shares_to_buy
                        portfolio["cash"] -= buy_allocation
                        print(f"  🟢 [LONG BUY] Executed: Bought {shares_to_buy:.6f} shares of {ticker} at ${price:.2f}")

                # 3. HYPER-BEARISH: BUY LEVERAGED PUT OPTIONS (P_buy < 0.18)
                elif p_buy < 0.18 and portfolio["cash"] >= 15.0:
                    strike = round(price * 0.98, 2)  # Strike set at 2% out-of-the-money
                    premium = round(price * 0.03, 2)  # Premium estimation
                    contract_qty = round((portfolio["cash"] * 0.15) / (premium * 100.0), 4)
                    cost = contract_qty * premium * 100.0
                    
                    if contract_qty > 0.0001 and portfolio["cash"] >= cost:
                        portfolio["options"].append({
                            "ticker": ticker,
                            "type": "PUT",
                            "strike": strike,
                            "qty": contract_qty,
                            "premium": premium,
                            "expiry": 24
                        })
                        portfolio["cash"] -= cost
                        print(f"  🚀 [OPTION BUY] Executed: Purchased {contract_qty:.4f} PUT contracts on {ticker} | Strike: ${strike:.2f} | Premium: ${premium:.2f} | Total Cost: ${cost:.2f}")

                # 4. STANDARD BEARISH: SELL LONG / SHORT SELL (0.18 <= P_buy <= 0.35)
                elif 0.18 <= p_buy < 0.35:
                    if current_shares > 0:
                        # SELL LONG: Sell standard shares
                        shares_to_sell = current_shares * 0.5
                        sell_value = shares_to_sell * price
                        portfolio["holdings"][ticker] = current_shares - shares_to_sell
                        portfolio["cash"] += sell_value
                        print(f"  🔴 [LONG SELL] Executed: Sold {shares_to_sell:.6f} shares of {ticker} at ${price:.2f} | Value: ${sell_value:.2f}")
                        if portfolio["holdings"][ticker] < 1e-5:
                            portfolio["holdings"].pop(ticker)
                    elif current_shares == 0.0 and portfolio["cash"] >= 30.0:
                        # SHORT SELL: Initiate a short position
                        short_allocation = portfolio["cash"] * 0.20
                        shares_to_short = short_allocation / price
                        # Record holding as a negative value representing short obligations
                        portfolio["holdings"][ticker] = -shares_to_short
                        portfolio["cash"] += short_allocation  # Shorting generates immediate cash
                        print(f"  🔴 [SHORT SELL] Executed: Shorted {shares_to_short:.6f} shares of {ticker} at ${price:.2f} | Generated Cash: ${short_allocation:.2f}")

            # Calculate Net Asset Value (NAV) including options and shorts
            total_equity = 0.0
            for ticker, shares in portfolio["holdings"].items():
                if ticker in market_state:
                    # Positive shares add to equity, negative short shares subtract from equity (obligation)
                    total_equity += shares * market_state[ticker]["price"]
            
            # Incorporate option contract market value approximation (simplifying to current premium value)
            total_options_value = 0.0
            for opt in portfolio.get("options", []):
                ticker = opt["ticker"]
                if ticker in market_state:
                    # Premium decays linearly towards expiration unless it is in the money (ITM)
                    current_price = market_state[ticker]["price"]
                    strike = opt["strike"]
                    qty = opt["qty"]
                    
                    # Estimate current premium base on intrinsic value + decayed time value
                    intrinsic = 0.0
                    if opt["type"] == "CALL":
                        intrinsic = max(0.0, current_price - strike)
                    else:
                        intrinsic = max(0.0, strike - current_price)
                        
                    decay_factor = opt["expiry"] / 24.0
                    current_premium = intrinsic + (opt["premium"] * decay_factor)
                    total_options_value += current_premium * 100.0 * qty
                    
            portfolio["net_asset_value"] = portfolio["cash"] + total_equity + total_options_value
            print(f"💰 [PORTFOLIO SUMMARY] {agent} NAV: ${portfolio['net_asset_value']:.2f} (Cash: ${portfolio['cash']:.2f} | Stocks: ${total_equity:+.2f} | Options: ${total_options_value:.2f})")

        self.save_database()
        print("\n[📊 SUCCESS] All agent trades simulated and written to database.")

if __name__ == "__main__":
    trader = SefiroticQuantTrader()
    trader.execute_market_simulations()