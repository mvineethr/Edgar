"""Command-line interface for edgar13f.

Examples:
    export EDGAR_USER_AGENT="Vineeth M your-email@example.com"

    edgar13f search berkshire
    edgar13f holdings buffett
    edgar13f holdings 1067983 --limit 1
    edgar13f holdings buffett --csv buffett_q1.csv
    edgar13f diff buffett
    edgar13f diff buffett --csv buffett_changes.csv
    edgar13f quote AAPL BRK-B ^GSPC
    edgar13f news --symbol AAPL
    edgar13f consensus
    edgar13f dashboard
"""

from __future__ import annotations

import csv
import os
import sys

import click
from rich.console import Console
from rich.table import Table

from .cache import FilingCache, cached_information_table
from .client import EdgarClient
from .consensus import build_consensus_rows, fetch_latest_portfolios
from .diff import STATUS_ORDER, diff_holdings
from .presets import FAMOUS_INVESTORS

console = Console()

_STATUS_COLORS = {
    "NEW": "green",
    "SOLD": "red",
    "INCREASED": "cyan",
    "DECREASED": "yellow",
    "UNCHANGED": "dim",
}


def _get_user_agent() -> str:
    ua = os.environ.get("EDGAR_USER_AGENT")
    if not ua:
        console.print(
            "[red]Set the EDGAR_USER_AGENT environment variable first[/red] - "
            "SEC requires a descriptive User-Agent on every request, e.g.:\n\n"
            '  export EDGAR_USER_AGENT="Jane Doe jane@example.com"\n'
        )
        sys.exit(1)
    return ua


def _resolve_cik(identifier: str) -> str:
    """Accept either a raw CIK or one of the FAMOUS_INVESTORS shortcuts."""
    key = identifier.strip().lower()
    if key in FAMOUS_INVESTORS:
        return FAMOUS_INVESTORS[key]
    return identifier.strip()


@click.group()
def main():
    """edgar13f - free CLI for SEC 13F institutional holdings data."""


@main.command()
@click.argument("name")
def search(name: str):
    """Search EDGAR for a manager/fund CIK by name.

    Example: edgar13f search berkshire
    """
    client = EdgarClient(_get_user_agent())
    results = client.search_company_cik(name)
    if not results:
        console.print(f"No matches for '{name}'.")
        return

    table = Table(title=f"Matches for '{name}'")
    table.add_column("CIK")
    table.add_column("Name")
    for r in results:
        table.add_row(r["cik"] or "?", r["name"])
    console.print(table)


@main.command()
@click.argument("identifier")
@click.option("--limit", default=1, show_default=True, help="How many recent 13F-HR filings to consider")
@click.option("--csv", "csv_path", default=None, help="Write holdings to this CSV path instead of printing")
def holdings(identifier: str, limit: int, csv_path: str | None):
    """Show the latest 13F holdings for a CIK or a preset name.

    IDENTIFIER can be a raw CIK (e.g. 1067983) or a shortcut name from
    presets.py (e.g. buffett, burry, ackman, icahn).
    """
    cik = _resolve_cik(identifier)
    client = EdgarClient(_get_user_agent())

    filings = client.list_13f_filings(cik, limit=limit)
    if not filings:
        console.print(f"No 13F-HR filings found for CIK {cik}.")
        return

    latest = filings[0]
    console.print(
        f"[bold]Period of report:[/bold] {latest.period_of_report}  "
        f"(filed {latest.filing_date}, accession {latest.accession_number})"
    )

    rows = cached_information_table(client, FilingCache(), latest)
    rows.sort(key=lambda h: h.value_usd, reverse=True)

    if csv_path:
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["issuer", "cusip", "value_usd", "shares", "share_type"])
            for h in rows:
                writer.writerow(
                    [h.name_of_issuer, h.cusip, h.value_usd, h.shares, h.share_type]
                )
        console.print(f"Wrote {len(rows)} holdings to {csv_path}")
        return

    table = Table(title=f"Top holdings - CIK {cik}")
    table.add_column("Issuer")
    table.add_column("Value ($)", justify="right")
    table.add_column("Shares", justify="right")
    for h in rows[:25]:
        table.add_row(h.name_of_issuer, f"{h.value_usd:,}", f"{h.shares:,}")
    console.print(table)

    if len(rows) > 25:
        console.print(f"... and {len(rows) - 25} more positions. Use --csv to export all of them.")


