from dotenv import load_dotenv
load_dotenv()
from services.screener_client import get_screener_data

stocks = {
    # IT
    'INFY': 'IT Services',
    'WIPRO': 'IT Services',
    'HCLTECH': 'IT Services',
    # Banking
    'ICICIBANK': 'Banking',
    'SBIN': 'Banking',
    'KOTAKBANK': 'Banking',
    # Pharma
    'DRREDDY': 'Pharmaceuticals',
    'CIPLA': 'Pharmaceuticals',
    # Auto
    'TATAMOTORS': 'Automobile',
    'BAJAJ-AUTO': 'Automobile',
    'HEROMOTOCO': 'Automobile',
    # FMCG
    'HINDUNILVR': 'FMCG',
    'ITC': 'FMCG',
    'NESTLEIND': 'FMCG',
    'BRITANNIA': 'FMCG',
    # Metals
    'JSWSTEEL': 'Steel',
    'SAIL': 'Steel',
    'VEDL': 'Metals & Mining',
    'COALINDIA': 'Metals & Mining',
    # Cement
    'ULTRACEMCO': 'Cement',
    'AMBUJACEM': 'Cement',
    # Oil & Gas
    'ONGC': 'Oil & Gas',
    'IOC': 'Oil & Gas',
    'BPCL': 'Oil & Gas',
    # Power
    'NTPC': 'Power & Utilities',
    'POWERGRID': 'Power & Utilities',
    'TATAPOWER': 'Power & Utilities',
    # Financial Services
    'BAJAJFINSV': 'Financial Services',
    'CHOLAFIN': 'Financial Services',
    # Telecom
    'BHARTIARTL': 'Telecom',
    # Infra
    'LT': 'Infrastructure',
    # Defence
    'HAL': 'Defence',
    'BEL': 'Defence',
    # Paints
    'BERGEPAINT': 'Paints',
    # Real Estate
    'DLF': 'Real Estate',
    # Chemicals
    'PIDILITIND': 'Chemicals',
    'UPL': 'Chemicals',
    # Hotels
    'INDHOTEL': 'Hotels & Tourism',
    # Retail
    'TRENT': 'Retail',
    'DMART': 'Retail',
    # Diversified
    'RELIANCE': 'Diversified',
    'ADANIENT': 'Diversified',
}

print(f"Testing {len(stocks)} stocks...\n")

correct = 0
wrong = 0

for sym, expected in stocks.items():
    r = get_screener_data(f'{sym}.NS')
    actual = r['sector']
    match = '✅' if actual == expected else '❌'
    if actual == expected:
        correct += 1
    else:
        wrong += 1
    print(f"{match} {sym:15s} Expected: {expected:25s} Got: {actual}")

print(f"\n{'='*60}")
print(f"Results: {correct}/{correct+wrong} correct ({wrong} wrong)")