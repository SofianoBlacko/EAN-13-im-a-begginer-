# EAN-13-im-a-begginer(this is just sharing my research with ppl are still learning or want to learn or just want to save time as i use python i saw ppl helping each other and wanted to help others i know ther's other ways but my english is bad i can't communicate with others and explain them without confusing them if you find this script helpfull share it with other ppl or you can even make a video or tutorial about it using this just share the Source with them and let me know i was part of it thks a lot for learning and sharing knowledge to anyone who is reading this <3)
#barcode generator EAN-13 + printer logic into image (which work with all printers)
#Note: this scripts im using them in real project POS and it works i tried to detail everything if you want to check my POS i will leave a page fb link to it (https://www.facebook.com/reel/1213425470574695)
#the first script is to generate the barcode in EAN-13 logic and save it to the database and you have to fellow the logic because EAN-13 even if you randomise the 12 digits the 13th (last degit) is calculated so you have to generate it correctly or when you want to print it using the second script you will get another barcode that will not match the saved barcode in database.
import random
def calculate_ean13_checksum(digits):
    """
    Calculate the EAN-13 checksum for the first 12 digits using the GTIN-13 method.
    - Odd positions (1, 3, 5, 7, 9, 11) are multiplied by 1.
    - Even positions (2, 4, 6, 8, 10, 12) are multiplied by 3.
    - Sum the results, find the remainder when divided by 10, subtract from 10.
    
    Args:
        digits (str): A 12-digit string (e.g., "501234500080").
    Returns:
        int: The checksum digit (0-9).
    """
    # Ensure digits is a 12-character string
    if len(digits) != 12 or not digits.isdigit():
        raise ValueError("EAN-13 checksum requires exactly 12 digits")

    # Step 1: Sum odd positions (1st, 3rd, 5th, 7th, 9th, 11th) multiplied by 1
    odd_sum = sum(int(digits[i]) for i in range(0, 12, 2))  # Positions 0, 2, 4, 6, 8, 10 (1st, 3rd, etc.)
    
    # Step 2: Sum even positions (2nd, 4th, 6th, 8th, 10th, 12th) multiplied by 3
    even_sum = sum(int(digits[i]) for i in range(1, 12, 2))  # Positions 1, 3, 5, 7, 9, 11 (2nd, 4th, etc.)
    even_sum *= 3
    
    # Step 3: Total sum
    total = odd_sum + even_sum
    
    # Step 4: Find the remainder when divided by 10
    remainder = total % 10
    
    # Step 5: Checksum is (10 - remainder), if 10 then use 0
    checksum = 10 - remainder if remainder != 0 else 0
    return checksum

def generate_barcode(item_id=None):
    """
    Generate a unique EAN-13 barcode (13 digits) for an item.
    If item_id is provided, updates the Inventory table with the new barcode.
    Sets barcode_generated_at to the current timestamp and is_printed to 0.
    
    EAN-13 Format:
    - Digits 1-2: Country code ("50" for UK)
    - Digits 3-7: Manufacturer code (random 5 digits)
    - Digits 8-12: Product code (random 5 digits, adjusted for uniqueness)
    - Digit 13: Checksum
    
    Args:
        item_id (int, optional): The ID of the item in the Inventory table. If None, the barcode
                                 is generated but not saved to the database.
    Returns:
        str: The generated EAN-13 barcode (13 digits, e.g., "5012345000800").
    Raises:
        Exception: If barcode generation fails due to database errors or too many attempts.
    """
    try:
        # Step 1: Construct the first 12 digits
        # Country code: "50" (UK)
        country_code = "50"
        # Manufacturer code: Random 5 digits
        manufacturer_code = f"{random.randint(0, 99999):05d}"  # e.g., 84721 -> "84721"
        
        # Step 2: Try generating a unique barcode
        counter = 0
        max_attempts = 1000  # Prevent infinite loops
        conn = get_connection()
        c = conn.cursor()

        while counter < max_attempts:
            # Product code: Use a random 5-digit number instead of item_id
            product_code = f"{random.randint(0, 99999):05d}"  # 5 digits (e.g., "01234")
            
            # First 12 digits: country_code (2) + manufacturer_code (5) + product_code (5)
            first_12_digits = f"{country_code}{manufacturer_code}{product_code}"
            
            # Step 3: Calculate the checksum
            checksum = calculate_ean13_checksum(first_12_digits)
            # Final EAN-13 barcode
            barcode = f"{first_12_digits}{checksum}"
            
            # Step 4: Check if this barcode already exists
            c.execute("SELECT COUNT(*) FROM Inventory WHERE barcode = ?", (barcode,))
            if c.fetchone()[0] == 0:  # Barcode is unique
                break
            
            # If barcode exists, increment counter and try again
            counter += 1
        
        if counter >= max_attempts:
            raise Exception("Failed to generate a unique barcode: too many attempts")

        # Step 5: Update the Inventory table if item_id is provided (edit case)
        if item_id is not None:
            current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("""
                UPDATE Inventory
                SET barcode = ?, barcode_generated_at = ?, is_printed = 0
                WHERE ID = ?
            """, (barcode, current_timestamp, item_id))
            conn.commit()
        
        # Step 6: Close connection and return the barcode
        conn.close()
        print(f"Generated 13-digit barcode{' for item ' + str(item_id) if item_id is not None else ''}: {barcode}")
        return barcode

    except sqlite3.IntegrityError as e:
        conn.close()
        raise Exception(f"Failed to generate barcode due to duplicate: {str(e)}")
    except sqlite3.Error as e:
        conn.close()
        raise Exception(f"Failed to generate barcode{' for item ' + str(item_id) if item_id is not None else ''}: {str(e)}")
    except Exception as e:
        conn.close()
        raise Exception(f"Failed to generate barcode{' for item ' + str(item_id) if item_id is not None else ''}: {str(e)}")