@main.command()
@click.argument("identifier")
@click.option("--csv", "csv_path", default=None, help="Write the full diff to this CSV path instead of printing")
@click.option("--show-unchanged", is_flag=True, default=False, help="Include positions with no share-count change")
def diff(identifier: str, csv_path: str | None, show_unchanged: bool):
    """Show what changed between a manager's two most recent 13F-HR filings.

    Compares share counts and reported value by CUSIP, aggregating
    multiple infoTable entries for the same security within one filing.

    IDENTIFIER can be a raw CIK (e.g. 1067983) or a shortcut name from
    presets.py (e.g. buffett, burry, ackman, icahn).
    """
    cik = _resolve_cik(identifier)
    client = EdgarClient(_get_user_agent())

    filings = client.list_13f_filings(cik, limit=2)
    if len(filings) < 2:
        console.print(f"Need at least 2 13F-HR filings to diff; found {len(filings)} for CIK {cik}.")
        return

    current_filing, prior_filing = filings[0], filings[1]
    console.print(
        f"[bold]Comparing[/bold] {prior_filing.period_of_report} -> {current_filing.period_of_report}"
    )

    cache = FilingCache()
    prior_holdings = cached_information_table(client, cache, prior_filing)
    current_holdings = cached_information_table(client, cache, current_filing)
    changes = diff_holdings(prior_holdings, current_holdings)

    if not show_unchanged:
        changes = [c for c in changes if c.status != "UNCHANGED"]
    changes.sort(key=lambda c: (STATUS_ORDER[c.status], -abs(c.value_change_usd)))

    if csv_path:
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "issuer",
                    "cusip",
                    "status",
                    "prior_value_usd",
                    "current_value_usd",
                    "value_change_usd",
                    "prior_shares",
                    "current_shares",
                    "shares_change",
                ]
            )
            for c in changes:
                writer.writerow(
                    [
                        c.name_of_issuer,
                        c.cusip,
                        c.status,
                        c.prior_value_usd,
                        c.current_value_usd,
                        c.value_change_usd,
                        c.prior_shares,
                        c.current_shares,
                        c.shares_change,
                    ]
                )
        console.print(f"Wrote {len(changes)} changes to {csv_path}")
        return

    table = Table(title=f"Holdings changes - CIK {cik}")
    table.add_column("Issuer")
    table.add_column("Status")
    table.add_column("Value change ($)", justify="right")
    table.add_column("Shares change", justify="right")
    for c in changes[:40]:
        color = _STATUS_COLORS.get(c.status, "white")
        table.add_row(
            c.name_of_issuer,
            f"[{color}]{c.status}[/{color}]",
            f"{c.value_change_usd:+,}",
            f"{c.shares_change:+,}",
        )
    console.print(table)

    if len(changes) > 40:
        console.print(f"... and {len(changes) - 40} more changes. Use --csv to export all of them.")


