# product_config.py

import random

# Product catalog with static pricing
PRODUCTS_AND_PRICES = {
    "Wireless Mouse": 20.00,
    "Bluetooth Speaker": 35.00,
    "Desk Lamp": 25.00,
    "Travel Mug": 15.00,
    "Yoga Mat": 30.00,
    "Laptop Sleeve": 18.00,
    "Water Bottle": 12.00,
    "Desk Organizer": 22.00,
    "Gaming Headset": 40.00,
    "USB-C Charger": 10.00,
    "Portable Hard Drive": 45.00,
    "Smartwatch Band": 12.00,
    "Noise-Canceling Earbuds": 60.00,
}

# Shipping methods and associated costs
SHIPPING_METHODS = ["Standard", "Express", "Overnight"]
SHIPPING_COSTS = {"Standard": 0.00, "Express": 10.00, "Overnight": 20.00}

# Discount codes and their discount rates
DISCOUNT_CODES = [None, "WELCOME10", "SPRING15", None, None]
DISCOUNT_MAP = {"WELCOME10": 0.10, "SPRING15": 0.15}  # 10% off  # 15% off

# Tax rates to pick from
TAX_RATES = [0.05, 0.08, 0.13]

# Probability of forcing a data error
ERROR_PROB = 0.03


def pick_product_and_price():
    """
    Returns a (product_name, price) tuple by choosing randomly from PRODUCTS_AND_PRICES.
    """
    return random.choice(list(PRODUCTS_AND_PRICES.items()))
