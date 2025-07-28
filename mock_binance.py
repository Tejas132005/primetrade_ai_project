import time
import random
import json
import os

ORDERS_FILE = "orders.json"

class MockClient:
    def __init__(self):
        self.orders = self._load_orders()

    def _load_orders(self):
        if os.path.exists(ORDERS_FILE):
            with open(ORDERS_FILE, "r") as f:
                return json.load(f)
        return []

    def save_orders(self):
        with open(ORDERS_FILE, "w") as f:
            json.dump(self.orders, f, indent=4)

    def futures_create_order(self, **kwargs):
        time.sleep(1)

        # Special handling for OCO orders - expect a flag "oco_group_id"
        oco_group_id = kwargs.get("oco_group_id")

        mock_order = {
            "symbol": kwargs.get("symbol", "BTCUSDT"),
            "side": kwargs.get("side", "BUY"),
            "type": kwargs.get("type", "MARKET"),
            "quantity": kwargs.get("quantity", 1),
            "price": kwargs.get("price", None),
            "stopPrice": kwargs.get("stopPrice", None),
            "status": "FILLED",
            "orderId": random.randint(100000, 999999),
            "timestamp": int(time.time() * 1000),
            "oco_group_id": oco_group_id  # group id for linked orders
        }

        self.orders.append(mock_order)

        # Removed immediate cancellation of other OCO linked orders on placement.
        # (Simulate both OCO orders coexisting until one triggers/cancelled separately.)

        self.save_orders()
        return mock_order

    def get_all_orders(self):
        return self.orders
