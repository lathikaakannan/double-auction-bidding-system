from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse
import os
from django.core.files.storage import FileSystemStorage
import pymysql
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
import matplotlib
matplotlib.use('Agg')
from datetime import date
import warnings
warnings.filterwarnings('ignore')
from datetime import datetime, timedelta
import json
from django.http import JsonResponse
from decimal import Decimal
# Global variables
global uname
uname = None

le1 = LabelEncoder()

# Load dataset
try:
    dataset = pd.read_csv("Dataset/CropDataset.csv", encoding='iso-8859-1', usecols=['variety', 'max_price', 'Rainfall'])
    dataset.fillna(0, inplace=True)
except:
    dataset = pd.DataFrame(columns=['variety', 'max_price', 'Rainfall'])

def PredictCropPricesAction(request):
    if request.method == 'POST':
        item = request.POST.get('item', False)
        dataset1 = pd.read_csv("Dataset/CropDataset.csv", encoding='iso-8859-1', usecols=['variety', 'max_price', 'Rainfall', 'district'])
        dataset1.fillna(0, inplace=True)
        df = dataset1.loc[(dataset1['variety'] == item)]
        print(df)
        Y = df.values[:, 2:3]
        district = df.values[:, 0:1].ravel()
        df.drop(['max_price'], axis=1, inplace=True)
        df.drop(['district'], axis=1, inplace=True)
        df['variety'] = pd.Series(le1.fit_transform(df['variety'].astype(str)))
        df.fillna(0, inplace=True)
        print(Y)
        X = df.values
        sc = MinMaxScaler(feature_range=(0, 1))
        X = sc.fit_transform(X)
        Y = sc.fit_transform(Y)
        X_train = X
        Y_train = Y
        X_test = X
        Y_test = Y

        dt_regression = DecisionTreeRegressor()
        dt_regression.fit(X_train, Y_train.ravel())
        predict = dt_regression.predict(X_test)
        dt_mse = mean_squared_error(Y_test.ravel(), predict.ravel())
        dt_accuracy = 1.0 - dt_mse

        knn_regression = KNeighborsRegressor(n_neighbors=2)
        knn_regression.fit(X_train, Y_train.ravel())
        predict = knn_regression.predict(X_test)
        knn_mse = mean_squared_error(Y_test.ravel(), predict.ravel())
        knn_accuracy = 1.0 - knn_mse

        rf_regression = RandomForestRegressor()
        rf_regression.fit(X_train, Y_train.ravel())
        predict = rf_regression.predict(X_test)
        rf_mse = mean_squared_error(Y_test.ravel(), predict.ravel())
        rf_accuracy = 1.0 - rf_mse
        predict1 = predict.reshape(predict.shape[0], 1)
        predict1 = sc.inverse_transform(predict1)
        predict1 = predict1.ravel()
        labels = sc.inverse_transform(Y_test)
        labels = labels.ravel()
        output = '<table border=1><tr><th><font size="" color="black">District Market</th><th><font size="" color="black">Crop Name</th><th><font size="" color="black">Original Price</th>'
        output += '<th><font size="" color="black">Predicted Price</th></tr>'
        for i in range(len(predict1)):
            output += '<tr><td><font size="" color="black">' + str(district[i]) + '</td>'
            output += '<td><font size="" color="black">' + str(item) + '</td>'
            output += '<td><font size="" color="black">' + str(labels[i]) + '</td>'
            output += '<td><font size="" color="black">' + str(predict1[i]) + '</td></tr>'
        output += '<tr><td><font size="" color="black">Random Forest Accuracy</td>'
        output += '<td><font size="" color="black">' + str(rf_accuracy) + '</td></tr>'
        output += '<tr><td><font size="" color="black">Decision Tree Accuracy</td>'
        output += '<td><font size="" color="black">' + str(dt_accuracy) + '</td></tr>'
        output += '<tr><td><font size="" color="black">KNN Accuracy</td>'
        output += '<td><font size="" color="black">' + str(knn_accuracy) + '</td></tr>'
        context = {'data': output}
        print(output)
        plt.plot(Y_test.ravel(), color='red', label='Original Price')
        plt.plot(predict.ravel(), color='green', label='Predicted Price')
        plt.title('Crop Price Forecasting')
        plt.xlabel('Current Price for Crop ' + item)
        plt.ylabel('Predicted Price for Crop ' + item)
        plt.legend()
        plt.show()
        return render(request, 'ViewPrices.html', context)

def PredictCropPrices(request):
    if request.method == 'GET':
        variety = np.unique(dataset['variety'])
        output = '<tr><td><font size="" color="black">Choose&nbsp;Crop&nbsp;Name</font></td><td><select name=item class="form-control">'
        for i in range(len(variety)):
            output += '<option value="' + str(variety[i]) + '">' + str(variety[i]) + '</option>'
        output += "</select></td></tr>"
        context = {'data1': output}
        return render(request, 'PredictCropPrices.html', context)


def index(request):
    if request.method == 'GET':
        return render(request, 'index.html', {})


def AdminLogin(request):
    if request.method == 'GET':
        return render(request, 'AdminLogin.html', {})


def FarmerLogin(request):
    if request.method == 'GET':
        return render(request, 'FarmerLogin.html', {})


def Signup(request):
    if request.method == 'GET':
        return render(request, 'Signup.html', {})


def getOutput(table, length):
    font = '<font size="" color=black>'
    output = ""
    try:
        con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='cropinfo', charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * from " + table)
            rows = cur.fetchall()
            for row in rows:
                output += "<tr>"
                for i in range(0, length):
                    output += "<td><font size='' color=black>" + font + str(row[i]) + "</td>"
    except Exception as e:
        output = "<tr><td colspan='" + str(length) + "'>No data found</td></tr>"
    return output





# ================ BIDDING SYSTEM MODELS ================

def CreateBiddingTables():
    """Create necessary tables for bidding system if they don't exist"""
    try:
        con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='cropinfo', charset='utf8')
        with con:
            cur = con.cursor()
            
            # Table for product negotiations/bidding sessions
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
            
            # Table for individual bid messages/offers
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
            
            # Table for accepted negotiations (contracts)
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
            
            con.commit()
            print("Bidding system tables created successfully")
    except Exception as e:
        print(f"Error creating bidding tables: {e}")

# Call this function when the module loads
CreateBiddingTables()


# ================ FARMER BIDDING FUNCTIONS ================

def FarmerBiddingDashboard(request):
    """Show all active negotiations for the farmer"""
    if request.method == 'GET':
        if 'username' not in request.session:
            return render(request, 'FarmerLogin.html', {'data': 'Please login first'})
        
        farmer_username = request.session.get('username')
        
        try:
            con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='cropinfo', charset='utf8')
            with con:
                cur = con.cursor()
                
                # Get active negotiations
                cur.execute("""
                    SELECT pn.negotiation_id, pn.product_id, pn.customer_email, c.full_name, 
                           pn.crop_name, pn.current_price, pn.quantity, pn.unit, 
                           pn.negotiation_status, pn.start_time, pn.expiry_time,
                           (SELECT COUNT(*) FROM negotiation_bids nb WHERE nb.negotiation_id = pn.negotiation_id) as bid_count,
                           (SELECT offered_price FROM negotiation_bids nb WHERE nb.negotiation_id = pn.negotiation_id 
                            ORDER BY nb.bid_time DESC LIMIT 1) as last_offer
                    FROM product_negotiations pn
                    LEFT JOIN customers c ON pn.customer_email = c.email
                    WHERE pn.farmer_username = %s AND pn.negotiation_status = 'active'
                    ORDER BY pn.last_updated DESC
                """, (farmer_username,))
                active_negotiations = cur.fetchall()
                
                # Get completed/accepted negotiations
                cur.execute("""
                    SELECT pn.negotiation_id, pn.product_id, pn.customer_email, c.full_name,
                           pn.crop_name, pn.current_price, pn.quantity, pn.unit,
                           pn.negotiation_status, pn.start_time, ab.contract_id, ab.payment_status
                    FROM product_negotiations pn
                    LEFT JOIN customers c ON pn.customer_email = c.email
                    LEFT JOIN accepted_bids ab ON pn.negotiation_id = ab.negotiation_id
                    WHERE pn.farmer_username = %s AND pn.negotiation_status IN ('accepted', 'completed', 'rejected')
                    ORDER BY pn.last_updated DESC
                    LIMIT 20
                """, (farmer_username,))
                completed_negotiations = cur.fetchall()
                
                # Get products available for negotiation
                cur.execute("""
                    SELECT product_id, crop_name, variety, quantity, unit, selling_price
                    FROM farmer_products 
                    WHERE farmer_username = %s AND status = 'available' AND quantity > 0
                    ORDER BY listing_date DESC
                """, (farmer_username,))
                available_products = cur.fetchall()
                
        except Exception as e:
            print(f"Error in FarmerBiddingDashboard: {e}")
            active_negotiations = []
            completed_negotiations = []
            available_products = []
        
        context = {
            'active_negotiations': active_negotiations,
            'completed_negotiations': completed_negotiations,
            'available_products': available_products,
            'farmer_name': farmer_username
        }
        return render(request, 'FarmerBiddingDashboard.html', context)