@main.command()
@click.argument("symbols", nargs=-1, required=True)
def quote(symbols: tuple[str, ...]):
    """Live-ish quotes from Yahoo Finance's free endpoint (no API key).

    Example: edgar13f quote AAPL BRK-B ^GSPC BTC-USD
    """
    from .market import YahooMarketClient

    market = YahooMarketClient()
    quotes = market.get_quotes(list(symbols))

    table = Table(title="Quotes (Yahoo Finance, may be delayed)")
    table.add_column("Symbol")
    table.add_column("Price", justify="right")
    table.add_column("Change", justify="right")
    table.add_column("Change %", justify="right")
    table.add_column("Ccy")
    for symbol in symbols:
        q = quotes.get(symbol)
        if q is None:
            table.add_row(symbol, "?", "?", "?", "?")
            continue
        color = "green" if (q.change or 0) >= 0 else "red"
        table.add_row(
            q.symbol,
            f"{q.price:,.2f}",
            f"[{color}]{q.change:+,.2f}[/{color}]" if q.change is not None else "-",
            f"[{color}]{q.change_pct:+.2f}%[/{color}]" if q.change_pct is not None else "-",
            q.currency or "-",
        )
    console.print(table)


@main.command()
@click.option("--symbol", "symbols", multiple=True, help="Ticker(s) for company-specific headlines; omit for market-wide news")
@click.option("--limit", default=20, show_default=True)
def news(symbols: tuple[str, ...], limit: int):
    """Latest market headlines from free RSS feeds (Yahoo/CNBC/MarketWatch/SEC).

    Examples:
        edgar13f news
        edgar13f news --symbol AAPL --symbol MSFT
    """
    from .news import NewsClient

    client = NewsClient()
    if symbols:
        items = client.get_ticker_news(list(symbols), limit=limit)
    else:
        items = client.get_market_news(limit=limit)

    if not items:
        console.print("No headlines fetched - the feeds may be unreachable right now.")
        return

    for item in items:
        when = item.published.strftime("%Y-%m-%d %H:%M") if item.published else "        "
        tag = f" [{item.symbol}]" if item.symbol else ""
        console.print(f"[dim]{when}[/dim] [yellow]{item.source}[/yellow]{tag} {item.title}")
        console.print(f"  [blue underline]{item.link}[/blue underline]")


@main.command()
@click.option("--min-managers", default=2, show_default=True, help="Only show names held by at least this many managers")
@click.option("--limit", default=25, show_default=True)
@click.option("--csv", "csv_path", default=None, help="Write full consensus to this CSV path instead of printing")
def consensus(min_managers: int, limit: int, csv_path: str | None):
    """Which stocks do the tracked famous managers agree on right now?

    Cross-references the latest 13F filing of every manager in presets.py
    by CUSIP and ranks by how many managers hold each name.
    """
    client = EdgarClient(_get_user_agent())
    portfolios = fetch_latest_portfolios(client, FAMOUS_INVESTORS, cache=FilingCache())
    if not portfolios:
        console.print("Could not load any manager portfolios.")
        return
    rows = build_consensus_rows(portfolios, min_managers=min_managers)

    if csv_path:
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["issuer", "cusip", "manager_count", "managers",
                 "total_value_usd", "combined_weight_pct"]
            )
            for r in rows:
                writer.writerow(
                    [r.name_of_issuer, r.cusip, r.manager_count,
                     ";".join(r.managers), r.total_value_usd,
                     f"{r.combined_weight_pct:.2f}"]
                )
        console.print(f"Wrote {len(rows)} consensus rows to {csv_path}")
        return

    labels = ", ".join(p.label for p in portfolios)
    table = Table(title=f"Smart money consensus - {labels}")
    table.add_column("Issuer")
    table.add_column("Held by", justify="right")
    table.add_column("Managers")
    table.add_column("Combined value ($)", justify="right")
    for r in rows[:limit]:
        table.add_row(
            r.name_of_issuer,
            f"{r.manager_count}/{len(portfolios)}",
            ", ".join(r.managers),
            f"{r.total_value_usd:,}",
        )
    console.print(table)


