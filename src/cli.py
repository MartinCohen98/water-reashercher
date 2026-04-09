import typer
from typing import List
from rich.console import Console
from dotenv import load_dotenv

load_dotenv()

from search.groq import GroqSearchProvider
from search.gpt import GptSearchProvider
from search.gemma import GemmaSearchProvider
from search.base import SearchResult

app = typer.Typer(no_args_is_help=True)

console = Console()

DEFAULT_QUERIES = {
    "Water stress": "Water stress (Level of scarcity or physical risk in the area) in {location}",
    "Incidents/Conflicts": "Incidents/Conflicts (Reports of strikes, protests, or previous water-related crises) in {location}",
    "Regulations": "Regulations (Relevant local regulations regarding industrial use of the resource) in {location}",
}

PROVIDERS = {
    "gemma": GemmaSearchProvider,
    "groq": GroqSearchProvider,
    "gpt": GptSearchProvider,
}


@app.command()
def search(
    location: str = typer.Argument(..., help="Location to search for"),
    sources: List[str] = typer.Option(
        ["gpt"],
        "--source", "-s",
        help="Search sources to use",
    ),
    limit: int = typer.Option(10, "--limit", "-n", help="Results per source"),
):
    """Search for water research data for a location."""
    all_results = []
    
    for source in sources:
        if source not in PROVIDERS:
            console.print(f"[yellow]Unknown source: {source}[/yellow]")
            continue
        
        provider_class = PROVIDERS[source]
        provider = provider_class(num_results=limit)
        
        if not provider.is_available():
            console.print(f"[yellow]{source} not available (missing API key)[/yellow]")
            continue
        
        console.print(f"[cyan]Searching {source}...[/cyan]")
        
        for dimension in DEFAULT_QUERIES:
            query_template = DEFAULT_QUERIES[dimension]
            query = query_template.replace("{location}", location)
            results: List[SearchResult] = provider.search(query)
            for result in results:
                result.source = dimension
            all_results.extend(results)
    
    display_results(all_results)


@app.command()
def test(source: str = typer.Argument(..., help="Source to test")):
    """Test if a search source is working by performing a simple search."""
    if source not in PROVIDERS:
        console.print(f"[red]Unknown source: {source}[/red]")
        return
    
    provider_class = PROVIDERS[source]
    provider = provider_class()
    
    result = provider.test()
    status = "[green]Working[/green]" if result.working else "[red]Not Working[/red]"
    console.print(f"[bold]{source} Test Result:[/bold]")
    console.print(f"  Query: {result.query}")
    console.print(f"  Response: {result.response}")
    console.print(f"  Status: {status}")


@app.command()
def providers():
    """List all available search providers."""
    console.print("[bold]Available Search Providers:[/bold]")
    for name, provider_class in PROVIDERS.items():
        provider = provider_class()
        status = "[green]Available[/green]" if provider.is_available() else "[red]Not Available[/red]"
        console.print(f"  {name}: {status}")


def display_results(results):
    if not results:
        console.print("[yellow]No results found.[/yellow]")
        return
    
    for result in results:
        console.print(f"## {result.source}")
        if result.parsed_response:
            console.print(f"**Data:** {result.parsed_response.get('Data', 'N/A')}")
            console.print("**Sources:**")
            for source in result.parsed_response.get('Sources', []):
                console.print(f"- **Source:** {source.get('Source', 'N/A')}")
                console.print(f"  **Excerpt:** {source.get('Excerpt', 'N/A')}")
                console.print(f"  **Relevance:** {source.get('Relevance', 'N/A')}")
                console.print(f"  **Validation:** {source.get('Validation', 'N/A')}")
        else:
            console.print(f"**Snippet:** {result.snippet}")
        console.print()


if __name__ == "__main__":
    app()
