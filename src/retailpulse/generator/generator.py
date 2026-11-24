"""Generate realistic, deterministic-in-shape retail datasets without large memory spikes."""

import csv
import json
import random
from datetime import UTC, datetime, timedelta
from pathlib import Path

from faker import Faker


class RetailDataGenerator:
    def __init__(self, output_dir: Path, seed: int = 42):
        self.output_dir = Path(output_dir)
        self.fake = Faker()
        Faker.seed(seed)
        random.seed(seed)

    def generate(self, customers: int, products: int, orders: int) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        customer_rows = []
        for index in range(1, customers + 1):
            customer_rows.append({
                "customer_id": index, "first_name": self.fake.first_name(),
                "last_name": self.fake.last_name(), "email": f"customer{index}@example.test",
                "city": self.fake.city(), "state": self.fake.state_abbr(),
                "country": "United States", "created_at": self._timestamp(),
                "updated_at": self._timestamp(),
            })
        self._write_csv("customers.csv", customer_rows)

        product_rows = []
        categories = ["electronics", "home", "beauty", "sports", "grocery"]
        for index in range(1, products + 1):
            price = round(random.uniform(8, 1200), 2)
            product_rows.append({
                "product_id": index, "product_name": self.fake.catch_phrase(),
                "category": random.choice(categories), "brand": self.fake.company(),
                "price": price, "cost_price": round(price * random.uniform(.45, .8), 2),
                "stock_quantity": random.randint(0, 1000), "created_at": self._timestamp(),
                "updated_at": self._timestamp(),
            })
        self._write_csv("products.csv", product_rows)

        order_rows, item_rows, payment_rows = [], [], []
        for order_id in range(1, orders + 1):
            order_date = datetime.now(UTC) - timedelta(days=random.randint(0, 730))
            item_count = random.randint(1, 5)
            item_total = 0.0
            for item_number in range(item_count):
                product_id = random.randint(1, products)
                quantity = random.randint(1, 4)
                unit_price = round(random.uniform(8, 1200), 2)
                subtotal = round(quantity * unit_price, 2)
                item_total += subtotal
                item_rows.append({"order_item_id": f"{order_id}-{item_number + 1}",
                                  "order_id": order_id, "product_id": product_id,
                                  "quantity": quantity, "unit_price": unit_price,
                                  "subtotal": subtotal})
            status = random.choices(["delivered", "shipped", "confirmed", "cancelled"], [.7, .15, .1, .05])[0]
            payment_status = "refunded" if status == "cancelled" else "paid"
            order_rows.append({"order_id": order_id, "customer_id": random.randint(1, customers),
                               "order_date": order_date.isoformat(), "order_status": status,
                               "total_amount": round(item_total, 2), "payment_status": payment_status,
                               "created_at": order_date.isoformat(), "updated_at": self._timestamp()})
            payment_rows.append({"payment_id": order_id, "order_id": order_id,
                                 "payment_method": random.choice(["card", "wallet", "bank_transfer"]),
                                 "payment_amount": round(item_total, 2), "payment_status": payment_status,
                                 "transaction_date": order_date.isoformat(), "updated_at": self._timestamp()})
        self._write_csv("orders.csv", order_rows)
        self._write_csv("order_items.csv", item_rows)
        self._write_csv("payments.csv", payment_rows)
        self._write_json("inventory.json", [{"product_id": i, "warehouse_id": "WH-01",
            "available_quantity": random.randint(0, 1000), "last_updated": self._timestamp()}
            for i in range(1, products + 1)])

    @staticmethod
    def _timestamp() -> str:
        return datetime.now(UTC).isoformat()

    def _write_csv(self, name: str, rows: list[dict]) -> None:
        with (self.output_dir / name).open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    def _write_json(self, name: str, rows: list[dict]) -> None:
        with (self.output_dir / name).open("w", encoding="utf-8") as file:
            json.dump(rows, file)
