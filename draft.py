
# Create DataFrame
df_activities = pd.DataFrame(activities_data)

# IMPORTANT: Recalculate active crime columns based on activities table
# (not the main df_display which includes unflagged entities)
if not df_activities.empty:
    activities_crime_columns = [crime.lower() for crime in FINANCIAL_CRIMES_ENHANCED 
                               if crime.lower() in df_activities.columns and df_activities[crime.lower()].any()]
else:
    activities_crime_columns = []

# Use these columns for the activities table display
display_crime_columns = st.session_state.selected_crime_columns if 'selected_crime_columns' in st.session_state else activities_crime_columns
