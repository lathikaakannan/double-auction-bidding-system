# migrations.py
import pymysql
from datetime import datetime

def run_migrations():
    """Execute all database table creation scripts"""
    
    print("Starting database migrations...")
    
    try:
        # Connect to MySQL
        con = pymysql.connect(
            host='127.0.0.1', 
            port=3306, 
            user='root', 
            password='root', 
            database='cropinfo', 
            charset='utf8'
        )
        
        with con:
            cur = con.cursor()
            
            # 1. Create signup table (farmers)
            print("Creating signup table...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS signup (
                    username VARCHAR(100) PRIMARY KEY,
                    password VARCHAR(100) NOT NULL,
                    contact_no VARCHAR(20),
                    gender VARCHAR(10),
                    email VARCHAR(100),
                    address TEXT,
                    registration_date DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 2. Create customers table
            print("Creating customers table...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id INT AUTO_INCREMENT PRIMARY KEY,
                    full_name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password VARCHAR(100) NOT NULL,
                    contact VARCHAR(20),
                    address TEXT,
                    city VARCHAR(50),
                    state VARCHAR(50),
                    pincode VARCHAR(10),
                    registration_date DATE
                )
            """)
            
            # 3. Create addscheme table
            print("Creating addscheme table...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS addscheme (
                    scheme_id VARCHAR(50) PRIMARY KEY,
                    scheme_name VARCHAR(200) NOT NULL,
                    description TEXT,
                    document TEXT,
                    start_date DATE,
                    end_date DATE
                )
            """)
            
            # 4. Create farmer_products table
            print("Creating farmer_products table...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS farmer_products (
                    product_id INT AUTO_INCREMENT PRIMARY KEY,
                    farmer_username VARCHAR(100),
                    crop_name VARCHAR(100),
                    variety VARCHAR(100),
                    quantity DECIMAL(10,2),
                    unit VARCHAR(20),
                    predicted_price DECIMAL(10,2),
                    selling_price DECIMAL(10,2),
                    district VARCHAR(100),
                    listing_date DATE,
                    status ENUM('available', 'sold', 'removed') DEFAULT 'available',
                    FOREIGN KEY (farmer_username) REFERENCES signup(username) ON DELETE SET NULL
                )
            """)
            
            # 5. Create customer_orders table
            print("Creating customer_orders table...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS customer_orders (
                    order_id INT AUTO_INCREMENT PRIMARY KEY,
                    customer_name VARCHAR(100),
                    customer_contact VARCHAR(20),
                    customer_email VARCHAR(100),
                    customer_address TEXT,
                    product_id INT,
                    farmer_username VARCHAR(100),
                    crop_name VARCHAR(100),
                    quantity DECIMAL(10,2),
                    unit VARCHAR(20),
                    price_per_unit DECIMAL(10,2),
                    total_amount DECIMAL(10,2),
                    order_date DATE,
                    delivery_date DATE,
                    order_status ENUM('pending', 'confirmed', 'shipped', 'delivered', 'cancelled') DEFAULT 'pending',
                    payment_status ENUM('pending', 'completed', 'failed') DEFAULT 'pending',
                    FOREIGN KEY (product_id) REFERENCES farmer_products(product_id) ON DELETE SET NULL,
                    FOREIGN KEY (farmer_username) REFERENCES signup(username) ON DELETE SET NULL,
                    FOREIGN KEY (customer_email) REFERENCES customers(email) ON DELETE SET NULL
                )
            """)
            
            # 6. Create product_negotiations table (Bidding System)
            print("Creating product_negotiations table...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS product_negotiations (
                    negotiation_id INT AUTO_INCREMENT PRIMARY KEY,
                    product_id INT NOT NULL,
                    farmer_username VARCHAR(100) NOT NULL,
                    customer_email VARCHAR(100) NOT NULL,
                    crop_name VARCHAR(100),
                    initial_price DECIMAL(10,2),
                    current_price DECIMAL(10,2),
                    quantity DECIMAL(10,2),
                    unit VARCHAR(50),
                    negotiation_status ENUM('active', 'accepted', 'rejected', 'expired', 'completed') DEFAULT 'active',
                    start_time DATETIME,
                    last_updated DATETIME,
                    expiry_time DATETIME,
                    delivery_date DATE,
                    notes TEXT,
                    FOREIGN KEY (product_id) REFERENCES farmer_products(product_id) ON DELETE CASCADE,
                    FOREIGN KEY (farmer_username) REFERENCES signup(username),
                    FOREIGN KEY (customer_email) REFERENCES customers(email)
                )
            """)
            
            # 7. Create negotiation_bids table
            print("Creating negotiation_bids table...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS negotiation_bids (
                    bid_id INT AUTO_INCREMENT PRIMARY KEY,
                    negotiation_id INT NOT NULL,
                    bidder_type ENUM('farmer', 'customer') NOT NULL,
                    bidder_name VARCHAR(100),
                    offered_price DECIMAL(10,2),
                    offered_quantity DECIMAL(10,2),
                    message TEXT,
                    bid_time DATETIME,
                    is_current BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (negotiation_id) REFERENCES product_negotiations(negotiation_id) ON DELETE CASCADE
                )
            """)
            
            # 8. Create accepted_bids table (Contracts)
            print("Creating accepted_bids table...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS accepted_bids (
                    contract_id INT AUTO_INCREMENT PRIMARY KEY,
                    negotiation_id INT NOT NULL,
                    product_id INT NOT NULL,
                    farmer_username VARCHAR(100),
                    customer_email VARCHAR(100),
                    final_price DECIMAL(10,2),
                    quantity DECIMAL(10,2),
                    unit VARCHAR(50),
                    total_amount DECIMAL(10,2),
                    delivery_date DATE,
                    contract_date DATETIME,
                    payment_status ENUM('pending', 'completed', 'failed') DEFAULT 'pending',
                    order_status ENUM('pending', 'processing', 'shipped', 'delivered', 'cancelled') DEFAULT 'pending',
                    transaction_id VARCHAR(100),
                    FOREIGN KEY (negotiation_id) REFERENCES product_negotiations(negotiation_id),
                    FOREIGN KEY (product_id) REFERENCES farmer_products(product_id)
                )
            """)
            
            # 9. Create farmer_notifications table
            print("Creating farmer_notifications table...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS farmer_notifications (
                    notification_id INT AUTO_INCREMENT PRIMARY KEY,
                    farmer_username VARCHAR(100),
                    order_id INT,
                    negotiation_id INT,
                    message TEXT,
                    notification_date DATETIME,
                    is_read BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (farmer_username) REFERENCES signup(username),
                    FOREIGN KEY (order_id) REFERENCES customer_orders(order_id),
                    FOREIGN KEY (negotiation_id) REFERENCES product_negotiations(negotiation_id)
                )
            """)
            
            # 10. Create customer_notifications table
            print("Creating customer_notifications table...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS customer_notifications (
                    notification_id INT AUTO_INCREMENT PRIMARY KEY,
                    customer_email VARCHAR(100),
                    negotiation_id INT,
                    order_id INT,
                    message TEXT,
                    notification_date DATETIME,
                    is_read BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (customer_email) REFERENCES customers(email),
                    FOREIGN KEY (negotiation_id) REFERENCES product_negotiations(negotiation_id),
                    FOREIGN KEY (order_id) REFERENCES customer_orders(order_id)
                )
            """)
            
            con.commit()
            print("✅ All migrations completed successfully!")
            
            # Show created tables
            cur.execute("SHOW TABLES")
            tables = cur.fetchall()
            print(f"\n📊 Tables in database ({len(tables)}):")
            for table in tables:
                print(f"   - {table[0]}")
            
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    run_migrations()