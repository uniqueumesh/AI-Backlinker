import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from ai_backlinking import find_backlink_opportunities, compose_personalized_email


# Streamlit UI function
def backlinking_ui():
    st.title("AI Backlinking Tool")

    # API keys (Phase 2)
    with st.expander("API Settings", expanded=False):
        serper_api_key = st.text_input("Serper API Key", type="password")
        firecrawl_api_key = st.text_input("Firecrawl API Key", type="password")

    # Step 1: Get user inputs
    keyword = st.text_input("Enter a keyword", value="AI tools + 'write for us'")

    # Step 2: Generate backlink opportunities
    if st.button("Find Backlink Opportunities"):
        if keyword:
            with st.spinner("Searching opportunities..."):
                backlink_opportunities = find_backlink_opportunities(
                    keyword,
                    serper_api_key=serper_api_key or None,
                    firecrawl_api_key=firecrawl_api_key or None,
                )

            # Convert results to a DataFrame for display
            df = pd.DataFrame(backlink_opportunities)

            if df.empty:
                st.info("No opportunities found yet. This demo shows sample rows. Try a different keyword.")
            else:
                # Create a selectable table using st-aggrid
                gb = GridOptionsBuilder.from_dataframe(df)
                gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren=True)
                gridOptions = gb.build()

                grid_response = AgGrid(
                    df,
                    gridOptions=gridOptions,
                    update_mode=GridUpdateMode.SELECTION_CHANGED,
                    height=300,
                    width='100%'
                )

                selected_rows = grid_response['selected_rows']

                if selected_rows:
                    st.write("Selected Opportunities:")
                    st.table(pd.DataFrame(selected_rows))

                    # Step 3: Option to generate personalized emails for selected opportunities
                    if st.button("Generate Emails for Selected Opportunities"):
                        user_proposal = {
                            "user_name": st.text_input("Your Name", value="John Doe"),
                            "user_email": st.text_input("Your Email", value="john@example.com")
                        }

                        emails = []
                        for selected in selected_rows:
                            insights = f"Insights based on content from {selected.get('url','')}."
                            email = compose_personalized_email(selected, insights, user_proposal)
                            emails.append(email)

                        st.subheader("Generated Emails:")
                        for email in emails:
                            st.write(email)
                            st.markdown("---")
        else:
            st.error("Please enter a keyword.")


# Ensure the UI renders when run via `streamlit run`
backlinking_ui()
