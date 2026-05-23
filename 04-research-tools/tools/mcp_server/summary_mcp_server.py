"""
MCP Server for Paper Summaries using FastMCP

Manages research paper summaries with basic metadata.

Usage:
    uv run python summary_mcp_server.py
"""

import json
from dataclasses import dataclass, asdict
from typing import Optional

try:
    from fastmcp import FastMCP
except ImportError:
    print("Error: FastMCP not installed. Run: uv add fastmcp")
    import sys
    sys.exit(1)

# Create FastMCP server
mcp = FastMCP("paper-summaries")


@dataclass
class PaperSummary:
    """Research paper summary"""
    id: str
    title: str
    authors: list[str]
    url: str
    summary: str
    publication_date: Optional[str] = None


# In-memory storage
papers: dict[str, PaperSummary] = {}


@mcp.tool()
def add_paper_summary(
    title: str,
    authors: list[str],
    url: str,
    summary: str,
    publication_date: Optional[str] = None
) -> str:
    """
    Add a research paper summary with metadata.

    Args:
        title: Title of the research paper
        authors: List of author names
        url: URL where the paper can be accessed
        summary: Summary of the paper's key findings and contributions
        publication_date: Publication date (YYYY or YYYY-MM-DD)

    Returns:
        Paper ID for the added summary
    """
    paper_id = f"paper_{abs(hash(url)) % 10000:04d}"
    papers[paper_id] = PaperSummary(
        id=paper_id,
        title=title,
        authors=authors,
        url=url,
        summary=summary,
        publication_date=publication_date
    )
    return f"✓ Added paper [{paper_id}]: {title}"


@mcp.tool()
def get_paper_summary(paper_id: str) -> str:
    """
    Get a paper summary by ID.

    Args:
        paper_id: Paper ID (e.g., 'paper_0001')

    Returns:
        Paper details including title, authors, URL, and summary
    """
    if paper_id not in papers:
        return f"✗ Paper not found: {paper_id}"

    paper = papers[paper_id]
    authors_str = ", ".join(paper.authors)
    output = [
        f"Title: {paper.title}",
        f"Authors: {authors_str}",
        f"URL: {paper.url}",
    ]
    if paper.publication_date:
        output.append(f"Published: {paper.publication_date}")
    output.append(f"\nSummary:\n{paper.summary}")

    return "\n".join(output)


@mcp.tool()
def list_summaries() -> str:
    """
    List all paper summaries.

    Returns:
        List of all stored papers with brief summaries
    """
    if not papers:
        return "No paper summaries stored yet."

    output = [f"Stored Papers ({len(papers)} total):\n"]
    for i, paper in enumerate(papers.values(), 1):
        authors_str = ", ".join(paper.authors)
        output.append(f"\n{i}. [{paper.id}] {paper.title}")
        output.append(f"   Authors: {authors_str}")
        output.append(f"   Summary: {paper.summary[:100]}...")

    return "\n".join(output)


@mcp.tool()
def search_summaries(query: str) -> str:
    """
    Search paper summaries by keyword in title, authors, or summary content.

    Args:
        query: Search query

    Returns:
        Matching papers with full details
    """
    query_lower = query.lower()
    matching_papers = []

    # Search in title, authors, and summary
    for paper in papers.values():
        if (query_lower in paper.title.lower() or
            query_lower in paper.summary.lower() or
            any(query_lower in author.lower() for author in paper.authors)):
            matching_papers.append(paper)

    if not matching_papers:
        return f"No papers found matching '{query}'"

    output = [f"Found {len(matching_papers)} paper(s) matching '{query}':\n"]
    for paper in matching_papers:
        authors_str = ", ".join(paper.authors)
        output.append(f"\n[{paper.id}] {paper.title}")
        output.append(f"Authors: {authors_str}")
        output.append(f"Summary: {paper.summary}")
        output.append("---")

    return "\n".join(output)


@mcp.resource("papers://all")
def get_all_papers() -> str:
    """Get all paper summaries in JSON format"""
    return json.dumps(
        [asdict(paper) for paper in papers.values()],
        indent=2,
        default=str
    )


@mcp.resource("papers://stats")
def get_paper_stats() -> str:
    """Get statistics about stored papers"""
    stats = {
        "total_papers": len(papers),
        "papers_with_dates": sum(1 for p in papers.values() if p.publication_date)
    }
    return json.dumps(stats, indent=2)


if __name__ == "__main__":
    mcp.run()
