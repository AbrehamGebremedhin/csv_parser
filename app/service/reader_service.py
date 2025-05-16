import polars as pl
import asyncio
import uuid
import datetime
import os
import tempfile
import time
from typing import Union, Optional
from app.utils.logger import Logger

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../OUTPUT_DIR')

class AsyncCSVReaderService:
    def __init__(self, logger: Optional[Logger] = None):
        self.logger = logger or Logger()

    async def aggregate_sales_by_department(
        self,
        input_csv_path: Union[str, bytes],
        output_dir: Union[str, bytes] = OUTPUT_DIR,
        retries: int = 3,
        delay: float = 2.0
    ) -> str:
        attempt = 0
        while attempt < retries:
            try:
                self.logger.info(f"Starting aggregation for file: {input_csv_path} (Attempt {attempt+1}/{retries})")
                loop = asyncio.get_event_loop()
                output_csv_path = await loop.run_in_executor(
                    None,
                    self._aggregate_sales_by_department_dex,
                    input_csv_path,
                    output_dir
                )
                self.logger.info(f"Aggregation complete. Output file: {output_csv_path}")
                return output_csv_path
            except Exception as e:
                attempt += 1
                self.logger.error(f"Attempt {attempt} failed: {e}")
                if attempt < retries:
                    self.logger.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    self.logger.critical(f"All {retries} attempts failed. Giving up.")
                    raise

    def _aggregate_sales_by_department_dex(
        self,
        input_csv_path: Union[str, bytes],
        output_dir: Union[str, bytes] = OUTPUT_DIR
    ) -> str:
        try:
            # Ensure output directory exists
            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            unique_id = uuid.uuid1().hex
            timestamp = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
            output_csv_path = os.path.join(
                str(output_dir), f"department_sales_{timestamp}_{unique_id}.csv"
            )
            self.logger.info(f"Converting CSV to Parquet for file: {input_csv_path}")
            with tempfile.NamedTemporaryFile(suffix='.parquet', delete=True) as tmp_parquet:
                lf: pl.LazyFrame = pl.scan_csv(
                    input_csv_path,
                    dtypes={
                        "Department Name": pl.Utf8,
                        "Date": pl.Date,
                        "Number of Sales": pl.Utf8,  # Read as string for cleaning
                    },
                    ignore_errors=True,
                    low_memory=True,
                    rechunk=False,
                )                # Step 1: Force all columns to string for consistent processing
                lf = lf.with_columns([
                    pl.col("Number of Sales").cast(pl.Utf8).alias("Number of Sales"),
                    pl.col("Department Name").cast(pl.Utf8).alias("Department Name"),
                    pl.col("Date").cast(pl.Utf8).alias("Date")
                ])
                  # Step 2: Clean and convert 'Number of Sales' to integer
                # - Replace empty strings with '0'
                # - For non-numeric strings, extract just the digits or use '0'
                # - Cast to Int64 and ensure no nulls
                lf = lf.with_columns([
                    pl.when(pl.col("Number of Sales") == "")
                      .then(pl.lit("0"))
                      .otherwise(pl.col("Number of Sales"))
                      .alias("Number of Sales")
                ])
                
                lf = lf.with_columns([
                    pl.col("Number of Sales")
                      .str.replace_all(r"[^0-9]", "")  # Remove all non-digits
                      .str.replace_all(r"^$", "0")     # Empty string to "0"
                      .cast(pl.Int64)                  # Cast to Int64
                      .fill_null(0)                    # Fill any nulls with 0
                      .alias("Number of Sales")
                ])
                  # Debug log the column type
                self.logger.info(f"Number of Sales column type: {lf.select('Number of Sales').collect().dtypes}")
                lf.collect().write_parquet(tmp_parquet.name)
                self.logger.info(f"CSV converted to Parquet: {tmp_parquet.name}")
                lf_parquet: pl.LazyFrame = pl.scan_parquet(tmp_parquet.name, low_memory=True)
                result: pl.LazyFrame = (
                    lf_parquet.group_by("Department Name")
                    .agg(pl.col("Number of Sales").sum().alias("Total Number of Sales"))
                    .select(["Department Name", "Total Number of Sales"])
                )
                self.logger.info("Aggregating sales by department using DEX engine.")
                df: pl.DataFrame = result.collect()
                df.write_csv(output_csv_path)
                self.logger.info(f"Aggregation written to CSV: {output_csv_path}")
            return output_csv_path
        except Exception as e:
            self.logger.error(f"Error during aggregation: {e}")
            raise
