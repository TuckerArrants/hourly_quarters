import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(layout='wide')

# ✅ Store username-password pairs
USER_CREDENTIALS = {
    "badboyz": "bangbang",
}

# ✅ Initialize session state for authentication
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None

# ✅ Login form (only shown if not authenticated)
if not st.session_state["authenticated"]:
    st.title("Login to Database")

    # Username and password fields
    username = st.text_input("Username:")
    password = st.text_input("Password:", type="password")

    # Submit button
    if st.button("Login"):
        if username in USER_CREDENTIALS and password == USER_CREDENTIALS[username]:
            st.session_state["authenticated"] = True
            st.session_state["username"] = username  # Store the username
            st.success(f"Welcome, {username}! Redirecting...")
            st.rerun()  # Refresh to load the dashboard
        else:
            st.error("Incorrect username or password. Please try again.")

    # Stop execution if user is not authenticated
    st.stop()

# ✅ If authenticated, show the full app
st.sidebar.success(f"Logged in as: **{st.session_state['username']}**")
st.title("Quartal Database")

# ✅ Logout button in the sidebar
if st.sidebar.button("Logout"):
    st.session_state["authenticated"] = False
    st.session_state["username"] = None
    st.rerun()

# Upload CSV File
url_1h = "https://raw.githubusercontent.com/TuckerArrants/hourly_quarters/refs/heads/main/Merged_Hourly_Quartal_1min_Processed_from_2016.csv"
url_3h = "https://raw.githubusercontent.com/TuckerArrants/hourly_quarters/refs/heads/main/Merged_3H_Quartal_1min_Processed_from_2016.csv"
df_1h = pd.read_csv(url_1h)
df_3h = pd.read_csv(url_3h)
df_1h = df_1h.drop(columns=['Unnamed: 0', 'Unnamed: 0.1'])
df_3h = df_3h.drop(columns=['Unnamed: 0', 'Unnamed: 0.1'])

