def calculation_engine(calculation_type: str, inputs: dict) -> dict:
    """Performs financial calculations."""
    try:
        if calculation_type == "growth_rate":
            current = float(inputs.get("current", 0))
            previous = float(inputs.get("previous", 1))
            if previous == 0: return {"error": "Division by zero"}
            rate = ((current - previous) / abs(previous)) * 100
            return {"calculation": "growth_rate", "result": f"{rate:.2f}%", "steps": [f"({current} - {previous}) / |{previous}|"]}
            
        elif calculation_type == "PE_ratio":
            price = float(inputs.get("price", 0))
            eps = float(inputs.get("eps", 1))
            if eps == 0: return {"error": "Division by zero"}
            pe = price / eps
            return {"calculation": "PE_ratio", "result": f"{pe:.2f}", "steps": [f"{price} / {eps}"]}
            
        return {"error": f"Unknown calculation type: {calculation_type}"}
    except Exception as e:
        return {"error": f"Calculation failed: {str(e)}"}
