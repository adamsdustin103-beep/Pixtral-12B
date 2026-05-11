import streamlit as st
from mistralai import Mistral
import PIL.Image
import io
import csv
import base64

st.set_page_config(page_title="Pixtral 12B Metadata AI", layout="wide")
st.title("💠 Pixtral 12B: Metadata Generator")

# সাইডবারে এপিআই কি
api_key = st.sidebar.text_input("Enter Mistral API Key", type="password")

def encode_image(image_file):
    """ছবিকে বেস৬৪ ফরম্যাটে রূপান্তর"""
    return base64.b64encode(image_file.read()).decode('utf-8')

if api_key:
    client = Mistral(api_key=api_key)
    
    uploaded_files = st.file_uploader("আপনার ফাইলগুলো সিলেক্ট করুন...", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

    if uploaded_files:
        if st.button("Generate with Pixtral 12B"):
            results = []
            
            for uploaded_file in uploaded_files:
                st.write(f"এনালাইসিস হচ্ছে: {uploaded_file.name}")
                
                try:
                    # ছবি এনকোড করা
                    base64_image = encode_image(uploaded_file)
                    
                    # Pixtral 12B মডেল কল করা
                    response = client.chat.complete(
                        model="pixtral-12b-2409",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": "Analyze this for Adobe Stock. Provide a Title (max 100 chars) and 45 keywords. Format: Title: [Title] Keywords: [Keywords separated by commas]"},
                                    {"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_image}"}
                                ]
                            }
                        ]
                    )
                    
                    res_text = response.choices[0].message.content
                    
                    # ডাটা প্রসেসিং
                    title = res_text.split('Title:')[1].split('Keywords:')[0].strip()
                    keywords = res_text.split('Keywords:')[1].strip()
                    
                    results.append([uploaded_file.name, title, keywords])
                    st.success(f"সফল: {uploaded_file.name}")
                    
                except Exception as e:
                    st.error(f"ভুল হয়েছে ({uploaded_file.name}): {e}")

            if results:
                output = io.StringIO()
                writer = csv.writer(output)
                writer.writerow(['Filename', 'Title', 'Keywords'])
                writer.writerows(results)
                st.download_button("📥 Download CSV", output.getvalue(), "metadata.csv", "text/csv")
else:
    st.sidebar.warning("অনুগ্রহ করে Mistral API Key দিন।")
