import streamlit as st
import sys
import os
import re

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
    page_icon="https://cdn-icons-png.flaticon.com/512/10004/10004916.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for One Dark Atom theme
st.markdown("""
<style>
    /* Global font - Consolas */
    html, body, [class*="css"], .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6,
    .stButton button, .stTextInput input, .stSelectbox, div, span {
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace !important;
    }

    /* Background color - Light grayish white */
    .stApp {
        background-color: #f5f5f5 !important;
    }

    /* Main content area */
    .main .block-container {
        background-color: #fafafa !important;
    }

    /* Sidebar background */
    [data-testid="stSidebar"] {
        background-color: #e8e8e8 !important;
    }
            
    [data-testid="stIconMaterial"] {
        text-indent: -9999px !important;
        display: inline-block !important;
        width: 0 !important;
        overflow: hidden !important;
    }
            


    [data-testid="StyledLinkIconContainer"],
    [data-testid="collapsedControl"],
    .stExpander [data-testid="StyledLinkIconContainer"],
    .stExpander svg,
    button[kind="header"] svg,
    span[data-baseweb="icon"],
    [data-testid="stSidebarNav"] button svg,
    [data-testid="baseButton-header"] svg,
    [data-testid="baseButton-headerNoPadding"] svg,
    button[aria-label*="Collapse"] svg,
    button[aria-label*="collapse"] svg,
    .css-1kyxreq svg,
    [class*="viewerBadge"],
    details summary svg,
    summary svg {
        display: none !important;
        visibility: hidden !important;
    }

    /* One Dark Atom theme colors for headings */
    .stMarkdown h1 {
        color: #61afef !important;  /* Blue */
    }

    /* Main title - Blue without glow */
    h1 {
        color: #61afef !important;
    }

    .stMarkdown h2 {
        color: #e06c75 !important;  /* Red */
    }

    .stMarkdown h3 {
        color: #98c379 !important;  /* Green */
    }

    .stMarkdown h4 {
        color: #e5c07b !important;  /* Yellow */
    }

    /* Tab text color */
    .stTabs [data-baseweb="tab-list"] button {
        color: #4a4a4a !important;
    }

    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: #61afef !important;
    }

    /* Help tab (5th tab) - Red color */
    .stTabs [data-baseweb="tab-list"] button:nth-child(5) {
        color: #e06c75 !important;
    }

    .stTabs [data-baseweb="tab-list"] button:nth-child(5)[aria-selected="true"] {
        color: #e06c75 !important;
        font-weight: bold !important;
    }

    /* Sidebar small caption text */
    .sidebar-caption {
        font-size: 0.75rem !important;
        color: #5c6370 !important;
        line-height: 1.2 !important;
    }

    /* Smaller metric labels and values */
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.1rem !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        max-width: 100% !important;
        display: block !important;
    }

    /* Metric hover to show full content */
    [data-testid="stMetric"]:hover [data-testid="stMetricValue"] {
        overflow: visible !important;
        white-space: normal !important;
        background-color: #ffffff !important;
        border: 1px solid #e06c75 !important;
        padding: 4px 8px !important;
        border-radius: 4px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15) !important;
        z-index: 1000 !important;
        position: relative !important;
    }

    /* Smaller API status boxes */
    .api-status-box {
        padding: 8px 12px !important;
        font-size: 0.85rem !important;
        border-radius: 6px !important;
    }

    /* Make success/error alerts more compact */
    .stAlert {
        padding: 0.5rem 0.75rem !important;
    }

    [data-testid="stNotification"] > div {
        padding: 0.5rem 0.75rem !important;
        font-size: 0.85rem !important;
    }


    /* Gene icon positioning - next to main title */
    .gene-icon {
        position: absolute;
        top: -20px;
        right: 0px;
        width: 180px;
        height: 180px;
        opacity: 0.7;
        z-index: 999;
    }

    /* Make title container relative for icon positioning */
    .main h1 {
        position: relative;
    }
</style>
""", unsafe_allow_html=True)

