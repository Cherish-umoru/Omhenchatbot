import streamlit as st
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Load restaurant information
def load_restaurant_info():
    with open("restaurant_info.txt", "r", encoding="utf-8") as file:
        return file.read()

# Create system prompt
def create_system_prompt():
    restaurant_info = load_restaurant_info()
    return f"""You are Omhen, the official AI concierge for Unu Omhen,
    a premium fine dining Nigerian restaurant located in
    Ikeja GRA, Lagos.
    
    You speak in a warm, professional and proudly Nigerian tone.
    You are helpful, knowledgeable and elegant in your responses.
    You only answer questions related to Unu Omhen restaurant.
    If asked anything unrelated to the restaurant, politely 
    redirect the conversation back to how you can help 
    with the restaurant.
    
    Here is everything you need to know about Unu Omhen:
    
    {restaurant_info}"""

# Streamlit app configuration
st.set_page_config(
    page_title="Omhen | Unu Omhen Concierge",
    page_icon="🍽️",
    layout="centered"
)

# App header
st.image("logo.png", width=150)
st.title("Welcome to Unu Omhen")
st.subheader("I am Omhen, your personal AI concierge")
st.write("Hello and welcome to Unu Omhen — Good Mouth, Great Food! How can I assist you today?")
st.divider()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask Omhen anything about Unu Omhen..."):
    
    # Add user message to chat history
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get response from OpenRouter
    with st.chat_message("assistant"):
        with st.spinner("Omhen is thinking..."):
            
            # Build messages list
            messages_for_ai = [
                {
                    "role": "system",
                    "content": create_system_prompt()
                }
            ]
            
            # Add conversation history
            for msg in st.session_state.messages:
                messages_for_ai.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Send to OpenRouter
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://unuomhen.com",
                    "X-Title": "Unu Omhen Concierge"
                },
                json={
                    "model": "nvidia/nemotron-3-super-120b-a12b:free",
                    "messages": messages_for_ai,
                    "max_tokens": 1000,
                    "temperature": 0.7
                },
                timeout=30
            )
            
            # Get response
            result = response.json()
            
            # Check if response is valid
            if "choices" in result:
                omhen_response = result["choices"][0]["message"]["content"]
            else:
                error_msg = result.get("error", {}).get("message", "Unknown error")
                omhen_response = f"I apologize, I am unable to process your request right now. Please try again! (Error: {error_msg})"
            
            # Display response
            st.markdown(omhen_response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({
        "role": "assistant",
        "content": omhen_response
    })