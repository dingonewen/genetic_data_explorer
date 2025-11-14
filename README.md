# Genetic Data Explorer

A lightweight Streamlit application for exploring and visualizing genetic variant data.

## Project Overview

This project is a web-based genetic data explorer that can:

* Fetch genetic variant information from multiple public APIs
* Merge and display information from different data sources
* Provide an interactive data visualization interface

---

## Quick Start

### 1. Install Dependencies

```bash
# Create and activate virtual environment (Linux / macOS)
python -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
venv\Scripts\Activate.ps1

# Install required packages
pip install -r requirements.txt
```

### 2. Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at: **[http://localhost:8501](http://localhost:8501)**

---

## Dependencies

* **streamlit** – Web application framework
* **requests** – HTTP library for API calls
* **pandas** – Data manipulation and analysis
* **plotly** – Data visualization

You can pin versions in `requirements.txt`, for example:

```
streamlit
requests
pandas
plotly
```

---

## Project Structure

```
genetic_data_explorer/
├── app.py              # Main application file
├── mock_data/          # Mock data files (for development/testing)
├── src/                # Source code (API clients, merge logic, viz helpers)
├── tests/              # Test files
├── requirements.txt    # Dependencies list
└── README.md           # Project documentation
```

---

## Development Plan

1. Environment setup
2. Install dependencies
3. Create basic Streamlit application (search + display layout)
4. Create mock data for integration testing
5. Implement data fetching and merging logic
6. Integrate real APIs and caching
7. Add interactive data visualizations (Plotly)
8. Improve error handling and logging
9. Add unit/integration tests and CI

---

## APIs (Planned)

* **FAVOR API** – Functional annotation of variants
* **GTEx API** – Gene expression data
* **AlphaGenome API** – Variant and functional annotations

> Note: add API keys / rate-limit handling and caching when integrating.

---

## Example Usage

1. Start the app:

```bash
streamlit run app.py
```

2. In the app UI, enter a variant ID such as `rs429358` or `rs7412` and click **Search** to view merged results from multiple sources.

---

## Author

Yiwen Ding (github@dingonewen)

---

## License

MIT License

