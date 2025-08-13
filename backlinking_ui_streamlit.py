import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from ai_backlinking import find_backlink_opportunities, compose_personalized_email, logger


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
        st.markdown("LLM Provider")
        provider = st.selectbox("Choose LLM", options=["Gemini", "OpenAI"], index=0)
        if provider == "Gemini":
            gemini_api_key = st.text_input("Gemini API Key", type="password")
            model_name = st.text_input("Gemini Model", value="gemini-2.5-flash")
            openai_api_key = None
        else:
            openai_api_key = st.text_input("OpenAI API Key", type="password")
            model_name = st.text_input("OpenAI Model", value="gpt-4o-mini")
            gemini_api_key = None

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
                tmp = pd.DataFrame(selected_rows)
                # Show which context powered the email
                ctx = tmp.get('context_source') if 'context_source' in tmp.columns else None
                st.table(tmp if ctx is None else tmp[[c for c in tmp.columns if c in ['title','url','domain','contact_email','guidelines_url','context_source']]])

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

                logger.info("Phase 3: starting personalized email generation for {n} rows", n=len(selected_df))
                email_rows = []
                diag_rows = []
                for _, selected in selected_df.iterrows():
                    selected_dict = selected.to_dict()
                    insights_parts = []
                    if selected_dict.get('notes'):
                        insights_parts.append(selected_dict.get('notes'))
                    if selected_dict.get('guidelines_url'):
                        insights_parts.append(f"Guidelines: {selected_dict.get('guidelines_url')}")
                    insights = "; ".join(insights_parts) or f"Page: {selected_dict.get('url','')}"

                    # Prefer page excerpt as insight if available
                    if selected_dict.get('page_excerpt'):
                        insights = selected_dict.get('page_excerpt')
                    ctx_src = selected_dict.get('context_source', '')
                    excerpt_len = len(selected_dict.get('page_excerpt') or '')
                    status = "ok"
                    note = ""
                    try:
                        body = compose_personalized_email(
                            selected_dict,
                            insights,
                            user_proposal,
                            provider=provider.lower(),
                            model=model_name,
                            openai_api_key=openai_api_key or None,
                            gemini_api_key=gemini_api_key or None,
                        )
                        if body.strip().lower().startswith("subject:"):
                            body = "\n".join(body.splitlines()[1:]).lstrip()
                        if body.startswith("[AI Draft]"):
                            status = "fallback"
                            note = "LLM placeholder (missing key or error)"
                            st.warning(f"LLM fallback used for {selected_dict.get('domain','')}. Provide an API key or try again later.")
                            logger.warning("Phase 3: placeholder draft for domain={domain} provider={prov} model={model}",
                                           domain=selected_dict.get('domain',''), prov=provider, model=model_name)
                        else:
                            logger.info("Phase 3: generated email for domain={domain} ctx={ctx} excerpt_chars={chars}",
                                        domain=selected_dict.get('domain',''), ctx=ctx_src or 'unknown', chars=excerpt_len)
                    except Exception as exc:
                        status = "error"
                        note = f"{type(exc).__name__}: {exc}"
                        body = ""
                        logger.error("Phase 3: generation error for domain={domain} -> {err}",
                                     domain=selected_dict.get('domain',''), err=str(exc))
                    to_email = selected_dict.get('contact_email', '') or ''
                    email_rows.append({
                        'to_email': to_email,
                        'subject': email_subject,
                        'body': body,
                        'url': selected_dict.get('url',''),
                        'domain': selected_dict.get('domain',''),
                        'title': selected_dict.get('title',''),
                        'context_source': ctx_src,
                        'excerpt_chars': excerpt_len,
                        'status': status,
                        'note': note,
                        'provider': provider,
                        'model': model_name,
                    })
                    diag_rows.append({
                        'domain': selected_dict.get('domain',''),
                        'context_source': ctx_src,
                        'excerpt_chars': excerpt_len,
                        'status': status,
                        'note': note,
                        'provider': provider,
                        'model': model_name,
                    })

                emails_df = pd.DataFrame(email_rows)
                st.session_state['emails_df'] = emails_df
                if diag_rows:
                    st.session_state['emails_diag_df'] = pd.DataFrame(diag_rows)
                logger.info("Phase 3: completed generation; ok={ok} fallback={fb} error={er}",
                            ok=sum(1 for r in email_rows if r['status']=='ok'),
                            fb=sum(1 for r in email_rows if r['status']=='fallback'),
                            er=sum(1 for r in email_rows if r['status']=='error'))

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
                diag_df = st.session_state.get('emails_diag_df')
                if diag_df is not None:
                    st.markdown("### Generation Diagnostics")
                    st.dataframe(diag_df, use_container_width=True, height=220)


# Ensure the UI renders when run via `streamlit run`
backlinking_ui()
