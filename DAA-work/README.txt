# Food Distribution Optimizer

## Overview

The **Food Distribution Optimizer** is a smart system designed to redistribute surplus food from donors (restaurants, events, grocery stores) to NGOs and shelters in need. It leverages real-time location data, optimization algorithms, and an intuitive dashboard to streamline food rescue efforts, minimizing wastage and maximizing social impact.

Built using **Python**, **Streamlit**, and **Google Maps API**, this project enables efficient donor-NGO-volunteer coordination and route optimization.

## Features

- 🌍 Real-time Map View of Donors, NGOs, and Volunteers
- ✅ Intelligent Matching of Food Surplus to NGO Requests
- ➡️ Shortest Route Calculation for Food Deliveries
- 🌐 User-friendly Streamlit Dashboard
- 📝 Export and Download Delivery Logs

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python, pandas, NumPy
- **APIs**: Google Maps Geocoding API, Directions API
- **Visualization**: Folium, Plotly, Seaborn
- **Deployment Ready**: Designed for easy hosting (Streamlit Cloud, AWS, Heroku)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/food-distribution-optimizer.git
cd food-distribution-optimizer
```

2. Install required packages:

```bash
pip install -r requirements.txt
```

3. Set up your Google Maps API Key:

- Create a `.env` file and add:

```
GOOGLE_MAPS_API_KEY=your_api_key_here
```
4. Activate venv scripts:
```bash
.\venv\Scripts\Activate.ps1
```

5. Run the Streamlit app:

```bash
streamlit run app.py
```

## Project Structure

```bash
/
|-- app.py               # Main Streamlit application
|-- routes.py            # Routing and optimization logic
|-- utils.py             # Helper functions
|-- data/                # Sample datasets (donors, NGOs)
|-- requirements.txt     # Python package requirements
|-- README.md             # Project overview (this file)
```

## Future Enhancements

- 📱 Mobile App for Volunteers
- 🤖 AI-based Demand Prediction for NGOs
- 🚿 IoT Integration for Food Safety Monitoring
- ⛓ Blockchain for Food Traceability


## Authors

- Kaustubh Sardesai(https://github.com/Kaustubh2k5)
- Govardhan Tandle(https://github.com/iamgovi)

---

> Empowering communities, reducing hunger, and saving the planet one meal at a time. 🌱
