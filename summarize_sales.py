"""店舗ごとのアイス売上CSVを読み込み、店舗・フレーバー別に集計します。"""

import csv
from collections import defaultdict
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
INPUT_DIR = PROJECT_DIR / "data" / "input"
OUTPUT_DIR = PROJECT_DIR / "output"
INPUT_COLUMNS = {"フレーバー", "個数", "単価"}


def read_sales_files(input_dir: Path) -> list[dict[str, str | int]]:
    """入力フォルダのCSVを読み込み、売上明細のリストを返します。"""
    files = sorted(input_dir.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"入力CSVが見つかりません: {input_dir}")

    sales: list[dict[str, str | int]] = []
    for file_path in files:
        with file_path.open(encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            if reader.fieldnames is None or not INPUT_COLUMNS.issubset(reader.fieldnames):
                expected = ", ".join(sorted(INPUT_COLUMNS))
                raise ValueError(
                    f"{file_path.name} の列名が正しくありません。必要な列: {expected}"
                )

            for line_number, row in enumerate(reader, start=2):
                try:
                    flavor = (row["フレーバー"] or "").strip()
                    quantity = int(row["個数"] or "")
                    unit_price = int(row["単価"] or "")
                except (TypeError, ValueError) as error:
                    raise ValueError(
                        f"{file_path.name} の{line_number}行目: "
                        "個数と単価は整数で入力してください"
                    ) from error

                if not flavor:
                    raise ValueError(f"{file_path.name} の{line_number}行目: フレーバーが空です")
                if quantity < 0 or unit_price < 0:
                    raise ValueError(
                        f"{file_path.name} の{line_number}行目: 個数と単価は0以上にしてください"
                    )

                sales.append(
                    {
                        "店舗": file_path.stem,
                        "フレーバー": flavor,
                        "個数": quantity,
                        "単価": unit_price,
                        "売上": quantity * unit_price,
                    }
                )
    return sales


def write_csv(file_path: Path, headers: list[str], rows: list[dict[str, str | int]]) -> None:
    """CSVをExcelや表計算ソフトで開きやすいUTF-8 BOM付きで保存します。"""
    with file_path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    sales = read_sales_files(INPUT_DIR)

    totals: dict[tuple[str, str], dict[str, str | int]] = defaultdict(
        lambda: {"店舗": "", "フレーバー": "", "合計個数": 0, "合計売上": 0}
    )
    for row in sales:
        key = (str(row["店舗"]), str(row["フレーバー"]))
        total = totals[key]
        total["店舗"], total["フレーバー"] = key
        total["合計個数"] += int(row["個数"])
        total["合計売上"] += int(row["売上"])

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    summary = [totals[key] for key in sorted(totals)]
    write_csv(
        OUTPUT_DIR / "sales_summary.csv",
        ["店舗", "フレーバー", "合計個数", "合計売上"],
        summary,
    )
    print(f"店舗・フレーバー別に{len(summary)}行を集計しました。")
    print(f"出力先: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
