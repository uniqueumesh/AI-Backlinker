import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from ai_backlinking import find_backlink_opportunities, compose_personalized_email


# Streamlit UI function
def backlinking_ui():
    st.title("AI Backlinking Tool")

    # Session state
    if 'results' not in st.session_state:
        st.session_state['results'] = None
    if 'selected_urls' not in st.session_state:
        st.session_state['selected_urls'] = []
    if 'emails_df' not in st.session_state:
        st.session_state['emails_df'] = None

    # API keys (Phase 2)
    with st.expander("API Settings", expanded=False):
        serper_api_key = st.text_input("Serper API Key", type="password")
        firecrawl_api_key = st.text_input("Firecrawl API Key", type="password")

    # Step 1: Get user inputs
    keyword = st.text_input("Enter a keyword", value="AI tools + 'write for us'")

    # Step 2: Generate backlink opportunities (persist in session_state)
    if st.button("Find Backlink Opportunities"):
        if keyword:
            with st.spinner("Searching opportunities..."):
                backlink_opportunities = find_backlink_opportunities(
                    keyword,
                    serper_api_key=serper_api_key or None,
                    firecrawl_api_key=firecrawl_api_key or None,
                )
            st.session_state['results'] = backlink_opportunities
        else:
            st.error("Please enter a keyword.")

    # Render results and Phase 3 if we have results in session
    results = st.session_state.get('results') or []
    if results:
        df = pd.DataFrame(results)
        if df.empty:
            st.info("No opportunities found yet. This demo shows sample rows. Try a different keyword.")
        else:
            gb = GridOptionsBuilder.from_dataframe(df)
            gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren=True)
            gridOptions = gb.build()

            grid_response = AgGrid(
                df,
                gridOptions=gridOptions,
                update_mode=GridUpdateMode.SELECTION_CHANGED,
                height=300,
                width='100%',
                key="opps_grid"
            )

            selected_rows = grid_response.get('selected_rows', [])
            st.session_state['selected_urls'] = [row.get('url') for row in selected_rows if row.get('url')]

            if selected_rows:
                st.write("Selected Opportunities:")
                st.table(pd.DataFrame(selected_rows))

            # Phase 3: Inputs and bulk email generation
            st.markdown("### Personalized Outreach")
            col1, col2 = st.columns(2)
            with col1:
                your_name = st.text_input("Your Name", value="John Doe")
                your_email = st.text_input("Your Email", value="john@example.com")
                proposed_topic = st.text_input("Proposed Topic (optional)", value="")
            with col2:
                email_subject = st.text_input("Email Subject", value="Guest post collaboration")

            if st.button("Generate Emails for Selected Opportunities"):
                # Fallback to session stored selection if current selection is empty on rerun
                urls = st.session_state.get('selected_urls') or []
                selected_df = df[df['url'].isin(urls)] if urls else df.iloc[0:0]

                user_proposal = {
                    "user_name": your_name,
                    "user_email": your_email,
                    "topic": proposed_topic or "a guest post",
                }

                email_rows = []
                for _, selected in selected_df.iterrows():
                    selected_dict = selected.to_dict()
                    insights_parts = []
                    if selected_dict.get('notes'):
                        insights_parts.append(selected_dict.get('notes'))
                    if selected_dict.get('guidelines_url'):
                        insights_parts.append(f"Guidelines: {selected_dict.get('guidelines_url')}")
                    insights = "; ".join(insights_parts) or f"Page: {selected_dict.get('url','')}"

                    body = compose_personalized_email(selected_dict, insights, user_proposal)
                    to_email = selected_dict.get('contact_email', '') or ''
                    email_rows.append({
                        'to_email': to_email,
                        'subject': email_subject,
                        'body': body,
                        'url': selected_dict.get('url',''),
                        'domain': selected_dict.get('domain',''),
                        'title': selected_dict.get('title',''),
                    })

                emails_df = pd.DataFrame(email_rows)
                st.session_state['emails_df'] = emails_df

            # Show generated emails if available
            if st.session_state.get('emails_df') is not None:
                emails_df = st.session_state['emails_df']
                st.subheader("Generated Emails")
                st.dataframe(emails_df, use_container_width=True, height=300)
                csv = emails_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Emails CSV",
                    data=csv,
                    file_name="generated_emails.csv",
                    mime="text/csv",
                )


# Ensure the UI renders when run via `streamlit run`
backlinking_ui()