@main.command()
@click.argument("symbol")
@click.option("--years", default=5, show_default=True)
def facts(symbol: str, years: int):
    """Annual fundamentals from SEC XBRL company facts (10-K data).

    Example: edgar13f facts AAPL
    """
    from .fundamentals import FundamentalsClient

    client = EdgarClient(_get_user_agent())
    fundamentals = FundamentalsClient(client)
    cik = fundamentals.ticker_to_cik(symbol)
    if cik is None:
        console.print(f"SEC has no filer for ticker '{symbol}'.")
        return
    rows = fundamentals.annual_metrics(symbol, years=years)
    if not rows:
        console.print(f"No annual XBRL facts for '{symbol}' (fund or foreign issuer?).")
        return

    def money(v):
        if v is None:
            return "-"
        return f"${v/1e9:,.2f}B" if abs(v) >= 1e9 else f"${v/1e6:,.1f}M"

    table = Table(title=f"{fundamentals.company_name(symbol)} (CIK {cik}) - annual, from 10-K XBRL")
    table.add_column("FY")
    table.add_column("Revenue", justify="right")
    table.add_column("Net income", justify="right")
    table.add_column("EPS dil.", justify="right")
    table.add_column("Assets", justify="right")
    table.add_column("Op. cash flow", justify="right")
    for r in rows:
        table.add_row(
            f"FY{r.fiscal_year} ({r.end_date})",
            money(r.revenue),
            money(r.net_income),
            f"{r.eps_diluted:,.2f}" if r.eps_diluted is not None else "-",
            money(r.total_assets),
            money(r.operating_cash_flow),
        )
    console.print(table)


@main.command()
@click.argument("identifier")
@click.argument("query")
@click.option("--quarters", default=8, show_default=True, help="How many quarters of 13F filings to walk")
def history(identifier: str, query: str, quarters: int):
    """One manager's stake in one security across N quarters of 13Fs.

    QUERY is a ticker (AAPL), a raw CUSIP, or an issuer-name substring.

    Example: edgar13f history buffett AAPL --quarters 12
    """
    from .views import Services, position_history_view

    svc = Services(_get_user_agent())
    console.print(f"[dim]Walking {quarters} quarters of 13F filings (first run fetches each filing once; cached afterwards)...[/dim]")
    result = position_history_view(svc, identifier, query, quarters=quarters)

    table = Table(
        title=f"{result['issuer']} held by {result['identifier']} "
        f"(CUSIP {', '.join(result['cusips'])})"
    )
    table.add_column("Period")
    table.add_column("Shares", justify="right")
    table.add_column("Value ($)", justify="right")
    table.add_column("Port. weight", justify="right")
    prev_shares = None
    for r in result["quarters"]:
        delta = ""
        if prev_shares is not None and r["shares"] != prev_shares:
            change = r["shares"] - prev_shares
            color = "green" if change > 0 else "red"
            delta = f"  [{color}]{change:+,}[/{color}]"
        table.add_row(
            r["period_of_report"] or "?",
            f"{r['shares']:,}{delta}",
            f"{r['value_usd']:,}",
            f"{r['weight_pct']:.1f}%",
        )
        prev_shares = r["shares"]
    console.print(table)