def StartNegotiation(request):
    """Farmer initiates a negotiation with a specific customer"""
    if request.method == 'POST':
        if 'username' not in request.session:
            return JsonResponse({'success': False, 'message': 'Please login first'})
        
        farmer_username = request.session.get('username')
        product_id = request.POST.get('product_id')
        customer_email = request.POST.get('customer_email')
        initial_price = request.POST.get('initial_price')
        quantity = request.POST.get('quantity')
        
        try:
            con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='cropinfo', charset='utf8')
            with con:
                cur = con.cursor()
                
                # Get product details
                cur.execute("""
                    SELECT crop_name, unit, selling_price 
                    FROM farmer_products 
                    WHERE product_id = %s AND farmer_username = %s
                """, (product_id, farmer_username))
                product = cur.fetchone()
                
                if not product:
                    return JsonResponse({'success': False, 'message': 'Product not found'})
                
                crop_name, unit, selling_price = product
                
                # Set negotiation expiry (24 hours by default)
                start_time = datetime.now()
                expiry_time = start_time + timedelta(hours=24)
                
                # Create negotiation
                cur.execute("""
                    INSERT INTO product_negotiations 
                    (product_id, farmer_username, customer_email, crop_name, initial_price, 
                     current_price, quantity, unit, negotiation_status, start_time, last_updated, expiry_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'active', %s, %s, %s)
                """, (product_id, farmer_username, customer_email, crop_name, initial_price, 
                      initial_price, quantity, unit, start_time, start_time, expiry_time))
                
                negotiation_id = cur.lastrowid
                
                # Create initial bid
                cur.execute("""
                    INSERT INTO negotiation_bids 
                    (negotiation_id, bidder_type, bidder_name, offered_price, offered_quantity, message, bid_time, is_current)
                    VALUES (%s, 'farmer', %s, %s, %s, 'Initial offer from farmer', %s, TRUE)
                """, (negotiation_id, farmer_username, initial_price, quantity, start_time))
                
                con.commit()
                
                return JsonResponse({
                    'success': True, 
                    'message': 'Negotiation started successfully',
                    'negotiation_id': negotiation_id
                })
                
        except Exception as e:
            print(f"Error starting negotiation: {e}")
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})


def ViewNegotiationDetails(request, negotiation_id):
    """View full negotiation history and details"""
    if request.method == 'GET':
        if 'username' not in request.session and 'customer_email' not in request.session:
            return JsonResponse({'success': False, 'message': 'Please login first'})
        
        is_farmer = 'username' in request.session
        username = request.session.get('username') or request.session.get('customer_email')
        
        try:
            con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='cropinfo', charset='utf8')
            with con:
                cur = con.cursor()
                
                # Get negotiation details
                cur.execute("""
                    SELECT pn.*, c.full_name as customer_name, c.contact as customer_contact,
                           fp.variety, fp.selling_price as original_price
                    FROM product_negotiations pn
                    LEFT JOIN customers c ON pn.customer_email = c.email
                    LEFT JOIN farmer_products fp ON pn.product_id = fp.product_id
                    WHERE pn.negotiation_id = %s
                """, (negotiation_id,))
                negotiation = cur.fetchone()
                
                # Get all bids in this negotiation
                cur.execute("""
                    SELECT * FROM negotiation_bids 
                    WHERE negotiation_id = %s 
                    ORDER BY bid_time ASC
                """, (negotiation_id,))
                bids = cur.fetchall()
                
                # Get column names
                cur.execute("DESCRIBE product_negotiations")
                negotiation_columns = [col[0] for col in cur.fetchall()]
                
                cur.execute("DESCRIBE negotiation_bids")
                bid_columns = [col[0] for col in cur.fetchall()]
                
        except Exception as e:
            print(f"Error viewing negotiation: {e}")
            negotiation = None
            bids = []
            negotiation_columns = []
            bid_columns = []
        
        context = {
            'negotiation': negotiation,
            'bids': bids,
            'negotiation_columns': negotiation_columns,
            'bid_columns': bid_columns,
            'is_farmer': is_farmer,
            'username': username
        }
        return render(request, 'NegotiationDetails.html', context)


def FarmerCounterOffer(request):
    """Farmer makes a counter offer in an active negotiation"""
    if request.method == 'POST':
        if 'username' not in request.session:
            return JsonResponse({'success': False, 'message': 'Please login first'})
        
        farmer_username = request.session.get('username')
        negotiation_id = request.POST.get('negotiation_id')
        offered_price = request.POST.get('offered_price')
        offered_quantity = request.POST.get('offered_quantity')
        message = request.POST.get('message', 'Counter offer from farmer')
        
        try:
            con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='cropinfo', charset='utf8')
            with con:
                cur = con.cursor()
                
                # Verify this negotiation belongs to this farmer and is active
                cur.execute("""
                    SELECT negotiation_id FROM product_negotiations 
                    WHERE negotiation_id = %s AND farmer_username = %s AND negotiation_status = 'active'
                """, (negotiation_id, farmer_username))
                
                if not cur.fetchone():
                    return JsonResponse({'success': False, 'message': 'Negotiation not found or not active'})
                
                # Update all previous bids to not current
                cur.execute("""
                    UPDATE negotiation_bids SET is_current = FALSE 
                    WHERE negotiation_id = %s
                """, (negotiation_id,))
                
                # Insert new bid
                bid_time = datetime.now()
                cur.execute("""
                    INSERT INTO negotiation_bids 
                    (negotiation_id, bidder_type, bidder_name, offered_price, offered_quantity, message, bid_time, is_current)
                    VALUES (%s, 'farmer', %s, %s, %s, %s, %s, TRUE)
                """, (negotiation_id, farmer_username, offered_price, offered_quantity, message, bid_time))
                
                # Update negotiation with current price and last updated time
                cur.execute("""
                    UPDATE product_negotiations 
                    SET current_price = %s, quantity = %s, last_updated = %s
                    WHERE negotiation_id = %s
                """, (offered_price, offered_quantity, bid_time, negotiation_id))
                
                con.commit()
                
                return JsonResponse({
                    'success': True, 
                    'message': 'Counter offer sent successfully',
                    'bid_time': str(bid_time)
                })
                
        except Exception as e:
            print(f"Error making counter offer: {e}")
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})


def AcceptNegotiation(request):
    """Farmer accepts the current offer and creates a contract"""
    if request.method == 'POST':
        if 'username' not in request.session:
            return JsonResponse({'success': False, 'message': 'Please login first'})
        
        try:
            farmer_username = request.session.get('username')
            negotiation_id = request.POST.get('negotiation_id')
            
            if not negotiation_id:
                return JsonResponse({'success': False, 'message': 'Negotiation ID is required'})
            
            con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='cropinfo', charset='utf8')
            with con:
                cur = con.cursor()
                
                # Get negotiation details
                cur.execute("""
                    SELECT pn.*, fp.product_id, fp.quantity as available_quantity
                    FROM product_negotiations pn
                    JOIN farmer_products fp ON pn.product_id = fp.product_id
                    WHERE pn.negotiation_id = %s AND pn.farmer_username = %s AND pn.negotiation_status = 'active'
                """, (negotiation_id, farmer_username))
                
                row = cur.fetchone()
                if not row:
                    return JsonResponse({'success': False, 'message': 'Negotiation not found or already completed'})
                
                # Get column names
                cur.execute("DESCRIBE product_negotiations")
                columns = [col[0] for col in cur.fetchall()]
                
                # Convert row to dict for easier access
                negotiation = dict(zip(columns, row[:len(columns)]))
                
                # Get the current winning bid (last customer offer)
                cur.execute("""
                    SELECT * FROM negotiation_bids 
                    WHERE negotiation_id = %s AND bidder_type = 'customer'
                    ORDER BY bid_time DESC LIMIT 1
                """, (negotiation_id,))
                
                current_bid_row = cur.fetchone()
                
                if not current_bid_row:
                    return JsonResponse({'success': False, 'message': 'No customer offer to accept'})
                
                # Get bid column names
                cur.execute("DESCRIBE negotiation_bids")
                bid_columns = [col[0] for col in cur.fetchall()]
                current_bid = dict(zip(bid_columns, current_bid_row[:len(bid_columns)]))
                
                # Extract values with proper type conversion
                try:
                    final_price = float(current_bid.get('offered_price', 0))
                except (ValueError, TypeError):
                    final_price = 0.0
                    
                try:
                    quantity = float(current_bid.get('offered_quantity', 0))
                except (ValueError, TypeError):
                    quantity = 0.0
                
                customer_email = negotiation.get('customer_email', '')
                product_id = negotiation.get('product_id', '')
                unit = negotiation.get('unit', 'kg')
                delivery_date = negotiation.get('delivery_date', None)
                
                # Validate values
                if final_price <= 0:
                    return JsonResponse({'success': False, 'message': 'Invalid price in offer'})
                
                if quantity <= 0:
                    return JsonResponse({'success': False, 'message': 'Invalid quantity in offer'})
                
                # Calculate total amount
                total_amount = final_price * quantity
                
                # Update negotiation status
                from datetime import datetime
                now = datetime.now()
                
                cur.execute("""
                    UPDATE product_negotiations 
                    SET negotiation_status = 'accepted', last_updated = %s
                    WHERE negotiation_id = %s
                """, (now, negotiation_id))
                
                # Generate transaction ID
                transaction_id = f"BID-{negotiation_id}-{now.strftime('%Y%m%d%H%M%S')}"
                
                # Create contract in accepted_bids table
                cur.execute("""
                    INSERT INTO accepted_bids 
                    (negotiation_id, product_id, farmer_username, customer_email, final_price, 
                     quantity, unit, total_amount, delivery_date, contract_date, payment_status, order_status, transaction_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending', 'pending', %s)
                """, (
                    negotiation_id,
                    product_id,
                    farmer_username,
                    customer_email,
                    final_price,
                    quantity,
                    unit,
                    total_amount,
                    delivery_date,
                    now,
                    transaction_id
                ))
                
                contract_id = cur.lastrowid
                
                # Update product quantity
                cur.execute("""
                    UPDATE farmer_products 
                    SET quantity = quantity - %s 
                    WHERE product_id = %s
                """, (quantity, product_id))
                
                # Check if product quantity is zero or less, update status
                cur.execute("""
                    UPDATE farmer_products 
                    SET status = 'sold' 
                    WHERE product_id = %s AND quantity <= 0
                """, (product_id,))
                
                con.commit()
                
                # Send notification to customer
                try:
                    SendBidAcceptanceNotification(negotiation_id, customer_email, farmer_username, final_price, quantity)
                except Exception as e:
                    print(f"Notification error: {e}")
                
                return JsonResponse({
                    'success': True, 
                    'message': 'Offer accepted successfully! Contract created.',
                    'contract_id': contract_id,
                    'transaction_id': transaction_id
                })
                
        except Exception as e:
            print(f"Error in AcceptNegotiation: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


def RejectNegotiation(request):
    """Farmer rejects the current negotiation"""
    if request.method == 'POST':
        if 'username' not in request.session:
            return JsonResponse({'success': False, 'message': 'Please login first'})
        
        farmer_username = request.session.get('username')
        negotiation_id = request.POST.get('negotiation_id')
        reason = request.POST.get('reason', 'Offer rejected by farmer')
        
        try:
            con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='cropinfo', charset='utf8')
            with con:
                cur = con.cursor()
                
                cur.execute("""
                    UPDATE product_negotiations 
                    SET negotiation_status = 'rejected', last_updated = %s, notes = %s
                    WHERE negotiation_id = %s AND farmer_username = %s AND negotiation_status = 'active'
                """, (datetime.now(), reason, negotiation_id, farmer_username))
                
                con.commit()
                
                return JsonResponse({'success': True, 'message': 'Negotiation rejected'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})


