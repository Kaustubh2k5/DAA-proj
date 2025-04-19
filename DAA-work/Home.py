import streamlit as st
import base64

# Page config
st.set_page_config(page_title="Food Distribution Optimizer", layout="wide")

# 🔧 Optional: Background image
def set_background(image_path):
    with open(image_path, "rb") as file:
        encoded = base64.b64encode(file.read()).decode()
    page_bg = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: white ;
    }}
    .main-container {{
        background-color: rgba(255, 255, 255, 0.85);
        border-radius: 1.5rem;
        padding: 3.5rem 3rem;
        margin: 2rem auto;
        max-width: 1000px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
    }}
    h1 {{
        text-align: center;
        color: #1b3b1f;
        font-size: 3rem;
        font-weight: bold;
        text-shadow: 1px 1px 2px #ffffff;
    }}
    h3 {{
        color: #184d47;
        margin-top: 1rem;
    }}
    ul {{
        margin-left: 1rem;
        line-height: 1.6;
    }}
    p, li {{
        color: white;
        font-size: 1.05rem;
    }}
    </style>
    """
    st.markdown(page_bg, unsafe_allow_html=True)

set_background("your_background.jpg") 

# 🧭 Main Content
st.markdown("<h1>🚚 Smart Food Routing System</h1>", unsafe_allow_html=True)
st.markdown("<div class='tagline'>Empowering Communities Through Smarter Food Delivery</div>", unsafe_allow_html=True)

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
