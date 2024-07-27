import sqlite3
from datetime import datetime, timedelta
import streamlit as st
from PIL import Image
import os
import google.generativeai as genai
from gtts import gTTS
from deep_translator import GoogleTranslator
import firebase_admin
from firebase_admin import credentials, auth
from datetime import datetime, timedelta
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# OpenAI Client initialization
client = OpenAI(base_url='<change_with_your_url>', api_key=os.getenv('OPENAI_API_KEY'))

# Firebase Admin SDK initialization 
if not firebase_admin._apps:
    cred = credentials.Certificate("your `serviceAccountKey.json` file")
    firebase_admin.initialize_app(cred)

# Firebase API key
FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY')

def verify_password(email, password):
    url = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}'
    payload = {
        'email': email,
        'password': password,
        'returnSecureToken': True
    }
    response = requests.post(url, data=payload)
    return response.json()

def translate_text(text, target_language):
    translator = GoogleTranslator(source='auto', target=target_language)
    translation = translator.translate(text)
    return translation

genai.configure(api_key=os.getenv("GOOGLE_GENERATIVEAI_API_KEY")) 

generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
}

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""

def login():
    email = st.session_state.email
    password = st.session_state.password
    result = verify_password(email, password)
    if 'idToken' in result:
        st.session_state.authenticated = True
        st.session_state.user_email = email
        st.rerun()
    else:
        st.error(result.get('error', {}).get('message', 'Login failed'))

def signout():
    st.session_state.authenticated = False
    st.session_state.user_email = ""
    st.session_state.email = ""
    st.session_state.password = ""
    st.rerun()

def create_account():
    email = st.session_state.email
    password = st.session_state.password
    try:
        user = auth.create_user(
            email=email,
            password=password
        )
        st.success('User created successfully')
    except Exception as e:
        st.error(e)

# Main interface
st.image("logo.png", width=200)
st.title("SightSync Harmony")

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            last_generation_time TEXT,
            generation_count INTEGER
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def get_user_data(email):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT last_generation_time, generation_count FROM users WHERE email = ?', (email,))
    row = cursor.fetchone()
    conn.close()
    if row:
        last_generation_time, generation_count = row
        return datetime.fromisoformat(last_generation_time), generation_count
    else:
        return None

def insert_user_data(email):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (email, last_generation_time, generation_count) VALUES (?, ?, ?)',
                   (email, (datetime.now() - timedelta(days=1)).isoformat(), 0))
    conn.commit()
    conn.close()

def update_user_data(email, last_generation_time, generation_count):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET last_generation_time = ?, generation_count = ? WHERE email = ?',
                   (last_generation_time.isoformat(), generation_count, email))
    conn.commit()
    conn.close()

