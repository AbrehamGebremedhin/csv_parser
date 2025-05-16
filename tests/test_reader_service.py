import pytest
import polars as pl
import tempfile
import os
import asyncio
from app.service.reader_service import AsyncCSVReaderService
from app.utils.logger import Logger

@pytest.mark.asyncio
async def test_aggregate_sales_by_department(tmp_path):
    # Prepare a sample CSV file
    csv_content = """Department Name,Date,Number of Sales\nSales,2024-01-01,10\nHR,2024-01-01,5\nSales,2024-01-02,15\n"""
    input_csv = tmp_path / "input.csv"
    input_csv.write_text(csv_content)
    output_dir = tmp_path
    service = AsyncCSVReaderService(logger=Logger())
    output_csv_path = await service.aggregate_sales_by_department(str(input_csv), str(output_dir))
    assert os.path.exists(output_csv_path)
    # Check output content
    df = pl.read_csv(output_csv_path)
    assert set(df.columns) == {"Department Name", "Total Number of Sales"}
    assert df.shape[0] == 2
    sales_row = df.filter(pl.col("Department Name") == "Sales")
    assert sales_row["Total Number of Sales"][0] == 25
    hr_row = df.filter(pl.col("Department Name") == "HR")
    assert hr_row["Total Number of Sales"][0] == 5