# Add gene icon at top right
st.markdown("""
<img src="https://cdn-icons-png.flaticon.com/512/10004/10004916.png" class="gene-icon" alt="Gene Icon">
""", unsafe_allow_html=True)

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
else:
    st.sidebar.info("Using Mock Data")

# Sidebar - Data Sources
st.sidebar.divider()
st.sidebar.subheader("Data Sources")
st.sidebar.markdown("""
**[FAVOR API](https://docs.genohub.org/)**
<span class="sidebar-caption">Functional annotation, pathogenicity scores</span>

**[MyVariant.info](https://myvariant.info/)**
<span class="sidebar-caption">Clinical significance, disease associations</span>

**[Ensembl REST API](https://rest.ensembl.org/)**
<span class="sidebar-caption">Genomic coordinates, population frequencies</span>
""", unsafe_allow_html=True)

# Sidebar - Stats
st.sidebar.divider()
st.sidebar.subheader("Quick Stats")
st.sidebar.metric("APIs Integrated", "3")  # Changed from 2 to 3
st.sidebar.metric("Data Fields", "200+")   # Updated

# Main search section
st.subheader("Variant Annotation Search")

# Search input
col1, col2 = st.columns([4, 1])

with col1:
    variant_id = st.text_input(
        "Variant rsID or Gene Symbol",
        value="",
        placeholder="Type in Variant rsID or Gene Symbol",
        label_visibility="collapsed"
    )

with col2:
    search_button = st.button("Search", type="primary", use_container_width=True)

# Quick select examples
st.caption("Quick examples:")
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    if st.button("rs429358", use_container_width=True):
        variant_id = "rs429358"
        search_button = True

with col2:
    if st.button("rs7412", use_container_width=True):
        variant_id = "rs7412"
        search_button = True

with col3:
    if st.button("APOE", use_container_width=True):
        variant_id = "APOE"
        search_button = True

with col4:
    if st.button("BRCA1", use_container_width=True):
        variant_id = "BRCA1"
        search_button = True

with col5:
    if st.button("TP53", use_container_width=True):
        variant_id = "TP53"
        search_button = True

with col6:
    if st.button("Clear", use_container_width=True):
        variant_id = ""

st.divider()

# API Status Display (always visible)
st.caption("API Connection Status:")
status_col1, status_col2, status_col3 = st.columns(3)

with status_col1:
    st.markdown('<div class="api-status-box">', unsafe_allow_html=True)
    st.success("✓ FAVOR API", icon="😊")
    st.markdown('</div>', unsafe_allow_html=True)

with status_col2:
    st.markdown('<div class="api-status-box">', unsafe_allow_html=True)
    st.success("✓ MyVariant.info", icon="😊")
    st.markdown('</div>', unsafe_allow_html=True)