def main():
    if st.session_state.authenticated:
        # Display welcome message for authenticated user
        user_email = st.session_state.user_email
        st.sidebar.header(f"Welcome, {user_email}!")

        # Add elements to the sidebar
        st.sidebar.header("Select the operation")
        selected_page = st.sidebar.radio("Choose", ["Detect", "Translate", "Custom Prompt", "Generate Image", "Sign Out"])

        if selected_page == "Sign Out":
            signout()
        
        elif selected_page == "Generate Image":

            st.text("Enter a prompt to generate an image. With the free plan, you can generate up to 2 images per day. Upgrade to the premium plan for unlimited image generation.")

            prompt = st.text_input('Enter a prompt')

            user_data = get_user_data(user_email)
            if user_data is None:
                insert_user_data(user_email)
                user_data = get_user_data(user_email)

            last_generation_time, generation_count = user_data
            # print(last_generation_time)

            # Check and update the generation count if 24 hours have passed
            current_time = datetime.now()
            # print(current_time)
            time_since_last_generation = current_time.date() - last_generation_time.date()
            # print(time_since_last_generation)

            if time_since_last_generation.days >= 1:
                generation_count = 0
                last_generation_time = current_time
                update_user_data(user_email, last_generation_time, generation_count)

            # Show current rate limit
            st.write(f"Image generation count for today: {generation_count}/2")

            if st.button("Generate Image"):
                if generation_count < 2:
                    try:
                        with st.spinner('Generating...'):
                            response = client.images.generate(
                                model='sdxl',
                                prompt=prompt
                            )
                            image_url = response.data[0].url

                        st.image(image_url, caption='Generated Image')

                        image_content = requests.get(image_url).content

                        st.download_button(label="Download Image", data=image_content, file_name="generated_image.png", mime="image/png")

                        generation_count += 1
                        last_generation_time = current_time

                        # Update user data in SQLite
                        update_user_data(user_email, last_generation_time, generation_count)

                        st.text("Interested in our premium plan? Click the button below, and we'll send you the details via email.")
                        st.markdown('<a href="mailto:archismwanchatterjee@gmail.com?subject=Interest%20in%20Premium%20Plan&body=Hi,%20I%27m%20interested%20in%20the%20premium%20plan.%20Please%20send%20me%20the%20details."><button>Contact Us</button></a>', unsafe_allow_html=True)

                        st.text("")
                        if st.button("Try another prompt"):
                            st.rerun()

                        st.success("Thanks for visiting 🤩!!")

                    except Exception as e:
                        st.error(f"An error occurred: {e}")
                else:
                    st.error("You have reached your daily limit for image generation. Please try again in 24 hours. For unlimited image generations, consider upgrading to our premium plan. Contact us for more details.")
                    st.markdown('<a href="mailto:archismwanchatterjee@gmail.com?subject=Interest%20in%20Premium%20Plan&body=Hi,%20I%27m%20interested%20in%20the%20premium%20plan.%20Please%20send%20me%20the%20details."><button>Contact Us</button></a>', unsafe_allow_html=True)
   
        elif selected_page == "Custom Prompt":
            
            disclaimer_message = """Upload any image and provide a custom prompt related to the image to work upon.Must include 'In this image'."""

            st.write("")
            with st.expander("Disclaimer ⚠️", expanded=False):
                st.markdown(disclaimer_message)
            
            uploaded_image = st.file_uploader("Choose an image ...",  type=None)

            if uploaded_image is not None:
                st.image(uploaded_image, caption="Uploaded Image.", use_column_width=True)

                image = Image.open(uploaded_image)
                width, height = image.size
                st.write("Image Dimensions:", f"{width}x{height}")
                
                st.write("Provide the custom prompt related to the image")
                prompt = st.text_input("Enter your prompt here")
                st.write("The current prompt is", prompt)

                if "in this image" not in prompt.lower():
                    st.warning("Please include 'In this image'")
                else:
                    if st.button("Generate"):
                        with st.spinner('Generating...'):
                            vision_model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest", generation_config=generation_config)
                            response = vision_model.generate_content([prompt, image])
                            st.session_state.objects_detected_text = response.text

                        st.write("The objects detected are \n")
                        st.write(st.session_state.objects_detected_text)

                        tts = gTTS(text=st.session_state.objects_detected_text, lang='en')
                        tts.save("output.mp3")
                        st.audio("output.mp3", format='audio/mp3', start_time=0)

                        if st.session_state.objects_detected_text:
                            
                            st.download_button(label="Download Results as Text",
                                data=st.session_state.objects_detected_text,
                                file_name="detected_objects.txt",
                                mime="text/plain"
                            )
                    
                        st.text("")
                        st.text("Go to Translate page from sidebar for translating the output")

                        st.text("")
                        st.success("Thanks for visiting 🤩!!")
                        
                        if st.button("Try another prompt"):
                            st.rerun()
                        

        elif selected_page == "Detect":
            disclaimer_message = """This is an object detector model so preferably use images containing different objects, tools... for best results 🙂."""

            st.write("")
            with st.expander("Disclaimer ⚠️", expanded=False):
                st.markdown(disclaimer_message)

            uploaded_image = st.file_uploader("Choose an image ...",  type=None)

            if uploaded_image is not None:
                st.image(uploaded_image, caption="Uploaded Image.", use_column_width=True)

                image = Image.open(uploaded_image)
                width, height = image.size
                st.write("Image Dimensions:", f"{width}x{height}")

                if st.button("Identify the objects"):
                    
                    with st.spinner('Detecting...'):
                        vision_model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest", generation_config=generation_config)
                        
                        response = vision_model.generate_content(["Extract the objects in the provided image and output them in a list along with their description, do not use an asterisk. Also, detect the environment of the image. Suppose the image contains famous personalities then try to identify them too.", image])
                        
                        st.session_state.objects_detected_text = response.text

                    st.write("The objects detected are \n")
                    st.write(st.session_state.objects_detected_text)

                    tts = gTTS(text=st.session_state.objects_detected_text, lang='en')
                    tts.save("output.mp3")
                    st.audio("output.mp3", format='audio/mp3', start_time=0)

                    if st.session_state.objects_detected_text:
                        
                        st.download_button(label="Download Results as Text",
                            data=st.session_state.objects_detected_text,
                            file_name="detected_objects.txt",
                            mime="text/plain"
                        )
                  
                    st.text("")
                    st.text("Go to Translate page from sidebar for translating the output")

                    st.text("")
                    st.success("Thanks for visiting 🤩!!")
                    st.info("For trying out with another image just click on browse files, enjoy 😄!!!")

                if st.button("Explain:"):
                    with st.spinner("Explaining..."):
                    
                        vision_model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest", generation_config=generation_config)
                        
                        response = vision_model.generate_content(["What is this picture?.", image])

                        st.session_state.objects_detected_text = response.text

                    st.write("The objects detected are \n")
                    st.write(st.session_state.objects_detected_text)

                    tts = gTTS(text=st.session_state.objects_detected_text, lang='en')
                    tts.save("output.mp3")
                    st.audio("output.mp3", format='audio/mp3', start_time=0)
                    

                    if st.session_state.objects_detected_text:
                        
                        st.download_button(label="Download Results as Text",
                            data=st.session_state.objects_detected_text,
                            file_name="detected_objects.txt",
                            mime="text/plain"
                        )

                    st.text("")
                    st.text("Go to Translate page from sidebar for translating the output")

                    st.text("")
                    st.success("Thanks for visiting 🤩!!")
                    st.info("For trying out with another image just click on browse files, enjoy 😄!!!")
        
        elif selected_page == "Translate":

            # Check if objects_detected_text is not set or is empty
            if not st.session_state.get('objects_detected_text'):
                st.warning("No objects are detected. Please use any image to detect the objects in the detect page.")
            else:
                st.write("The text to be translated : ")
                st.text("")
                st.write(st.session_state.objects_detected_text)
                target_language = st.selectbox("Select target language:", ["Gujrati(gu)", "Kannada(kn)", "Malayalam(ml)", "Marathi(mr)", "Urdu(ur)", "Hindi(hi)", "Bengali(bn)", "Tamil(ta)", "Telegu(te)","American(en-US)", "Russian(ru)", "Spanish(es)", "German(de)", "Portuguese(pt)","Arabic(ar)", "French(fr)", "Italian(it)", "Japanese(ja)", "Korean(ko)", "Chinese(zh)"])
                language=target_language[-3:-1]

                # Translate text on button click
                if st.button("Translate"):
                    translated_text = translate_text(st.session_state.objects_detected_text, language)
                    st.success(f"Translation: {translated_text}")
                    
                    tts = gTTS(text=translated_text, lang=language)
                    tts.save("output2.mp3")
                    st.audio("output2.mp3", format='audio/mp3', start_time=0)
                    
                    if translated_text:
                        st.download_button(label="Download Results as Text",
                            data=translated_text,
                            file_name="detected_objects.txt",
                            mime="text/plain"
                        )

    else:
        choice = st.selectbox('Login/Signup', ['Login', 'Signup'])
        
        st.text_input('Email', key='email')
        st.text_input('Password', type='password', key='password')
        
        if choice == 'Login':
            if st.button('Login'):
                login()
        elif choice == 'Signup':
            if st.button('Create Account'):
                create_account()

if __name__ == "__main__":
    main()
 