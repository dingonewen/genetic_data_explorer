import streamlit as st
import json
import pandas as pd
import os

# Page configuration
st.set_page_config(
    page_title="Genetic Data Explorer",
    page_icon="🧬",
    layout="wide"
)

# Title
st.title("🧬 Genetic Data Explorer")
st.write("Explore genetic variant data from multiple sources")

# Sidebar
st.sidebar.title("📋 Navigation")
st.sidebar.write("Use this tool to query genetic variant information")

# User input
variant_id = st.text_input(
    "🔍 Enter Variant ID:",
    value="rs429358",
    help="Examples: rs429358, rs7412"
)

# Search button
if st.button("🔎 Search", type="primary"):
    st.write("---")
    st.subheader(f"📊 Results for: {variant_id}")
    
    # Initialize data containers
    favor_basic = {}
    favor_regulatory = {}
    gtex_data = {}
    
    # Load FAVOR basic annotation
    try:
        with open("mock_data/favor_mock.json", "r") as f:
            favor_basic = json.load(f)
        st.success("✅ FAVOR Basic Annotation loaded!")
    except Exception as e:
        st.error(f"❌ Error loading FAVOR basic data: {e}")
    
    # Load FAVOR regulatory features (favor_mock2.json)
    try:
        with open("mock_data/favor_mock2.json", "r") as f:
            favor_regulatory = json.load(f)
        st.success("✅ FAVOR Regulatory Features loaded!")
    except Exception as e:
        st.error(f"❌ Error loading FAVOR regulatory data: {e}")
    
    # Load GTEx expression data
    try:
        with open("mock_data/gtex_mock.json", "r") as f:
            gtex_data = json.load(f)
        st.success("✅ GTEx Expression Data loaded!")
    except Exception as e:
        st.error(f"❌ Error loading GTEx data: {e}")
    
    # Display data from each source
    st.write("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("### 🧪 FAVOR - Basic")
        st.metric("Gene", favor_basic.get("gene", "N/A"))
        st.metric("Annotation Score", favor_basic.get("annotation_score", "N/A"))
        st.metric("Consequence", favor_basic.get("consequence", "N/A"))
        st.metric("Impact", favor_basic.get("impact", "N/A"))
    
    with col2:
        st.write("### 🧬 FAVOR - Regulatory")
        st.metric("Regulatory Feature", favor_regulatory.get("regulatory_feature", "N/A"))
        st.metric("Tissue Activity", favor_regulatory.get("tissue_activity", "N/A"))
        st.metric("cCRE ID", favor_regulatory.get("cCRE_id", "N/A"))
    
    with col3:
        st.write("### 🧠 GTEx - Expression")
        st.metric("Tissue", gtex_data.get("tissue", "N/A"))
        st.metric("Expression Level", gtex_data.get("expression_level", "N/A"))
        st.metric("TPM", gtex_data.get("tpm", "N/A"))
        diseases = gtex_data.get("associated_diseases", [])
        if diseases:
            st.write("**Diseases:**")
            for disease in diseases:
                st.write(f"- {disease}")
    
    # Merged data view
    st.write("---")
    st.write("### 📋 Merged Data View")
    
    merged_data = {
        "Variant ID": variant_id,
        "Gene": favor_basic.get("gene", "N/A"),
        "Impact": favor_basic.get("impact", "N/A"),
        "Annotation Score": favor_basic.get("annotation_score", "N/A"),
        "Regulatory Feature": favor_regulatory.get("regulatory_feature", "N/A"),
        "Tissue Activity": favor_regulatory.get("tissue_activity", "N/A"),
        "Expression Tissue": gtex_data.get("tissue", "N/A"),
        "Expression Level": gtex_data.get("expression_level", "N/A"),
        "TPM": gtex_data.get("tpm", "N/A")
    }
    
    df = pd.DataFrame([merged_data])
    st.dataframe(df, use_container_width=True)
    
    # Export functionality
    st.write("---")
    st.write("### 💾 Export Data")
    
    col1, col2 = st.columns(2)
    with col1:
        # Export as JSON
        json_str = json.dumps(merged_data, indent=2)
        st.download_button(
            label="📥 Download as JSON",
            data=json_str,
            file_name=f"{variant_id}_merged_data.json",
            mime="application/json"
        )
    
    with col2:
        # Export as CSV
        csv_str = df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv_str,
            file_name=f"{variant_id}_merged_data.csv",
            mime="text/csv"
        )

# Sidebar information
st.sidebar.write("---")
st.sidebar.write("### 📚 About")
st.sidebar.info(
    """
    This app integrates data from 3 sources:
    - FAVOR Basic: Variant annotation
    - FAVOR Regulatory: cCRE features
    - GTEx: Gene expression data
    
    Enter a variant ID to view merged information.
    """
)

st.sidebar.write("---")
st.sidebar.write("### 📊 Data Sources")
st.sidebar.write("""
- **favor_mock.json**: Basic variant annotations
- **favor_mock2.json**: Regulatory features
- **gtex_mock.json**: Gene expression data
""")