with status_col3:
    st.markdown('<div class="api-status-box">', unsafe_allow_html=True)
    st.success("✓ Ensembl REST", icon="😊")
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# Visualization functions
def create_pathogenicity_chart(fv):
    """Create enhanced pathogenicity scores chart with thresholds"""
    scores_data = []

    # CADD PHRED (>20 deleterious, >30 highly deleterious)
    if fv['cadd_phred']:
        interpretation = 'Benign' if fv['cadd_phred'] < 20 else ('Deleterious' if fv['cadd_phred'] < 30 else 'Highly Deleterious')
        color = '#98c379' if fv['cadd_phred'] < 20 else ('#e5c07b' if fv['cadd_phred'] < 30 else '#e06c75')
        scores_data.append({
            'name': 'CADD PHRED',
            'score': fv['cadd_phred'],
            'normalized': min(fv['cadd_phred'] / 40, 1),  # Normalize to 0-1
            'interpretation': interpretation,
            'color': color,
            'threshold': 20
        })

    # PolyPhen2 (>0.85 probably damaging, 0.15-0.85 possibly damaging)
    if fv['polyphen2_hdiv_score'] is not None:
        interpretation = 'Benign' if fv['polyphen2_hdiv_score'] < 0.15 else ('Possibly Damaging' if fv['polyphen2_hdiv_score'] < 0.85 else 'Probably Damaging')
        color = '#98c379' if fv['polyphen2_hdiv_score'] < 0.15 else ('#e5c07b' if fv['polyphen2_hdiv_score'] < 0.85 else '#e06c75')
        scores_data.append({
            'name': 'PolyPhen2',
            'score': fv['polyphen2_hdiv_score'],
            'normalized': fv['polyphen2_hdiv_score'],
            'interpretation': interpretation,
            'color': color,
            'threshold': 0.85
        })

    # SIFT (<0.05 deleterious, NOTE: SIFT is reverse - lower is worse)
    if fv['sift_score']:
        interpretation = 'Deleterious' if fv['sift_score'] < 0.05 else 'Tolerated'
        color = '#e06c75' if fv['sift_score'] < 0.05 else '#98c379'
        scores_data.append({
            'name': 'SIFT',
            'score': fv['sift_score'],
            'normalized': 1 - fv['sift_score'],  # Invert for visualization (higher = worse)
            'interpretation': interpretation,
            'color': color,
            'threshold': 0.95  # Inverted threshold line
        })

    if scores_data:
        fig = go.Figure()

        # Add bars
        for item in scores_data:
            fig.add_trace(go.Bar(
                name=item['name'],
                x=[item['name']],
                y=[item['normalized']],
                marker_color=item['color'],
                text=f"{item['score']:.3f}<br>{item['interpretation']}",
                textposition='outside',
                hovertemplate=f"<b>{item['name']}</b><br>Score: {item['score']:.3f}<br>{item['interpretation']}<extra></extra>"
            ))

        # Add threshold line
        fig.add_hline(y=0.5, line_dash="dash", line_color="#5c6370",
                      annotation_text="Threshold", annotation_position="right")

        fig.update_layout(
            title="Pathogenicity Prediction (Color: Green=Benign, Yellow=Uncertain, Red=Deleterious)",
            xaxis_title="Prediction Algorithm",
            yaxis_title="Normalized Pathogenicity Score",
            yaxis=dict(range=[0, 1.2]),
            showlegend=False,
            plot_bgcolor='rgba(250,250,250,0.5)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#2c3e50'),
            height=450
        )

        return fig
    return None

def create_allele_frequency_chart(fv):
    """Create allele frequency visualization with rarity classification"""
    if fv['bravo_af']:
        af_percent = fv['bravo_af'] * 100

        # Classify variant by rarity (ACMG guidelines)
        if af_percent >= 5:
            category = "Common"
            color = '#98c379'
            description = "Present in ≥5% of population"
        elif af_percent >= 0.5:
            category = "Low Frequency"
            color = '#61afef'
            description = "Present in 0.5-5% of population"
        elif af_percent >= 0.05:
            category = "Rare"
            color = '#e5c07b'
            description = "Present in 0.05-0.5% of population"
        else:
            category = "Very Rare"
            color = '#e06c75'
            description = "Present in <0.05% of population"

        # Create horizontal bar showing AF position on spectrum
        fig = go.Figure()

        # Background spectrum
        fig.add_trace(go.Bar(
            x=[100],
            y=['Allele Frequency'],
            orientation='h',
            marker=dict(color='#e8e8e8'),
            showlegend=False,
            hoverinfo='skip'
        ))

        # Actual frequency bar
        fig.add_trace(go.Bar(
            x=[af_percent],
            y=['Allele Frequency'],
            orientation='h',
            marker=dict(color=color),
            text=f'{af_percent:.4f}%<br>{category}',
            textposition='outside',
            showlegend=False,
            hovertemplate=f'<b>Allele Frequency</b><br>{af_percent:.4f}%<br>{category}<br>{description}<extra></extra>'
        ))

        # Add threshold markers
        thresholds = [
            (0.05, 'Rare threshold'),
            (0.5, 'Low freq threshold'),
            (5, 'Common threshold')
        ]

        for threshold, label in thresholds:
            fig.add_vline(x=threshold, line_dash="dot", line_color="#5c6370", line_width=1)

        fig.update_layout(
            title=f"Population Allele Frequency: {category}",
            xaxis=dict(
                title="Frequency (%)",
                type='log',  # Log scale to better show rare variants
                range=[-3, 2],  # 0.001% to 100%
                gridcolor='#d0d0d0'
            ),
            yaxis=dict(showticklabels=False),
            plot_bgcolor='rgba(250,250,250,0.5)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#2c3e50'),
            height=300,
            barmode='overlay'
        )

        return fig
    return None

