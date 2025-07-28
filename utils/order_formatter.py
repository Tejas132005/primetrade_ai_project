# utils/order_formatter.py

from rich.table import Table
from rich.console import Console
import datetime

def format_order(order):
    """Format a single order dictionary into a readable string."""
    ts = order.get("timestamp")
    dt = datetime.datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d %H:%M:%S") if ts else "-"
    return (
        f"[{order.get('symbol')}] {order.get('side')} {order.get('type')} | Qty: {order.get('quantity')} | "
        f"Status: {order.get('status')} | Time: {dt}"
    )

def print_orders_table(orders):
    console = Console()
    table = Table(title="📋 Open Orders", show_lines=True)

    table.add_column("#", style="cyan", no_wrap=True)
    table.add_column("Symbol", style="magenta")
    table.add_column("Side")  # Style will be applied dynamically per row
    table.add_column("Type", style="blue")
    table.add_column("Qty", style="yellow")
    table.add_column("Price", style="white")
    table.add_column("Status", style="bold")
    table.add_column("Time", style="dim")

    for idx, order in enumerate(orders, 1):
        dt = "-"
        if "timestamp" in order:
            try:
                dt = datetime.datetime.fromtimestamp(order["timestamp"] / 1000).strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                dt = "Invalid Time"

        side = order.get("side", "-")
        side_colored = f"[green]{side}[/green]" if side.upper() == "BUY" else f"[red]{side}[/red]"

        table.add_row(
            str(idx),
            order.get("symbol", "-"),
            side_colored,
            order.get("type", "-"),
            str(order.get("quantity", "-")),
            str(order.get("price", "-")),
            order.get("status", "-"),
            dt
        )

    console.print(table)

def print_oco_orders_table(oco_groups):
    """
    Print OCO orders grouped by their OCO order ID or clientOrderId.
    
    oco_groups: List of dicts, where each dict represents one OCO group, 
                containing its child orders (usually 2 orders).
    """
    console = Console()
    table = Table(title="🔗 OCO Orders Grouped", show_lines=True)

    # Columns:
    # OCO Group ID, Symbol, Side (Order 1), Type (Order 1), Price (Order 1), Stop Price (Order 1), Qty (Order 1), Status (Order 1), Time (Order 1),
    # Side (Order 2), Type (Order 2), Price (Order 2), Stop Price (Order 2), Qty (Order 2), Status (Order 2), Time (Order 2)

    table.add_column("OCO Group ID", style="cyan", no_wrap=True)
    table.add_column("Symbol", style="magenta")

    # First order columns
    table.add_column("Side 1")
    table.add_column("Type 1", style="blue")
    table.add_column("Price 1", style="white")
    table.add_column("Stop Price 1", style="white")
    table.add_column("Qty 1", style="yellow")
    table.add_column("Status 1", style="bold")
    table.add_column("Time 1", style="dim")

    # Second order columns
    table.add_column("Side 2")
    table.add_column("Type 2", style="blue")
    table.add_column("Price 2", style="white")
    table.add_column("Stop Price 2", style="white")
    table.add_column("Qty 2", style="yellow")
    table.add_column("Status 2", style="bold")
    table.add_column("Time 2", style="dim")

    for oco in oco_groups:
        # Extract OCO group ID from OCO order if available
        oco_id = oco.get("orderListId") or oco.get("clientOrderId") or "N/A"
        symbol = oco.get("symbol") or "-"
        orders = oco.get("orders") or oco.get("childOrders") or []

        # Ensure exactly two orders (OCO has 2 legs)
        order1 = orders[0] if len(orders) > 0 else {}
        order2 = orders[1] if len(orders) > 1 else {}

        def format_side(side):
            if not side:
                return "-"
            side = side.upper()
            return f"[green]{side}[/green]" if side == "BUY" else f"[red]{side}[/red]"

        def format_time(ts):
            if not ts:
                return "-"
            try:
                return datetime.datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                return "Invalid Time"

        table.add_row(
            str(oco_id),
            symbol,

            format_side(order1.get("side")),
            order1.get("type", "-"),
            str(order1.get("price", "-")),
            str(order1.get("stopPrice", "-")),
            str(order1.get("origQty") or order1.get("quantity") or "-"),
            order1.get("status", "-"),
            format_time(order1.get("time") or order1.get("timestamp")),

            format_side(order2.get("side")),
            order2.get("type", "-"),
            str(order2.get("price", "-")),
            str(order2.get("stopPrice", "-")),
            str(order2.get("origQty") or order2.get("quantity") or "-"),
            order2.get("status", "-"),
            format_time(order2.get("time") or order2.get("timestamp")),
        )

    console.print(table)
