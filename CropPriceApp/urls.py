from django.urls import path
from . import views

urlpatterns = [
    # Add this line for the root URL
    path('', views.index, name='home'),  # ← ADD THIS LINE
    
    path("index.html", views.index, name="index"),
    path("index", views.index, name="index_no_html"),  # Add this line
    path("AdminLogin.html", views.AdminLogin, name="AdminLogin"),
    path("AdminLoginAction", views.AdminLoginAction, name="AdminLoginAction"),
    path("FarmerLogin.html", views.FarmerLogin, name="FarmerLogin"),
    path("FarmerLoginAction", views.FarmerLoginAction, name="FarmerLoginAction"),
    path("Signup.html", views.Signup, name="Signup"),
    path("SignupAction", views.SignupAction, name="SignupAction"),	    
    path("AddScheme.html", views.AddScheme, name="AddScheme"),
    path("AddSchemeAction", views.AddSchemeAction, name="AddSchemeAction"),	 
    path("PredictCropPrices.html", views.PredictCropPrices, name="PredictCropPrices"),
    path("PredictCropPricesAction", views.PredictCropPricesAction, name="PredictCropPricesAction"),	 
    path("ViewSchemes", views.ViewSchemes, name="ViewSchemes"),
    path("ComparePrices/<str:crop_name>", views.CompareProductPrices, name="ComparePrices"),
    path("GetFarmerNotifications", views.GetFarmerNotifications, name="GetFarmerNotifications"),
    path("MarkNotificationAsRead", views.MarkNotificationAsRead, name="MarkNotificationAsRead"),
    path("GetBestPriceForCrop/<str:crop_name>", views.GetBestPriceForCrop, name="GetBestPriceForCrop"),
    
    # Bidding System URLs
    path('FarmerBiddingDashboard/', views.FarmerBiddingDashboard, name='FarmerBiddingDashboard'),
    path('StartNegotiation/', views.StartNegotiation, name='StartNegotiation'),
    path('ViewNegotiationDetails/<int:negotiation_id>/', views.ViewNegotiationDetails, name='ViewNegotiationDetails'),
    path('FarmerCounterOffer/', views.FarmerCounterOffer, name='FarmerCounterOffer'),
    path('AcceptNegotiation/', views.AcceptNegotiation, name='AcceptNegotiation'),
    path('RejectNegotiation/', views.RejectNegotiation, name='RejectNegotiation'),
    path('CustomerBiddingDashboard/', views.CustomerBiddingDashboard, name='CustomerBiddingDashboard'),
    path('RequestNegotiation/', views.RequestNegotiation, name='RequestNegotiation'),
    path('CustomerCounterOffer/', views.CustomerCounterOffer, name='CustomerCounterOffer'),
    path('AcceptFarmerOffer/', views.AcceptFarmerOffer, name='AcceptFarmerOffer'),
    path('CancelNegotiation/', views.CancelNegotiation, name='CancelNegotiation'),
    path('GetCustomerNotifications/', views.GetCustomerNotifications, name='GetCustomerNotifications'),
    path('CompleteTransaction/<int:contract_id>/', views.CompleteTransaction, name='CompleteTransaction'),
    # Logout URLs - Add these lines
    path("logout/", views.logout_view, name="logout"),
    path("FarmerLogout/", views.farmer_logout, name="FarmerLogout"),
    path("CustomerLogout/", views.customer_logout, name="CustomerLogout"),
    path("AdminLogout/", views.admin_logout, name="AdminLogout"),
    # New URLs for farmer products
    path("FarmerDashboard", views.FarmerDashboard, name="FarmerDashboard"),
    path("AddProduct.html", views.AddProduct, name="AddProduct"),
    path("AddProductAction", views.AddProductAction, name="AddProductAction"),
    path("MyProducts", views.MyProducts, name="MyProducts"),
    path("UpdateProductStatus", views.UpdateProductStatus, name="UpdateProductStatus"),
    path("FarmerOrders", views.FarmerOrders, name="FarmerOrders"),
    path("UpdateOrderStatus", views.UpdateOrderStatus, name="UpdateOrderStatus"),
    
    # New URLs for customers
    path("CustomerSignup.html", views.CustomerSignup, name="CustomerSignup"),
    path("CustomerSignupAction", views.CustomerSignupAction, name="CustomerSignupAction"),
    path("CustomerLogin.html", views.CustomerLogin, name="CustomerLogin"),
    path("CustomerLoginAction", views.CustomerLoginAction, name="CustomerLoginAction"),
    path("CustomerDashboard", views.CustomerDashboard, name="CustomerDashboard"),
    path("AvailableProducts", views.AvailableProducts, name="AvailableProducts"),
    path("ProductDetails/<int:product_id>", views.ProductDetails, name="ProductDetails"),
    path("PlaceOrderAction", views.PlaceOrderAction, name="PlaceOrderAction"),
    path("MyOrders", views.MyOrders, name="MyOrders"),
    path("CancelOrder", views.CancelOrder, name="CancelOrder"),
]