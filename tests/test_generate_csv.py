import os
import csv
import tempfile
import shutil
import pytest
from app.utils.generate_csv import generate_csv

def test_generate_csv_creates_valid_file():
    # Create a temporary directory for output
    with tempfile.TemporaryDirectory() as tmpdir:
        file_index = 1
        records_per_file = 10
        start_date = "2022-01-01"
        end_date = "2022-12-31"
        generate_csv(file_index, records_per_file, tmpdir, start_date, end_date)
        output_file = os.path.join(tmpdir, f"sales_data_{file_index}.csv")
        assert os.path.exists(output_file)
        # Check CSV content
        with open(output_file, newline='') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)
            assert rows[0] == ["Department Name", "Date", "Number of Sales"]
            assert len(rows) == records_per_file + 1  # header + records
            for row in rows[1:]:
                assert row[0]  # Department Name not empty
                assert row[1]  # Date not empty
                assert row[2].isdigit()  # Number of Sales is a digit
