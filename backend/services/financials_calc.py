
import yfinance as yf
from utils.cache import get_cache, set_cache
from utils.helpers import safe_round
from utils.yf_client import get_ticker, with_retries
import requests

# Patch yfinance session with browser headers
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
})

def get_financial_metrics(symbol: str) -> dict:
    """
    Calculate ROCE%, OPM%, and other financial metrics
    from yfinance financial statements
    """
    cache_key = f"financials_{symbol}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    try:
        ticker = get_ticker(symbol)
        info = with_retries(lambda: ticker.info)

        # Basic metrics from info
        pe_ratio = safe_round(info.get("trailingPE"))
        pb_ratio = safe_round(info.get("priceToBook"))
        market_cap = info.get("marketCap")
        current_price = info.get("regularMarketPrice") or info.get("currentPrice")

        # Get financial statements
        income_stmt = ticker.financials  # annual income statement
        balance_sheet = ticker.balance_sheet

        roce = "N/A"
        opm = "N/A"
        revenue = "N/A"
        net_profit = "N/A"
        operating_profit = "N/A"

        # Calculate OPM (Operating Profit Margin)
        if income_stmt is not None and not income_stmt.empty:
            try:
                # Get latest year data
                latest = income_stmt.iloc[:, 0]  # first column = latest year

                # Revenue
                total_revenue = None
                for key in ["Total Revenue", "Revenue", "Operating Revenue"]:
                    if key in latest.index:
                        total_revenue = latest[key]
                        break

                # Operating Income / EBIT
                ebit = None
                for key in ["EBIT", "Operating Income", "Operating Profit"]:
                    if key in latest.index:
                        ebit = latest[key]
                        break

                # Net Income
                net_income = None
                for key in ["Net Income", "Net Income Common Stockholders"]:
                    if key in latest.index:
                        net_income = latest[key]
                        break

                if total_revenue and total_revenue > 0:
                    revenue = safe_round(total_revenue / 10000000)  # in Cr

                    if ebit:
                        opm = safe_round((ebit / total_revenue) * 100)
                        operating_profit = safe_round(ebit / 10000000)

                    if net_income:
                        net_profit = safe_round(net_income / 10000000)

            except Exception as e:
                print(f"Income statement error for {symbol}: {e}")

        # Calculate ROCE (Return on Capital Employed)
        if income_stmt is not None and balance_sheet is not None:
            try:
                if not income_stmt.empty and not balance_sheet.empty:
                    latest_income = income_stmt.iloc[:, 0]
                    latest_bs = balance_sheet.iloc[:, 0]

                    # EBIT
                    ebit_val = None
                    for key in ["EBIT", "Operating Income"]:
                        if key in latest_income.index:
                            ebit_val = latest_income[key]
                            break

                    # Total Assets
                    total_assets = None
                    for key in ["Total Assets"]:
                        if key in latest_bs.index:
                            total_assets = latest_bs[key]
                            break

                    # Current Liabilities
                    current_liabilities = None
                    for key in ["Current Liabilities", "Total Current Liabilities"]:
                        if key in latest_bs.index:
                            current_liabilities = latest_bs[key]
                            break

                    # ROCE = EBIT / (Total Assets - Current Liabilities) * 100
                    if ebit_val and total_assets and current_liabilities:
                        capital_employed = total_assets - current_liabilities
                        if capital_employed > 0:
                            roce = safe_round((ebit_val / capital_employed) * 100)

            except Exception as e:
                print(f"ROCE calculation error for {symbol}: {e}")

        # 52 week return
        week_52_return = "N/A"
        try:
            high = info.get("fiftyTwoWeekHigh")
            low = info.get("fiftyTwoWeekLow")
            if current_price and low and low > 0:
                week_52_return = safe_round(((current_price - low) / low) * 100)
        except Exception:
            pass

        result = {
            "pe_ratio": pe_ratio,
            "pb_ratio": pb_ratio,
            "roce_pct": roce,
            "opm_pct": opm,
            "revenue_cr": revenue,
            "net_profit_cr": net_profit,
            "operating_profit_cr": operating_profit,
            "market_cap": market_cap,
            "current_price": safe_round(current_price),
            "week_52_return": week_52_return,
        }

        # Cache for 24 hours (financials don't change daily)
        set_cache(cache_key, result, ttl_seconds=86400)
        return result

    except Exception as e:
        print(f"Financial metrics error for {symbol}: {e}")
        return {
            "pe_ratio": "N/A",
            "pb_ratio": "N/A",
            "roce_pct": "N/A",
            "opm_pct": "N/A",
            "revenue_cr": "N/A",
            "net_profit_cr": "N/A",
            "operating_profit_cr": "N/A",
            "market_cap": None,
            "current_price": "N/A",
            "week_52_return": "N/A",
        }