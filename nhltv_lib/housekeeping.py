import os
from datetime import datetime, timedelta
from nhltv_lib.common import tprint
from nhltv_lib.game import get_days_back
from nhltv_lib.settings import get_download_folder, get_retentiondays


def do_housekeeping() -> None:
    retention_days = get_retentiondays()
    if not retention_days:
        return

    tprint(
        f"Running housekeeping.."
    )

    days_back = get_days_back()
    if retention_days < days_back:
        tprint(
            "WARNING: will use --days-back instead of --keep for housekeeping,"
            + " as keep is shorter than days-back (to avoid deleting downloaded games immediately)"
        )
        retention_days = days_back

    download_folder = get_download_folder()
    cutoff_date = datetime.now() - timedelta(days=retention_days)

    for filename in os.listdir(download_folder):
        if filename.endswith(".mkv"):
            # Extract the date part from the file name
            date_part = filename.split("_")[0]
            try:
                file_date = datetime.strptime(date_part, "%Y-%m-%d")
                if file_date < cutoff_date:
                    os.remove(os.path.join(download_folder, filename))
                    tprint(f"Deleted: {filename}")
            except ValueError:
                continue  # Skip files where the date is not properly formatted