# ================ CUSTOMER BIDDING FUNCTIONS ================

def CustomerBiddingDashboard(request):
    """Show all products available for bidding and customer's active negotiations"""
    if request.method == 'GET':
        if 'customer_email' not in request.session:
            return render(request, 'CustomerLogin.html', {'data': 'Please login first'})
        
        customer_email = request.session.get('customer_email')
        
        try:
            con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='cropinfo', charset='utf8')
            with con:
                cur = con.cursor()
                
                # Get products available for bidding (farmers can add to bidding)
                cur.execute("""
                    SELECT fp.product_id, fp.farmer_username, s.contact_no, 
                           fp.crop_name, fp.variety, fp.quantity, fp.unit, 
                           fp.selling_price, fp.predicted_price, fp.district, fp.listing_date
                    FROM farmer_products fp
                    LEFT JOIN signup s ON fp.farmer_username = s.username
                    WHERE fp.status = 'available' AND fp.quantity > 0
                    ORDER BY fp.listing_date DESC
                    LIMIT 50
                """)
                available_products = cur.fetchall()
                
                # Get customer's active negotiations
                cur.execute("""
                    SELECT pn.negotiation_id, pn.product_id, pn.farmer_username, 
                           pn.crop_name, pn.current_price, pn.quantity, pn.unit,
                           pn.negotiation_status, pn.start_time, pn.expiry_time,
                           (SELECT offered_price FROM negotiation_bids nb 
                            WHERE nb.negotiation_id = pn.negotiation_id 
                            AND nb.bidder_type = 'customer'
                            ORDER BY nb.bid_time DESC LIMIT 1) as my_last_offer
                    FROM product_negotiations pn
                    WHERE pn.customer_email = %s AND pn.negotiation_status = 'active'
                    ORDER BY pn.last_updated DESC
                """, (customer_email,))
                active_negotiations = cur.fetchall()
                
                # Get customer's accepted bids (contracts)
                cur.execute("""
                    SELECT ab.*, pn.crop_name, pn.farmer_username
                    FROM accepted_bids ab
                    JOIN product_negotiations pn ON ab.negotiation_id = pn.negotiation_id
                    WHERE ab.customer_email = %s
                    ORDER BY ab.contract_date DESC
                """, (customer_email,))
                contracts = cur.fetchall()
                
        except Exception as e:
            print(f"Error in CustomerBiddingDashboard: {e}")
            available_products = []
            active_negotiations = []
            contracts = []
        
        context = {
            'available_products': available_products,
            'active_negotiations': active_negotiations,
            'contracts': contracts,
            'customer_name': request.session.get('customer_name', 'Customer')
        }
        return render(request, 'CustomerBiddingDashboard.html', context)


def RequestNegotiation(request):
    """Customer requests to start negotiation on a product"""
    if request.method == 'POST':
        if 'customer_email' not in request.session:
            return JsonResponse({'success': False, 'message': 'Please login first'})
        
        try:
            customer_email = request.session.get('customer_email')
            customer_name = request.session.get('customer_name', 'Customer')
            
            product_id = request.POST.get('product_id')
            initial_offer = request.POST.get('initial_offer')
            quantity = request.POST.get('quantity')
            delivery_date = request.POST.get('delivery_date')
            
            # Validate inputs
            if not all([product_id, initial_offer, quantity, delivery_date]):
                return JsonResponse({'success': False, 'message': 'All fields are required'})
            
            con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='cropinfo', charset='utf8')
            with con:
                cur = con.cursor()
                
                # Get product and farmer details
                cur.execute("""
                    SELECT farmer_username, crop_name, unit, selling_price, quantity 
                    FROM farmer_products 
                    WHERE product_id = %s AND status = 'available'
                """, (product_id,))
                product = cur.fetchone()
                
                if not product:
                    return JsonResponse({'success': False, 'message': 'Product not available'})
                
                farmer_username, crop_name, unit, selling_price, available_quantity = product
                
                # Check if requested quantity is available
                if float(quantity) > float(available_quantity):
                    return JsonResponse({'success': False, 'message': f'Only {available_quantity} {unit} available'})
                
                # Check if negotiation already exists for this product and customer
                cur.execute("""
                    SELECT negotiation_id FROM product_negotiations 
                    WHERE product_id = %s AND customer_email = %s AND negotiation_status = 'active'
                """, (product_id, customer_email))
                
                existing = cur.fetchone()
                if existing:
                    return JsonResponse({
                        'success': False, 
                        'message': 'You already have an active negotiation for this product',
                        'negotiation_id': existing[0]
                    })
                
                # Create negotiation
                from datetime import datetime, timedelta
                start_time = datetime.now()
                expiry_time = start_time + timedelta(hours=24)
                
                cur.execute("""
                    INSERT INTO product_negotiations 
                    (product_id, farmer_username, customer_email, crop_name, initial_price, 
                     current_price, quantity, unit, negotiation_status, start_time, last_updated, expiry_time, delivery_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'active', %s, %s, %s, %s)
                """, (product_id, farmer_username, customer_email, crop_name, initial_offer, 
                      initial_offer, quantity, unit, start_time, start_time, expiry_time, delivery_date))
                
                negotiation_id = cur.lastrowid
                
                # Create initial bid from customer
                cur.execute("""
                    INSERT INTO negotiation_bids 
                    (negotiation_id, bidder_type, bidder_name, offered_price, offered_quantity, message, bid_time, is_current)
                    VALUES (%s, 'customer', %s, %s, %s, 'Initial offer from customer', %s, TRUE)
                """, (negotiation_id, customer_name, initial_offer, quantity, start_time))
                
                con.commit()
                
                return JsonResponse({
                    'success': True, 
                    'message': 'Negotiation request sent to farmer successfully!',
                    'negotiation_id': negotiation_id
                })
                
        except Exception as e:
            print(f"Error in RequestNegotiation: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


def CustomerCounterOffer(request):
    """Customer makes a counter offer in an active negotiation"""
    if request.method == 'POST':
        if 'customer_email' not in request.session:
            return JsonResponse({'success': False, 'message': 'Please login first'})
        
        customer_email = request.session.get('customer_email')
        customer_name = request.session.get('customer_name', 'Customer')
        negotiation_id = request.POST.get('negotiation_id')
        offered_price = request.POST.get('offered_price')
        offered_quantity = request.POST.get('offered_quantity')
        message = request.POST.get('message', 'Counter offer from customer')
        
        try:
            con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='cropinfo', charset='utf8')
            with con:
                cur = con.cursor()
                
                # Verify this negotiation belongs to this customer and is active
                cur.execute("""
                    SELECT negotiation_id FROM product_negotiations 
                    WHERE negotiation_id = %s AND customer_email = %s AND negotiation_status = 'active'
                """, (negotiation_id, customer_email))
                
                if not cur.fetchone():
                    return JsonResponse({'success': False, 'message': 'Negotiation not found or not active'})
                
                # Update all previous bids to not current
                cur.execute("""
                    UPDATE negotiation_bids SET is_current = FALSE 
                    WHERE negotiation_id = %s
                """, (negotiation_id,))
                
                # Insert new bid
                bid_time = datetime.now()
                cur.execute("""
                    INSERT INTO negotiation_bids 
                    (negotiation_id, bidder_type, bidder_name, offered_price, offered_quantity, message, bid_time, is_current)
                    VALUES (%s, 'customer', %s, %s, %s, %s, %s, TRUE)
                """, (negotiation_id, customer_name, offered_price, offered_quantity, message, bid_time))
                
                # Update negotiation with current price and last updated time
                cur.execute("""
                    UPDATE product_negotiations 
                    SET current_price = %s, quantity = %s, last_updated = %s
                    WHERE negotiation_id = %s
                """, (offered_price, offered_quantity, bid_time, negotiation_id))
                
                con.commit()
                
                return JsonResponse({
                    'success': True, 
                    'message': 'Counter offer sent successfully',
                    'bid_time': str(bid_time)
                })
                
        except Exception as e:
            print(f"Error making counter offer: {e}")
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})


