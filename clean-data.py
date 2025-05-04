import pandas as pd
import re


# Function to parse and clean supported languages
def parse_languages(text):
    if pd.isna(text):
        return []

    # Replace escape sequences and known text patterns
    text = text.replace("\\r\\n", ",")
    text = text.replace("languages with full audio support", "")
    text = text.replace("(Subtitles)", "")
    text = text.replace("(full audio)", "")
    text = text.replace("*", "").strip()

    # Split and clean each language
    languages = [lang.strip() for lang in text.split(",") if lang.strip()]

    # Remove HTML/BBCode tags from each language
    cleaned_languages = [
        re.sub(r"<.*?>|\[.*?\]|;", "", lang).strip() for lang in languages
    ]

    return [lang for lang in cleaned_languages if lang]


# Set pandas options for better readability
pd.set_option("display.max_columns", None)

# Read the dataset and remove duplicates
dtype_dict = {"column_name": str, "other_column": float}
df = pd.read_csv("game_data.csv", low_memory=False, dtype=dtype_dict)
df = df.drop_duplicates()

# Drop unnecessary columns
df = df.drop(columns=["developers[0]", "publishers[0]"], errors="ignore")

# Define attributes to query from the dataframe
query_attributes = [
    "_id",
    "app_id",
    "name",
    "type",
    "required_age",
    "is_free",
    "supported_languages",
    "developers",
    "publishers",
    "price_final",
    "platforms_windows",
    "platforms_mac",
    "platforms_linux",
    "categories",
    "genres",
    "recommendations_total",
    "release_date",
    "price_currency",
]

info_attributes = [
    "metacritic_score",
    "short_description",
    "detailed_description",
    "about_the_game",
    "website",
    "discount_percent",
    "pc_min_os",
    "pc_min_processor",
    "pc_min_memory",
    "pc_min_graphics",
    "pc_min_directx",
    "pc_min_network",
    "pc_min_storage",
    "header_image",
    "background",
    "screenshots_count",
    "movies_count",
    "pc_rec_os",
    "pc_rec_processor",
    "pc_rec_memory",
    "pc_rec_graphics",
    "support_email",
    "pc_rec_directx",
    "pc_rec_network",
    "pc_rec_storage",
]

# Subset the dataframe to include only necessary columns
df_subset = df[[*query_attributes, *info_attributes]]

# Select rows that have type game
df_subset = df_subset[df_subset["type"] == "game"]

# Select rows that have more than 500 recommendations
df_subset = df_subset[df_subset["recommendations_total"] > 500]

# Convert genres to a list of genres
df_subset.loc[:, "genres"] = df_subset["genres"].apply(
    lambda x: [genre.strip() for genre in x.split(",")] if pd.notna(x) else []
)

# Convert categories to a list of categories
df_subset.loc[:, "categories"] = df_subset["categories"].apply(
    lambda x: [category.strip() for category in x.split(",")] if pd.notna(x) else []
)

# Extract and clean supported languages, and filter rows with empty supported languages
df_subset.loc[:, "supported_languages"] = df_subset["supported_languages"].apply(
    parse_languages
)
df_subset = df_subset[df_subset["supported_languages"].apply(lambda x: len(x) > 0)]

# Total games
total_games = len(df_subset)
print(f"Total number of games: {total_games}")

# Count the games free
free_games_count = df_subset[df_subset["is_free"] == True].shape[0]
print(f"Number of free games: {free_games_count}")

# Count the games not free
not_free_games_count = df_subset[df_subset["is_free"] == False].shape[0]
print(f"Number of not free games: {not_free_games_count}")

# Flatten the list of lists and get unique languages
all_languages = set(
    lang for sublist in df_subset["supported_languages"] for lang in sublist
)
# Sort and print the result
print("All lanugages:", sorted(all_languages))

# Flatten the list of lists and get unique categories
all_cagegories = set(
    cagegory for subcagegory in df_subset["categories"] for cagegory in subcagegory
)
# Sort and print the result
print("All categories:", sorted(all_cagegories))


# Save the cleaned data to a new CSV
# df_subset.to_csv("game_data_clean.csv", index=False)
