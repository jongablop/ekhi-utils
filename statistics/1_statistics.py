import pandas as pd

CSV_PATH = "metadata_summary_clean_corrected_dataset.csv"

df = pd.read_csv(CSV_PATH)

# Ensure numeric
df["n_datapoints"] = pd.to_numeric(df["n_datapoints"], errors="coerce").fillna(0)
df["temperature_min_k"] = pd.to_numeric(df.get("temperature_min_k", 298), errors="coerce")
df["temperature_max_k"] = pd.to_numeric(df.get("temperature_max_k", 298), errors="coerce")

ROOM_TEMP = 298  # Kelvin

print("\n================ GLOBAL STATISTICS ================\n")

print(f"Total datasets (rows): {len(df)}")
print(f"Total datapoints: {int(df['n_datapoints'].sum())}")
print(f"Unique materials: {df['material'].nunique()}")
print(f"Unique properties: {df['properties'].nunique()}")
print(f"Year range: {df['year'].min()} - {df['year'].max()}")
print(f"Average datapoints per dataset: {df['n_datapoints'].mean():.2f}")
print(f"Median datapoints per dataset: {df['n_datapoints'].median():.2f}")

# ---------------------------------------------------
# 📂 DATAPOINTS BY MAIN CATEGORY
# ---------------------------------------------------
print("\n================ DATAPOINTS BY CATEGORY ================\n")

# Split multi-category rows
df_categories = df.copy()
df_categories["categories"] = df_categories["categories"].fillna("")

df_categories = df_categories.assign(
    category_split=df_categories["categories"].str.split("; ")
).explode("category_split")

# Remove empty category rows
df_categories = df_categories[df_categories["category_split"] != ""]

category_summary = (
    df_categories.groupby("category_split")
    .agg(
        datasets=("category_split", "count"),
        total_datapoints=("n_datapoints", "sum")
    )
    .sort_values("total_datapoints", ascending=False)
)

# Optional: percentage of total
total_global = df["n_datapoints"].sum()
category_summary["percent_of_total_datapoints"] = (
    100 * category_summary["total_datapoints"] / total_global
)

print(category_summary)


# ---------------------------------------------------
# 📦 Statistics by Material
# ---------------------------------------------------
print("\n================ BY MATERIAL ================\n")

by_material = (
    df.groupby("material")
    .agg(
        datasets=("material", "count"),
        total_datapoints=("n_datapoints", "sum"),
        avg_datapoints=("n_datapoints", "mean")
    )
    .sort_values("total_datapoints", ascending=False)
)

print(by_material.head(20))

# ---------------------------------------------------
# 🧪 Statistics by Property
# ---------------------------------------------------
print("\n================ BY PROPERTY ================\n")

# Split multi-property rows
df_properties = df.copy()
df_properties["properties"] = df_properties["properties"].fillna("")
df_properties = df_properties.assign(
    property_split=df_properties["properties"].str.split("; ")
).explode("property_split")

by_property = (
    df_properties.groupby("property_split")
    .agg(
        datasets=("property_split", "count"),
        total_datapoints=("n_datapoints", "sum"),
        avg_datapoints=("n_datapoints", "mean")
    )
    .sort_values("total_datapoints", ascending=False)
)

print(by_property.head(20))

# ---------------------------------------------------
# 🌡 Temperature classification per property
# ---------------------------------------------------
print("\n================ BY PROPERTY AND TEMPERATURE ================\n")

def classify_temperature(row):
    if row["temperature_max_k"] < ROOM_TEMP:
        return "below_room_temp"
    elif row["temperature_min_k"] > ROOM_TEMP:
        return "above_room_temp"
    else:
        return "room_temp"

df_properties["temp_class"] = df_properties.apply(classify_temperature, axis=1)

temp_stats = (
    df_properties.groupby(["property_split", "temp_class"])
    .agg(
        datasets=("property_split", "count"),
        total_datapoints=("n_datapoints", "sum")
    )
    .unstack(fill_value=0)
)

# Flatten MultiIndex columns
temp_stats.columns = ["_".join(col).strip() for col in temp_stats.columns.values]

print(temp_stats)

# ---------------------------------------------------
# 📅 By Year
# ---------------------------------------------------
print("\n================ BY YEAR ================\n")

df["year"] = pd.to_numeric(df["year"], errors="coerce")

by_year = (
    df.groupby("year")
    .agg(
        datasets=("year", "count"),
        total_datapoints=("n_datapoints", "sum")
    )
    .sort_index()
)

print(by_year.tail(20))

# ---------------------------------------------------
# 📖 By Journal
# ---------------------------------------------------
print("\n================ BY JOURNAL ================\n")

by_journal = (
    df.groupby("journal")
    .agg(
        datasets=("journal", "count"),
        total_datapoints=("n_datapoints", "sum")
    )
    .sort_values("datasets", ascending=False)
)

print(by_journal.head(15))

# ---------------------------------------------------
# 📐 Geometry distribution
# ---------------------------------------------------
if "geometry" in df.columns:
    print("\n================ GEOMETRY DISTRIBUTION ================\n")
    print(df["geometry"].value_counts().head(10))

# ---------------------------------------------------
# 🔝 Largest datasets
# ---------------------------------------------------
print("\n================ LARGEST DATASETS ================\n")

largest = df.sort_values("n_datapoints", ascending=False)[
    ["material", "properties", "year", "n_datapoints"]
].head(10)

print(largest)

# ---------------------------------------------------
# 📉 Missing metadata report
# ---------------------------------------------------
print("\n================ MISSING METADATA ================\n")

missing_report = df.isna().sum().sort_values(ascending=False)
print(missing_report[missing_report > 0])

print("\n================ DONE ================\n")