@main.command()
@click.argument("symbol")
@click.option("--filings", default=15, show_default=True, help="How many recent Form 4 filings to scan")
@click.option("--all", "show_all", is_flag=True, default=False, help="Show every transaction code, not just open-market P/S")
def insiders(symbol: str, filings: int, show_all: bool):
    """Form 4 insider transactions for a company (who's actually buying).

    By default only open-market purchases (P) and sales (S) are shown -
    grants, RSU vests, and tax withholding are noise for this signal.
    Use --all to see everything.

    Example: edgar13f insiders AAPL
    """
    from .views import Services, insiders_view

    svc = Services(_get_user_agent())
    result = insiders_view(svc, symbol, filings=filings)

    s = result["summary"]
    console.print(
        f"[bold]{result['company']}[/bold] (CIK {result['cik']}) - "
        f"last {result['filings_scanned']} Form 4 filings: "
        f"[green]{s['open_market_purchases']} open-market buys "
        f"(${s['purchase_value_usd']:,.0f})[/green], "
        f"[red]{s['open_market_sales']} open-market sells "
        f"(${s['sale_value_usd']:,.0f})[/red]"
    )

    rows = result["transactions"]
    if not show_all:
        rows = [t for t in rows if t["code"] in ("P", "S")]
    if not rows:
        console.print(
            "No open-market insider trades in these filings. "
            "Use --all to see grants/vests/withholding, or raise --filings."
        )
        return

    table = Table(title=f"Insider transactions - {result['symbol']}")
    table.add_column("Date")
    table.add_column("Insider")
    table.add_column("Role")
    table.add_column("Type")
    table.add_column("Shares", justify="right")
    table.add_column("Price", justify="right")
    table.add_column("Value ($)", justify="right")
    table.add_column("Owned after", justify="right")
    for t in rows[:40]:
        color = (
            "green" if t["code"] == "P"
            else "red" if t["code"] == "S"
            else "dim"
        )
        table.add_row(
            t["date"] or "?",
            t["insider"],
            t["relationship"],
            f"[{color}]{t['code_label']}[/{color}]",
            f"{t['shares']:,.0f}",
            f"{t['price_per_share']:,.2f}" if t["price_per_share"] else "-",
            f"{t['value_usd']:,.0f}" if t["value_usd"] else "-",
            f"{t['shares_owned_after']:,.0f}" if t["shares_owned_after"] is not None else "-",
        )
    console.print(table)
    if len(rows) > 40:
        console.print(f"... and {len(rows) - 40} more transactions.")


@main.command()
@click.argument("symbol")
def holders(symbol: str):
    """Which tracked famous managers hold a ticker (Bloomberg HDS-style).

    Example: edgar13f holders AAPL
    """
    from .views import Services, holders_view

    svc = Services(_get_user_agent())
    console.print("[dim]Cross-referencing tracked managers' latest 13Fs (first run maps every CUSIP and can take a minute)...[/dim]")
    result = holders_view(svc, symbol)
    if not result["holders"]:
        console.print(
            f"None of the tracked managers ({', '.join(result['tracked_managers'])}) "
            f"reported holding {result['symbol']} in their latest 13F."
        )
        return
    table = Table(title=f"Tracked managers holding {result['symbol']}")
    table.add_column("Manager")
    table.add_column("Shares", justify="right")
    table.add_column("Value ($)", justify="right")
    table.add_column("Port. weight", justify="right")
    table.add_column("As of")
    for h in result["holders"]:
        table.add_row(
            h["manager"],
            f"{h['shares']:,}",
            f"{h['value_usd']:,}",
            f"{h['weight_pct']:.1f}%",
            h["period_of_report"] or "?",
        )
    console.print(table)


@main.command()
def mcp():
    """Run the MCP tool server (stdio) so AI agents can use this terminal.

    Exposes portfolios, Q/Q changes, consensus, holders, quotes, charts,
    fundamentals, news, and world markets as MCP tools. Setup:

        claude mcp add edgar13f -e EDGAR_USER_AGENT="You you@example.com" -- edgar13f mcp

    Requires: pip install "edgar13f[mcp]"
    """
    ua = _get_user_agent()
    try:
        from .mcp_server import run_mcp_server
        run_mcp_server(ua)
    except ImportError as exc:
        console.print(f"[red]{exc}[/red]")
        sys.exit(1)


@main.command()
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", default=8813, show_default=True)
def dashboard(host: str, port: int):
    """Launch the Bloomberg-style terminal dashboard in your browser.

    Combines 13F portfolios, Q/Q changes, live quotes, a market tape,
    cross-manager consensus, and multi-source news on one dark screen.
    """
    from .dashboard import run_dashboard

    ua = _get_user_agent()
    console.print(
        f"[bold]EDGAR13F TERMINAL[/bold] starting at "
        f"[blue underline]http://{host}:{port}[/blue underline]  (Ctrl+C to stop)"
    )
    run_dashboard(ua, host=host, port=port)


if __name__ == "__main__":
    main()
