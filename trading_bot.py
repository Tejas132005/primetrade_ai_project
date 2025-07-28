import logging
from mock_binance import MockClient as Client  # Simulated client
import uuid

class BasicBot:
    def __init__(self, api_key=None, api_secret=None, testnet=True):
        self.client = Client()
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def place_order(self, symbol, side, order_type, quantity, price=None, stop_price=None, stop_limit_price=None):
        try:
            symbol = symbol.upper()
            side = 'BUY' if side.lower() == 'buy' else 'SELL'
            order_type = order_type.upper()

            if order_type == "OCO":
                # Validate inputs
                if price is None or stop_price is None or stop_limit_price is None:
                    raise ValueError("OCO requires limit price, stop price, and stop limit price.")

                # Generate unique group ID for linked orders
                oco_group_id = str(uuid.uuid4())

                # Place limit sell order (take profit)
                limit_order = self.client.futures_create_order(
                    symbol=symbol,
                    side=side,
                    type="LIMIT",
                    quantity=quantity,
                    price=price,
                    timeInForce="GTC",
                    oco_group_id=oco_group_id
                )

                # Place stop-limit sell order (stop loss)
                stop_limit_order = self.client.futures_create_order(
                    symbol=symbol,
                    side=side,
                    type="STOP_LIMIT",
                    quantity=quantity,
                    stopPrice=stop_price,
                    price=stop_limit_price,
                    timeInForce="GTC",
                    oco_group_id=oco_group_id
                )

                self.logger.info(f"✅ OCO Orders Placed:\nLimit Order: {limit_order}\nStop-Limit Order: {stop_limit_order}")

                return {"OCO": [limit_order, stop_limit_order]}

            else:
                order_data = {
                    'symbol': symbol,
                    'side': side,
                    'type': order_type,
                    'quantity': quantity,
                }

                if order_type == "LIMIT":
                    if price is None:
                        raise ValueError("LIMIT order requires a price.")
                    order_data['price'] = price
                    order_data['timeInForce'] = "GTC"

                elif order_type == "STOP_MARKET":
                    if stop_price is None:
                        raise ValueError("STOP_MARKET requires a stop price.")
                    order_data['stopPrice'] = stop_price

                elif order_type == "STOP_LIMIT":
                    if stop_price is None or price is None:
                        raise ValueError("STOP_LIMIT requires both stop and limit prices.")
                    order_data['stopPrice'] = stop_price
                    order_data['price'] = price
                    order_data['timeInForce'] = "GTC"

                order = self.client.futures_create_order(**order_data)
                self.logger.info(f"✅ Order Placed: {order}")
                return order

        except Exception as e:
            self.logger.error(f"❌ Error placing order: {e}")
            return None
