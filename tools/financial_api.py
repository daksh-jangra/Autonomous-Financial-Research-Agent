import yfinance as yf
import json
import logging

def financial_data_api(ticker: str, statement_type: str, period: str, years: int) -> str:
    """Retrieves structured financial data using yfinance."""
    stock = yf.Ticker(ticker)
    
    try:
        if statement_type == "income_statement":
            df = stock.financials if period == "annual" else stock.quarterly_financials
        elif statement_type == "balance_sheet":
            df = stock.balance_sheet if period == "annual" else stock.quarterly_balance_sheet
        elif statement_type == "cash_flow":
            df = stock.cashflow if period == "annual" else stock.quarterly_cashflow
        else:
            return "Unsupported statement type."
            
        if df.empty:
            return f"No {statement_type} data found for {ticker}."
            
        # Select the requested number of years/periods and convert to dict
        data = df.iloc[:, :years].to_dict()
        
        # Convert Timestamp keys to strings for JSON serialization
        cleaned_data = {}
        for date_key, metrics in data.items():
            str_date = date_key.strftime('%Y-%m-%d') if hasattr(date_key, 'strftime') else str(date_key)
            cleaned_data[str_date] = metrics
            
        return json.dumps({
            "ticker": ticker,
            "statement_type": statement_type,
            "period": period,
            "data": cleaned_data
        })
        
    except Exception as e:
        logging.error(f"yfinance error for {ticker}: {str(e)}")
        return f"Error retrieving data for {ticker}: {str(e)}"
