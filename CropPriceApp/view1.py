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