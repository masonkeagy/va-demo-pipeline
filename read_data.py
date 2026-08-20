import pandas as pd

# Stage 1: Read
df = pd.read_excel('data/sample-data.xlsx')
print("After reading:", df.shape)

# Stage 2: Clean (now df_clean exists!)
df_clean = df.dropna()        # example: remove empty rows
print("After cleaning:", df_clean.shape)
print(df_clean.head())                       # Does the data look sensible?

# Stage 3: Analyze
print("\n--- Stage 3: Analysis ---")
print("Total sales:", df_clean['Sales_Amount'].sum())
print("Total units sold:", df_clean['Units_Sold'].sum())
print("\nSales by Region:")
print(df_clean.groupby('Region')['Sales_Amount'].sum())
print("\nSales by Product:")
print(df_clean.groupby('Product')['Sales_Amount'].sum())