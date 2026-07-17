from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


TABLES_DIR = Path("reports/tables")
FIGURES_DIR = Path("reports/figures")


def save_bar_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str, output_name: str) -> None:
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.bar(df[x_col].astype(str), df[y_col])
    ax.set_title(title)
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    output_path = FIGURES_DIR / output_name
    plt.savefig(output_path, dpi=150)
    plt.close()

    print(f"Saved {output_path}")


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    cases_by_year = pd.read_csv(TABLES_DIR / "cases_by_year.csv")
    target_distribution = pd.read_csv(TABLES_DIR / "target_distribution.csv")
    top_states = pd.read_csv(TABLES_DIR / "top_states.csv")
    top_event_types = pd.read_csv(TABLES_DIR / "top_event_types.csv")
    high_severity_by_event_type = pd.read_csv(TABLES_DIR / "high_severity_by_event_type.csv")

    save_bar_chart(
        cases_by_year,
        x_col="event_year",
        y_col="cases",
        title="Severe Injury Cases by Year",
        output_name="cases_by_year.png",
    )

    save_bar_chart(
        target_distribution,
        x_col="high_severity_outcome",
        y_col="cases",
        title="Target Distribution",
        output_name="target_distribution.png",
    )

    save_bar_chart(
        top_states,
        x_col="state",
        y_col="cases",
        title="Top States by Number of Severe Injury Cases",
        output_name="top_states.png",
    )

    save_bar_chart(
        top_event_types,
        x_col="event_title",
        y_col="cases",
        title="Top Event Types by Number of Cases",
        output_name="top_event_types.png",
    )

    save_bar_chart(
        high_severity_by_event_type,
        x_col="event_title",
        y_col="high_severity_rate",
        title="Highest High-Severity Rates by Event Type",
        output_name="high_severity_by_event_type.png",
    )


if __name__ == "__main__":
    main()