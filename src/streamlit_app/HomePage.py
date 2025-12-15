import streamlit as st
from components.sidebar import show_sidebar # Import the function from your sidebar.py

st.set_page_config(
    page_title="DIGICare - We serve the nation ",
    page_icon="☮️",
    layout="wide"
)

st.markdown(
    "<h1 style='font-size: 1.8rem; font-weight: 700; margin-bottom: 0.5rem;'>☮️ DIGICare Insurance</h1>",
    unsafe_allow_html=True
)
#st.title("☮️ DigiCare Insurance")

# Call the function to display the custom sidebar content
show_sidebar()
#st.sidebar.success("Welcome to DigiHealth Insurance App!")

def hide_menuItem():
    st.markdown(
        """
        <style>
        /* Target the menu item and make it invisible */
        span[label="Configure"] {
            visibility: hidden; /* hide background */
            display: none; /* hide the entire element */
        }
        </style>
        """,
        unsafe_allow_html=True
    )
#Hide the "Configure" menu item
hide_menuItem()

st.markdown(
    """
    <div style='background-color: #f5f5f5; padding: 16px 0 16px 24px; border-radius: 10px; display: flex; align-items: center; gap: 16px;'>
        <div style='background: #fff; box-shadow: 0 2px 8px rgba(0,0,0,0.07); border-radius: 12px; padding: 10px 32px; display: inline-block;'>
            <span style='color: #d32f2f; font-weight: bold; font-size: 20px;'>Health</span>
        </div>
        <div style='padding: 10px 32px; display: inline-block;'>
            <span style='color: #616161; font-weight: 500; font-size: 20px;'>Car</span>
        </div>
         <div style='padding: 10px 32px; display: inline-block;'>
            <span style='color: #616161; font-weight: 500; font-size: 20px;'>Bike</span>
        </div>
        <div style='padding: 10px 32px; display: inline-block;'>
            <span style='color: #616161; font-weight: 500; font-size: 20px;'>Travel</span>
        </div>
        <div style='padding: 10px 32px; display: inline-block;'>
            <span style='color: #616161; font-weight: 500; font-size: 20px;'>Home</span>
        </div>
         <div style='padding: 10px 32px; display: inline-block;'>
            <span style='color: #616161; font-weight: 500; font-size: 20px;'>Pet</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
#st.markdown("")
st.markdown("""
**Health insurance** provides a financial protection from unexpected medical emergency that can occur 
            due to any illnesses or accident. DIGICare brings a variety of health insurance products 
            for different needs which provides benefits like cashless hospitalisation through its large network,
            tax savings under `Section 80D`, no-claim bonus and many more. 
            <a href="https://your-link-here.com" style="color: red; text-decoration: underline;">Explore more..</a>

""",unsafe_allow_html=True)

st.markdown("<hr style='margin-top:8px; margin-bottom:16px; border: none; border-top: 1.5px solid #eee;'>", unsafe_allow_html=True)
#st.divider()

#st.subheader("- Our Offerings -")

#st.write("Use the navigation links in the sidebar to switch between pages.")


# Three cards side by side using columns and st.button for navigation, preserving card design
card_titles = ["Review & Underwriting", "CAT Triage", "Litigation & Subrogation "]
card_details = [
    ["Risk evaluation", "Reduce conflicts", "Best premium offer"],
    ["Claim prioritization", "Imagery analysis", "Faster settlement"],
    ["Low premium", "Cost recovery", "Protecting rights"]
]
cols = st.columns(3, gap="large")

for i, col in enumerate(cols):
    with col:
        with st.container():
            list_items = "".join([f"<li>{item}</li>" for item in card_details[i]])
            card_html = f"""
            <div style='background: #f7f7fa; border-radius: 14px; padding: 12px 32px 20px 32px; width: 100%; max-width: 420px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);'>
                <div style='font-size: 17px; font-weight: 400; color: #174ea6; margin-bottom: 8px;'>{card_titles[i]}</div>
                <ul style='margin-bottom: 24px; color: #444; font-size: 16px;'>
                    {list_items}
                </ul>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            button_cols = st.columns(2, gap="small")
            with button_cols[0]:
                if st.button("Detail View", key=f"view_{i}"):
                    st.switch_page("./pages/2_📊_Detail.py")
            with button_cols[1]:
                if st.button("New Review", key=f"buy_{i}"):
                    st.switch_page("./pages/1_🙋‍♂️_Application.py")