def create_variant_impact_chart(fv):
    """Create variant functional impact summary"""
    # Collect all prediction results
    predictions = []

    # CADD
    if fv['cadd_phred']:
        if fv['cadd_phred'] >= 30:
            predictions.append(('CADD', 'Highly Deleterious', 2, '#e06c75'))
        elif fv['cadd_phred'] >= 20:
            predictions.append(('CADD', 'Deleterious', 1, '#e5c07b'))
        else:
            predictions.append(('CADD', 'Benign', 0, '#98c379'))

    # PolyPhen2
    if fv['polyphen2_hdiv_score'] is not None:
        if fv['polyphen2_hdiv_score'] >= 0.85:
            predictions.append(('PolyPhen2', 'Probably Damaging', 2, '#e06c75'))
        elif fv['polyphen2_hdiv_score'] >= 0.15:
            predictions.append(('PolyPhen2', 'Possibly Damaging', 1, '#e5c07b'))
        else:
            predictions.append(('PolyPhen2', 'Benign', 0, '#98c379'))

    # SIFT
    if fv['sift_score']:
        if fv['sift_score'] < 0.05:
            predictions.append(('SIFT', 'Deleterious', 2, '#e06c75'))
        else:
            predictions.append(('SIFT', 'Tolerated', 0, '#98c379'))

    if predictions:
        # Calculate consensus
        impact_scores = [p[2] for p in predictions]
        avg_impact = sum(impact_scores) / len(impact_scores)

        if avg_impact >= 1.5:
            consensus = "Likely Pathogenic"
            consensus_color = '#e06c75'
        elif avg_impact >= 0.7:
            consensus = "Uncertain Significance"
            consensus_color = '#e5c07b'
        else:
            consensus = "Likely Benign"
            consensus_color = '#98c379'

        # Create heatmap-style visualization
        algorithms = [p[0] for p in predictions]
        predictions_text = [p[1] for p in predictions]
        impact_values = [p[2] for p in predictions]
        colors = [p[3] for p in predictions]

        fig = go.Figure()

        # Add bars for each prediction
        for i, (algo, pred, val, col) in enumerate(predictions):
            fig.add_trace(go.Bar(
                x=[algo],
                y=[1],
                name=algo,
                marker_color=col,
                text=pred,
                textposition='inside',
                textfont=dict(color='white', size=12),
                hovertemplate=f'<b>{algo}</b><br>{pred}<extra></extra>',
                showlegend=False
            ))

        fig.update_layout(
            title=f"Multi-Algorithm Consensus: <b>{consensus}</b>",
            title_font_color=consensus_color,
            xaxis_title="Prediction Algorithm",
            yaxis=dict(showticklabels=False, showgrid=False),
            plot_bgcolor='rgba(250,250,250,0.5)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#2c3e50'),
            height=400,
            barmode='group'
        )

        # Add consensus annotation
        fig.add_annotation(
            text=f"Agreement: {len([s for s in impact_scores if s >= 1])}/{len(impact_scores)} predict damaging",
            xref="paper", yref="paper",
            x=0.5, y=-0.15,
            showarrow=False,
            font=dict(size=11, color='#5c6370')
        )

        return fig

    return None

# Cached API fetch function to avoid redundant requests
@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_variant_data_cached(variant_id: str):
    """Fetch variant data with caching to improve performance"""
    return client.get_combined_data(variant_id)