df_1h["three_hour_start"] = (df_1h["hour"] // 3) * 3

# Now merge the two dataframes on 'date', 'Instrument' (if applicable), and the computed three-hour period.
# Use suffixes to differentiate columns that exist in both dataframes.
merged_tf = pd.merge(
    df_1h,
    df_3h,
    left_on=["date", "Instrument", "three_hour_start"],  # from hourly
    right_on=["date", "Instrument", "start_hour"],         # from three-hour
    how="left",
    suffixes=("_hourly", "_3h")
)

if df_1h is not None:

    ### **Sidebar: Select Instrument and DR Range**
    instrument_options = df_1h['Instrument'].dropna().unique().tolist()
    selected_instrument = st.sidebar.selectbox("Select Instrument", instrument_options)
    hour_options = ['All'] + list(range(0, 24))
    three_hour_options = ['All'] + [0, 3, 6, 9, 12, 15, 18, 21]
    selected_hour = st.sidebar.selectbox("Select Hour", hour_options)
    selected_three_hour = st.sidebar.selectbox("Select 3H Start", three_hour_options)
    day_options = ['All'] + ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    selected_day = st.sidebar.selectbox("Day of Week", day_options)

    # Centered line with four Q-direction dropdowns
    st.markdown("### Hour Filters")
    q_col1, q_col2, q_col3, q_col4, q_col5, q_col6, q_col7 = st.columns([1, 1, 1, 1, 1, 1, 1.5])  # Extra column for centering

    q1_filter = q_col1.radio(
        "Q1",
        options=["All"] + sorted(df_1h["Q1_direction"].dropna().unique().tolist()),
        horizontal=False
    )
    q2_filter = q_col2.radio(
        "Q2",
        options=["All"] + sorted(df_1h["Q2_direction"].dropna().unique().tolist()),
        horizontal=False
    )
    q3_filter = q_col3.radio(
        "Q3",
        options=["All"] + sorted(df_1h["Q3_direction"].dropna().unique().tolist()),
        horizontal=False
    )
    q4_filter = q_col4.radio(
        "Q4",
        options=["All"] + sorted(df_1h["Q4_direction"].dropna().unique().tolist()),
        horizontal=False
    )
    
    prev_hour_filter = q_col5.radio("Prev. Hour Direction", 
                                    options=["All"] + ["Long", "Short", "Neutral"],
                                    horizontal=False)
    orb_filter = q_col6.radio("5m ORB Direction",
                              options=["All"] + sorted(df_1h["ORB_direction"].dropna().unique().tolist()),
                              horizontal=False)
    with q_col7:
        low_filter = st.multiselect(
            "Low Exclusion",
            options=sorted(df_1h["low_bucket"].dropna().unique().tolist())
        )
        high_filter = st.multiselect(
            "High Exclusion",
            options=sorted(df_1h["high_bucket"].dropna().unique().tolist())
        )

    ###  Apply Filters
    filtered_df_1h = df_1h[df_1h['Instrument'] == selected_instrument]
    filtered_df_1h['prev_hour_direction'] = filtered_df_1h['hour_direction'].shift(1)

    # Optional: Apply hour filter (if it's not "All")
    if selected_hour != 'All':
        # Assumes you have a column like 'Hour' as int. If not, adapt accordingly.
        filtered_df_1h = filtered_df_1h[filtered_df_1h['hour'] == selected_hour]

    # Optional: Apply day filter (if it's not "All")
    if selected_day != 'All':
        # Assumes you have a column like 'Day' with string values like 'Monday'
        filtered_df_1h = filtered_df_1h[filtered_df_1h['day_of_week'] == selected_day]

    # Filter by Q directions
    if q1_filter != "All":
        filtered_df_1h = filtered_df_1h[filtered_df_1h['Q1_direction'] == q1_filter]
    if q2_filter != "All":
        filtered_df_1h = filtered_df_1h[filtered_df_1h['Q2_direction'] == q2_filter]
    if q3_filter != "All":
        filtered_df_1h = filtered_df_1h[filtered_df_1h['Q3_direction'] == q3_filter]
    if q4_filter != "All":
        filtered_df_1h = filtered_df_1h[filtered_df_1h['Q4_direction'] == q4_filter]
    if prev_hour_filter != 'All':
        filtered_df_1h = filtered_df_1h[filtered_df_1h['prev_hour_direction'] == prev_hour_filter] 
    if orb_filter != 'All':
        filtered_df_1h = filtered_df_1h[filtered_df_1h['ORB_direction'] == orb_filter] 
    if low_filter:
        filtered_df_1h = filtered_df_1h[~filtered_df_1h['low_bucket'].isin(low_filter)]
    if high_filter:
        filtered_df_1h = filtered_df_1h[~filtered_df_1h['high_bucket'].isin(high_filter)]

    # Calculate probability distributions for "low bucket" and "high bucket"
    low_counts = filtered_df_1h["low_bucket"].value_counts(normalize=True).reset_index()
    low_counts.columns = ["value", "probability"]

    high_counts = filtered_df_1h["high_bucket"].value_counts(normalize=True).reset_index()
    high_counts.columns = ["value", "probability"]

    # Create a bar chart for "low bucket" probabilities with text annotations
    desired_order = ["Q1", "Q2", "Q3", "Q4"]
    fig_low = px.bar(
        low_counts,
        x="value",
        y="probability",
        title="Low of Hour Bucket",
        labels={"value": "Low Bucket", "probability": "Probability"},
        # Format the probability as a percentage (e.g., "12.34%")
        text=low_counts["probability"].apply(lambda x: f"{x:.2%}")
    )
    # Position the text annotations outside the bars
    fig_low.update_traces(textposition="outside")
    fig_low.update_layout(
    xaxis=dict(
        categoryorder='array',
        categoryarray=desired_order
    )
)

    # Create a bar chart for "high bucket" probabilities with text annotations
    fig_high = px.bar(
        high_counts,
        x="value",
        y="probability",
        title="High of Hour Bucket",
        labels={"value": "High Bucket", "probability": "Probability"},
        text=high_counts["probability"].apply(lambda x: f"{x:.2%}")
    )
    fig_high.update_traces(textposition="outside")
    fig_high.update_layout(
    xaxis=dict(
        categoryorder='array',
        categoryarray=desired_order
    )
)

    # Display the two charts side by side using st.columns
    col1, col2 = st.columns(2)
    col1.plotly_chart(fig_low, use_container_width=True)
    col2.plotly_chart(fig_high, use_container_width=True)

# Calculate distribution of hour_direction in the filtered data
# Normalize direction values
filtered_df_1h['hour_direction'] = filtered_df_1h['hour_direction'].str.strip().str.title()

# Recalculate counts
hour_direction_counts = filtered_df_1h['hour_direction'].value_counts().reset_index()
hour_direction_counts.columns = ['direction', 'count']

direction_order = ["Long", "Short", "Neutral"]
direction_colors = {
    "Long": "#2ecc71",       # Green
    "Short": "#e74c3c",     # Red
    "Neutral": "#5d6d7e"   # Gray
}


st.markdown("### Quarter and Hourly Direction")

quartals = ["Q1_direction", "Q2_direction", "Q3_direction", "Q4_direction", "hour_direction"]
quartal_titles = ["Q1 Direction", "Q2 Direction", "Q3 Direction", "Q4 Direction", "Hour Direction"]

q_cols = st.columns(5)

for i, q_col in enumerate(quartals):
    # Normalize and count values
    filtered_df_1h[q_col] = filtered_df_1h[q_col].str.strip().str.title()
    q_counts = filtered_df_1h[q_col].value_counts().reset_index()
    q_counts.columns = ['direction', 'count']

    # Build pie chart
    fig_q = px.pie(
        q_counts,
        names='direction',
        values='count',
        color='direction',
        title=quartal_titles[i],
        hole=0.3,
        category_orders={'direction': direction_order},
        color_discrete_map=direction_colors
    )
    fig_q.update_traces(textinfo='percent+label')
    q_cols[i].plotly_chart(fig_q, use_container_width=True)

st.caption(f"Sample size: {len(filtered_df_1h):,} rows")

if df_3h is not None:

    # Centered line with four Q-direction dropdowns
    st.markdown("### 3H Filters")
    q_col1_3h, q_col2_3h, q_col3_3h, q_col4_3h, q_col5_3h, q_col6_3h, q_col7_3h = st.columns([1, 1, 1, 1, 1, 1, 1.5])  # Extra column for centering

    q1_filter_3h = q_col1_3h.radio(
        "Q1",
        options=["All"] + sorted(df_3h["Q1_direction"].dropna().unique().tolist()),
        horizontal=False,
        key="q1_filter_3h"
    )
    q2_filter_3h = q_col2_3h.radio(
        "Q2",
        options=["All"] + sorted(df_3h["Q2_direction"].dropna().unique().tolist()),
        horizontal=False,
        key="q2_filter_3h"
    )
    q3_filter_3h = q_col3_3h.radio(
        "Q3",
        options=["All"] + sorted(df_3h["Q3_direction"].dropna().unique().tolist()),
        horizontal=False,
        key="q3_filter_3h"
    )
    q4_filter_3h = q_col4_3h.radio(
        "Q4",
        options=["All"] + sorted(df_3h["Q4_direction"].dropna().unique().tolist()),
        horizontal=False,
        key="q4_filter_3h"
    )
    
    prev_hour_filter_3h = q_col5_3h.radio("Prev. 3H Direction",
                                          options=["All"] + ["Long", "Short", "Neutral"],
                                          horizontal=False,
                                          key="prev_hour_filter_3h")
    orb_filter_3h = q_col6_3h.radio("15m ORB Direction",
                                    options=["All"] +sorted(df_3h["ORB_direction"].dropna().unique().tolist()),
                                    horizontal=False,
                                    key="orb_filter_3h")
    with q_col7_3h:
        low_filter_3h = st.multiselect(
            "Low Exclusion",
            options=sorted(df_3h["low_bucket"].dropna().unique().tolist()),
            key="low_filter_3h"
        )
        high_filter_3h = st.multiselect(
            "High Exclusion",
            options=sorted(df_3h["high_bucket"].dropna().unique().tolist()),
            key="high_filter_3h"
        )


    ###  Apply Filters
    filtered_df_3h = df_3h[df_3h['Instrument'] == selected_instrument]
    filtered_df_3h['prev_three_hour_direction'] = filtered_df_3h['three_hour_direction'].shift(1)

    # Optional: Apply hour filter (if it's not "All")
    if selected_three_hour != 'All':
        # Assumes you have a column like 'Hour' as int. If not, adapt accordingly.
        filtered_df_3h = filtered_df_3h[filtered_df_3h['start_hour'] == selected_three_hour]

    # Optional: Apply day filter (if it's not "All")
    if selected_day != 'All':
        # Assumes you have a column like 'Day' with string values like 'Monday'
        filtered_df_3h = filtered_df_3h[filtered_df_3h['day_of_week'] == selected_day]

    # Filter by Q directions
    if q1_filter_3h != "All":
        filtered_df_3h = filtered_df_3h[filtered_df_3h['Q1_direction'] == q1_filter_3h]
    if q2_filter_3h != "All":
        filtered_df_3h = filtered_df_3h[filtered_df_3h['Q2_direction'] == q2_filter_3h]
    if q3_filter_3h != "All":
        filtered_df_3h = filtered_df_3h[filtered_df_3h['Q3_direction'] == q3_filter_3h]
    if q4_filter_3h != "All":
        filtered_df_3h = filtered_df_3h[filtered_df_3h['Q4_direction'] == q4_filter_3h]
    if prev_hour_filter_3h != 'All':
        filtered_df_3h = filtered_df_3h[filtered_df_3h['prev_three_hour_direction'] == prev_hour_filter_3h] 
    if orb_filter_3h != 'All':
        filtered_df_3h = filtered_df_3h[filtered_df_3h['ORB_direction'] == orb_filter_3h] 
    if low_filter_3h:
        filtered_df_3h = filtered_df_3h[~filtered_df_3h['low_bucket'].isin(low_filter_3h)]
    if high_filter_3h:
        filtered_df_3h = filtered_df_3h[~filtered_df_3h['high_bucket'].isin(high_filter_3h)]

    # Calculate probability distributions for "low bucket" and "high bucket"
    low_counts = filtered_df_3h["low_bucket"].value_counts(normalize=True).reset_index()
    low_counts.columns = ["value", "probability"]

    high_counts = filtered_df_3h["high_bucket"].value_counts(normalize=True).reset_index()
    high_counts.columns = ["value", "probability"]

    # Create a bar chart for "low bucket" probabilities with text annotations
    desired_order = ["Q1", "Q2", "Q3", "Q4"]
    fig_low = px.bar(
        low_counts,
        x="value",
        y="probability",
        title="Low of 3H Bucket",
        labels={"value": "Low Bucket", "probability": "Probability"},
        # Format the probability as a percentage (e.g., "12.34%")
        text=low_counts["probability"].apply(lambda x: f"{x:.2%}")
    )
    # Position the text annotations outside the bars
    fig_low.update_traces(textposition="outside")
    fig_low.update_layout(
    xaxis=dict(
        categoryorder='array',
        categoryarray=desired_order
    )
)

    # Create a bar chart for "high bucket" probabilities with text annotations
    fig_high = px.bar(
        high_counts,
        x="value",
        y="probability",
        title="High of 3H Bucket",
        labels={"value": "High Bucket", "probability": "Probability"},
        text=high_counts["probability"].apply(lambda x: f"{x:.2%}")
    )
    fig_high.update_traces(textposition="outside")
    fig_high.update_layout(
    xaxis=dict(
        categoryorder='array',
        categoryarray=desired_order
    )
)

    # Display the two charts side by side using st.columns
    col1, col2 = st.columns(2)
    col1.plotly_chart(fig_low, use_container_width=True)
    col2.plotly_chart(fig_high, use_container_width=True)

# Calculate distribution of hour_direction in the filtered data
# Normalize direction values
filtered_df_3h['three_hour_direction'] = filtered_df_3h['three_hour_direction'].str.strip().str.title()

# Recalculate counts
three_hour_direction_counts = filtered_df_3h['three_hour_direction'].value_counts().reset_index()
three_hour_direction_counts.columns = ['direction', 'count']

direction_order = ["Long", "Short", "Neutral"]
direction_colors = {
    "Long": "#2ecc71",       # Green
    "Short": "#e74c3c",     # Red
    "Neutral": "#5d6d7e"   # Gray
}

quartals = ["Q1_direction", "Q2_direction", "Q3_direction", "Q4_direction", "three_hour_direction"]
quartal_titles = ["Q1 Direction", "Q2 Direction", "Q3 Direction", "Q4 Direction", "Hour Direction"]

q_cols = st.columns(5)

for i, q_col in enumerate(quartals):
    # Normalize and count values
    filtered_df_3h[q_col] = filtered_df_3h[q_col].str.strip().str.title()
    q_counts = filtered_df_3h[q_col].value_counts().reset_index()
    q_counts.columns = ['direction', 'count']

    # Build pie chart
    fig_q = px.pie(
        q_counts,
        names='direction',
        values='count',
        color='direction',
        title=quartal_titles[i],
        hole=0.3,
        category_orders={'direction': direction_order},
        color_discrete_map=direction_colors
    )
    fig_q.update_traces(textinfo='percent+label')
    q_cols[i].plotly_chart(fig_q, use_container_width=True)

st.caption(f"Sample size: {len(filtered_df_3h):,} rows")

if merged_tf is not None:
    st.markdown("### Combined Data (Hourly and 3H Filters Applied)")

    # Initialize filtered_merged based on Instrument (common filter)
    merged_filtered = merged_tf[merged_tf['Instrument'] == selected_instrument].copy()
    
    # (Optional) Create shifted columns for previous direction if needed
    merged_filtered['prev_hour_direction_hourly'] = merged_filtered['hour_direction'].shift(1)
    merged_filtered['prev_three_hour_direction'] = merged_filtered['three_hour_direction'].shift(1)
    
    # Apply time and day filters
    if selected_hour != 'All':
        merged_filtered = merged_filtered[merged_filtered['hour'] == selected_hour]
    if selected_three_hour != 'All':
        # Here we use the three-hour field. Note: you might also use 'three_hour_start' from the hourly side—choose the one that
        # best reflects the intended filtering.
        merged_filtered = merged_filtered[merged_filtered['start_hour'] == selected_three_hour]
    if selected_day != 'All':
        merged_filtered = merged_filtered[merged_filtered['day_of_week'] == selected_day]
    
    # Apply the hourly Q-direction filters
    if q1_filter != "All":
        merged_filtered = merged_filtered[merged_filtered['Q1_direction_hourly'].str.strip().str.title() == q1_filter]
    if q2_filter != "All":
        merged_filtered = merged_filtered[merged_filtered['Q2_direction_hourly'].str.strip().str.title() == q2_filter]
    if q3_filter != "All":
        merged_filtered = merged_filtered[merged_filtered['Q3_direction_hourly'].str.strip().str.title() == q3_filter]
    if q4_filter != "All":
        merged_filtered = merged_filtered[merged_filtered['Q4_direction_hourly'].str.strip().str.title() == q4_filter]
    if prev_hour_filter != 'All':
        merged_filtered = merged_filtered[merged_filtered['prev_hour_direction_hourly'] == prev_hour_filter]
    if orb_filter != 'All':
        merged_filtered = merged_filtered[merged_filtered['ORB_direction_hourly'] == orb_filter]
    
    # Apply the 3H Q-direction filters
    if q1_filter_3h != "All":
        merged_filtered = merged_filtered[merged_filtered['Q1_direction_3h'].str.strip().str.title() == q1_filter_3h]
    if q2_filter_3h != "All":
        merged_filtered = merged_filtered[merged_filtered['Q2_direction_3h'].str.strip().str.title() == q2_filter_3h]
    if q3_filter_3h != "All":
        merged_filtered = merged_filtered[merged_filtered['Q3_direction_3h'].str.strip().str.title() == q3_filter_3h]
    if q4_filter_3h != "All":
        merged_filtered = merged_filtered[merged_filtered['Q4_direction_3h'].str.strip().str.title() == q4_filter_3h]
    if prev_hour_filter_3h != 'All':
        merged_filtered = merged_filtered[merged_filtered['prev_three_hour_direction'] == prev_hour_filter_3h]
    if orb_filter_3h != 'All':
        merged_filtered = merged_filtered[merged_filtered['ORB_direction_3h'] == orb_filter_3h]
    
    # Apply low/high bucket exclusions.
    # Note: Depending on your needs you might want to exclude based on the hourly values, the 3H values, or both.
    if low_filter:
        merged_filtered = merged_filtered[~merged_filtered['low_bucket_hourly'].isin(low_filter)]
    if high_filter:
        merged_filtered = merged_filtered[~merged_filtered['high_bucket_hourly'].isin(high_filter)]
    if low_filter_3h:
        merged_filtered = merged_filtered[~merged_filtered['low_bucket_3h'].isin(low_filter_3h)]
    if high_filter_3h:
        merged_filtered = merged_filtered[~merged_filtered['high_bucket_3h'].isin(high_filter_3h)]
    
    # === Bar Charts for Bucket Distributions ===
    # For the hourly side (low/high buckets from the hourly columns)
    low_counts_merged_hourly = merged_filtered["low_bucket_hourly"].value_counts(normalize=True).reset_index()
    low_counts_merged_hourly.columns = ["value", "probability"]
    high_counts_merged_hourly = merged_filtered["high_bucket_hourly"].value_counts(normalize=True).reset_index()
    high_counts_merged_hourly.columns = ["value", "probability"]
    
    # Create bar chart for hourly low bucket
    fig_low_merged_hourly = px.bar(
        low_counts_merged_hourly,
        x="value",
        y="probability",
        title="Combined Low of Hour Bucket",
        labels={"value": "Low Bucket", "probability": "Probability"},
        text=low_counts_merged_hourly["probability"].apply(lambda x: f"{x:.2%}")
    )
    fig_low_merged_hourly.update_traces(textposition="outside")
    # Use the same desired order as before (ensure desired_order is defined, e.g., desired_order = ["Q1", "Q2", "Q3", "Q4"])
    fig_low_merged_hourly.update_layout(xaxis=dict(categoryorder='array', categoryarray=desired_order))
    
    # Create bar chart for hourly high bucket
    fig_high_merged_hourly = px.bar(
        high_counts_merged_hourly,
        x="value",
        y="probability",
        title="Combined High of Hour Bucket",
        labels={"value": "High Bucket", "probability": "Probability"},
        text=high_counts_merged_hourly["probability"].apply(lambda x: f"{x:.2%}")
    )
    fig_high_merged_hourly.update_traces(textposition="outside")
    fig_high_merged_hourly.update_layout(xaxis=dict(categoryorder='array', categoryarray=desired_order))
    
    # Display the two bar charts side by side
    col1_merged, col2_merged = st.columns(2)
    col1_merged.plotly_chart(fig_low_merged_hourly, use_container_width=True)
    col2_merged.plotly_chart(fig_high_merged_hourly, use_container_width=True)
    
    # Optionally, you can also do similar bar charts for the 3H side:
    low_counts_merged_3h = merged_filtered["low_bucket_3h"].value_counts(normalize=True).reset_index()
    low_counts_merged_3h.columns = ["value", "probability"]
    high_counts_merged_3h = merged_filtered["high_bucket_3h"].value_counts(normalize=True).reset_index()
    high_counts_merged_3h.columns = ["value", "probability"]
    
    fig_low_merged_3h = px.bar(
        low_counts_merged_3h,
        x="value",
        y="probability",
        title="Combined Low of 3H Bucket",
        labels={"value": "Low Bucket", "probability": "Probability"},
        text=low_counts_merged_3h["probability"].apply(lambda x: f"{x:.2%}")
    )
    fig_low_merged_3h.update_traces(textposition="outside")
    fig_low_merged_3h.update_layout(xaxis=dict(categoryorder='array', categoryarray=desired_order))
    
    fig_high_merged_3h = px.bar(
        high_counts_merged_3h,
        x="value",
        y="probability",
        title="Combined High of 3H Bucket",
        labels={"value": "High Bucket", "probability": "Probability"},
        text=high_counts_merged_3h["probability"].apply(lambda x: f"{x:.2%}")
    )
    fig_high_merged_3h.update_traces(textposition="outside")
    fig_high_merged_3h.update_layout(xaxis=dict(categoryorder='array', categoryarray=desired_order))
    
    col1_merged_3h, col2_merged_3h = st.columns(2)
    col1_merged_3h.plotly_chart(fig_low_merged_3h, use_container_width=True)
    col2_merged_3h.plotly_chart(fig_high_merged_3h, use_container_width=True)
    
    # === Pie Charts for Directional Statistics ===
    # For the hourly directional stats in the merged dataframe
    st.markdown("### Combined Directional Stats (Hourly)")
    quartals_hourly = ["Q1_direction_hourly", "Q2_direction_hourly", "Q3_direction_hourly", "Q4_direction_hourly", "hour_direction"]
    quartal_titles_hourly = ["Q1 Direction", "Q2 Direction", "Q3 Direction", "Q4 Direction", "Hour Direction"]
    
    q_cols_merged_hourly = st.columns(5)
    for i, col_name in enumerate(quartals_hourly):
        merged_filtered[col_name] = merged_filtered[col_name].str.strip().str.title()
        q_counts = merged_filtered[col_name].value_counts().reset_index()
        q_counts.columns = ['direction', 'count']
    
        fig_q = px.pie(
            q_counts,
            names='direction',
            values='count',
            color='direction',
            title=quartal_titles_hourly[i],
            hole=0.3,
            category_orders={'direction': direction_order},
            color_discrete_map=direction_colors
        )
        fig_q.update_traces(textinfo='percent+label')
        q_cols_merged_hourly[i].plotly_chart(fig_q, use_container_width=True)
    
    st.caption(f"Combined sample size (Hourly): {len(merged_filtered):,} rows")
    
    # And similarly for the 3H directional stats:
    st.markdown("### Combined Directional Stats (3H)")
    quartals_3h = ["Q1_direction_3h", "Q2_direction_3h", "Q3_direction_3h", "Q4_direction_3h", "three_hour_direction"]
    quartal_titles_3h = ["Q1 Direction", "Q2 Direction", "Q3 Direction", "Q4 Direction", "3H Direction"]
    
    q_cols_merged_3h = st.columns(5)
    for i, col_name in enumerate(quartals_3h):
        merged_filtered[col_name] = merged_filtered[col_name].str.strip().str.title()
        q_counts = merged_filtered[col_name].value_counts().reset_index()
        q_counts.columns = ['direction', 'count']
    
        fig_q = px.pie(
            q_counts,
            names='direction',
            values='count',
            color='direction',
            title=quartal_titles_3h[i],
            hole=0.3,
            category_orders={'direction': direction_order},
            color_discrete_map=direction_colors
        )
        fig_q.update_traces(textinfo='percent+label')
        q_cols_merged_3h[i].plotly_chart(fig_q, use_container_width=True)
    
    st.caption(f"Combined sample size (3H): {len(merged_filtered):,} rows")
