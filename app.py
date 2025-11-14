import streamlit as st
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from src.api_client import GeneticDataAPIClient
import pandas as pd
import json
import plotly.graph_objects as go
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Genetic Data Explorer",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize API client
@st.cache_resource
def get_api_client():
    return GeneticDataAPIClient()

client = get_api_client()

# Header
st.title("Genetic Data Explorer")
st.markdown("**Comprehensive variant annotation from multiple data sources**")
st.divider()

# Sidebar - Settings
st.sidebar.title("Settings")

# Toggle for Mock vs Real API
use_real_api = st.sidebar.checkbox(
    "Use Real API",
    value=True,
    help="Toggle between real API calls and mock data"
)

if use_real_api:
    st.sidebar.success("Using Real APIs")
    st.sidebar.caption("FAVOR + MyVariant.info")
else:
    st.sidebar.info("Using Mock Data")
    st.sidebar.caption("Local JSON files")

# Sidebar - Data Sources
st.sidebar.divider()
st.sidebar.subheader("Data Sources")
st.sidebar.markdown("""
**FAVOR API**  
Functional annotation, pathogenicity scores

**MyVariant.info**  
Clinical significance, disease associations
""")

# Sidebar - Stats
st.sidebar.divider()
st.sidebar.subheader("Quick Stats")
st.sidebar.metric("APIs Integrated", "2")
st.sidebar.metric("Data Fields", "184+")

# Main search section
st.subheader("Variant Search")

# Search input
col1, col2 = st.columns([4, 1])

with col1:
    variant_id = st.text_input(
        "Variant rsID",
        value="rs429358",
        placeholder="e.g., rs429358, rs7412",
        label_visibility="collapsed"
    )

with col2:
    search_button = st.button("Search", type="primary", use_container_width=True)

# Quick select examples
st.caption("Quick examples:")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("rs429358", use_container_width=True):
        variant_id = "rs429358"
        search_button = True

with col2:
    if st.button("rs7412", use_container_width=True):
        variant_id = "rs7412"
        search_button = True

with col3:
    if st.button("rs3865444", use_container_width=True):
        variant_id = "rs3865444"
        search_button = True

with col4:
    if st.button("Clear", use_container_width=True):
        variant_id = ""

st.divider()

# Visualization functions
def create_pathogenicity_chart(fv):
    """Create bar chart for pathogenicity scores"""
    scores = []
    labels = []
    colors = []
    
    if fv['cadd_phred']:
        scores.append(fv['cadd_phred'])
        labels.append('CADD PHRED')
        colors.append('#e06c75')
    
    if fv['polyphen2_hdiv_score'] is not None:
        scores.append(fv['polyphen2_hdiv_score'])
        labels.append('PolyPhen2 HDIV')
        colors.append('#61afef')
    
    if fv['polyphen2_hvar_score'] is not None:
        scores.append(fv['polyphen2_hvar_score'])
        labels.append('PolyPhen2 HVAR')
        colors.append('#56b6c2')
    
    if fv['sift_score']:
        scores.append(fv['sift_score'])
        labels.append('SIFT')
        colors.append('#98c379')
    
    if scores:
        fig = go.Figure(data=[
            go.Bar(
                x=labels,
                y=scores,
                marker_color=colors,
                text=[f"{s:.3f}" if s else "N/A" for s in scores],
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title="Pathogenicity Scores Comparison",
            xaxis_title="Score Type",
            yaxis_title="Score Value",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#abb2bf'),
            height=400
        )
        
        return fig
    return None

def create_allele_frequency_chart(fv):
    """Create gauge chart for allele frequency"""
    if fv['bravo_af']:
        af_percent = fv['bravo_af'] * 100
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=af_percent,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Allele Frequency (%)", 'font': {'color': '#abb2bf'}},
            number={'suffix': "%", 'font': {'color': '#98c379'}},
            gauge={
                'axis': {'range': [None, 100], 'tickcolor': '#abb2bf'},
                'bar': {'color': "#61afef"},
                'steps': [
                    {'range': [0, 1], 'color': "#21252b"},
                    {'range': [1, 5], 'color': "#2c313a"},
                    {'range': [5, 50], 'color': "#3e4451"}
                ],
                'threshold': {
                    'line': {'color': "#e06c75", 'width': 4},
                    'thickness': 0.75,
                    'value': af_percent
                }
            }
        ))
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#abb2bf'),
            height=300
        )
        
        return fig
    return None

