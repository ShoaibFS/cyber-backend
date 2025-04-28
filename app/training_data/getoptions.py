import pandas as pd

def get_unique_options(csv_path: str):
    """
    Reads the CSV at `csv_path` and returns a dict mapping
    each categorical column to its sorted list of unique values.
    """
    df = pd.read_csv(csv_path)

    categorical_cols = [
        "Protocol",
        "Packet Type",
        "Traffic Type",
        "Attack Type",
    ]

    options = {}
    for col in categorical_cols:
        # drop NaNs, get uniques, sort for consistency
        uniques = df[col].dropna().unique().tolist()
        try:
            # if they’re all numeric strings, cast to int
            uniques = sorted(int(u) for u in uniques)
        except Exception:
            uniques = sorted(uniques)
        options[col] = uniques

    return options

if __name__ == "__main__":
    CSV_PATH = "./cybersecurity_attacks.csv"
    opts = get_unique_options(CSV_PATH)
    for col, vals in opts.items():
        print(f"{col} options ({len(vals)}): {vals}")
