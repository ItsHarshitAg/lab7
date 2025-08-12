"""
Lab 6: Hotel Management and Booking System - Interactive Web Application using Streamlit
Author: Student Name
Domain: Hotel Management System

This application demonstrates:
- Interactive web interface using Streamlit
- Dynamic data visualization with charts and graphs
- Real-time booking management
- Customer feedback system
- Room availability tracking
- Revenue analytics dashboard
- Responsive design with multiple pages
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import re
import json
import os
from typing import Dict, List, Any
import numpy as np

# Configure the Streamlit page
st.set_page_config(
    page_title="🏨 Luxury Hotel Management System",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size: 1.5rem;
        color: #A23B72;
        margin: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2E86AB 0%, #A23B72 100%);
    }
</style>
""", unsafe_allow_html=True)

# Data file paths
DATA_DIR = "hotel_data"
BOOKINGS_FILE = os.path.join(DATA_DIR, "bookings.json")
CUSTOMERS_FILE = os.path.join(DATA_DIR, "customers.json")
FEEDBACK_FILE = os.path.join(DATA_DIR, "feedback.json")
ROOMS_FILE = os.path.join(DATA_DIR, "rooms.json")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

class HotelDataManager:
    """Manages all hotel data operations"""
    
    @staticmethod
    def load_data(file_path: str) -> List[Dict]:
        """Load data from JSON file"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            st.error(f"Error loading data: {e}")
        return []
    
    @staticmethod
    def save_data(file_path: str, data: List[Dict]) -> None:
        """Save data to JSON file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            st.error(f"Error saving data: {e}")
    
    @staticmethod
    def initialize_rooms():
        """Initialize room data if not exists"""
        rooms = HotelDataManager.load_data(ROOMS_FILE)
        if not rooms:
            default_rooms = [
                {"room_number": "101", "room_type": "Standard", "price": 2500, "capacity": 2, "status": "Available"},
                {"room_number": "102", "room_type": "Standard", "price": 2500, "capacity": 2, "status": "Available"},
                {"room_number": "201", "room_type": "Deluxe", "price": 4000, "capacity": 3, "status": "Available"},
                {"room_number": "202", "room_type": "Deluxe", "price": 4000, "capacity": 3, "status": "Available"},
                {"room_number": "301", "room_type": "Suite", "price": 7500, "capacity": 4, "status": "Available"},
                {"room_number": "302", "room_type": "Suite", "price": 7500, "capacity": 4, "status": "Available"},
                {"room_number": "401", "room_type": "Presidential", "price": 15000, "capacity": 6, "status": "Available"},
            ]
            HotelDataManager.save_data(ROOMS_FILE, default_rooms)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    HotelDataManager.initialize_rooms()

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """Validate Indian phone number"""
    pattern = r'^(\+91[-\s]?)?[6-9]\d{9}$'
    return re.match(pattern, phone.strip()) is not None

def calculate_booking_amount(room_type: str, nights: int, guests: int) -> float:
    """Calculate total booking amount"""
    base_prices = {
        "Standard": 2500,
        "Deluxe": 4000,
        "Suite": 7500,
        "Presidential": 15000
    }
    
    base_price = base_prices.get(room_type, 2500)
    
    # Additional charges
    extra_guest_charge = max(0, guests - 2) * 500 * nights
    
    # Discounts for longer stays
    if nights >= 7:
        discount = 0.15
    elif nights >= 3:
        discount = 0.10
    else:
        discount = 0
    
    total = (base_price * nights) + extra_guest_charge
    total = total * (1 - discount)
    
    return round(total, 2)