def AcceptFarmerOffer(request):
    """Customer accepts farmer's offer"""
    if request.method == 'POST':
        if 'customer_email' not in request.session:
            return JsonResponse({'success': False, 'message': 'Please login first'})
        
        customer_email = request.session.get('customer_email')
        negotiation_id = request.POST.get('negotiation_id')
        
        try:
            con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='cropinfo', charset='utf8')
            with con:
                cur = con.cursor()
                
                # Get the latest farmer offer
                cur.execute("""
                    SELECT * FROM negotiation_bids 
                    WHERE negotiation_id = %s AND bidder_type = 'farmer'
                    ORDER BY bid_time DESC LIMIT 1
                """, (negotiation_id,))
                
                farmer_offer = cur.fetchone()
                
                if not farmer_offer:
                    return JsonResponse({'success': False, 'message': 'No farmer offer to accept'})
                
                # Update negotiation status
                cur.execute("""
                    UPDATE product_negotiations 
                    SET negotiation_status = 'accepted', last_updated = %s
                    WHERE negotiation_id = %s AND customer_email = %s
                """, (datetime.now(), negotiation_id, customer_email))
                
                # Get negotiation details for contract
                cur.execute("""
                    SELECT product_id, farmer_username, unit, delivery_date 
                    FROM product_negotiations WHERE negotiation_id = %s
                """, (negotiation_id,))
                negotiation = cur.fetchone()
                
                # Create contract
                total_amount = float(farmer_offer[5]) * float(farmer_offer[6])
                transaction_id = f"BID-{negotiation_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                cur.execute("""
                    INSERT INTO accepted_bids 
                    (negotiation_id, product_id, farmer_username, customer_email, final_price, 
                     quantity, unit, total_amount, delivery_date, contract_date, payment_status, order_status, transaction_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending', 'pending', %s)
                """, (
                    negotiation_id,
                    negotiation[0],
                    negotiation[1],
                    customer_email,
                    farmer_offer[5],
                    farmer_offer[6],
                    negotiation[2],
                    total_amount,
                    negotiation[3],
                    datetime.now(),
                    transaction_id
                ))
                
                con.commit()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Offer accepted successfully! Contract created.',
                    'transaction_id': transaction_id
                })
                
        except Exception as e:
            print(f"Error accepting offer: {e}")
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})


def CancelNegotiation(request):
    """Customer cancels an active negotiation"""
    if request.method == 'POST':
        if 'customer_email' not in request.session:
            return JsonResponse({'success': False, 'message': 'Please login first'})
        
        customer_email = request.session.get('customer_email')
        negotiation_id = request.POST.get('negotiation_id')
        reason = request.POST.get('reason', 'Cancelled by customer')
        
        try:
            con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='cropinfo', charset='utf8')
            with con:
                cur = con.cursor()
                
                cur.execute("""
                    UPDATE product_negotiations 
                    SET negotiation_status = 'rejected', last_updated = %s, notes = %s
                    WHERE negotiation_id = %s AND customer_email = %s AND negotiation_status = 'active'
                """, (datetime.now(), reason, negotiation_id, customer_email))
                
                con.commit()
                
                return JsonResponse({'success': True, 'message': 'Negotiation cancelled'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})


# ================ HELPER FUNCTIONS ================

def SendBidAcceptanceNotification(negotiation_id, customer_email, farmer_name, final_price, quantity):
    """Send notification to customer when farmer accepts their bid"""
    try:
        con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='cropinfo', charset='utf8')
        with con:
            cur = con.cursor()
            
            # Create customer notifications table if not exists
            cur.execute("""
                CREATE TABLE IF NOT EXISTS customer_notifications (
                    notification_id INT AUTO_INCREMENT PRIMARY KEY,
                    customer_email VARCHAR(100),
                    negotiation_id INT,
                    message TEXT,
                    notification_date DATETIME,
                    is_read BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (customer_email) REFERENCES customers(email)
                )
            """)
            
            message = f"Your bid for negotiation #{negotiation_id} has been accepted! Farmer {farmer_name} accepted your offer of ₹{final_price} for {quantity} units. Contract has been created."
            
            cur.execute("""
                INSERT INTO customer_notifications (customer_email, negotiation_id, message, notification_date, is_read)
                VALUES (%s, %s, %s, %s, FALSE)
            """, (customer_email, negotiation_id, message, datetime.now()))
            
            con.commit()
            return True
    except Exception as e:
        print(f"Error sending bid acceptance notification: {e}")
        return False


def GetCustomerNotifications(request):
    """Get notifications for the logged-in customer"""
    if request.method == 'GET':
        if 'customer_email' not in request.session:
            return JsonResponse({'success': False, 'message': 'Not logged in'})
        
        customer_email = request.session.get('customer_email')
        
        try:
            con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='cropinfo', charset='utf8')
            with con:
                cur = con.cursor()
                
                cur.execute("""
                    SELECT notification_id, negotiation_id, message, notification_date, is_read
                    FROM customer_notifications 
                    WHERE customer_email = %s 
                    ORDER BY notification_date DESC
                    LIMIT 20
                """, (customer_email,))
                
                notifications = cur.fetchall()
                
                # Mark as read
                cur.execute("""
                    UPDATE customer_notifications SET is_read = TRUE 
                    WHERE customer_email = %s AND is_read = FALSE
                """, (customer_email,))
                
                con.commit()
                
                return JsonResponse({
                    'success': True,
                    'notifications': notifications
                })
                
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})


def CompleteTransaction(request, contract_id):
    """Mark a transaction as complete (payment received)"""
    if request.method == 'POST':
        # This could be called by farmer or admin
        if 'username' not in request.session and 'customer_email' not in request.session:
            return JsonResponse({'success': False, 'message': 'Please login first'})
        
        try:
            con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='cropinfo', charset='utf8')
            with con:
                cur = con.cursor()
                
                cur.execute("""
                    UPDATE accepted_bids 
                    SET payment_status = 'completed', order_status = 'delivered' 
                    WHERE contract_id = %s
                """, (contract_id,))
                
                # Also update related negotiation
                cur.execute("""
                    UPDATE product_negotiations pn
                    JOIN accepted_bids ab ON pn.negotiation_id = ab.negotiation_id
                    SET pn.negotiation_status = 'completed'
                    WHERE ab.contract_id = %s
                """, (contract_id,))
                
                con.commit()
                
                return JsonResponse({'success': True, 'message': 'Transaction completed successfully'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})



# Add this to your views.py file
def logout_view(request):
    """Universal logout function for all users"""
    try:
        # Clear farmer session
        if 'username' in request.session:
            del request.session['username']
        
        # Clear customer session
        if 'customer_email' in request.session:
            del request.session['customer_email']
        if 'customer_name' in request.session:
            del request.session['customer_name']
        
        # Clear user type
        if 'user_type' in request.session:
            del request.session['user_type']
        
        # Clear any other session data
        request.session.flush()
        
        messages.success(request, 'You have been successfully logged out.')
    except:
        pass
    
    return render(request, 'index.html', {'data': 'Logged out successfully'})

def farmer_logout(request):
    """Farmer specific logout"""
    try:
        if 'username' in request.session:
            del request.session['username']
        if 'user_type' in request.session:
            del request.session['user_type']
        request.session.flush()
        messages.success(request, 'Farmer logged out successfully.')
    except:
        pass
    return render(request, 'FarmerLogin.html', {'data': 'Logged out successfully'})

def customer_logout(request):
    """Customer specific logout"""
    try:
        if 'customer_email' in request.session:
            del request.session['customer_email']
        if 'customer_name' in request.session:
            del request.session['customer_name']
        request.session.flush()
        messages.success(request, 'Customer logged out successfully.')
    except:
        pass
    return render(request, 'CustomerLogin.html', {'data': 'Logged out successfully'})

def admin_logout(request):
    """Admin specific logout"""
    try:
        if 'username' in request.session:
            del request.session['username']
        if 'user_type' in request.session:
            del request.session['user_type']
        request.session.flush()
        messages.success(request, 'Admin logged out successfully.')
    except:
        pass
    return render(request, 'AdminLogin.html', {'data': 'Logged out successfully'})



def ViewSchemes(request):
    if request.method == 'GET':
        output = '<table border=1 align=center width=100% class="table table-bordered">'
        font = '<font size="" color=black>'
        arr = ['Scheme ID', 'Scheme Name', 'Scheme Description', 'Required Documents', 'Scheme Launch Date', 'Scheme End Date']
        output += "<tr>"
        for i in range(len(arr)):
            output += "<th>" + font + arr[i] + "</th>"
        output += getOutput("addscheme", len(arr))
        output += "</table>"
        context = {'data': output}
        return render(request, 'ViewSchemes.html', context)


# Farmer Product Management Functions
def FarmerDashboard(request):
    global uname
    if request.method == 'GET':
        if 'username' not in request.session:
            return render(request, 'FarmerLogin.html', {'data': 'Please login first'})
        
        uname = request.session.get('username')
        
        try:
            con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='cropinfo', charset='utf8')
            with con:
                cur = con.cursor()
                cur.execute("SELECT COUNT(*) FROM farmer_products WHERE farmer_username=%s AND status='available'", (uname,))
                product_count = cur.fetchone()[0]

                cur.execute("SELECT COUNT(*) FROM customer_orders WHERE farmer_username=%s", (uname,))
                order_count = cur.fetchone()[0]

                cur.execute("SELECT COUNT(*) FROM customer_orders WHERE farmer_username=%s AND order_status='pending'", (uname,))
                pending_count = cur.fetchone()[0]
        except:
            product_count = 0
            order_count = 0
            pending_count = 0

        context = {
            'data': 'Welcome ' + uname,
            'product_count': product_count,
            'order_count': order_count,
            'pending_count': pending_count
        }
        return render(request, 'FarmerDashboard.html', context)


def AddProduct(request):
    if request.method == 'GET':
        if 'username' not in request.session:
            return render(request, 'FarmerLogin.html', {'data': 'Please login first'})
        
        # Get unique crop varieties for dropdown
        variety = np.unique(dataset['variety'])
        crop_output = '<select name="crop_name" class="form-control" required>'
        crop_output += '<option value="">Select Crop</option>'
        for i in range(len(variety)):
            crop_output += '<option value="' + str(variety[i]) + '">' + str(variety[i]) + '</option>'
        crop_output += '</select>'

        # Get districts from the CropDataset for dropdown
        try:
            dataset1 = pd.read_csv("Dataset/CropDataset.csv", encoding='iso-8859-1', usecols=['district'])
            districts = np.unique(dataset1['district'].dropna())
            district_output = '<select name="district" class="form-control" required>'
            district_output += '<option value="">Select District</option>'
            for district in districts:
                district_output += '<option value="' + str(district) + '">' + str(district) + '</option>'
            district_output += '</select>'
        except:
            # Fallback if dataset doesn't have districts or can't be read
            district_output = '<input type="text" name="district" class="form-control" placeholder="Your district" required>'

        context = {
            'crop_dropdown': crop_output,
            'district_dropdown': district_output
        }
        return render(request, 'AddProduct.html', context)


def AddProductAction(request):
    if request.method == 'POST':
        if 'username' not in request.session:
            return render(request, 'FarmerLogin.html', {'data': 'Please login first'})
        
        farmer_username = request.session.get('username')
        
        crop_name = request.POST.get('crop_name', '')
        variety = request.POST.get('variety', '')
        quantity = request.POST.get('quantity', 0)
        unit = request.POST.get('unit', '')
        selling_price = request.POST.get('selling_price', 0)
        district = request.POST.get('district', '')

        # Get predicted price from dataset
        predicted_price = 0
        try:
            dataset1 = pd.read_csv("Dataset/CropDataset.csv", encoding='iso-8859-1', usecols=['variety', 'max_price', 'Rainfall', 'district'])
            df = dataset1.loc[(dataset1['variety'] == crop_name)]
            if not df.empty:
                predicted_price = df['max_price'].mean()
        except:
            predicted_price = float(selling_price) * 0.9  # Default 10% less than selling price

        today = date.today()

        output = "none"
        try:
            db_connection = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='cropinfo', charset='utf8')
            db_cursor = db_connection.cursor()

            sql_query = """INSERT INTO farmer_products 
                          (farmer_username, crop_name, variety, quantity, unit, predicted_price, selling_price, district, listing_date, status) 
                          VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, 'available')"""

            db_cursor.execute(sql_query, (farmer_username, crop_name, variety, quantity, unit, predicted_price, selling_price, district, today))
            db_connection.commit()

            if db_cursor.rowcount == 1:
                output = 'Product added successfully!'
            else:
                output = 'Failed to add product'
        except Exception as e:
            output = 'Error: ' + str(e)

        context = {'data': output}
        return render(request, 'AddProduct.html', context)


def MyProducts(request):
    if request.method == 'GET':
        if 'username' not in request.session:
            return render(request, 'FarmerLogin.html', {'data': 'Please login first'})
        
        farmer_username = request.session.get('username')
        
        try:
            con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='cropinfo', charset='utf8')
            with con:
                cur = con.cursor()
                cur.execute("""SELECT product_id, crop_name, variety, quantity, unit, 
                              predicted_price, selling_price, district, listing_date, status 
                              FROM farmer_products WHERE farmer_username=%s ORDER BY listing_date DESC""", (farmer_username,))
                rows = cur.fetchall()

            output = '<table border="1" class="table table-bordered">'
            output += '<tr><th>Product ID</th><th>Crop</th><th>Variety</th><th>Quantity</th><th>Unit</th>'
            output += '<th>Predicted Price</th><th>Selling Price</th><th>District</th><th>Listing Date</th><th>Status</th><th>Action</th></tr>'

            for row in rows:
                output += '<tr>'
                for i in range(len(row)-1):
                    output += '<td>' + str(row[i]) + '</td>'
                # Status column
                status = row[9]
                output += '<td><span class="badge ' + ('badge-success" style="background-color:green; color:white"' if status == "available" else 'badge-secondary" style="background-color:gray; color:white"') + '>' + status + '</span></td>'
                # Action column
                if status == 'available':
                    output += '<td><button onclick="updateStatus(' + str(row[0]) + ', \'removed\')" class="btn btn-sm btn-danger">Remove</button></td>'
                else:
                    output += '<td>-</td>'
                output += '</tr>'

            output += '</table>'
        except:
            output = '<div class="alert alert-info">No products found</div>'

        context = {'products': output}
        return render(request, 'MyProducts.html', context)


def UpdateProductStatus(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        status = request.POST.get('status')

        try:
            con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='cropinfo', charset='utf8')
            with con:
                cur = con.cursor()
                cur.execute("UPDATE farmer_products SET status=%s WHERE product_id=%s", (status, product_id))
                con.commit()
            return HttpResponse("Status updated successfully")
        except:
            return HttpResponse("Error updating status")


def FarmerOrders(request):
    if request.method == 'GET':
        if 'username' not in request.session:
            return render(request, 'FarmerLogin.html', {'data': 'Please login first'})
        
        farmer_username = request.session.get('username')
        
        try:
            con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='cropinfo', charset='utf8')
            with con:
                cur = con.cursor()
                cur.execute("""SELECT order_id, customer_name, customer_contact, crop_name, quantity, unit, 
                              price_per_unit, total_amount, order_date, delivery_date, order_status, payment_status 
                              FROM customer_orders WHERE farmer_username=%s ORDER BY order_date DESC""", (farmer_username,))
                rows = cur.fetchall()

            output = '<table border="1" class="table table-bordered">'
            output += '<tr><th>Order ID</th><th>Customer</th><th>Contact</th><th>Crop</th><th>Quantity</th>'
            output += '<th>Unit</th><th>Price/Unit</th><th>Total</th><th>Order Date</th><th>Delivery Date</th><th>Order Status</th><th>Payment</th><th>Action</th></tr>'

            for row in rows:
                output += '<tr>'
                for i in range(len(row)-2):
                    output += '<td>' + str(row[i]) + '</td>'
                # Order Status
                order_status = row[10]
                output += '<td><select onchange="updateOrderStatus(' + str(row[0]) + ', this.value)" class="form-control form-control-sm">'
                statuses = ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']
                for status in statuses:
                    selected = 'selected' if status == order_status else ''
                    output += '<option value="' + status + '" ' + selected + '>' + status.capitalize() + '</option>'
                output += '</select></td>'
                # Payment Status
                output += '<td>' + str(row[11]) + '</td>'
                # Action column
                if order_status not in ['delivered', 'cancelled']:
                    output += '<td><button onclick="cancelOrder(' + str(row[0]) + ')" class="btn btn-sm btn-danger">Cancel</button></td>'
                else:
                    output += '<td>-</td>'
                output += '</tr>'

            output += '</table>'
        except:
            output = '<div class="alert alert-info">No orders found</div>'

        context = {'orders': output}
        return render(request, 'FarmerOrders.html', context)


def UpdateOrderStatus(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        status = request.POST.get('status')

        try:
            con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='cropinfo', charset='utf8')
            with con:
                cur = con.cursor()
                cur.execute("UPDATE customer_orders SET order_status=%s WHERE order_id=%s", (status, order_id))
                con.commit()
            return HttpResponse("Order status updated successfully")
        except:
            return HttpResponse("Error updating order status")


# Customer Functions
def CustomerSignup(request):
    if request.method == 'GET':
        return render(request, 'CustomerSignup.html', {})


def CustomerSignupAction(request):
    if request.method == 'POST':
        full_name = request.POST.get('t1', '')
        email = request.POST.get('t2', '')
        password = request.POST.get('t3', '')
        contact = request.POST.get('t4', '')
        address = request.POST.get('t5', '')
        city = request.POST.get('t6', '')
        state = request.POST.get('t7', '')
        pincode = request.POST.get('t8', '')

        today = date.today()

        output = "none"
        try:
            con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='cropinfo', charset='utf8')
            with con:
                cur = con.cursor()
                cur.execute("SELECT email FROM customers WHERE email=%s", (email,))
                row = cur.fetchone()
                if row:
                    output = "Email already exists!"
                else:
                    cur.execute("""INSERT INTO customers(full_name, email, password, contact, address, city, state, pincode, registration_date) 
                                  VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                              (full_name, email, password, contact, address, city, state, pincode, today))
                    con.commit()
                    if cur.rowcount == 1:
                        output = 'Customer registration successful! Please login.'
        except Exception as e:
            output = 'Error: ' + str(e)

        context = {'data': output}
        return render(request, 'CustomerSignup.html', context)


