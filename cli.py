# cli.py

from trading_bot import BasicBot
from dotenv import load_dotenv
import os
from utils.order_formatter import print_orders_table, print_oco_orders_table

def get_user_input():
    symbol = input("Enter symbol (e.g., BTCUSDT): ").upper()

    while True:
        side = input("Enter side (buy/sell): ").lower()
        if side in ["buy", "sell"]:
            break
        print("❌ Invalid side. Please enter 'buy' or 'sell'.")

    while True:
        order_type = input("Enter order type (MARKET/LIMIT/STOP_LIMIT/STOP_MARKET/OCO): ").upper()
        if order_type in ["MARKET", "LIMIT", "STOP_LIMIT", "STOP_MARKET", "OCO"]:
            break
        print("❌ Invalid order type. Please choose from: MARKET, LIMIT, STOP_LIMIT, STOP_MARKET, OCO.")

    while True:
        try:
            quantity = float(input("Enter quantity: "))
            if quantity <= 0:
                raise ValueError
            break
        except ValueError:
            print("❌ Quantity must be a positive number.")

    price = stop_price = stop_limit_price = None

    if order_type == "LIMIT":
        price = float(input("Enter limit price: "))
    elif order_type == "STOP_LIMIT":
        stop_price = float(input("Enter stop price (trigger): "))
        price = float(input("Enter limit price (after trigger): "))
    elif order_type == "STOP_MARKET":
        stop_price = float(input("Enter stop price (trigger): "))
    elif order_type == "OCO":
        price = float(input("Enter take profit limit price: "))
        stop_price = float(input("Enter stop price (trigger): "))
        stop_limit_price = float(input("Enter stop limit price (after trigger): "))

    return symbol, side, order_type, quantity, price, stop_price, stop_limit_price


def print_grouped_orders(orders):
    """
    Groups orders by oco_group_id.
    Prints standalone orders with rich table.
    Prints OCO groups using rich table.
    """
    grouped = {}
    standalone = []

    for order in orders:
        oco_id = order.get("oco_group_id") or order.get("orderListId")  # Support possible keys for grouping OCO
        if oco_id:
            grouped.setdefault(oco_id, []).append(order)
        else:
            standalone.append(order)

    # Print standalone orders with rich table
    if standalone:
        print("\nStandalone Orders:")
        print_orders_table(standalone)

    # Print grouped OCO orders using the rich OCO table
    if grouped:
        print("\nOCO Order Groups:")
        # Prepare OCO groups in a list of dicts with keys 'orderListId' (group id), 'symbol', and 'orders' (list)
        oco_groups = []
        for oco_id, group_orders in grouped.items():
            # Try to get symbol from first order in group or fallback to '-'
            symbol = group_orders[0].get("symbol", "-") if group_orders else "-"
            oco_groups.append({
                "orderListId": oco_id,
                "symbol": symbol,
                "orders": group_orders
            })

        print_oco_orders_table(oco_groups)


if __name__ == "__main__":
    load_dotenv()

    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        print("❌ API key or secret not found. Please set them in the .env file.")
        exit()

    bot = BasicBot(api_key, api_secret)

    while True:
        print("\n🎯 Binance Mock Trading CLI")
        print("1️⃣  Place new order")
        print("2️⃣  View all orders")
        print("3️⃣  Exit")
        print("4️⃣  Clear all orders")

        choice = input("Choose an option (1/2/3/4): ").strip()

        if choice == "1":
            try:
                symbol, side, order_type, quantity, price, stop_price, stop_limit_price = get_user_input()
                order = bot.place_order(symbol, side, order_type, quantity, price, stop_price, stop_limit_price)

                if order:
                    if order_type == "OCO":
                        print("\n✅ OCO Order executed:")
                        # Assuming order['OCO'] is a list/dict of two orders
                        # Adapt this printout depending on your BasicBot output structure
                        if isinstance(order.get('OCO'), list):
                            for idx, oco_leg in enumerate(order['OCO'], 1):
                                print(f" - Leg {idx}: {oco_leg}")
                        else:
                            print(order['OCO'])
                    else:
                        print(f"\n✅ Order executed:\n{order}")
                else:
                    print("❌ Order failed.")
            except Exception as e:
                print(f"❌ Error: {e}")

        elif choice == "2":
            try:
                orders = bot.client.get_all_orders()
                if not orders:
                    print("📦 No orders placed yet.")
                else:
                    print(f"\n📋 Total Orders: {len(orders)}")
                    print_grouped_orders(orders)  # Use updated printing with OCO table support
            except Exception as e:
                print(f"❌ Error fetching orders: {e}")

        elif choice == "3":
            print("👋 Exiting.")
            break

        elif choice == "4":
            confirm = input("⚠ Are you sure you want to delete all orders? (yes/no): ").lower()
            if confirm == "yes":
                bot.client.orders = []
                bot.client.save_orders()
                print("🗑 All orders have been cleared.")
            else:
                print("❌ Cancelled.")

        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
