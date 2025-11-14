# Genetic Data Explorer

A professional web-based application for comprehensive genetic variant analysis, integrating multiple public genomics APIs with interactive visualizations following ACMG clinical guidelines.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## 🧬 Project Overview

This application provides a unified interface for exploring genetic variants by:

* **Multi-API Integration**: Fetches and merges data from 3 complementary public genomics databases
* **Clinical Interpretation**: Provides pathogenicity predictions using industry-standard algorithms (CADD, PolyPhen2, SIFT)
* **ACMG-Compliant Visualizations**: Professional charts for variant frequency classification and clinical decision support
* **Interactive Interface**: Real-time search with tabbed data organization and export capabilities

---

## ✨ Key Features

### 📊 Professional Visualizations
- **Pathogenicity Prediction Chart**: Multi-algorithm consensus with color-coded clinical interpretations
- **Allele Frequency Spectrum**: ACMG-based rarity classification (Common/Low Freq/Rare/Very Rare)
- **Algorithm Consensus Analysis**: Aggregates predictions from CADD, PolyPhen2, and SIFT

### 🔬 Comprehensive Data Sources
- **FAVOR API**: Functional annotation with 184+ data fields including conservation scores
- **MyVariant.info**: Clinical significance from ClinVar and disease associations
- **Ensembl REST API**: Genomic coordinates, variant consequences, and population frequencies

### 💾 Data Export
- JSON and CSV export for downstream analysis
- Structured data tables with all annotation fields

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Internet connection for API access

### Installation

```bash
# Clone the repository
git clone https://github.com/dingonewen/genetic_data_explorer.git
cd genetic_data_explorer

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows (Git Bash):
source venv/Scripts/activate
# Windows (PowerShell):
venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Run the Application

```bash
streamlit run app.py
```

The application will open automatically in your browser at `http://localhost:8501`

---

## 📁 Project Structure

```
genetic_data_explorer/
├── app.py                  # Main Streamlit application
├── src/
│   └── api_client.py      # API integration client
├── mock_data/             # Mock data for testing
│   ├── favor_mock.json
│   ├── favor_mock2.json
│   └── gtex_mock.json
├── test/                  # Test files
│   └── conftest.py
├── requirements.txt       # Python dependencies
└── README.md             # Documentation
```

---

## 🔗 API Selection & Rationale

This project integrates **3 public REST APIs** that provide complementary genetic variant information:

### 1. **FAVOR API** (Primary Functional Annotation)
- **Endpoint**: `https://api.genohub.org/v1/rsids/{rsid}`
- **Why Selected**:
  - Comprehensive functional annotation database with 184+ fields
  - Includes pathogenicity scores (CADD, PolyPhen2, SIFT, MutationTaster)
  - Provides conservation scores and exonic/intronic annotations
  - No API key required, accepts rsID queries directly

- **Key Data**:
  - CADD PHRED scores (>20 = deleterious)
  - PolyPhen2 predictions (protein function impact)
  - SIFT scores (evolutionary conservation)
  - Allele frequencies from BRAVO database

### 2. **MyVariant.info** (Clinical Significance)
- **Endpoint**: `https://myvariant.info/v1/variant/{rsid}`
- **Why Selected**:
  - Aggregates ClinVar clinical significance data
  - Provides disease-variant associations
  - Includes additional CADD and dbSNP cross-references
  - Free public API with no authentication

- **Key Data**:
  - ClinVar clinical significance (Pathogenic/Benign/VUS)
  - Associated diseases and conditions
  - Gene-level annotations
  - Variant consequences

### 3. **Ensembl REST API** (Genomic Context)
- **Endpoint**: `https://rest.ensembl.org/variation/human/{rsid}`
- **Why Selected**:
  - Authoritative source for genomic coordinates
  - Provides variant class and most severe consequence
  - Includes population frequency data across ethnicities
  - Well-maintained by EMBL-EBI with comprehensive documentation

- **Key Data**:
  - Genomic location and assembly coordinates
  - Variant class (SNP, insertion, deletion, etc.)
  - Most severe consequence (missense, synonymous, etc.)
  - Evidence sources and cross-references

### APIs Considered but NOT Used

**GTEx API**:
- ❌ Returns tissue expression metadata, not variant-specific data
- ❌ Requires Ensembl Gene IDs (ENSG*) instead of rsIDs
- ❌ Better suited for expression QTL studies than variant annotation

**dbSNP/NCBI API**:
- ❌ No structured REST API for variant queries
- ❌ Data already aggregated in MyVariant.info

**gnomAD API**:
- ❌ GraphQL interface adds complexity
- ❌ Frequency data already available in FAVOR/Ensembl

---

## 🎯 Usage Examples

### Basic Search
1. Enter a variant rsID (e.g., `rs429358`, `rs7412`, `rs1815739`)
2. Click **Search** or use quick example buttons
3. View results across 4 organized tabs:
   - **Overview**: Key metrics and annotations
   - **Visualizations**: Clinical interpretation charts
   - **Detailed Data**: Complete API responses
   - **Export**: Download data in JSON/CSV

### Interpreting Results

**Pathogenicity Chart**:
- 🟢 Green bars = Benign/Tolerated
- 🟡 Yellow bars = Uncertain significance
- 🔴 Red bars = Deleterious/Pathogenic

**Allele Frequency**:
- Common (≥5%): Likely polymorphism
- Rare (<0.5%): May be clinically significant
- Very Rare (<0.05%): Candidate pathogenic variant

**Algorithm Consensus**:
- "Likely Pathogenic": 2+ algorithms predict damaging
- "Uncertain Significance": Mixed predictions
- "Likely Benign": Most algorithms predict tolerated

---

## 🛠️ Dependencies

```
streamlit      # Web application framework
requests       # HTTP API client
pandas         # Data manipulation
plotly         # Interactive visualizations
```

Install all dependencies:
```bash
pip install -r requirements.txt
```

---

## 🧪 Testing

Mock data is provided for offline testing:

```bash
# Toggle "Use Real API" off in the sidebar
# Search using mock data from mock_data/ folder
```

---

## 📊 Bonus Features Implemented

- ✅ **3 Public APIs** integrated (exceeds minimum requirement)
- ✅ **Interactive Visualizations** with clinical interpretations
- ✅ **ACMG Guideline Compliance** for variant classification
- ✅ **Multi-algorithm Consensus** analysis
- ✅ **Professional UI** with One Dark Atom theme
- ✅ **Data Export** capabilities (JSON/CSV)
- ✅ **Real-time API status** indicators

---

## 👨‍💻 Author

**Yiwen Ding**
- GitHub: [@dingonewen](https://github.com/dingonewen)
- Project: Genetic Data Explorer

---

## 📄 License

MIT License - see LICENSE file for details

---

## 🙏 Acknowledgments

- **FAVOR**: Functional annotation of variants online resource
- **MyVariant.info**: Biothings API for variant annotations
- **Ensembl**: EMBL-EBI genomics database
- **ACMG**: Standards and guidelines for variant interpretation

---

## 📚 References

1. FAVOR API Documentation: https://docs.genohub.org/
2. MyVariant.info API: https://myvariant.info/
3. Ensembl REST API: https://rest.ensembl.org/
4. ACMG Standards: Richards et al. (2015) Genet Med

