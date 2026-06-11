# JSON schemas for tools following OpenAI function calling specification

SEC_FILING_SEARCH_SCHEMA = {
    "name": "sec_filing_search",
    "description": "Search and retrieve SEC EDGAR filings for a publicly traded US company. Use this tool when you need official regulatory disclosures including annual reports (10-K), quarterly reports (10-Q), material event reports (8-K), or proxy statements (DEF 14A). Returns the full text of the filing.",
    "parameters": {
        "type": "object",
        "properties": {
            "ticker": {
                "type": "string",
                "description": "Stock ticker symbol (e.g., AAPL, MSFT)"
            },
            "filing_type": {
                "type": "string",
                "enum": ["10-K", "10-Q", "8-K", "DEF 14A"],
                "description": "Type of SEC filing to retrieve"
            },
            "year": {
                "type": "integer",
                "description": "Filing year (defaults to most recent)"
            }
        },
        "required": ["ticker", "filing_type"]
    }
}

WEB_SEARCH_SCHEMA = {
    "name": "web_search",
    "description": "Performs web search for current news, analysis, and commentary about a company or financial topic.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query."
            },
            "num_results": {
                "type": "integer",
                "description": "Number of results to return.",
                "default": 10
            },
            "date_range": {
                "type": "string",
                "description": "Optional date range for the search."
            }
        },
        "required": ["query"]
    }
}

EARNINGS_TRANSCRIPT_SCHEMA = {
    "name": "earnings_transcript",
    "description": "Retrieves earnings call transcript for a specific company, quarter, and year.",
    "parameters": {
        "type": "object",
        "properties": {
            "ticker": {
                "type": "string",
                "description": "Stock ticker symbol."
            },
            "quarter": {
                "type": "string",
                "description": "Quarter (Q1-Q4)."
            },
            "year": {
                "type": "integer",
                "description": "Year of the earnings call."
            }
        },
        "required": ["ticker", "quarter", "year"]
    }
}

FINANCIAL_DATA_API_SCHEMA = {
    "name": "financial_data_api",
    "description": "Retrieves structured financial data including income statement, balance sheet, cash flow, and key ratios.",
    "parameters": {
        "type": "object",
        "properties": {
            "ticker": {
                "type": "string",
                "description": "Stock ticker symbol."
            },
            "statement_type": {
                "type": "string",
                "enum": ["income_statement", "balance_sheet", "cash_flow", "ratios"],
                "description": "Type of financial data to retrieve."
            },
            "period": {
                "type": "string",
                "enum": ["annual", "quarterly"],
                "description": "Reporting period."
            },
            "years": {
                "type": "integer",
                "description": "Number of historical years to retrieve."
            }
        },
        "required": ["ticker", "statement_type", "period", "years"]
    }
}

NEWS_SENTIMENT_SCHEMA = {
    "name": "news_sentiment",
    "description": "Analyzes sentiment of recent news articles about a company or topic using NLP.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Company ticker or topic to search news for."
            },
            "num_articles": {
                "type": "integer",
                "description": "Number of articles to analyze."
            },
            "lookback_days": {
                "type": "integer",
                "description": "Number of past days to search."
            }
        },
        "required": ["query", "num_articles", "lookback_days"]
    }
}

VECTOR_DB_SEARCH_SCHEMA = {
    "name": "vector_db_search",
    "description": "Searches the agent's long-term memory (vector database) for previously researched information.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query."
            },
            "top_k": {
                "type": "integer",
                "description": "Number of relevant chunks to retrieve."
            },
            "filter": {
                "type": "object",
                "description": "Optional metadata filters (e.g., {'ticker': 'AAPL'})."
            }
        },
        "required": ["query", "top_k"]
    }
}

VECTOR_DB_STORE_SCHEMA = {
    "name": "vector_db_store",
    "description": "Stores new research findings in the agent's long-term memory for future retrieval.",
    "parameters": {
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "Text content to store."
            },
            "metadata": {
                "type": "object",
                "description": "Dictionary containing metadata (ticker, date, source_type)."
            }
        },
        "required": ["content", "metadata"]
    }
}

COMPANY_PROFILE_SCHEMA = {
    "name": "company_profile",
    "description": "Retrieves basic company information including sector, industry, market cap, executives, and description.",
    "parameters": {
        "type": "object",
        "properties": {
            "ticker": {
                "type": "string",
                "description": "Stock ticker symbol."
            }
        },
        "required": ["ticker"]
    }
}

PEER_COMPARISON_SCHEMA = {
    "name": "peer_comparison",
    "description": "Identifies peer companies and retrieves comparative financial metrics.",
    "parameters": {
        "type": "object",
        "properties": {
            "ticker": {
                "type": "string",
                "description": "Target company ticker."
            },
            "num_peers": {
                "type": "integer",
                "description": "Number of peers to compare against."
            },
            "metrics": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of financial metrics to compare (e.g., ['ROE', 'EBITDA Margin'])."
            }
        },
        "required": ["ticker", "num_peers", "metrics"]
    }
}

REPORT_GENERATOR_SCHEMA = {
    "name": "report_generator",
    "description": "Formats researched data into a structured investment research report following a specified template.",
    "parameters": {
        "type": "object",
        "properties": {
            "template": {
                "type": "string",
                "description": "Name of the template (e.g., 'risk_assessment', 'earnings_analysis')."
            },
            "sections": {
                "type": "object",
                "description": "Dictionary of section headers mapping to text content."
            },
            "sources": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of sources used in the report."
            }
        },
        "required": ["template", "sections", "sources"]
    }
}

FACT_CHECKER_SCHEMA = {
    "name": "fact_checker",
    "description": "Cross-references a specific claim against multiple authoritative sources to verify accuracy.",
    "parameters": {
        "type": "object",
        "properties": {
            "claim": {
                "type": "string",
                "description": "The specific claim to verify."
            },
            "sources": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional list of sources to check."
            }
        },
        "required": ["claim"]
    }
}

CALCULATION_ENGINE_SCHEMA = {
    "name": "calculation_engine",
    "description": "Performs financial calculations including DCF, ratios, growth rates, and statistical analysis.",
    "parameters": {
        "type": "object",
        "properties": {
            "calculation_type": {
                "type": "string",
                "description": "Type of calculation (e.g., 'growth_rate', 'DCF', 'PE_ratio')."
            },
            "inputs": {
                "type": "object",
                "description": "Dictionary of numerical inputs required for the calculation."
            }
        },
        "required": ["calculation_type", "inputs"]
    }
}

ALL_SCHEMAS = [
    SEC_FILING_SEARCH_SCHEMA,
    WEB_SEARCH_SCHEMA,
    EARNINGS_TRANSCRIPT_SCHEMA,
    FINANCIAL_DATA_API_SCHEMA,
    NEWS_SENTIMENT_SCHEMA,
    VECTOR_DB_SEARCH_SCHEMA,
    VECTOR_DB_STORE_SCHEMA,
    COMPANY_PROFILE_SCHEMA,
    PEER_COMPARISON_SCHEMA,
    REPORT_GENERATOR_SCHEMA,
    FACT_CHECKER_SCHEMA,
    CALCULATION_ENGINE_SCHEMA
]