def CustomerLogin(request):
    if request.method == 'GET':
        return render(request, 'CustomerLogin.html', {})


def CustomerLoginAction(request):
    if request.method == 'POST':
        email = request.POST.get('t1', '')
        password = request.POST.get('t2', '')

        try:
            con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='cropinfo', charset='utf8')
            with con:
                cur = con.cursor()
                cur.execute("SELECT * FROM customers WHERE email=%s AND password=%s", (email, password))
                row = cur.fetchone()

                if row:
                    request.session['customer_email'] = email
                    request.session['customer_name'] = row[1]
                    context = {
                        'data': 'Welcome ' + row[1],
                        'customer_name': row[1]
                    }
                    return render(request, 'CustomerDashboard.html', context)
                else:
                    context = {'data': 'Invalid email or password'}
                    return render(request, 'CustomerLogin.html', context)
        except:
            context = {'data': 'Database connection error'}
            return render(request, 'CustomerLogin.html', context)


def CustomerDashboard(request):
    if request.method == 'GET':
        if 'customer_email' in request.session:
            context = {
                'customer_name': request.session.get('customer_name', 'Customer')
            }
            return render(request, 'CustomerDashboard.html', context)
        else:
            return render(request, 'CustomerLogin.html', {})


def AvailableProducts(request):
    if request.method == 'GET':
        # Filter by crop if specified
        crop_filter = request.GET.get('crop', '')

        try:
            con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='cropinfo', charset='utf8')
            with con:
                cur = con.cursor()
                if crop_filter:
                    cur.execute("""SELECT fp.product_id, fp.farmer_username, s.contact_no, fp.crop_name, fp.variety, 
                                  fp.quantity, fp.unit, fp.predicted_price, fp.selling_price, fp.district, fp.listing_date
                                  FROM farmer_products fp
                                  LEFT JOIN signup s ON fp.farmer_username = s.username
                                  WHERE fp.status='available' AND fp.crop_name=%s
                                  ORDER BY fp.selling_price ASC, fp.listing_date DESC""", (crop_filter,))
                else:
                    cur.execute("""SELECT fp.product_id, fp.farmer_username, s.contact_no, fp.crop_name, fp.variety, 
                                  fp.quantity, fp.unit, fp.predicted_price, fp.selling_price, fp.district, fp.listing_date
                                  FROM farmer_products fp
                                  LEFT JOIN signup s ON fp.farmer_username = s.username
                                  WHERE fp.status='available'
                                  ORDER BY fp.selling_price ASC, fp.listing_date DESC""")
                rows = cur.fetchall()

                # Get unique crops for filter
                cur.execute("SELECT DISTINCT crop_name FROM farmer_products WHERE status='available'")
                crops = cur.fetchall()

            # Build crop filter dropdown
            filter_html = '<select id="cropFilter" class="form-control" onchange="filterProducts()">'
            filter_html += '<option value="">All Crops</option>'
            for crop in crops:
                selected = 'selected' if crop[0] == crop_filter else ''
                filter_html += '<option value="' + str(crop[0]) + '" ' + selected + '>' + str(crop[0]) + '</option>'
            filter_html += '</select>'

            # Build products display - FIXED: No row[3] in template, all HTML is built here
            output = '<div class="row">'
            if rows:
                # Get the lowest price for each crop to highlight best deals
                for row in rows:
                    # Calculate savings
                    savings = 0
                    if row[7] and row[8]:  # predicted_price and selling_price
                        savings = float(row[7]) - float(row[8])
                    
                    # Check if this is the lowest price for this crop
                    is_lowest_price = False
                    # Check if this product has the lowest price among all available of same crop
                    for r in rows:
                        if r[3] == row[3] and r[8] < row[8]:
                            is_lowest_price = False
                            break
                    else:
                        is_lowest_price = True
                    
                    best_price_class = 'best-price' if is_lowest_price else ''
                    
                    output += f'''
                    <div class="col-md-4 mb-4">
                        <div class="card {best_price_class}">
                            <div class="card-body">
                                <h5 class="card-title">{row[3]} {row[4] if row[4] else ''}</h5>
                                <p class="card-text">
                                    <strong>Farmer:</strong> {row[1]}<br>
                                    <strong>Contact:</strong> {row[2] if row[2] else 'N/A'}<br>
                                    <strong>Quantity:</strong> {row[5]} {row[6]}<br>
                                    <strong>Price:</strong> ₹{row[8]}/{row[6]}<br>
                                    <strong>Predicted Market Price:</strong> ₹{round(row[7] if row[7] else 0, 2)}<br>
                                    <strong>District:</strong> {row[9]}<br>
                                    <strong>Listed on:</strong> {row[10]}
                    '''
                    if savings > 0:
                        output += f'<br><span class="price-savings">You save: ₹{round(savings, 2)}</span>'
                    
                    output += f'''
                                </p>
                                <div class="btn-group" role="group">
                                    <a href="/ProductDetails/{row[0]}" class="btn btn-primary">View Details</a>
                                    <a href="/ComparePrices/{row[3]}" class="btn btn-info">Compare Prices</a>
                                </div>
                    '''
                    if is_lowest_price:
                        output += '<br><span class="badge badge-success mt-2">✨ Best Price</span>'
                    
                    output += '''
                            </div>
                        </div>
                    </div>
                    '''
            else:
                output += '<div class="col-12"><div class="alert alert-info">No products available at the moment.</div></div>'
            output += '</div>'
            
        except Exception as e:
            print("Error in AvailableProducts:", e)
            filter_html = '<input type="text" class="form-control" placeholder="Filter by crop">'
            output = '<div class="alert alert-danger">Error loading products. Please try again.</div>'

        context = {
            'products': output,
            'filter_dropdown': filter_html,
            'current_filter': crop_filter
        }
        return render(request, 'AvailableProducts.html', context)

