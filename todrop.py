            st.markdown("---")
            with st.container():
                st.header("📊 Activities Table")

                try:
                    with open(outputs_folder / "risk_assessment.json", "r") as f:
                        risks = json.load(f)

                    # List of all crime types (from database_utils.py)
                    CRIME_CATEGORIES = [
                        "money_laundering",
                        "sanctions_evasion",
                        "terrorist_financing",
                        "bribery",
                        "corruption",
                        "embezzlement",
                        "fraud",
                        "tax_evasion",
                        "insider_trading",
                        "market_manipulation",
                        "ponzi_scheme",
                        "pyramid_scheme",
                        "identity_theft",
                        "cybercrime",
                        "human_trafficking"
                    ]

                    # Build activities table data - ONLY for flagged entities
                    activities_data = []
                    for flagged_entity in risks.get("flagged_entities", []):
                        entity_name = flagged_entity['entity_name']
                        description = flagged_entity.get('description', '')
                        reasoning = flagged_entity['reasoning']
                        entity_crime_set = set(flagged_entity['crimes_flagged'])

                        # Build summary (description from risk_assessment.json)
                        summary = description

                        # Create row data
                        row = {
                            "Entity": entity_name,
                            "Summary": summary,
                            "Comments": "",  # Empty comments field
                            "Flagged": True  # All entities here are flagged
                        }

                        # Add crime columns
                        for crime in CRIME_CATEGORIES:
                            row[crime] = crime in entity_crime_set

                        activities_data.append(row)

                    # Create DataFrame
                    df_activities = pd.DataFrame(activities_data)

                    # Function to apply checkmarks and crosses
                    def apply_checkmarks(val):
                        if isinstance(val, bool):
                            if val:
                                return '<span style="color: green; font-size: 18px;">✓</span>'
                            else:
                                return '<span style="color: red; font-size: 18px;">✗</span>'
                        return val

                    # Find crime columns that have at least one flagged entity
                    used_crime_columns = []
                    for crime in CRIME_CATEGORIES:
                        if any(row[crime] for row in activities_data):
                            used_crime_columns.append(crime)
                    
                    # Filter DataFrame to only include used crime columns
                    columns_to_keep = ["Entity", "Summary", "Comments", "Flagged"] + used_crime_columns
                    df_activities = df_activities[columns_to_keep]

                    # Apply styling to boolean columns
                    styled_df = df_activities.copy()
                    boolean_columns = ["Flagged"] + used_crime_columns

                    for col in boolean_columns:
                        styled_df[col] = styled_df[col].apply(apply_checkmarks)

                    # Display the table
                    st.write(f"**Total entities: {len(activities_data)}**")
                    st.write(f"**Flagged entities: {sum(1 for row in activities_data if row['Flagged'])}**")
                    st.write(f"**Crime types detected: {len(used_crime_columns)} out of {len(CRIME_CATEGORIES)}**")

                    # Prepare DataFrame for HTML table - reorder columns
                    cols_to_exclude = ["Entity", "Summary", "Comments", "Flagged"]
                    col_boolean_wo_flagged_list = used_crime_columns

                    # Reorder columns: fixed columns first, then crime columns
                    desired_cols = cols_to_exclude + used_crime_columns
                    filtered_df = styled_df[desired_cols]

                    # Generate custom HTML table
                    html_table = define_html(filtered_df, cols_to_exclude, col_boolean_wo_flagged_list)

                    # Display the custom HTML table using components.html for proper rendering
                    components.html(html_table, height=950, scrolling=True)

                except Exception as e:
                    st.error(f"Could not load activities table: {e}")
