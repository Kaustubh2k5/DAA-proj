import streamlit as st
import base64

# Page config
st.set_page_config(page_title="Food Distribution Optimizer", layout="wide")

# 🔧 Optional: Background image
def set_background(image_path):
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    bg_css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #f5f5f5;
    }}
    .main-container {{
        background-color: rgba(0, 0, 0, 0.7);
        border-radius: 1.5rem;
        padding: 3rem;
        margin: 2rem auto;
        max-width: 1000px;
        box-shadow: 0 4px 25px rgba(0,0,0,0.4);
        animation: fadeIn 1.2s ease-in-out;
    }}
    h1 {{
        text-align: center;
        color: #90ee90;
        font-size: 3rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.6);
    }}
    h2, h3 {{
        color: #ffffff;
        font-weight: bold;
        margin-top: 2rem;
    }}
    ul {{
        margin-left: 1rem;
        line-height: 1.6;
    }}
    .tagline {{
        font-size: 1.2rem;
        color: #a5d6a7;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 500;
    }}
    .highlight {{
        background: rgba(255, 255, 255, 0.05);
        border-left: 4px solid #66bb6a;
        padding: 1rem 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        color: #eeeeee;
        box-shadow: 0 1px 6px rgba(0,0,0,0.3);
        font-size: 1rem;
    }}
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    </style>
    """
    st.markdown(bg_css, unsafe_allow_html=True)

# Set background image (replace with your image filename)

# 🧭 Main Content
st.markdown("<h1>🚚 Smart Food Routing System</h1>", unsafe_allow_html=True)
st.markdown("<div class='tagline'>Empowering Communities Through Smarter Food Delivery</div>", unsafe_allow_html=True)

st.markdown("<div class='main-container'>", unsafe_allow_html=True)

st.markdown("""
<h2>⚠️ The Challenge</h2>
<div class="highlight">
Even though we have food in surplus, it fails to reach the hungry in time due to poor coordination and inefficient routing.
</div>

---

<h2>💡 Our Smart Solution</h2>

We bring together technology and community to:
<ul>
    <li>🏢 Connect <b>NGOs</b> with food surplus</li>
    <li>🚐 Assign <b>Volunteers</b> for efficient deliveries</li>
    <li>📍 Map <b>Destinations</b> in need</li>
    <li>🧠 Calculate <b>Optimized Routes</b> using AI</li>
</ul>

---

<h2>🎯 Our Mission</h2>
<div class="highlight">
To ensure no food goes to waste and no person goes hungry — using smart, community-powered routing.
</div>

Together, let's eliminate food waste and fill every empty plate.

""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
