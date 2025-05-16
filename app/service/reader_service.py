import polars as pl
import asyncio
import uuid
import datetime
import os
import tempfile
from typing import Union

class AsyncCSVReaderService:
    @staticmethod
    async def aggregate_sales_by_department(
        input_csv_path: Union[str, bytes], output_dir: Union[str, bytes]
    ) -> str:
        """
        Asynchronously reads a very large CSV file, converts it to Parquet for DEX processing,
        aggregates total sales by department, and writes the result to a new CSV file with a time-based UUID in the filename.
        Returns the output file path.
        """
        loop = asyncio.get_event_loop()
        output_csv_path = await loop.run_in_executor(
            None,
            AsyncCSVReaderService._aggregate_sales_by_department_dex,
            input_csv_path,
            output_dir
        )
        return output_csv_path

    @staticmethod
    def _aggregate_sales_by_department_dex(
        input_csv_path: Union[str, bytes], output_dir: Union[str, bytes]
    ) -> str:
        # Generate a time-based UUID for the result file
        unique_id = uuid.uuid1().hex
        timestamp = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
        output_csv_path = os.path.join(
            str(output_dir), f"department_sales_{timestamp}_{unique_id}.csv"
        )
        # Step 1: Convert CSV to Parquet using streaming
        with tempfile.NamedTemporaryFile(suffix='.parquet', delete=True) as tmp_parquet:
            lf: pl.LazyFrame = pl.scan_csv(
                input_csv_path,
                dtypes={
                    "Department Name": pl.Utf8,
                    "Date": pl.Date,
                    "Number of Sales": pl.Int64,
                },
                ignore_errors=True,
                low_memory=True,
                rechunk=False,
            )
            lf.collect(streaming=True).write_parquet(tmp_parquet.name)

            # Step 2: Use DEX engine to aggregate from Parquet
            lf_parquet: pl.LazyFrame = pl.scan_parquet(tmp_parquet.name, low_memory=True)
            result: pl.LazyFrame = (
                lf_parquet.group_by("Department Name")
                .agg(pl.col("Number of Sales").sum().alias("Total Number of Sales"))
                .select(["Department Name", "Total Number of Sales"])
            )
            # Step 3: Collect and write to CSV
            df: pl.DataFrame = result.collect(streaming=True)
            df.write_csv(output_csv_path)
        return output_csv_path

# Example usage (in an async context):
# output_file = await AsyncCSVReaderService.aggregate_sales_by_department('input.csv', 'output_directory')