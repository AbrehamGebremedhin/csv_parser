"""
CSV Sales Data Generator

Improvements:
- Progress bar using tqdm
- Command-line arguments for flexibility
- Buffered writing for performance
- Optional random seed for reproducibility
- Logging for status and errors
"""
import csv
import random
from datetime import datetime, timedelta
from faker import Faker
import os
import argparse
import logging
from tqdm import tqdm
import threading

fake = Faker()

# Example department names (feel free to expand)
departments = [
    "Electronics", "Clothing", "Grocery", "Home & Kitchen", "Toys", 
    "Books", "Beauty", "Sports", "Automotive", "Health", 
    "Garden", "Jewelry", "Shoes", "Office Supplies", "Pet Supplies"
]

def generate_date(start_date="2020-01-01", end_date="2024-12-31"):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    delta = end - start
    random_days = random.randint(0, delta.days)
    return (start + timedelta(days=random_days)).date().isoformat()

def generate_csv(file_index, records_per_file, output_dir, start_date, end_date):
    filename = os.path.join(output_dir, f"sales_data_{file_index}.csv")
    try:
        with open(filename, mode='w', newline='', buffering=1024*1024) as file:
            writer = csv.writer(file)
            writer.writerow(["Department Name", "Date", "Number of Sales"])
            for _ in tqdm(range(records_per_file), desc=f"File {file_index}", unit="rows"):
                dept = random.choice(departments)
                date = generate_date(start_date, end_date)
                sales = random.randint(0, 500)
                writer.writerow([dept, date, sales])
        logging.info(f"Generated {filename}")
    except Exception as e:
        logging.error(f"Failed to generate {filename}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Generate synthetic sales CSV files.")
    parser.add_argument("-n", "--num_files", type=int, default=3, help="Number of CSV files to generate.")
    parser.add_argument("-r", "--records_per_file", type=int, default=10_000_000, help="Records per file.")
    parser.add_argument("-o", "--output_dir", type=str, default="sales_data", help="Output directory.")
    parser.add_argument("--start_date", type=str, default="2020-01-01", help="Start date (YYYY-MM-DD).")
    parser.add_argument("--end_date", type=str, default="2024-12-31", help="End date (YYYY-MM-DD).")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
    os.makedirs(args.output_dir, exist_ok=True)
    if args.seed is not None:
        random.seed(args.seed)
        Faker.seed(args.seed)

    threads = []
    for i in range(1, args.num_files + 1):
        t = threading.Thread(target=generate_csv, args=(i, args.records_per_file, args.output_dir, args.start_date, args.end_date))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()