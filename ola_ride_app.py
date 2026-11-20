
import streamlit as st
import pandas as pd
import mysql.connector

# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="OLA Ride Insights",
    page_icon="🚕",
    layout="wide"
)

st.title("🚕 OLA RIDE INSIGHTS")
st.subheader("Ride-Sharing & Mobility Analytics")

st.write(
    "An interactive data analytics application "
    "for exploring OLA ride booking information."
)

# ---------------- DATABASE CONNECTION ----------------

def connect_database():
    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="",
        database="OLA_Cleaned_Data"
    )

@st.cache_data(ttl=300)
def load_data():
    connection = connect_database()

    try:
        data = pd.read_sql_query(
            "SELECT * FROM ola_rides",
            connection
        )
        return data

    finally:
        connection.close()

try:
    df = load_data()
    st.success("MySQL Database Connected Successfully!")

except Exception as e:
    st.error(f"Database Connection Error: {e}")
    st.stop()

# ---------------- INTERACTIVE FILTERS ----------------

st.sidebar.header("Interactive Filters")

filtered_df = df.copy()

if "Vehicle_Type" in df.columns:
    vehicle_options = sorted(
        df["Vehicle_Type"].dropna().unique()
    )

    selected_vehicles = st.sidebar.multiselect(
        "Vehicle Type",
        vehicle_options
    )

    if selected_vehicles:
        filtered_df = filtered_df[
            filtered_df["Vehicle_Type"].isin(selected_vehicles)
        ]

if "Booking_Status" in df.columns:
    status_options = sorted(
        df["Booking_Status"].dropna().unique()
    )

    selected_status = st.sidebar.multiselect(
        "Booking Status",
        status_options
    )

    if selected_status:
        filtered_df = filtered_df[
            filtered_df["Booking_Status"].isin(selected_status)
        ]

if "Payment_Method" in df.columns:
    payment_options = sorted(
        df["Payment_Method"].dropna().unique()
    )

    selected_payments = st.sidebar.multiselect(
        "Payment Method",
        payment_options
    )

    if selected_payments:
        filtered_df = filtered_df[
            filtered_df["Payment_Method"].isin(selected_payments)
        ]

# ---------------- KEY PERFORMANCE INDICATORS ----------------

st.header("Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

total_rides = len(filtered_df)

successful_rides = (
    (filtered_df["Booking_Status"] == "Success").sum()
    if "Booking_Status" in filtered_df.columns else 0
)

total_booking_value = (
    filtered_df["Booking_Value"].sum()
    if "Booking_Value" in filtered_df.columns else 0
)

average_distance = (
    filtered_df["Ride_Distance"].mean()
    if "Ride_Distance" in filtered_df.columns else 0
)

col1.metric("Total Rides", f"{total_rides:,}")
col2.metric("Successful Rides", f"{successful_rides:,}")
col3.metric("Total Booking Value", f"₹{total_booking_value:,.2f}")
col4.metric("Average Ride Distance", f"{average_distance:.2f} km")

# ---------------- SEARCH RIDE RECORDS ----------------

st.header("Search Ride Records")

search_value = st.text_input(
    "Search by Booking ID or Customer ID"
)

search_df = filtered_df.copy()

if search_value:
    booking_match = search_df["Booking_ID"].astype(str).str.contains(
        search_value, case=False, na=False
    )

    customer_match = search_df["Customer_ID"].astype(str).str.contains(
        search_value, case=False, na=False
    )

    search_df = search_df[
        booking_match | customer_match
    ]

st.dataframe(
    search_df,
    use_container_width=True
)

st.caption(f"Total Records Displayed: {len(search_df):,}")

# ---------------- SQL QUERY ANALYSIS ----------------

st.header("SQL Query Analysis")

queries = {

    "1. Successful Bookings": """
        SELECT *
        FROM ola_rides
        WHERE Booking_Status = 'Success'
    """,

    "2. Average Ride Distance by Vehicle Type": """
        SELECT
            Vehicle_Type,
            AVG(Ride_Distance) AS Average_Ride_Distance
        FROM ola_rides
        GROUP BY Vehicle_Type
    """,

    "3. Total Customer Cancellations": """
        SELECT
            COUNT(*) AS Total_Customer_Cancellations
        FROM ola_rides
        WHERE Booking_Status = 'Canceled by Customer'
    """,

    "4. Top 5 Customers by Number of Rides": """
        SELECT
            Customer_ID,
            COUNT(Booking_ID) AS Total_Rides
        FROM ola_rides
        GROUP BY Customer_ID
        ORDER BY Total_Rides DESC
        LIMIT 5
    """,

    "5. Driver Cancellations": """
        SELECT
            COUNT(*) AS Total_Driver_Cancellations
        FROM ola_rides
        WHERE Canceled_Rides_by_Driver =
        'Personal & Car related issue'
    """,

    "6. Prime Sedan Driver Ratings": """
        SELECT
            MAX(Driver_Ratings) AS Maximum_Rating,
            MIN(Driver_Ratings) AS Minimum_Rating
        FROM ola_rides
        WHERE Vehicle_Type = 'Prime Sedan'
    """,

    "7. Rides Paid Using UPI": """
        SELECT *
        FROM ola_rides
        WHERE Payment_Method = 'UPI'
    """,

    "8. Average Customer Rating by Vehicle Type": """
        SELECT
            Vehicle_Type,
            AVG(Customer_Rating) AS Average_Customer_Rating
        FROM ola_rides
        GROUP BY Vehicle_Type
    """,

    "9. Total Booking Value of Successful Rides": """
        SELECT
            SUM(Booking_Value) AS Total_Booking_Value
        FROM ola_rides
        WHERE Booking_Status = 'Success'
    """,

    "10. Incomplete Rides with Reasons": """
        SELECT
            Booking_ID,
            Incomplete_Rides,
            Incomplete_Rides_Reason
        FROM ola_rides
        WHERE Incomplete_Rides = 'Yes'
    """
}

selected_query = st.selectbox(
    "Select SQL Query",
    list(queries.keys())
)

if st.button("Run SQL Query"):

    connection = None

    try:
        connection = connect_database()

        result = pd.read_sql_query(
            queries[selected_query],
            connection
        )

        st.subheader("SQL Query Results")

        st.dataframe(
            result,
            use_container_width=True
        )

        st.success("SQL Query Executed Successfully!")

    except Exception as e:
        st.error(f"SQL Query Error: {e}")

    finally:
        if connection and connection.is_connected():
            connection.close()

# ---------------- FOOTER ----------------

st.divider()

st.caption(
    "OLA Ride Insights | Data Analytics Project"
)