def ProductDetails(request, product_id):
    if request.method == 'GET':
        if 'customer_email' not in request.session:
            return render(request, 'CustomerLogin.html', {})

        try:
            con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='cropinfo', charset='utf8')
            with con:
                cur = con.cursor()
                cur.execute("""SELECT fp.product_id, fp.farmer_username, s.contact_no, fp.crop_name, fp.variety, 
                              fp.quantity, fp.unit, fp.predicted_price, fp.selling_price, fp.district, fp.listing_date
                              FROM farmer_products fp
                              LEFT JOIN signup s ON fp.farmer_username = s.username
                              WHERE fp.product_id=%s AND fp.status='available'""", (product_id,))
                row = cur.fetchone()

            if row:
                # Convert Decimal values to float for JSON serialization
                product = {
                    'product_id': row[0],
                    'farmer': row[1],
                    'contact': row[2] if row[2] else 'N/A',
                    'crop': row[3],
                    'variety': row[4] if row[4] else '',
                    'quantity': float(row[5]) if row[5] else 0,  # Convert to float
                    'unit': row[6],
                    'predicted_price': float(row[7]) if row[7] else 0,  # Convert to float
                    'selling_price': float(row[8]) if row[8] else 0,  # Convert to float
                    'district': row[9],
                    'listing_date': str(row[10]) if row[10] else ''  # Convert date to string
                }
                context = {
                    'product': product,
                    'customer_name': request.session.get('customer_name', 'Customer'),
                    'customer_email': request.session.get('customer_email', '')
                }
                return render(request, 'ProductDetails.html', context)
            else:
                return HttpResponse("Product not found or no longer available")
        except Exception as e:
            print("Product details error:", e)
            return HttpResponse("Error loading product details: " + str(e))


from decimal import Decimal

