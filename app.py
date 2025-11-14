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

# Available variants
available_variants = ["rs429358", "rs7412", "rs3865444"]

# User input
variant_id = st.text_input(
    "🔍 Enter Variant ID:",
    value="rs429358",
    help="Examples: rs429358, rs7412"
)

# Quick select buttons
st.write("**Quick Select:**")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("rs429358"):
        variant_id = "rs429358"
with col2:
    if st.button("rs7412"):
        variant_id = "rs7412"
with col3:
    if st.button("rs3865444"):
        variant_id = "rs3865444"

# Search button
if st.button("🔎 Search", type="primary"):
    st.write("---")
    st.subheader(f"📊 Results for: {variant_id}")
    
    # Load FAVOR data
    try:
        favor_file = f"mock_data/favor_mock.json"
        if os.path.exists(favor_file):
            with open(favor_file, "r") as f:
                favor_data = json.load(f)
        else:
            # Use default file
            with open("mock_data/favor_mock.json", "r") as f:
                favor_data = json.load(f)
        
        st.success("✅ FAVOR Data loaded successfully!")
        
        # Display FAVOR data
        st.write("### 🧪 FAVOR API - Functional Annotation")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Gene", favor_data.get("gene", "N/A"))
            st.metric("Annotation Score", favor_data.get("annotation_score", "N/A"))
            st.metric("Impact", favor_data.get("impact", "N/A"))
        
        with col2:
            st.metric("Consequence", favor_data.get("consequence", "N/A"))
            st.metric("CADD Score", favor_data.get("cadd_score", "N/A"))
            st.metric("Tissue Activity", favor_data.get("tissue_activity", "N/A"))
        
    except FileNotFoundError:
        st.error("❌ FAVOR mock data file not found!")
    except json.JSONDecodeError:
        st.error("❌ Error reading FAVOR data!")
    
    # Load GTEx data
    try:
        gtex_file = f"mock_data/gtex_mock.json"
        if os.path.exists(gtex_file):
            with open(gtex_file, "r") as f:
                gtex_data = json.load(f)
        else:
            with open("mock_data/gtex_mock.json", "r") as f:
                gtex_data = json.load(f)
        
        st.success("✅ GTEx Data loaded successfully!")
        
        # Display GTEx data
        st.write("### 🧠 GTEx API - Gene Expression")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Tissue", gtex_data.get("tissue", "N/A"))
            st.metric("Expression Level", gtex_data.get("expression_level", "N/A"))
            st.metric("TPM", gtex_data.get("tpm", "N/A"))
        
        with col2:
            st.metric("Tissue Specific", str(gtex_data.get("tissue_specific", "N/A")))
            diseases = gtex_data.get("associated_diseases", [])
            st.write("**Associated Diseases:**")
            for disease in diseases:
                st.write(f"- {disease}")
        
    except FileNotFoundError:
        st.error("❌ GTEx mock data file not found!")
    except json.JSONDecodeError:
        st.error("❌ Error reading GTEx data!")
    
    # Merged data view
    st.write("---")
    st.write("### 📋 Merged Data View")
    
    merged_data = {
        "Variant ID": variant_id,
        "Gene": favor_data.get("gene", "N/A"),
        "Impact": favor_data.get("impact", "N/A"),
        "FAVOR Score": favor_data.get("annotation_score", "N/A"),
        "Expression Tissue": gtex_data.get("tissue", "N/A"),
        "Expression Level": gtex_data.get("expression_level", "N/A")
    }
    
    df = pd.DataFrame([merged_data])
    st.dataframe(df, use_container_width=True)

# Sidebar information
st.sidebar.write("---")
st.sidebar.write("### 📚 About")
st.sidebar.info(
    """
    This app integrates multiple genetic data sources:
    - FAVOR: Functional annotation
    - GTEx: Gene expression data
    
    Enter a variant ID to view detailed information.
    """
)