import asyncio
import argparse
import logging
import shutil
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

async def copy_file(file_path: Path, output_folder: Path):
    try:
        extension = file_path.suffix.lower().lstrip('.')
        if not extension:
            extension = "no_extension"
        target_dir = output_folder / extension

        await asyncio.to_thread(target_dir.mkdir, parents=True, exist_ok=True)

        target_path = target_dir / file_path.name

        await asyncio.to_thread(shutil.copyfile, str(file_path), str(target_path))
        logger.info(f"Copied: {file_path.name} -> {target_dir}")
    except Exception as e:
        logger.error(f"Error copying {file_path.name}: {e}")

async def read_folder(source_folder: Path, output_folder: Path):
    tasks = []
    try:
        for item in source_folder.iterdir():
            if item.is_dir():
                tasks.append(read_folder(item, output_folder))
            elif item.is_file():
                tasks.append(copy_file(item, output_folder))
        if tasks:
            await asyncio.gather(*tasks)
    except Exception as e:
        logger.error(f"Error reading folder {source_folder}: {e}")

async def main():
    parser = argparse.ArgumentParser(description="Async file sorter by extension")
    parser.add_argument("--source", "-s", required=True, help="Path to the source folder")
    parser.add_argument("--output", "-o", default="dist", help="Path to the output folder (default: dist)")

    args = parser.parse_args()

    source_path = Path(args.source)
    output_path = Path(args.output)

    if not source_path.exists() or not source_path.is_dir():
        logger.error(f"Source path '{args.source}' does not exist or is not a directory.")
        return
    
    logger.info(f"Starting sorting from '{source_path}' to '{output_path}'...")

    await read_folder(source_path, output_path)
    logger.info("Sorting completed.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Process interrupted by user.")
