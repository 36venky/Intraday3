import os
def load_stock_data_txt(filename="1Reg.txt.txt"):

    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)
    target_dir = os.path.join(project_root, "Signals")

    filepath = os.path.join(target_dir, filename)

    if not os.path.exists(filepath):
        return {}

    if os.path.getsize(filepath) == 0:
        return {}

    all_stocks = {}

    try:

        with open(filepath, "r") as file:

            for line in file:

                line = line.strip()

                if not line:
                    continue

                parts = line.split(",")

                if len(parts) != 3:
                    continue

                ticker = parts[0].strip()
                r2 = float(parts[1].strip())
                smooth_val = float(parts[2].strip())

                all_stocks[ticker] = {

                    "r2": r2,
                    "smooth_val": smooth_val
                }

    except Exception as e:

        print(f"TXT Load Error: {e}")

    return all_stocks

all_stocks = load_stock_data_txt("stock_data.txt")
print(all_stocks)