"""
AWS Lambda Handler for Citation Manager

Provides citation management functionality through Lambda.
Supports adding, retrieving, searching, and formatting citations in APA, MLA, and Chicago styles.

Event Format:
{
    "action": "add_citation" | "get_citation" | "list_citations" | "search_citations" | "remove_citation",
    "parameters": {
        # For add_citation:
        "title": "Paper Title",
        "url": "https://example.com/paper",
        "authors": ["Author 1", "Author 2"],
        "publication_date": "2024",
        "publisher": "Publisher Name",
        "doi": "10.xxxx/xxxxx",
        "citation_type": "website"

        # For get_citation:
        "citation_id": "cite_1234",
        "format": "apa" | "mla" | "chicago" | "json"

        # For list_citations:
        "format": "apa" | "mla" | "chicago"

        # For search_citations:
        "query": "search term"

        # For remove_citation:
        "citation_id": "cite_1234"
    }
}

Response Format:
{
    "statusCode": 200,
    "body": {
        "result": "...",
        "citation_id": "cite_1234"  # for add_citation
    }
}
"""

import json
import logging
from datetime import datetime
from typing import Literal
from dataclasses import dataclass

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


@dataclass
class Citation:
    """Research citation data"""
    id: str
    title: str
    url: str
    authors: list[str]
    access_date: datetime
    citation_type: str = "website"
    publication_date: str | None = None
    publisher: str | None = None
    doi: str | None = None

    def to_apa(self) -> str:
        """Format citation in APA style"""
        # Authors
        if len(self.authors) == 0:
            author_str = "Unknown"
        elif len(self.authors) == 1:
            author_str = self.authors[0]
        elif len(self.authors) == 2:
            author_str = f"{self.authors[0]} & {self.authors[1]}"
        else:
            author_str = f"{self.authors[0]} et al."

        # Date
        year = self.publication_date or self.access_date.strftime("%Y")

        # Build citation
        parts = [f"{author_str}. ({year})."]
        parts.append(f"{self.title}.")

        if self.publisher:
            parts.append(f"{self.publisher}.")

        parts.append(f"Retrieved {self.access_date.strftime('%B %d, %Y')}, from {self.url}")

        return " ".join(parts)

    def to_mla(self) -> str:
        """Format citation in MLA style"""
        # Authors
        if len(self.authors) == 0:
            author_str = "Unknown"
        else:
            author_str = self.authors[0]

        # Build citation
        parts = [f"{author_str}."]
        parts.append(f'"{self.title}."')

        if self.publisher:
            parts.append(f"{self.publisher},")

        if self.publication_date:
            parts.append(f"{self.publication_date}.")

        parts.append(f"Web. {self.access_date.strftime('%d %b. %Y')}.")
        parts.append(f"<{self.url}>.")

        return " ".join(parts)

    def to_chicago(self) -> str:
        """Format citation in Chicago style"""
        # Authors
        if len(self.authors) == 0:
            author_str = "Unknown"
        else:
            author_str = self.authors[0]

        # Build citation
        parts = [f"{author_str}."]
        parts.append(f'"{self.title}."')

        if self.publisher:
            parts.append(f"{self.publisher}.")

        if self.publication_date:
            parts.append(f"{self.publication_date}.")

        parts.append(f"Accessed {self.access_date.strftime('%B %d, %Y')}.")
        parts.append(f"{self.url}.")

        return " ".join(parts)


