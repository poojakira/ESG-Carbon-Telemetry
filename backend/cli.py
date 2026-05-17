import typer # type: ignore
import requests # type: ignore
import json
import time
from rich.console import Console # type: ignore
from rich.table import Table # type: ignore
from rich.progress import Progress, SpinnerColumn, TextColumn # type: ignore
import os

app = typer.Typer(help="Carbon Analytics CLI")
console = Console()
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

def get_auth_header(token):
    return {"Authorization": f"Bearer {token}"}

@app.command()
def login(username: str = typer.Option(..., prompt=True), password: str = typer.Option(..., prompt=True, hide_input=True)):
    """ Authenticate with the the API. """
    with console.status("[bold green]Authenticating...") as status:
        try:
            r = requests.post(f"{BACKEND_URL}/api/v1/auth/login", json={"username": username, "password": password})
            if r.status_code == 200:
                token = r.json()["access_token"]
                with open(".ecotrack_token", "w") as f:
                    f.write(token)
                console.print("✅ [bold green]Access Granted.[/bold green] Token cached.")
            else:
                console.print(f"❌ [bold red]Access Denied:[/bold red] {r.text}")
        except Exception as e:
            console.print(f"💥 [bold red]Connection Error:[/bold red] {e}")

@app.command()
def verify():
    """ Run a full cryptographic audit of the ledger. """
    if not os.path.exists(".ecotrack_token"):
        console.print("❌ [bold red]Not Authenticated.[/bold red] Run 'ecotrack login' first.")
        return

    with open(".ecotrack_token", "r") as f:
        token = f.read()

    with console.status("[bold cyan]Executing Merkle Chain Audit...") as status:
        r = requests.get(f"{BACKEND_URL}/api/v1/ledger/verify-chain", headers=get_auth_header(token))
        if r.status_code == 200:
            res = r.json()
            color = "green" if res["status"] == "SECURE" else "red"
            console.print(f"🛡️  Status: [bold {color}]{res['status']}[/bold {color}]")
            console.print(f"📊 Records Scanned: {res['records_scanned']}")
            if res["status"] == "SECURE":
                console.print("💎 [bold green]Ledger Integrity Validated via Merkle Root.[/bold green]")
        else:
            console.print(f"❌ Audit Failed: {r.text}")

@app.command()
def ingest(file: str):
    """ High-throughput streaming ingestion from a local file. """
    if not os.path.exists(".ecotrack_token"):
         console.print("❌ [bold red]Not Authenticated.[/bold red]")
         return
    
    with open(".ecotrack_token", "r") as f:
        token = f.read()

    try:
        with open(file, "r") as f:
            data = json.load(f)
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
            progress.add_task(description="Streaming...", total=None)
            r = requests.post(f"{BACKEND_URL}/api/v1/data/ingest", json=data, headers=get_auth_header(token))
            
        if r.status_code == 202:
            res = r.json()
            console.print(f"🚀 [bold green]Ingestion Accepted.[/bold green] Batch ID: [cyan]{res['batch_id']}[/cyan] (Queued: {res['records_queued']})")
        else:
            console.print(f"❌ Ingestion Rejected: {r.text}")
    except Exception as e:
         console.print(f"💥 Error: {e}")

@app.command()
def status():
    """ Check API health and AI status. """
    r = requests.get(f"{BACKEND_URL}/health")
    if r.status_code == 200:
        res = r.json()
        table = Table(title="the API Status")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="magenta")
        table.add_row("Status", res["status"])
        table.add_row("Node", res["node"])
        table.add_row("Timestamp", res["timestamp"])
        console.print(table)
    else:
        console.print("❌ Nexus Offline.")

if __name__ == "__main__":
    app()
