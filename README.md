# Institutional Trade Execution Simulator 📈

An interactive Streamlit application designed for professional traders and financial engineers to visualize and model **Market Impact** (Slippage) and **Execution Risk** for large orders.

![Streamlit UI Concept](https://img.shields.io/badge/Streamlit-Dark_Theme-00E676?style=flat-square&logo=streamlit)

## 📌 Features

*   **Market Impact Models**: Implements Square-Root, Temporary, and Permanent impact models.
*   **3D Slippage Visualization**: Interactive 3D surface plot (`Plotly`) mapping Participation Rate & Order Size against total slippage (bps).
*   **Interactive Simulation**: Generates an animated price path deviation (VWAP-style execution) taking into account the impact.
*   **Granular Parameter Adjustments**: Real-time side panel to tweak Risk Aversion ($\lambda$), Expected Volatility ($\sigma$), Average Daily Volume (ADV), and total Order Size ($Q$).
*   **Cost Breakdown**: Categorized view of the execution cost: Temporary Cost, Permanent Cost, and Risk Penalty.
*   **Slippage Heatmap**: Fast spatial evaluation map to identify low-cost (Green) vs. high-cost (Red) execution structures.

## 🛠️ Tech Stack

*   **UI Framework**: [Streamlit](https://streamlit.io/)
*   **Data Processing**: `numpy`, `pandas`
*   **Visualization Engine**: `plotly` (Graph Objects & Express)

## 🚀 Getting Started

### Prerequisites

Ensure you have Python 3.9+ installed, along with the required libraries.

```bash
pip install streamlit pandas numpy plotly
```

### Running the App Locally

Execute the following command in the root folder of the repository:

```bash
python3 -m streamlit run app.py
```

## 📐 Mathematical Models Used

1.  **Temporary Impact ($I_{temp}$)**: Drives the immediate cost of liquidity consumption, typically modeled as proportional to $\sigma \sqrt{\frac{Q}{V}}$.
2.  **Permanent Impact ($I_{perm}$)**: Drives the long-lasting information leakage into the market. It scales proportionally as the fraction of volume consumed over the execution span.
3.  **Risk Cost**: A penalty parameter assessing the variance/uncertainty of extending the execution over a longer horizon.

## 💡 Why This Tool?
Trading institutions routinely split large multi-million share blocks throughout the day. Navigating the trade-off between finishing the trade swiftly (which spikes *slippage*) versus trading too slowly (which subjects the stock to raw *execution risk* and standard volatility) is critical for optimal performance footprint.

---
*Created as a side project for modeling execution strategy and trading analytics.*