def PlaceOrderAction(request):
    if request.method == 'POST':
        if 'customer_email' not in request.session:
            return HttpResponse("Please login first")

        product_id = request.POST.get('product_id')
        quantity = Decimal(request.POST.get('quantity'))  # Convert to Decimal
        customer_name = request.POST.get('customer_name')
        customer_contact = request.POST.get('customer_contact')
        customer_email = request.POST.get('customer_email')
        customer_address = request.POST.get('customer_address')
        delivery_date = request.POST.get('delivery_date')

        try:
            con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='cropinfo', charset='utf8')
            with con:
                cur = con.cursor()

                # Get product details
                cur.execute("""SELECT farmer_username, crop_name, selling_price, unit, quantity 
                              FROM farmer_products WHERE product_id=%s AND status='available'""", (product_id,))
                product = cur.fetchone()

                if not product:
                    return HttpResponse("Product not available")

                product_quantity = Decimal(str(product[4]))  # Convert to Decimal
                if quantity > product_quantity:
                    return HttpResponse("Requested quantity exceeds available stock")

                farmer_username = product[0]
                crop_name = product[1]
                price_per_unit = Decimal(str(product[2]))  # Convert to Decimal
                unit = product[3]
                total_amount = quantity * price_per_unit  # Both are Decimal

                from datetime import date
                today = date.today()

                # Insert order (convert Decimal to string for MySQL)
                cur.execute("""INSERT INTO customer_orders 
                              (customer_name, customer_contact, customer_email, customer_address, 
                               product_id, farmer_username, crop_name, quantity, unit, 
                               price_per_unit, total_amount, order_date, delivery_date, order_status, payment_status) 
                              VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending', 'pending')""",
                          (customer_name, customer_contact, customer_email, customer_address,
                           product_id, farmer_username, crop_name, float(quantity), unit,
                           float(price_per_unit), float(total_amount), today, delivery_date))
                
                order_id = cur.lastrowid

                # Update product quantity
                new_quantity = product_quantity - quantity
                if new_quantity <= 0:
                    cur.execute("UPDATE farmer_products SET status='sold', quantity=0 WHERE product_id=%s",
                              (product_id,))
                else:
                    cur.execute("UPDATE farmer_products SET quantity=%s WHERE product_id=%s",
                              (float(new_quantity), product_id))

                con.commit()
                
                # Send notification to farmer
                try:
                    SendOrderNotification(request, order_id, farmer_username, customer_name)
                except Exception as e:
                    print("Notification error:", e)
                
                return HttpResponse(f"Order placed successfully! Order ID: {order_id}")

        except Exception as e:
            print("Order placement error:", e)
            return HttpResponse("Error placing order: " + str(e))

def MyOrders(request):
    if request.method == 'GET':
        if 'customer_email' not in request.session:
            return render(request, 'CustomerLogin.html', {})

        customer_email = request.session.get('customer_email')

        try:
            con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='cropinfo', charset='utf8')
            with con:
                cur = con.cursor()
                cur.execute("""SELECT order_id, farmer_username, crop_name, quantity, unit, 
                              price_per_unit, total_amount, order_date, delivery_date, order_status, payment_status
                              FROM customer_orders 
                              WHERE customer_email=%s 
                              ORDER BY order_date DESC""", (customer_email,))
                rows = cur.fetchall()

            output = '<table border="1" class="table table-bordered">'
            output += '<tr><th>Order ID</th><th>Farmer</th><th>Crop</th><th>Quantity</th><th>Unit</th>'
            output += '<th>Price/Unit</th><th>Total</th><th>Order Date</th><th>Delivery Date</th><th>Status</th><th>Payment</th><th>Action</th></tr>'

            for row in rows:
                output += '<tr>'
                for i in range(len(row)-2):
                    output += '<td>' + str(row[i]) + '</td>'
                output += '<td>' + str(row[9]) + '</td>'  # Order status
                output += '<td>' + str(row[10]) + '</td>'  # Payment status
                # Action column
                if row[9] == 'pending':
                    output += '<td><button onclick="cancelOrder(' + str(row[0]) + ')" class="btn btn-sm btn-danger">Cancel</button></td>'
                else:
                    output += '<td>-</td>'
                output += '</tr>'

            output += '</table>'
        except:
            output = '<div class="alert alert-info">No orders found</div>'

        context = {'orders': output}
        return render(request, 'MyOrders.html', context)


def CancelOrder(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')

        try:
            con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='cropinfo', charset='utf8')
            with con:
                cur = con.cursor()
                cur.execute("UPDATE customer_orders SET order_status='cancelled' WHERE order_id=%s AND order_status='pending'", (order_id,))
                con.commit()
            return HttpResponse("Order cancelled successfully")
        except:
            return HttpResponse("Error cancelling order")


def AdminLoginAction(request):
    global uname
    if request.method == 'POST':
        username = request.POST.get('t1', '')
        password = request.POST.get('t2', '')
        if username == 'admin' and password == 'admin':
            uname = username
            request.session['username'] = username
            request.session['user_type'] = 'admin'
            context = {'data': 'welcome ' + username}
            return render(request, 'AdminScreen.html', context)
        else:
            context = {'data': 'login failed'}
            return render(request, 'AdminLogin.html', context)


def FarmerLoginAction(request):
    global uname
    if request.method == 'POST':
        username = request.POST.get('t1', '')
        password = request.POST.get('t2', '')
        index = 0
        try:
            con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='cropinfo', charset='utf8')
            with con:
                cur = con.cursor()
                cur.execute("select username,password FROM signup")
                rows = cur.fetchall()
                for row in rows:
                    if row[0] == username and password == row[1]:
                        uname = username
                        request.session['username'] = username
                        request.session['user_type'] = 'farmer'
                        index = 1
                        break
        except:
            pass
        
        if index == 1:
            context = {'data': 'welcome ' + uname}
            return render(request, 'FarmerScreen.html', context)
        else:
            context = {'data': 'login failed'}
            return render(request, 'FarmerLogin.html', context)


def SignupAction(request):
    if request.method == 'POST':
        username = request.POST.get('t1', '')
        password = request.POST.get('t2', '')
        contact = request.POST.get('t3', '')
        gender = request.POST.get('t4', '')
        email = request.POST.get('t5', '')
        address = request.POST.get('t6', '')
        output = "none"
        
        try:
            con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='cropinfo', charset='utf8')
            with con:
                cur = con.cursor()
                cur.execute("select username FROM signup")
                rows = cur.fetchall()
                for row in rows:
                    if row[0] == username:
                        output = username + " Username already exists"
                        break
            if output == 'none':
                db_connection = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='cropinfo', charset='utf8')
                db_cursor = db_connection.cursor()
                student_sql_query = "INSERT INTO signup(username,password,contact_no,gender,email,address) VALUES(%s,%s,%s,%s,%s,%s)"
                db_cursor.execute(student_sql_query, (username, password, contact, gender, email, address))
                db_connection.commit()
                print(db_cursor.rowcount, "Record Inserted")
                if db_cursor.rowcount == 1:
                    output = 'Signup Process Completed'
        except Exception as e:
            output = 'Error: ' + str(e)
            
        context = {'data': output}
        return render(request, 'Signup.html', context)


def AddScheme(request):
    if request.method == 'GET':
        return render(request, 'AddScheme.html', {})
# Add these new functions for price comparison and notifications

def CompareProductPrices(request, crop_name):
    """
    Compare prices of the same crop from different farmers
    and show the lowest price option
    """
    if request.method == 'GET':
        try:
            con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='cropinfo', charset='utf8')
            with con:
                cur = con.cursor()
                cur.execute("""
                    SELECT fp.product_id, fp.farmer_username, s.contact_no, s.email,
                           fp.crop_name, fp.variety, fp.quantity, fp.unit, 
                           fp.selling_price, fp.predicted_price, fp.district, 
                           DATE_FORMAT(fp.listing_date, '%%Y-%%m-%%d') as listing_date,
                           (fp.predicted_price - fp.selling_price) as price_difference
                    FROM farmer_products fp
                    LEFT JOIN signup s ON fp.farmer_username = s.username
                    WHERE fp.status='available' AND fp.crop_name=%s
                    ORDER BY fp.selling_price ASC, fp.listing_date DESC
                """, (crop_name,))
                products = cur.fetchall()
                
                # Get the lowest price farmer
                lowest_price_product = products[0] if products else None
                
                # Format output for display
                output = '<h3 class="text-center mb-4">Price Comparison for ' + crop_name + '</h3>'
                output += '<table class="table table-bordered table-hover">'
                output += '<thead><tr><th>Farmer</th><th>Contact</th><th>Quantity</th><th>Selling Price</th>'
                output += '<th>Predicted Price</th><th>District</th><th>Savings</th><th>Action</th></tr></thead><tbody>'
                
                for product in products:
                    product_id = product[0]
                    farmer = product[1]
                    contact = product[2] if product[2] else 'N/A'
                    quantity = product[6]
                    unit = product[7]
                    selling_price = product[8]
                    predicted_price = product[9] if product[9] else 0
                    district = product[10]
                    savings = predicted_price - selling_price if predicted_price > selling_price else 0
                    
                    highlight = 'class="table-success"' if product == lowest_price_product else ''
                    
                    output += f'<tr {highlight}>'
                    output += f'<td>{farmer}</td>'
                    output += f'<td>{contact}</td>'
                    output += f'<td>{quantity} {unit}</td>'
                    output += f'<td>₹{selling_price}/{unit}</td>'
                    output += f'<td>₹{round(predicted_price, 2)}</td>'
                    output += f'<td>{district}</td>'
                    output += f'<td>₹{round(savings, 2)}</td>'
                    
                    if product == lowest_price_product:
                        output += f'<td><button onclick="selectLowestPriceFarmer({product_id})" class="btn btn-success btn-sm">Best Price - Select</button></td>'
                    else:
                        output += f'<td><button onclick="selectFarmer({product_id})" class="btn btn-primary btn-sm">Select</button></td>'
                    output += '</tr>'
                
                output += '</tbody></table>'
                
                context = {
                    'comparison_data': output,
                    'crop_name': crop_name,
                }
                return render(request, 'ComparePrices.html', context)
        except Exception as e:
            print("Error comparing prices:", e)
            return HttpResponse("Error comparing prices: " + str(e))


