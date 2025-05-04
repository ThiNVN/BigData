import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def load_and_analyze_data():
    # Read the dataset and remove duplicates
    dtype_dict = {"column_name": str, "other_column": float}
    df = pd.read_csv("game_data.csv", low_memory=False, dtype=dtype_dict)
    df = df.drop_duplicates()

    # Convert recommendations to numeric (just in case)
    df["recommendations_total"] = pd.to_numeric(
        df["recommendations_total"], errors="coerce"
    )

    # Plot distribution
    plt.figure(figsize=(12, 6))
    plot = sns.histplot(
        df["recommendations_total"].dropna(), bins=50, kde=True, log_scale=True
    )  # Using log scale for better visualization

    plt.title("Distribution of Game Recommendations (Log Scale)")
    plt.xlabel("Number of Recommendations (log scale)")
    plt.ylabel("Count of Games")

    # Add reference lines
    median_val = df["recommendations_total"].median()
    mean_val = df["recommendations_total"].mean()

    plt.axvline(
        x=median_val, color="r", linestyle="--", label=f"Median: {median_val:.0f}"
    )
    plt.axvline(x=mean_val, color="g", linestyle="-", label=f"Mean: {mean_val:.0f}")
    plt.legend()

    # Save the plot
    plt.savefig("recommendations_distribution.png")
    print("Plot saved as recommendations_distribution.png")

    # Print statistics
    print("\nRecommendations Analysis:")
    print(df["recommendations_total"].describe())

    # Calculate and show percentiles
    percentiles = [10, 25, 50, 75, 90, 95, 99]
    print("\nPercentile Analysis:")
    for p in percentiles:
        value = df["recommendations_total"].quantile(p / 100)
        print(f"{p}th percentile: {value:.0f} recommendations")

    # Suggest a cutoff
    suggested_cutoff = df["recommendations_total"].quantile(0.25)  # 25th percentile
    print(
        f"\nSuggested cutoff (25th percentile): {suggested_cutoff:.0f} recommendations"
    )
    print(
        f"This would remove {len(df[df['recommendations_total'] < suggested_cutoff])} games"
    )
    print(f"and keep {len(df[df['recommendations_total'] >= suggested_cutoff])} games")


if __name__ == "__main__":
    load_and_analyze_data()
