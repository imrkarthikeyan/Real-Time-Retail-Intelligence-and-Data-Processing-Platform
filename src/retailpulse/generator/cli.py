import argparse

from retailpulse.config import settings
from retailpulse.generator.generator import RetailDataGenerator


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate RetailPulse CSV and JSON data")
    parser.add_argument("--customers", type=int, default=settings.gen_customers)
    parser.add_argument("--products", type=int, default=settings.gen_products)
    parser.add_argument("--orders", type=int, default=settings.gen_orders)
    parser.add_argument("--output", default=str(settings.data_root / "generated"))
    args = parser.parse_args()
    RetailDataGenerator(args.output).generate(args.customers, args.products, args.orders)


if __name__ == "__main__":
    main()