def main_dashboard():
    """Main dashboard with overview"""
    st.markdown('<h1 class="main-header">🏨 Luxury Hotel Management System</h1>', unsafe_allow_html=True)
    
    # Load data
    bookings = HotelDataManager.load_data(BOOKINGS_FILE)
    customers = HotelDataManager.load_data(CUSTOMERS_FILE)
    feedback = HotelDataManager.load_data(FEEDBACK_FILE)
    rooms = HotelDataManager.load_data(ROOMS_FILE)
    
    # Key Metrics
    st.markdown('<h2 class="sub-header">📊 Key Metrics</h2>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_bookings = len(bookings)
        st.metric("Total Bookings", total_bookings, delta="📈")
    
    with col2:
        total_revenue = sum(booking.get('total_amount', 0) for booking in bookings)
        st.metric("Total Revenue", f"₹{total_revenue:,.2f}", delta="💰")
    
    with col3:
        occupied_rooms = len([r for r in rooms if r['status'] == 'Occupied'])
        occupancy_rate = (occupied_rooms / len(rooms)) * 100 if rooms else 0
        st.metric("Occupancy Rate", f"{occupancy_rate:.1f}%", delta="🏠")
    
    with col4:
        total_customers = len(customers)
        st.metric("Total Customers", total_customers, delta="👥")
    
    # Charts
    if bookings:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<h3 class="sub-header">Room Type Bookings</h3>', unsafe_allow_html=True)
            df_bookings = pd.DataFrame(bookings)
            room_counts = df_bookings['room_type'].value_counts()
            fig = px.pie(values=room_counts.values, names=room_counts.index, 
                        title="Bookings by Room Type")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown('<h3 class="sub-header">Monthly Revenue Trend</h3>', unsafe_allow_html=True)
            df_bookings['check_in'] = pd.to_datetime(df_bookings['check_in'])
            monthly_revenue = df_bookings.groupby(df_bookings['check_in'].dt.to_period('M'))['total_amount'].sum()
            fig = px.line(x=monthly_revenue.index.astype(str), y=monthly_revenue.values,
                         title="Monthly Revenue", labels={'x': 'Month', 'y': 'Revenue (₹)'})
            st.plotly_chart(fig, use_container_width=True)
    
    # Recent Bookings
    if bookings:
        st.markdown('<h3 class="sub-header">Recent Bookings</h3>', unsafe_allow_html=True)
        recent_bookings = sorted(bookings, key=lambda x: x.get('booking_date', ''), reverse=True)[:5]
        df_recent = pd.DataFrame(recent_bookings)
        st.dataframe(df_recent[['customer_name', 'room_type', 'check_in', 'check_out', 'total_amount']], 
                    use_container_width=True)

def booking_system():
    """Room booking system"""
    st.markdown('<h1 class="main-header">🛏️ Room Booking System</h1>', unsafe_allow_html=True)
    
    # Load rooms data
    rooms = HotelDataManager.load_data(ROOMS_FILE)
    available_rooms = [r for r in rooms if r['status'] == 'Available']
    
    if not available_rooms:
        st.error("No rooms available for booking!")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<h2 class="sub-header">Make a Reservation</h2>', unsafe_allow_html=True)
        
        with st.form("booking_form"):
            # Customer Information
            st.subheader("Customer Information")
            col_a, col_b = st.columns(2)
            
            with col_a:
                customer_name = st.text_input("Full Name*")
                customer_email = st.text_input("Email Address*")
                customer_phone = st.text_input("Phone Number*")
            
            with col_b:
                customer_address = st.text_area("Address")
                id_proof = st.selectbox("ID Proof Type", 
                                      ["Aadhar Card", "PAN Card", "Driving License", "Passport"])
                id_number = st.text_input("ID Number")
            
            # Booking Details
            st.subheader("Booking Details")
            col_c, col_d = st.columns(2)
            
            with col_c:
                room_type = st.selectbox("Room Type", 
                                       list(set(r['room_type'] for r in available_rooms)))
                guests = st.number_input("Number of Guests", min_value=1, max_value=6, value=2)
                
            with col_d:
                check_in = st.date_input("Check-in Date", min_value=date.today())
                check_out = st.date_input("Check-out Date", 
                                        min_value=check_in + timedelta(days=1))
            
            special_requests = st.text_area("Special Requests (Optional)")
            
            # Calculate and display price
            if check_in and check_out and room_type:
                nights = (check_out - check_in).days
                if nights > 0:
                    total_amount = calculate_booking_amount(room_type, nights, guests)
                    st.info(f"Total Amount: ₹{total_amount:,.2f} for {nights} night(s)")
            
            submitted = st.form_submit_button("Book Room", type="primary")
            
            if submitted:
                # Validation
                errors = []
                
                if not customer_name.strip():
                    errors.append("Customer name is required")
                if not customer_email.strip() or not validate_email(customer_email):
                    errors.append("Valid email address is required")
                if not customer_phone.strip() or not validate_phone(customer_phone):
                    errors.append("Valid phone number is required")
                if check_out <= check_in:
                    errors.append("Check-out date must be after check-in date")
                
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    # Find available room of selected type
                    selected_room = next((r for r in available_rooms if r['room_type'] == room_type), None)
                    
                    if selected_room:
                        # Create booking
                        booking = {
                            "booking_id": f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}",
                            "customer_name": customer_name,
                            "customer_email": customer_email,
                            "customer_phone": customer_phone,
                            "customer_address": customer_address,
                            "id_proof": id_proof,
                            "id_number": id_number,
                            "room_number": selected_room['room_number'],
                            "room_type": room_type,
                            "guests": guests,
                            "check_in": str(check_in),
                            "check_out": str(check_out),
                            "nights": nights,
                            "total_amount": total_amount,
                            "special_requests": special_requests,
                            "booking_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "status": "Confirmed"
                        }
                        
                        # Save booking
                        bookings = HotelDataManager.load_data(BOOKINGS_FILE)
                        bookings.append(booking)
                        HotelDataManager.save_data(BOOKINGS_FILE, bookings)
                        
                        # Update room status
                        for room in rooms:
                            if room['room_number'] == selected_room['room_number']:
                                room['status'] = 'Occupied'
                        HotelDataManager.save_data(ROOMS_FILE, rooms)
                        
                        # Save customer if new
                        customers = HotelDataManager.load_data(CUSTOMERS_FILE)
                        if not any(c['email'] == customer_email for c in customers):
                            customer = {
                                "name": customer_name,
                                "email": customer_email,
                                "phone": customer_phone,
                                "address": customer_address,
                                "registration_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            customers.append(customer)
                            HotelDataManager.save_data(CUSTOMERS_FILE, customers)
                        
                        st.success(f"✅ Booking confirmed! Booking ID: {booking['booking_id']}")
                        st.balloons()
    
    with col2:
        st.markdown('<h2 class="sub-header">Available Rooms</h2>', unsafe_allow_html=True)
        
        for room_type in set(r['room_type'] for r in available_rooms):
            rooms_of_type = [r for r in available_rooms if r['room_type'] == room_type]
            st.markdown(f"**{room_type}**")
            st.write(f"Available: {len(rooms_of_type)} rooms")
            st.write(f"Price: ₹{rooms_of_type[0]['price']}/night")
            st.write(f"Capacity: {rooms_of_type[0]['capacity']} guests")
            st.markdown("---")

def room_management():
    """Room management interface"""
    st.markdown('<h1 class="main-header">🏠 Room Management</h1>', unsafe_allow_html=True)
    
    # Load data
    rooms = HotelDataManager.load_data(ROOMS_FILE)
    bookings = HotelDataManager.load_data(BOOKINGS_FILE)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<h2 class="sub-header">Room Status Overview</h2>', unsafe_allow_html=True)
        
        # Room status table
        df_rooms = pd.DataFrame(rooms)
        st.dataframe(df_rooms, use_container_width=True)
        
        # Room status actions
        st.markdown('<h3 class="sub-header">Update Room Status</h3>', unsafe_allow_html=True)
        
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            room_to_update = st.selectbox("Select Room", 
                                        options=[r['room_number'] for r in rooms])
        
        with col_b:
            new_status = st.selectbox("New Status", 
                                    ["Available", "Occupied", "Maintenance", "Cleaning"])
        
        with col_c:
            if st.button("Update Status"):
                for room in rooms:
                    if room['room_number'] == room_to_update:
                        room['status'] = new_status
                        break
                HotelDataManager.save_data(ROOMS_FILE, rooms)
                st.success(f"Room {room_to_update} status updated to {new_status}")
                st.rerun()
    
    with col2:
        st.markdown('<h2 class="sub-header">Room Statistics</h2>', unsafe_allow_html=True)
        
        # Status distribution
        status_counts = pd.Series([r['status'] for r in rooms]).value_counts()
        fig = px.pie(values=status_counts.values, names=status_counts.index,
                    title="Room Status Distribution")
        st.plotly_chart(fig, use_container_width=True)
        
        # Room type distribution
        type_counts = pd.Series([r['room_type'] for r in rooms]).value_counts()
        st.write("**Room Types:**")
        for room_type, count in type_counts.items():
            st.write(f"• {room_type}: {count} rooms")

def customer_feedback():
    """Customer feedback system"""
    st.markdown('<h1 class="main-header">💬 Customer Feedback</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<h2 class="sub-header">Submit Feedback</h2>', unsafe_allow_html=True)
        
        with st.form("feedback_form"):
            customer_name = st.text_input("Your Name*")
            customer_email = st.text_input("Email Address*")
            booking_id = st.text_input("Booking ID (Optional)")
            
            rating = st.select_slider("Overall Rating", 
                                    options=[1, 2, 3, 4, 5],
                                    value=5,
                                    format_func=lambda x: "⭐" * x)
            
            service_areas = st.multiselect("Rate our services:",
                                         ["Room Quality", "Staff Behavior", "Food Service", 
                                          "Cleanliness", "Amenities", "Check-in/Check-out"])
            
            feedback_text = st.text_area("Your Feedback*", height=100)
            suggestions = st.text_area("Suggestions for Improvement", height=80)
            
            submitted = st.form_submit_button("Submit Feedback", type="primary")
            
            if submitted:
                if not customer_name.strip():
                    st.error("Name is required")
                elif not customer_email.strip() or not validate_email(customer_email):
                    st.error("Valid email is required")
                elif not feedback_text.strip():
                    st.error("Feedback cannot be empty")
                else:
                    feedback_entry = {
                        "feedback_id": f"FB{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        "customer_name": customer_name,
                        "customer_email": customer_email,
                        "booking_id": booking_id,
                        "rating": rating,
                        "service_areas": service_areas,
                        "feedback": feedback_text,
                        "suggestions": suggestions,
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    feedback_data = HotelDataManager.load_data(FEEDBACK_FILE)
                    feedback_data.append(feedback_entry)
                    HotelDataManager.save_data(FEEDBACK_FILE, feedback_data)
                    
                    st.success("Thank you for your feedback! 🙏")
                    st.balloons()
    
    with col2:
        st.markdown('<h2 class="sub-header">Recent Feedback</h2>', unsafe_allow_html=True)
        
        feedback_data = HotelDataManager.load_data(FEEDBACK_FILE)
        
        if feedback_data:
            # Feedback analytics
            ratings = [f['rating'] for f in feedback_data]
            avg_rating = sum(ratings) / len(ratings)
            st.metric("Average Rating", f"{avg_rating:.1f} ⭐")
            
            # Recent feedback
            recent_feedback = sorted(feedback_data, key=lambda x: x['date'], reverse=True)[:3]
            
            for fb in recent_feedback:
                with st.expander(f"{fb['customer_name']} - {'⭐' * fb['rating']}"):
                    st.write(f"**Date:** {fb['date']}")
                    st.write(f"**Feedback:** {fb['feedback']}")
                    if fb['suggestions']:
                        st.write(f"**Suggestions:** {fb['suggestions']}")
        else:
            st.info("No feedback received yet.")

def analytics_dashboard():
    """Analytics and reporting dashboard"""
    st.markdown('<h1 class="main-header">📈 Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    bookings = HotelDataManager.load_data(BOOKINGS_FILE)
    feedback_data = HotelDataManager.load_data(FEEDBACK_FILE)
    rooms = HotelDataManager.load_data(ROOMS_FILE)
    
    if not bookings:
        st.warning("No booking data available for analytics.")
        return
    
    # Convert to DataFrame
    df_bookings = pd.DataFrame(bookings)
    df_bookings['check_in'] = pd.to_datetime(df_bookings['check_in'])
    df_bookings['check_out'] = pd.to_datetime(df_bookings['check_out'])
    df_bookings['booking_date'] = pd.to_datetime(df_bookings['booking_date'])
    
    # Time period filter
    col1, col2, col3 = st.columns(3)
    
    with col1:
        start_date = st.date_input("Start Date", 
                                 value=df_bookings['check_in'].min().date())
    with col2:
        end_date = st.date_input("End Date",
                               value=df_bookings['check_in'].max().date())
    with col3:
        room_type_filter = st.multiselect("Room Types",
                                        options=df_bookings['room_type'].unique(),
                                        default=df_bookings['room_type'].unique())
    
    # Filter data
    mask = (
        (df_bookings['check_in'].dt.date >= start_date) &
        (df_bookings['check_in'].dt.date <= end_date) &
        (df_bookings['room_type'].isin(room_type_filter))
    )
    filtered_df = df_bookings[mask]
    
    if filtered_df.empty:
        st.warning("No data available for the selected filters.")
        return
    
    # Key metrics for filtered data
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Bookings", len(filtered_df))
    with col2:
        total_revenue = filtered_df['total_amount'].sum()
        st.metric("Total Revenue", f"₹{total_revenue:,.2f}")
    with col3:
        avg_booking_value = filtered_df['total_amount'].mean()
        st.metric("Avg. Booking Value", f"₹{avg_booking_value:,.2f}")
    with col4:
        avg_nights = filtered_df['nights'].mean()
        st.metric("Avg. Stay Duration", f"{avg_nights:.1f} nights")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Revenue trend
        st.subheader("Revenue Trend")
        daily_revenue = filtered_df.groupby(filtered_df['check_in'].dt.date)['total_amount'].sum()
        fig = px.line(x=daily_revenue.index, y=daily_revenue.values,
                     title="Daily Revenue", labels={'x': 'Date', 'y': 'Revenue (₹)'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Booking distribution by room type
        st.subheader("Bookings by Room Type")
        room_type_counts = filtered_df['room_type'].value_counts()
        fig = px.bar(x=room_type_counts.index, y=room_type_counts.values,
                    title="Bookings by Room Type", labels={'x': 'Room Type', 'y': 'Bookings'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Additional analytics
    col1, col2 = st.columns(2)
    
    with col1:
        # Guest distribution
        st.subheader("Guest Distribution")
        guest_counts = filtered_df['guests'].value_counts().sort_index()
        fig = px.pie(values=guest_counts.values, names=guest_counts.index,
                    title="Distribution by Number of Guests")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Booking duration analysis
        st.subheader("Stay Duration Analysis")
        fig = px.histogram(filtered_df, x='nights', nbins=10,
                          title="Distribution of Stay Duration")
        st.plotly_chart(fig, use_container_width=True)
    
    # Customer feedback analytics
    if feedback_data:
        st.subheader("Customer Satisfaction")
        df_feedback = pd.DataFrame(feedback_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            avg_rating = df_feedback['rating'].mean()
            st.metric("Average Rating", f"{avg_rating:.1f} ⭐")
            
            rating_dist = df_feedback['rating'].value_counts().sort_index()
            fig = px.bar(x=rating_dist.index, y=rating_dist.values,
                        title="Rating Distribution", labels={'x': 'Rating', 'y': 'Count'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Service area feedback
            if any(fb.get('service_areas') for fb in feedback_data):
                all_services = []
                for fb in feedback_data:
                    if fb.get('service_areas'):
                        all_services.extend(fb['service_areas'])
                
                if all_services:
                    service_counts = pd.Series(all_services).value_counts()
                    fig = px.bar(x=service_counts.values, y=service_counts.index,
                                orientation='h', title="Service Area Feedback")
                    st.plotly_chart(fig, use_container_width=True)

def main():
    """Main application function"""
    
    # Sidebar navigation
    st.sidebar.title("🏨 Navigation")
    
    pages = {
        "🏠 Dashboard": main_dashboard,
        "🛏️ Book Room": booking_system,
        "🏠 Room Management": room_management,
        "💬 Feedback": customer_feedback,
        "📈 Analytics": analytics_dashboard
    }
    
    selected_page = st.sidebar.selectbox("Choose a page", list(pages.keys()))
    
    # Hotel information sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🏨 Hotel Information")
    st.sidebar.info("""
    **Luxury Hotel Suite**
    
    📍 123 Premium Street, City Center
    
    📞 +91 98765 43210
    
    ✉️ info@luxuryhotel.com
    
    ⭐ 5-Star Rating
    """)
    
    # Display selected page
    pages[selected_page]()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "© 2025 Luxury Hotel Management System | Built with Streamlit"
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
