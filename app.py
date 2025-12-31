import streamlit as st
import pandas as pd
from logic import trace_url

st.set_page_config(page_title="Redirect Finalizer", layout="wide")

st.title("🔗 Redirect Chain Auditor")
st.markdown("Upload a CSV to find where your redirected links *actually* end up.")

# File uploader
uploaded_file = st.file_uploader("Upload CSV (must have a column named 'url')", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    if 'url' not in df.columns:
        st.error("Your CSV needs a column exactly named 'url'")
    else:
        if st.button("Start Audit"):
            results = []
            progress_text = "Analyzing URLs..."
            bar = st.progress(0, text=progress_text)
            
            for i, row in df.iterrows():
                # Call the engine we wrote in logic.py
                chain, final_status = trace_url(row['url'])
                
                results.append({
                    "Initial URL": row['url'],
                    "Final Destination": chain[-1]['url'],
                    "Hops": len(chain) - 1,
                    "Final Status": final_status,
                    "Full Path": " → ".join([str(c['status']) for c in chain])
                })
                # Update progress bar
                bar.progress((i + 1) / len(df))
            
            # Display results
            result_df = pd.DataFrame(results)
            
            # Highlight 4xx errors in red for the user
            def color_status(val):
                if str(val).startswith('4'): return 'background-color: #ffcccc'
                if str(val).startswith('2'): return 'background-color: #ccffcc'
                return ''

            st.dataframe(result_df.style.applymap(color_status, subset=['Final Status']))
            
            # Export button
            csv = result_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download Audit Results", csv, "audit_results.csv", "text/csv")