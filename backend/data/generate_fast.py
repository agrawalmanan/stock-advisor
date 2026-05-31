import pandas as pd
import json

def generate_fast():
    print("Reading NSE CSV...")
    df = pd.read_csv("nse_equity_list.csv")

    # Strip spaces from ALL column names first
    df.columns = df.columns.str.strip()

    # Also strip spaces from SERIES column values
    df["SERIES"] = df["SERIES"].str.strip()

    # Keep only EQ series (regular stocks, filters out ETFs/bonds)
    df = df[df["SERIES"] == "EQ"]

    print(f"Total EQ stocks found: {len(df)}")

    stocks = []
    for _, row in df.iterrows():
        symbol = str(row["SYMBOL"]).strip() + ".NS"
        name = str(row["NAME OF COMPANY"]).strip()
        stocks.append({
            "name": name,
            "symbol": symbol,
            "sector": "Unknown",
            "peers": []
        })

    with open("nse_stocks.json", "w") as f:
        json.dump(stocks, f, indent=2)

    print(f"Done! Saved {len(stocks)} stocks to nse_stocks.json")

if __name__ == "__main__":
    generate_fast()