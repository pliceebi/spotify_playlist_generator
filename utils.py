from datetime import datetime, timedelta


def yesterday_date_as_str() -> str:
    """Return yesterday date as string in DD-MM-YYYY format."""
    return (datetime.today() - timedelta(days=1)).date().strftime('%d-%m-%Y')