def create_annotation_quality_chart(fv):
    """Create radar chart for annotation completeness"""
    categories = []
    values = []
    
    # Check which annotations are available
    annotations = {
        'CADD': fv['cadd_phred'],
        'PolyPhen2': fv['polyphen2_hdiv_score'],
        'SIFT': fv['sift_score'],
        'Frequency': fv['bravo_af'],
        'Exonic Info': fv['exonic_info']
    }
    
    for key, value in annotations.items():
        categories.append(key)
        values.append(1 if value else 0)
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(97, 175, 239, 0.3)',
        line=dict(color='#61afef', width=2)
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                tickmode='array',
                tickvals=[0, 1],
                ticktext=['Missing', 'Available'],
                gridcolor='#3e4451',
                color='#abb2bf'
            ),
            angularaxis=dict(
                gridcolor='#3e4451',
                color='#abb2bf'
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        showlegend=False,
        title="Annotation Completeness",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#abb2bf'),
        height=400
    )
    
    return fig

# Search functionality
if search_button and variant_id:
    st.subheader(f"Results for: {variant_id}")
    
    if use_real_api:
        # Use Real API
        with st.spinner(f"Fetching data for {variant_id}..."):
            data = client.get_combined_data(variant_id)
        
        if data['success']:
            # Create tabs for organized display
            tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Visualizations", "Detailed Data", "Export"])
            
            # Tab 1: Overview
            with tab1:
                if data['favor']:
                    fv = data['favor']
                    
                    st.markdown("### Basic Information")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Gene", fv['gene'] or "N/A")
                    
                    with col2:
                        st.metric("Category", fv['category'] or "N/A")
                    
                    with col3:
                        st.metric("Exonic Type", fv['exonic_category'] or "N/A")
                    
                    with col4:
                        st.metric("Allele Freq", f"{fv['bravo_af']:.4f}" if fv['bravo_af'] else "N/A")
                    
                    st.markdown("### Pathogenicity Scores")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("CADD PHRED", fv['cadd_phred'] or "N/A")
                    
                    with col2:
                        st.metric("PolyPhen2 HDIV", fv['polyphen2_hdiv_score'] or "N/A")
                    
                    with col3:
                        st.metric("PolyPhen2 HVAR", fv['polyphen2_hvar_score'] or "N/A")
                    
                    with col4:
                        st.metric("SIFT", fv['sift_score'] or "N/A")
                    
                    # Clinical data from MyVariant
                    if data['myvariant']:
                        mv = data['myvariant']
                        st.divider()
                        st.markdown("### Clinical Information")
                        
                        if mv['clinical_significance']:
                            st.info(f"**Clinical Significance:** {mv['clinical_significance']}")
                        
                        if mv['diseases']:
                            st.markdown("**Associated Diseases:**")
                            for disease in mv['diseases']:
                                st.markdown(f"- {disease}")
                
                else:
                    st.warning("No data available for this variant")
            
            # Tab 2: Visualizations
            with tab2:
                if data['favor']:
                    fv = data['favor']
                    
                    # Pathogenicity scores chart
                    st.markdown("### Pathogenicity Scores")
                    path_chart = create_pathogenicity_chart(fv)
                    if path_chart:
                        st.plotly_chart(path_chart, use_container_width=True)
                    else:
                        st.info("No pathogenicity scores available")
                    
                    # Two columns for other charts
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### Allele Frequency")
                        af_chart = create_allele_frequency_chart(fv)
                        if af_chart:
                            st.plotly_chart(af_chart, use_container_width=True)
                        else:
                            st.info("No frequency data available")
                    
                    with col2:
                        st.markdown("### Annotation Completeness")
                        quality_chart = create_annotation_quality_chart(fv)
                        if quality_chart:
                            st.plotly_chart(quality_chart, use_container_width=True)
                
                else:
                    st.warning("No data available for visualizations")
            
            # Tab 3: Detailed Data

            with tab3:
                if data['favor']:
                    fv = data['favor']
                    
                    st.markdown("### FAVOR Annotation Details")
                    
                    with st.expander("View Complete FAVOR Data", expanded=False):
                        st.markdown(f"**Variant VCF:** `{fv['variant_vcf']}`")
                        st.markdown(f"**Chromosome:** {fv['chromosome']}")
                        st.markdown(f"**Position:** {fv['position']}")
                        st.markdown(f"**Filter Status:** {fv['filter_status']}")
                        
                        if fv['exonic_info']:
                            st.markdown(f"**Exonic Info:** {fv['exonic_info']}")
                        
                        st.markdown(f"**BRAVO AN:** {fv['bravo_an']}" if fv['bravo_an'] else "**BRAVO AN:** N/A")
                        st.markdown(f"**BRAVO AC:** {fv['bravo_ac']}" if fv['bravo_ac'] else "**BRAVO AC:** N/A")
                        st.markdown(f"**Mutation Taster Score:** {fv['mutation_taster_score']}" if fv['mutation_taster_score'] else "**Mutation Taster Score:** N/A")
                        st.markdown(f"**Mutation Assessor Score:** {fv['mutation_assessor_score']}" if fv['mutation_assessor_score'] else "**Mutation Assessor Score:** N/A")
                        st.markdown(f"**MetaSVM Prediction:** {fv['metasvm_pred']}" if fv['metasvm_pred'] else "**MetaSVM Prediction:** N/A")
                
                if data['myvariant']:
                    mv = data['myvariant']
                    
                    st.markdown("### MyVariant.info Data")
                    
                    with st.expander("View MyVariant.info Data", expanded=False):
                        st.markdown(f"**Gene:** {mv['gene']}")
                        st.markdown(f"**Consequence:** {mv['consequence']}")
                        st.markdown(f"**CADD Score:** {mv['cadd_score']}")
                        st.markdown(f"**Clinical Significance:** {mv['clinical_significance']}")
                        if mv['diseases']:
                            st.markdown("**Diseases:**")
                            for disease in mv['diseases']:
                                st.markdown(f"- {disease}")
            
            # Tab 4: Export
            with tab4:
                st.markdown("### Data Summary Table")
                
                merged_data = {
                    "Variant ID": variant_id,
                    "Gene": data['favor']['gene'] if data['favor'] else (data['myvariant']['gene'] if data['myvariant'] else "N/A"),
                    "Category": data['favor']['category'] if data['favor'] else "N/A",
                    "Exonic Type": data['favor']['exonic_category'] if data['favor'] else "N/A",
                    "Allele Frequency": data['favor']['bravo_af'] if data['favor'] else "N/A",
                    "CADD PHRED": data['favor']['cadd_phred'] if data['favor'] else "N/A",
                    "Clinical Significance": data['myvariant']['clinical_significance'] if data['myvariant'] else "N/A"
                }
                
                df = pd.DataFrame([merged_data])
                st.dataframe(df, use_container_width=True)
                
                st.markdown("### Export Options")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    export_data = {
                        "variant_id": variant_id,
                        "favor": data['favor'],
                        "myvariant": data['myvariant']
                    }
                    json_str = json.dumps(export_data, indent=2)
                    st.download_button(
                        label="Download JSON",
                        data=json_str,
                        file_name=f"{variant_id}_data.json",
                        mime="application/json",
                        use_container_width=True
                    )
                
                with col2:
                    csv_str = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv_str,
                        file_name=f"{variant_id}_data.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
        
        else:
            st.error(f"Failed to retrieve data for {variant_id}")
            st.info("Try using mock data mode or verify the variant ID is valid")
    
    else:
        # Use Mock Data
        st.info("Using Mock Data (Real API disabled)")
        
        try:
            favor_mock = client.load_mock_data("favor_mock.json")
            favor_mock2 = client.load_mock_data("favor_mock2.json")
            gtex_mock = client.load_mock_data("gtex_mock.json")
            
            tab1, tab2, tab3 = st.tabs(["FAVOR Basic", "FAVOR Regulatory", "GTEx"])
            
            with tab1:
                if favor_mock:
                    st.success("Mock FAVOR data loaded")
                    st.json(favor_mock)
            
            with tab2:
                if favor_mock2:
                    st.success("Mock FAVOR regulatory data loaded")
                    st.json(favor_mock2)
            
            with tab3:
                if gtex_mock:
                    st.success("Mock GTEx data loaded")
                    st.json(gtex_mock)
        
        except Exception as e:
            st.error(f"Error loading mock data: {e}")

# Footer
st.divider()
st.caption("Genetic Data Explorer | Data from FAVOR API & MyVariant.info")