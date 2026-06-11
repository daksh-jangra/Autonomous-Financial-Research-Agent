import json
import jsonschema
from typing import Dict, Any, Callable
from .schemas.tool_schemas import ALL_SCHEMAS
from . import stubs

class ToolRegistry:
    def __init__(self):
        from .sec_edgar import get_sec_edgar_tool
        from .web_search import get_web_search_tool
        from .financial_api import financial_data_api
        from .news_sentiment import news_sentiment
        from .company_profile import company_profile
        from .earnings import earnings_transcript
        from .peer_comparison import peer_comparison
        from .report_gen import report_generator
        from .fact_checker import fact_checker
        from .calculator import calculation_engine
        from .memory_tools import vector_db_search, vector_db_store
        
        self.schemas = {schema["name"]: schema for schema in ALL_SCHEMAS}
        self.functions: Dict[str, Callable] = {
            "sec_filing_search": get_sec_edgar_tool(),
            "web_search": get_web_search_tool(),
            "earnings_transcript": earnings_transcript,
            "financial_data_api": financial_data_api,
            "news_sentiment": news_sentiment,
            "vector_db_search": vector_db_search,
            "vector_db_store": vector_db_store,
            "company_profile": company_profile,
            "peer_comparison": peer_comparison,
            "report_generator": report_generator,
            "fact_checker": fact_checker,
            "calculation_engine": calculation_engine
        }

    def get_all_schemas(self):
        return list(self.schemas.values())

    def validate_inputs(self, tool_name: str, kwargs: dict) -> bool:
        if tool_name not in self.schemas:
            raise ValueError(f"Tool {tool_name} not found in registry.")
        schema = self.schemas[tool_name]["parameters"]
        try:
            jsonschema.validate(instance=kwargs, schema=schema)
            return True
        except jsonschema.exceptions.ValidationError as e:
            raise ValueError(f"Validation error for {tool_name}: {e.message}")

    def execute_tool(self, tool_name: str, kwargs: dict) -> Any:
        self.validate_inputs(tool_name, kwargs)
        func = self.functions.get(tool_name)
        if not func:
            raise NotImplementedError(f"Function for tool {tool_name} is not implemented.")
        try:
            return func(**kwargs)
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"