def SendOrderNotification(request, order_id, farmer_username, customer_name):
    """
    Send notification to farmer when customer selects their product
    """
    try:
        con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='cropinfo', charset='utf8')
        with con:
            cur = con.cursor()
            
            # Create notification
            notification_message = f"New order #{order_id} from customer {customer_name}. Please check your orders."
            
            # Check if notifications table exists, if not create it
            cur.execute("""
                CREATE TABLE IF NOT EXISTS farmer_notifications (
                    notification_id INT AUTO_INCREMENT PRIMARY KEY,
                    farmer_username VARCHAR(100),
                    order_id INT,
                    message TEXT,
                    notification_date DATETIME,
                    is_read BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (farmer_username) REFERENCES signup(username),
                    FOREIGN KEY (order_id) REFERENCES customer_orders(order_id)
                )
            """)
            
            from datetime import datetime
            now = datetime.now()
            
            cur.execute("""
                INSERT INTO farmer_notifications (farmer_username, order_id, message, notification_date, is_read)
                VALUES (%s, %s, %s, %s, %s)
            """, (farmer_username, order_id, notification_message, now, False))
            
            con.commit()
            return True
    except Exception as e:
        print("Notification error:", e)
        return False


def GetFarmerNotifications(request):
    """
    Get all notifications for a specific farmer
    """
    if request.method == 'GET':
        if 'username' not in request.session:
            return HttpResponse("Please login first")
        
        farmer_username = request.session.get('username')
        
        try:
            con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='cropinfo', charset='utf8')
            with con:
                cur = con.cursor()
                
                # Create table if not exists
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS farmer_notifications (
                        notification_id INT AUTO_INCREMENT PRIMARY KEY,
                        farmer_username VARCHAR(100),
                        order_id INT,
                        message TEXT,
                        notification_date DATETIME,
                        is_read BOOLEAN DEFAULT FALSE,
                        FOREIGN KEY (farmer_username) REFERENCES signup(username),
                        FOREIGN KEY (order_id) REFERENCES customer_orders(order_id)
                    )
                """)
                
                # Get unread notifications count
                cur.execute("""
                    SELECT COUNT(*) FROM farmer_notifications 
                    WHERE farmer_username=%s AND is_read=FALSE
                """, (farmer_username,))
                unread_count = cur.fetchone()[0]
                
                # Get all notifications
                cur.execute("""
                    SELECT notification_id, order_id, message, notification_date, is_read
                    FROM farmer_notifications 
                    WHERE farmer_username=%s 
                    ORDER BY notification_date DESC
                    LIMIT 20
                """, (farmer_username,))
                notifications = cur.fetchall()
            
            # Format notifications for display
            notification_html = '<div class="notifications-container">'
            notification_html += f'<h3>Notifications <span class="badge badge-danger">{unread_count} New</span></h3>'
            
            if notifications:
                notification_html += '<ul class="list-group">'
                for notif in notifications:
                    read_class = 'unread' if not notif[4] else ''
                    notification_html += f'''
                        <li class="list-group-item {read_class}">
                            <small class="text-muted">{notif[3]}</small><br>
                            {notif[2]}
                            <br>
                            <button onclick="markAsRead({notif[0]})" class="btn btn-sm btn-info">Mark as Read</button>
                        </li>
                    '''
                notification_html += '</ul>'
            else:
                notification_html += '<p>No notifications</p>'
            
            notification_html += '</div>'
            
            context = {
                'notifications': notification_html,
                'unread_count': unread_count
            }
            return render(request, 'FarmerNotifications.html', context)
            
        except Exception as e:
            return HttpResponse("Error loading notifications: " + str(e))


def MarkNotificationAsRead(request):
    """
    Mark a notification as read
    """
    if request.method == 'POST':
        notification_id = request.POST.get('notification_id')
        
        try:
            con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='cropinfo', charset='utf8')
            with con:
                cur = con.cursor()
                cur.execute("UPDATE farmer_notifications SET is_read=TRUE WHERE notification_id=%s", (notification_id,))
                con.commit()
            return HttpResponse("Notification marked as read")
        except Exception as e:
            return HttpResponse("Error: " + str(e))


def PlaceOrderAction(request):
    if request.method == 'POST':
        if 'customer_email' not in request.session:
            return HttpResponse("Please login first")

        product_id = request.POST.get('product_id')
        quantity = float(request.POST.get('quantity'))  # Convert to float
        customer_name = request.POST.get('customer_name')
        customer_contact = request.POST.get('customer_contact')
        customer_email = request.POST.get('customer_email')
        customer_address = request.POST.get('customer_address')
        delivery_date = request.POST.get('delivery_date')

        try:
            con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='cropinfo', charset='utf8')
            with con:
                cur = con.cursor()

                # Get product details
                cur.execute("""SELECT farmer_username, crop_name, selling_price, unit, quantity 
                              FROM farmer_products WHERE product_id=%s AND status='available'""", (product_id,))
                product = cur.fetchone()

                if not product:
                    return HttpResponse("Product not available")

                if quantity > float(product[4]):  # Convert to float for comparison
                    return HttpResponse("Requested quantity exceeds available stock")

                farmer_username = product[0]
                crop_name = product[1]
                price_per_unit = float(product[2])  # Convert Decimal to float
                unit = product[3]
                total_amount = quantity * price_per_unit  # Now both are float

                from datetime import date, datetime
                today = date.today()

                # Insert order
                cur.execute("""INSERT INTO customer_orders 
                              (customer_name, customer_contact, customer_email, customer_address, 
                               product_id, farmer_username, crop_name, quantity, unit, 
                               price_per_unit, total_amount, order_date, delivery_date, order_status, payment_status) 
                              VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending', 'pending')""",
                          (customer_name, customer_contact, customer_email, customer_address,
                           product_id, farmer_username, crop_name, quantity, unit,
                           price_per_unit, total_amount, today, delivery_date))
                
                order_id = cur.lastrowid

                # Update product quantity
                new_quantity = float(product[4]) - quantity  # Convert to float
                if new_quantity <= 0:
                    cur.execute("UPDATE farmer_products SET status='sold', quantity=%s WHERE product_id=%s",
                              (0, product_id))  # Set to 0 instead of new_quantity
                else:
                    cur.execute("UPDATE farmer_products SET quantity=%s WHERE product_id=%s",
                              (new_quantity, product_id))

                con.commit()
                
                # Send notification to farmer
                try:
                    SendOrderNotification(request, order_id, farmer_username, customer_name)
                except Exception as e:
                    print("Notification error:", e)  # Log but don't fail the order
                
                return HttpResponse(f"Order placed successfully! Order ID: {order_id}. Notification sent to farmer.")

        except Exception as e:
            print("Order placement error:", e)  # Log the error for debugging
            return HttpResponse("Error placing order: " + str(e))


# New view to get best price for a crop
def GetBestPriceForCrop(request, crop_name):
    """
    Get the best (lowest) price for a specific crop
    """
    try:
        con = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='cropinfo', charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("""
                SELECT farmer_username, selling_price, quantity, unit, district
                FROM farmer_products 
                WHERE status='available' AND crop_name=%s 
                ORDER BY selling_price ASC 
                LIMIT 1
            """, (crop_name,))
            best_price = cur.fetchone()
            
        if best_price:
            return HttpResponse(f"Best price for {crop_name}: ₹{best_price[1]}/{best_price[3]} by {best_price[0]} from {best_price[4]}")
        else:
            return HttpResponse(f"No available products found for {crop_name}")
    except Exception as e:
        return HttpResponse("Error: " + str(e))

def AddSchemeAction(request):
    if request.method == 'POST':
        sid = request.POST.get('t1', '')
        name = request.POST.get('t2', '')
        desc = request.POST.get('t3', '')
        document = request.POST.get('t4', '')
        start = request.POST.get('t5', '')
        end = request.POST.get('t6', '')

        output = "none"
        try:
            db_connection = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='cropinfo', charset='utf8')
            db_cursor = db_connection.cursor()
            student_sql_query = "INSERT INTO addscheme(scheme_id,scheme_name,description,document,start_date,end_date) VALUES(%s,%s,%s,%s,%s,%s)"
            db_cursor.execute(student_sql_query, (sid, name, desc, document, start, end))
            db_connection.commit()
            print(db_cursor.rowcount, "Record Inserted")
            if db_cursor.rowcount == 1:
                output = 'New Scheme details added'
        except Exception as e:
            output = 'Error: ' + str(e)
            
        context = {'data': output}
        return render(request, 'AddScheme.html', context)