def report_generator(template: str, sections: dict, sources: list) -> str:
    """Formats researched data into a structured investment research report."""
    report = f"# Investment Research Report\n**Template:** {template}\n\n"
    
    for title, content in sections.items():
        report += f"## {title}\n{content}\n\n"
        
    report += "## Sources and Methodology\n"
    for source in sources:
        report += f"- {source}\n"
        
    return report