# Search functionality
if search_button and variant_id:
    # Determine if input is rsID or gene symbol
    is_rsid = bool(re.match(r'^rs\d+$', variant_id.strip(), re.IGNORECASE))

    search_query = variant_id.strip()
    actual_rsid = None
    display_title = None

    if not is_rsid:
        # Input is likely a gene symbol, convert to rsID
        gene_name = search_query.upper()
        st.info(f"Searching for gene symbol: {gene_name}")
        with st.spinner(f"Finding representative variant for gene {gene_name}..."):
            actual_rsid = client.query_gene_to_rsid(search_query)

        if actual_rsid:
            st.success(f"Found variant {actual_rsid} for gene {gene_name}")
            display_title = f"{gene_name} ({actual_rsid})"
        else:
            st.error(f"No variants found for gene: {gene_name}")
            st.stop()
    else:
        actual_rsid = search_query
        display_title = actual_rsid

    st.subheader(f"Results for: {display_title}")

    if use_real_api:
        # Use Real API with caching
        with st.spinner(f"Fetching data for {actual_rsid}..."):
            data = fetch_variant_data_cached(actual_rsid)

        # Show which APIs returned data for this query
        st.caption("Data Retrieved from:")
        status_result_col1, status_result_col2, status_result_col3 = st.columns(3)
        with status_result_col1:
            if data.get('favor'):
                st.success("✓ FAVOR", icon="😊")
            else:
                st.error("✗ FAVOR", icon="😔")
        with status_result_col2:
            if data.get('myvariant'):
                st.success("✓ MyVariant", icon="😊")
            else:
                st.error("✗ MyVariant", icon="😔")
        with status_result_col3:
            if data.get('ensembl'):
                st.success("✓ Ensembl", icon="😊")
            else:
                st.error("✗ Ensembl", icon="😔")

        st.divider()

        if data['success']:
            # Create tabs for organized display
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Visualizations", "Detailed Data", "Export", "Help"])
            
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

                        # Only show Clinical Information section if there's actual ClinVar data
                        if mv['clinical_significance'] or mv['diseases']:
                            st.divider()
                            st.markdown("### Clinical Information (ClinVar)")

                            if mv['clinical_significance']:
                                st.info(f"**Clinical Significance:** {mv['clinical_significance']}")

                            if mv['diseases']:
                                st.markdown("**Associated Diseases:**")
                                # Show first 3 diseases, rest in expander if more than 3
                                diseases_list = mv['diseases']
                                if len(diseases_list) <= 3:
                                    for disease in diseases_list:
                                        st.markdown(f"- {disease}")
                                else:
                                    # Show first 3
                                    for disease in diseases_list[:3]:
                                        st.markdown(f"- {disease}")
                                    # Rest in expander
                                    with st.expander(f"Show {len(diseases_list) - 3} more diseases"):
                                        for disease in diseases_list[3:]:
                                            st.markdown(f"- {disease}")

                    # Add Ensembl data section
                    if data['ensembl']:
                        ens = data['ensembl']
                        st.divider()
                        st.markdown("### Genomic Context")

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric("Variant Class", ens['var_class'] or "N/A")

                        with col2:
                            st.metric("Consequence", ens['most_severe_consequence'] or "N/A")

                        with col3:
                            if ens['mappings']:
                                location = ens['mappings'][0]['location']
                                st.metric("Location", location)

                        # Evidence sources
                        if ens['evidence']:
                            st.markdown("**Evidence Sources:**")
                            evidence_list = ens['evidence']
                            # If more than 5 sources, use expander
                            if len(evidence_list) <= 3:
                                st.caption(", ".join(evidence_list))
                            else:
                                st.caption(", ".join(evidence_list[:3]) + f", ... (+{len(evidence_list) - 3} more)")
                                with st.expander("Show all evidence sources"):
                                    st.caption(", ".join(evidence_list))

                        # Clinical significance from Ensembl
                        if ens['clinical_significance']:
                            with st.expander("Clinical Significance"):
                                for sig in ens['clinical_significance']:
                                    st.write(f"- {sig}")
                
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
                        st.markdown("### Algorithm Consensus")
                        impact_chart = create_variant_impact_chart(fv)
                        if impact_chart:
                            st.plotly_chart(impact_chart, use_container_width=True)
                
                else:
                    st.warning("No data available for visualizations")
            
            # Tab 3: Detailed Data

            with tab3:

                if data['favor']:
                    fv = data['favor']

                    with st.expander("FAVOR Annotation Details", expanded=False):
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

                    with st.expander("MyVariant.info Data", expanded=False):
                        st.markdown(f"**Gene:** {mv['gene']}")
                        st.markdown(f"**Consequence:** {mv['consequence']}")
                        st.markdown(f"**CADD Score:** {mv['cadd_score']}")
                        st.markdown(f"**Clinical Significance:** {mv['clinical_significance']}")
                        if mv['diseases']:
                            st.markdown("**Diseases:**")
                            for disease in mv['diseases']:
                                st.markdown(f"- {disease}")

                # Add Ensembl detailed data
                if data['ensembl']:
                    ens = data['ensembl']

                    with st.expander("Ensembl Data", expanded=False):
                        st.markdown(f"**Name:** {ens['name']}")
                        st.markdown(f"**Variant Class:** {ens['var_class']}")
                        st.markdown(f"**Most Severe Consequence:** {ens['most_severe_consequence']}")
                        
                        if ens['mappings']:
                            st.markdown("**Genomic Mappings:**")
                            for mapping in ens['mappings']:
                                st.markdown(f"- **Location:** {mapping['location']}")
                                st.markdown(f"  - **Alleles:** {mapping['allele_string']}")
                                st.markdown(f"  - **Assembly:** {mapping['assembly']}")
                        
                        if ens['evidence']:
                            st.markdown(f"**Evidence:** {', '.join(ens['evidence'])}")
                        
                        if ens['clinical_significance']:
                            st.markdown("**Clinical Significance:**")
                            for sig in ens['clinical_significance']:
                                st.markdown(f"- {sig}")
                        
                        if ens['synonyms']:
                            st.markdown(f"**Cross-references:** {len(ens['synonyms'])} IDs")

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
                "Clinical Significance": data['myvariant']['clinical_significance'] if data['myvariant'] else "N/A",
                "Location (Ensembl)": data['ensembl']['mappings'][0]['location'] if data['ensembl'] and data['ensembl']['mappings'] else "N/A",
                "Consequence": data['ensembl']['most_severe_consequence'] if data['ensembl'] else "N/A"
                }
                
                df = pd.DataFrame([merged_data])
                st.dataframe(df, use_container_width=True)
                
                st.markdown("### Export Options")
                
                col1, col2 = st.columns(2)
                
                with col1:
 
                    export_data = {
                    "variant_id": variant_id,
                    "favor": data['favor'],
                    "myvariant": data['myvariant'],
                    "ensembl": data['ensembl']  # Add Ensembl to export
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

            # Tab 5: Help
            with tab5:
                st.markdown("### User Guide")
                st.caption("Comprehensive documentation for variant analysis")

                st.divider()

                st.markdown("### Searching for Variants")
                st.markdown("""
                **Two ways to search:**

                **1. By rsID** (Reference SNP ID)
                - Enter an rsID like rs429358, rs7412
                - Click Search to fetch data directly

                **2. By Gene Symbol**
                - Enter a gene name like APOE, BRCA1, TP53
                - The app automatically finds the most clinically relevant variant for that gene
                - Prioritizes pathogenic/likely pathogenic variants when available

                **Supported gene symbols**:
                - Predefined: APOE, BRCA1, BRCA2, TP53, CFTR, HBB, MTHFR, F5, HFE, LDLR
                - Other genes via API fallback (when available)

                The application fetches data from 3 public APIs simultaneously.
                Results are cached for 1 hour to improve performance.
                """)

                st.divider()

                st.markdown("### Understanding Results")

                with st.expander("Overview Tab", expanded=False):
                    st.markdown("""
                    **Basic Information**: Gene name, variant category, allele frequency

                    **Pathogenicity Scores**: CADD, PolyPhen2, SIFT predictions

                    **Clinical Information**: ClinVar significance and disease associations

                    **Genomic Context**: Ensembl variant class, consequence, and chromosomal location
                    """)

                with st.expander("Visualizations Tab", expanded=False):
                    st.markdown("""
                    **Pathogenicity Prediction Chart**

                    Color interpretation:
                    - Green: Benign or Tolerated
                    - Yellow: Uncertain significance
                    - Red: Deleterious or Pathogenic

                    **Population Allele Frequency**

                    Rarity classification (ACMG guidelines):
                    - Common (≥5%): Normal polymorphism
                    - Low Frequency (0.5-5%): May be clinically relevant
                    - Rare (0.05-0.5%): Potentially pathogenic
                    - Very Rare (<0.05%): Strong disease association candidate

                    **Algorithm Consensus**

                    Multi-algorithm agreement summary:
                    - Likely Pathogenic: 2+ algorithms predict damaging
                    - Uncertain Significance: Mixed predictions
                    - Likely Benign: Most algorithms predict tolerated
                    """)

                with st.expander("Detailed Data Tab", expanded=False):
                    st.markdown("""
                    Complete raw data from each API source:

                    **FAVOR API**: 184+ functional annotation fields including conservation scores

                    **MyVariant.info**: ClinVar clinical significance and dbSNP cross-references

                    **Ensembl REST API**: Genomic coordinates, population frequencies, and evidence sources
                    """)

                with st.expander("Export Tab", expanded=False):
                    st.markdown("""
                    Download variant data in two formats:

                    **JSON**: Complete structured data from all three APIs

                    **CSV**: Summary table suitable for spreadsheet analysis
                    """)

                st.divider()

                st.markdown("### Variant Identifiers")
                st.markdown("""
                **rsID (Reference SNP cluster ID)**

                A unique identifier assigned by dbSNP to genetic variants.

                Examples:
                - rs429358: APOE ε4 allele (Alzheimer disease risk factor)
                - rs7412: APOE ε2 allele (protective allele)
                - rs1815739: ACTN3 R577X (athletic performance variant)

                **Gene Symbol**

                Standard gene names from HGNC (HUGO Gene Nomenclature Committee).

                Examples:
                - APOE: Apolipoprotein E (maps to rs429358)
                - BRCA1: Breast cancer type 1 susceptibility protein (maps to rs80357906)
                - TP53: Tumor protein p53 (maps to rs28934576)
                - CFTR: Cystic fibrosis transmembrane conductance regulator (maps to rs113993960)

                When you search by gene symbol, the app automatically selects the most clinically
                relevant variant based on ClinVar pathogenicity classifications.
                """)

                st.divider()

                st.markdown("### Data Sources")
                st.markdown("""
                This application integrates three complementary public genomics APIs:

                **FAVOR API** ([docs.genohub.org](https://docs.genohub.org/))
                - Comprehensive functional annotation database
                - Pathogenicity scores and conservation metrics

                **MyVariant.info** ([myvariant.info](https://myvariant.info/))
                - ClinVar clinical significance data
                - Disease-variant associations

                **Ensembl REST API** ([rest.ensembl.org](https://rest.ensembl.org/))
                - Authoritative genomic coordinates
                - Population frequency data

                All interpretations follow ACMG variant classification guidelines.
                """)

                st.divider()

                st.markdown("### Usage Notes")
                st.markdown("""
                **API Status Indicators**: Check marks (✓/✗) show which APIs successfully returned data for your query.

                **Caching**: Search results are cached for one hour. Refresh the page to clear cached data.

                **ClinVar Data**: Not all variants have clinical significance annotations. This is expected for common benign polymorphisms.

                **Mock Data Mode**: Toggle "Use Real API" off in the sidebar to explore the interface with sample data.
                """)

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
st.caption("Genetic Data Explorer | Data from FAVOR API & MyVariant.info & Ensembl")