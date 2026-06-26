# Hardcoded market data for the MVP
MARKET_DATA = {
    "nifty": {
        "name": "Nifty 50",
        "current_level": "23,500",
        "1_year_return": "26.5%",
        "3_year_return": "15.2%",
        "5_year_return": "14.8%",
        "10_year_return": "12.5%",
        "pe_ratio": "22.4",
        "52_week_high": "23,600",
        "52_week_low": "18,800"
    },
    "sensex": {
        "name": "BSE Sensex",
        "current_level": "77,300",
        "1_year_return": "25.1%",
        "3_year_return": "14.9%",
        "5_year_return": "14.5%",
        "10_year_return": "12.2%",
        "pe_ratio": "23.1",
        "52_week_high": "77,400",
        "52_week_low": "62,500"
    }
}

def get_market_data(stock_name: str) -> dict:
    """Checks if the user asked for Nifty or Sensex and returns the data."""
    name_lower = stock_name.lower()
    if "nifty" in name_lower:
        return MARKET_DATA["nifty"]
    elif "sensex" in name_lower:
        return MARKET_DATA["sensex"]
    else:
        return None