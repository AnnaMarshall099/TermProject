from typing import Any, List, Optional
import os
import csv
from dotenv import load_dotenv

# Global Lists
vendors: List["Vendor"] = []
expenses: List["MonthlyVendorExpense"] = []
categories: List[str] = []

# Class Vendor
class Vendor:
    def __init__(self, vendor_id: int, name: str, category: str) -> None:
        self.vendor_id = vendor_id
        self.name = name
        self.category = category

# Class MonthlyVendorExpense
class MonthlyVendorExpense:
    def __init__(self, vendorId: int, month: str, amount: float) -> None:
        self.vendorId = vendorId
        self.month = month
        self.amount = amount

# Global Functions
# Global Variables
EXPENSE_FILE: str = ""

def load_environment_variables() -> None:
    global EXPENSE_FILE
    load_dotenv()
    EXPENSE_FILE = os.getenv("EXPENSE_FILE", "Expenses.csv")

def readExpenseFile() -> None:
    global vendors, expenses, EXPENSE_FILE, categories
    
    # Clear existing lists to avoid duplicates if called multiple times
    vendors.clear()
    expenses.clear()

    if not os.path.exists(EXPENSE_FILE):
        print(f"Error: {EXPENSE_FILE} not found.")
        return

    try:
        with open(EXPENSE_FILE, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            
            # Read header
            try:
                header = next(reader)
            except StopIteration:
                print("Error: Empty CSV file.")
                return

            # Map months from header (indices 4-15)
            # Expected Header: Work Vendor?, Vendor, Category, 2024 Total, Jan-XX, ..., Dec-XX, ...
            if len(header) < 16:
                print("Error: CSV format incorrect (missing month columns).")
                return

            month_labels = header[4:16]

            vendor_id_counter = 0

            for row in reader:
                # 0: Work Vendor?, 1: Vendor, 2: Category, 3: Total
                # 4-15: Months
                if not row or len(row) < 3:
                    continue
                
                name = row[1].strip()
                category = row[2].strip()
                
                # Create Vendor
                current_vendor = Vendor(vendor_id_counter, name, category)
                vendors.append(current_vendor)

                # Process Monthly Expenses
                for i, month_name in enumerate(month_labels):
                    col_index = 4 + i
                    if col_index < len(row):
                        amount_str = row[col_index].replace(',', '').replace('$', '').strip()
                        if not amount_str:
                            continue
                        
                        try:
                            amount = float(amount_str)
                            if amount != 0.00:
                                amount = -1 * amount
                            # Store even if 0.00? Usually yes, checking for non-zero or specific logic needed?
                            # Prompt implies storing expenses.
                            expense = MonthlyVendorExpense(vendor_id_counter, month_name, amount)
                            expenses.append(expense)
                        except ValueError:
                            # Handle cases like empty strings or non-numeric if somehow slipped through
                            pass
                
                vendor_id_counter += 1
                
        categories = get_sorted_categories()
        print(f"Successfully read {len(vendors)} vendors and {len(expenses)} expenses.")

    except Exception as e:
        print(f"Error reading expense file: {e}")

def displayVendorData(vendorId: int, months: str) -> None:
    #get vendor name and category
    vendor = vendors[vendorId]
    print(vendor.name, vendor.category)
    months = "," + months.replace(" ", "") + ","
    total = 0.00
    #get all expenses for this vendor
    for expense in expenses:
        if expense.vendorId == vendorId and months.find("," + expense.month + ",") != -1:
            print(expense.month, f"${expense.amount:,.2f}")
            total += expense.amount 
    print(f"Total: ${total:,.2f}") 


def displayVendorMenu() -> None:
    while True:
        #display every vendor
        for vendor in vendors:
            print(vendor.vendor_id, vendor.name, vendor.category)
        #prompt user to pick vendor or exit vendor menu
        vendorId = input("Enter vendor ID or 'x' to exit: ").lower().strip()
        if vendorId == "x":
            break
        # See what months they want to see:
        monthStr = input("Enter months for which you want to see the data: ").lower().strip()
        displayVendorData(int(vendorId), monthStr)
        input("Type any key to continue...")

def displayCategoryData(category: str, months: str) -> None:
    #get category name
    print(category)
    months = "," + months.replace(" ", "") + ","
    total = 0.00
    monthlyAmounts = [0.00] * 12
    #get all vendors for this category
    for vendor in vendors:
        if vendor.category == category:
            for expense in expenses:
                if expense.vendorId == vendor.vendor_id and months.find("," + expense.month + ",") != -1:
                    #print(vendor.name,expense.month, f"${expense.amount:,.2f}")
                    monthlyAmounts[int(expense.month) - 1] += expense.amount 
    for i, amount in enumerate(monthlyAmounts):
        if amount != 0.00:  
            print(f"{i+1}: ${amount:,.2f}")
            total += amount
    print(f"Total: ${total:,.2f}") 


def get_sorted_categories() -> List[str]:
    return sorted({vendor.category for vendor in vendors})
    
def displayCategoryMenu() -> None:
    while True:
        print("")
        print("Categories:")
        for i, category in enumerate(categories):
            print(i, category)
        categoryId = input("Enter category or 'x' to exit: ").lower().strip()
        if categoryId == "x":
            break
        monthStr = input("Enter months for which you want to see the data: ").lower().strip()
        displayCategoryData(categories[int(categoryId)] , monthStr)
        input("Type any key to continue...")

def main():
    load_environment_variables()
    #objects: vendor, monthly vendor expense (vendorID, month, amount), 
    readExpenseFile()
    while True:
        choice = input("Would you like to see expenses by Vendor (v) or by Category (c), or exit (x)? ").lower()
        if choice == "x":
            print("Goodbye!")
            break
        if choice == "v":
            displayVendorMenu()
        elif choice == "c":
            displayCategoryMenu()
        else:
            print("Invalid input. Please try again.")


if __name__ == "__main__":
    main()