class CitationManager:
    """Manages a collection of citations (in-memory for Lambda)"""

    def __init__(self):
        """Initialize citation manager"""
        self.citations: dict[str, Citation] = {}

    def add_citation(
        self,
        title: str,
        url: str,
        authors: list[str] | None = None,
        publication_date: str | None = None,
        publisher: str | None = None,
        doi: str | None = None,
        citation_type: str = "website"
    ) -> str:
        """Add a new citation and return citation ID"""
        # Validate
        if not title or len(title) < 3:
            raise ValueError("Title must be at least 3 characters")

        if not url.startswith(('http://', 'https://')):
            raise ValueError("Invalid URL format")

        # Generate ID from URL
        citation_id = f"cite_{abs(hash(url)) % 10000:04d}"

        # Create citation
        citation = Citation(
            id=citation_id,
            title=title,
            url=url,
            authors=authors or [],
            access_date=datetime.now(),
            citation_type=citation_type,
            publication_date=publication_date,
            publisher=publisher,
            doi=doi
        )

        self.citations[citation_id] = citation
        return citation_id

    def get_citation(
        self,
        citation_id: str,
        format: Literal["apa", "mla", "chicago", "json"] = "apa"
    ) -> str:
        """Get citation by ID in specified format"""
        if citation_id not in self.citations:
            raise ValueError(f"Citation {citation_id} not found")

        citation = self.citations[citation_id]

        if format == "apa":
            return citation.to_apa()
        elif format == "mla":
            return citation.to_mla()
        elif format == "chicago":
            return citation.to_chicago()
        elif format == "json":
            return json.dumps({
                'id': citation.id,
                'title': citation.title,
                'url': citation.url,
                'authors': citation.authors,
                'access_date': citation.access_date.isoformat(),
                'publication_date': citation.publication_date,
                'publisher': citation.publisher,
                'doi': citation.doi,
                'type': citation.citation_type
            }, indent=2)
        else:
            raise ValueError(f"Unknown format: {format}")

    def list_citations(self, format: str = "apa") -> list[str]:
        """List all citations"""
        return [
            self.get_citation(cid, format=format)
            for cid in sorted(self.citations.keys())
        ]

    def search_citations(self, query: str) -> list[str]:
        """Search citations by title or author"""
        query_lower = query.lower()
        matches = []

        for cid, citation in self.citations.items():
            # Search in title
            if query_lower in citation.title.lower():
                matches.append(cid)
                continue

            # Search in authors
            if any(query_lower in author.lower() for author in citation.authors):
                matches.append(cid)
                continue

        return matches

    def remove_citation(self, citation_id: str) -> bool:
        """Remove citation by ID"""
        if citation_id in self.citations:
            del self.citations[citation_id]
            return True
        return False


# Global citation manager instance (persists across Lambda invocations)
citation_manager = CitationManager()


def handler(event, context):
    """
    AWS Lambda handler function for citation management

    Args:
        event: Lambda event containing action and parameters
        context: Lambda context object

    Returns:
        dict: Response with statusCode and body
    """
    logger.info(f"Lambda invoked with event: {json.dumps(event)}")

    try:
        # Extract action and parameters
        action = event.get('action', '')
        parameters = event.get('parameters', {})

        if not action:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Missing required field: action'
                })
            }

        # Route to appropriate handler
        if action == 'add_citation':
            citation_id = citation_manager.add_citation(
                title=parameters.get('title', ''),
                url=parameters.get('url', ''),
                authors=parameters.get('authors'),
                publication_date=parameters.get('publication_date'),
                publisher=parameters.get('publisher'),
                doi=parameters.get('doi'),
                citation_type=parameters.get('citation_type', 'website')
            )
            result = {
                'message': 'Citation added successfully',
                'citation_id': citation_id
            }

        elif action == 'get_citation':
            citation_id = parameters.get('citation_id', '')
            format = parameters.get('format', 'apa')
            result = {
                'citation': citation_manager.get_citation(citation_id, format=format)
            }

        elif action == 'list_citations':
            format = parameters.get('format', 'apa')
            result = {
                'citations': citation_manager.list_citations(format=format),
                'count': len(citation_manager.citations)
            }

        elif action == 'search_citations':
            query = parameters.get('query', '')
            matches = citation_manager.search_citations(query)
            result = {
                'matches': matches,
                'count': len(matches)
            }

        elif action == 'remove_citation':
            citation_id = parameters.get('citation_id', '')
            removed = citation_manager.remove_citation(citation_id)
            result = {
                'message': 'Citation removed' if removed else 'Citation not found',
                'removed': removed
            }

        else:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': f'Unknown action: {action}',
                    'valid_actions': ['add_citation', 'get_citation', 'list_citations',
                                     'search_citations', 'remove_citation']
                })
            }

        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': str(e),
                'type': 'ValidationError'
            })
        }

    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'type': type(e).__name__
            })
        }


# Health check handler
def health_check(event, context):
    """Simple health check handler"""
    return {
        'statusCode': 200,
        'body': json.dumps({
            'status': 'healthy',
            'service': 'citation-manager',
            'version': '1.0.0',
            'citations_count': len(citation_manager.citations)
        })
    }
