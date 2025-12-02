import csv
import random
import os
from calendar import monthrange
from datetime import date

# Configuration
BASE_DIR = "/Users/cemilfahreci/Desktop/veriler"
TODAY = date(2025, 12, 2)
PRODUCTS = ["Chicken Shawarma", "Meat Shawarma", "Mixed Shawarma"]
SIZES = ["Small", "Medium", "Large"]
PRICES = {
    "Chicken Shawarma": {"Small": 10, "Medium": 12, "Large": 14},
    "Meat Shawarma": {"Small": 12, "Medium": 15, "Large": 18},
    "Mixed Shawarma": {"Small": 14, "Medium": 17, "Large": 20},
}

def ensure_dir(year):
    path = os.path.join(BASE_DIR, str(year))
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def calculate_smart_quantity(current_date, product, size):
    """
    Generates a realistic quantity based on patterns.
    """
    base_qty = 20
    
    # 1. Yearly Trend (Growth)
    year_factor = 1.0 + (current_date.year - 2022) * 0.1  # 10% growth per year
    
    # 2. Seasonality (Summer is busy)
    month = current_date.month
    if month in [6, 7, 8]:  # Summer
        season_factor = 1.4
    elif month in [12, 1, 2]:  # Winter
        season_factor = 0.8
    else:
        season_factor = 1.0
        
    # 3. Weekly Pattern (Weekend is busy)
    # Monday=0, Sunday=6. Let's say Fri(4), Sat(5), Sun(6) are busy.
    weekday = current_date.weekday()
    if weekday >= 4:
        weekend_factor = 1.5
    else:
        weekend_factor = 1.0
        
    # 4. Product Popularity
    if product == "Chicken Shawarma":
        product_factor = 1.5  # Most popular
    elif product == "Meat Shawarma":
        product_factor = 1.2
    else:
        product_factor = 1.0
        
    # 5. Size Popularity
    if size == "Medium":
        size_factor = 1.5
    elif size == "Large":
        size_factor = 1.2
    else:
        size_factor = 1.0
        
    # Calculate deterministic part
    expected_qty = base_qty * year_factor * season_factor * weekend_factor * product_factor * size_factor
    
    # 6. Add Random Noise (Variance)
    # +/- 20% randomness
    noise = random.uniform(0.8, 1.2)
    
    final_qty = int(expected_qty * noise)
    return max(1, final_qty)  # Ensure at least 1 sold

def generate_full_year(year):
    dir_path = ensure_dir(year)
    filename = os.path.join(dir_path, f"sales_{year}_FULL.csv")
    
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["date", "product_name", "size", "unit_price", "quantity"])
        
        total_rows = 0
        for month in range(1, 13):
            num_days = monthrange(year, month)[1]
            for day in range(1, num_days + 1):
                current_date = date(year, month, day)
                date_str = current_date.isoformat()
                
                for product in PRODUCTS:
                    for size in SIZES:
                        quantity = calculate_smart_quantity(current_date, product, size)
                        unit_price = PRICES[product][size]
                        writer.writerow([date_str, product, size, unit_price, quantity])
                        total_rows += 1
                        
    print(f"Generated {year} Full Data: {filename} ({total_rows} rows)")

def generate_2025_seasonal():
    year = 2025
    dir_path = ensure_dir(year)
    
    file_summer = os.path.join(dir_path, f"sales_{year}_SUMMER.csv")
    file_winter = os.path.join(dir_path, f"sales_{year}_WINTER.csv")
    
    # Open both files
    f_summer = open(file_summer, mode='w', newline='')
    f_winter = open(file_winter, mode='w', newline='')
    
    w_summer = csv.writer(f_summer)
    w_winter = csv.writer(f_winter)
    
    header = ["date", "product_name", "size", "unit_price", "quantity"]
    w_summer.writerow(header)
    w_winter.writerow(header)
    
    rows_summer = 0
    rows_winter = 0
    
    for month in range(1, 13):
        # Determine season
        if month in [6, 7, 8]:
            writer = w_summer
            is_target = True
            is_summer = True
        elif month in [1, 2, 12]:
            writer = w_winter
            is_target = True
            is_summer = False
        else:
            is_target = False
            
        if not is_target:
            continue

        num_days = monthrange(year, month)[1]
        for day in range(1, num_days + 1):
            current_date = date(year, month, day)
            if current_date > TODAY:
                break
            
            date_str = current_date.isoformat()
            for product in PRODUCTS:
                for size in SIZES:
                    quantity = calculate_smart_quantity(current_date, product, size)
                    unit_price = PRICES[product][size]
                    writer.writerow([date_str, product, size, unit_price, quantity])
                    
                    if is_summer:
                        rows_summer += 1
                    else:
                        rows_winter += 1
                        
    f_summer.close()
    f_winter.close()
                        
    print(f"Generated 2025 SUMMER Data: {file_summer} ({rows_summer} rows)")
    print(f"Generated 2025 WINTER Data: {file_winter} ({rows_winter} rows)")

if __name__ == "__main__":
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)
        
    generate_full_year(2022)
    generate_full_year(2023)
    generate_full_year(2024)
    generate_2025_seasonal()
