![logo-removebg-preview](https://github.com/user-attachments/assets/ce4fe9bb-5608-4ab3-aa23-a3b65e50e9b6)


# SightSync Harmony: Empowering Independence through Auditory Vision

![License](https://badgen.net/github/license/micromatch/micromatch)

SightSync Harmony revolutionizes the way individuals, both visually impaired and sighted, perceive and interact with their surroundings. Leveraging advanced AI-powered image detection and generation, the web app enables users to upload images and receive detailed audio descriptions of detected objects, alongside contextual information about the environment. Sighted users can also benefit from these features, gaining insights and translations in various languages, enhancing their understanding of diverse environments.

Click [here](https://sight-sync-harmony.streamlit.app/) to try out

## Features:

- **Image Detection**: Identify objects within uploaded images and provide comprehensive descriptions.
- **Image Generation using Text**: Create images based on textual descriptions.
- **Audio Output**: Receive audio output along with text output, which can be translated into any chosen language.
- **Custom Prompt Feature**: Upload an image and ask specific questions or doubts related to that image.

SightSync Harmony supports translation of audio and text responses into a wide range of languages, including major Indian languages like Hindi, Bengali, Tamil, Telugu, Kannada, Marathi, Malayalam, Gujarati, and Urdu, as well as global languages such as English, Russian, Spanish, German, Portuguese, Arabic, French, Italian, Japanese, Korean, and Chinese. This ensures accessibility and inclusivity for a broad and diverse audience.

## Plans:

- **Free Plan**: Users have 2 image generation tokens per day.
- **Premium Plan**: Users have unlimited image generation tokens.

If you are interested in the premium plan, please [email me](mailto:archismwanchatterjee@gmail.comsubject=Interest%20in%20Premium%20Plan&body=Hi,%20I'm%20interested%20in%20the%20premium%20plan.%20Please%20send%20me%20the%20details.).

## Technologies and Libraries Used:

- **Streamlit**: For building the web application.
- **Pillow**: For image processing.
- **IPython**: For interactive Python capabilities.
- **gTTS**: For text-to-speech conversion.
- **google.generativeai**: For generative AI capabilities.
- **deep-translator**: For translating text into various languages.
- **firebase**: For user authentication and data storage.
- **firebase-admin**: For Firebase administration.
- **Requests**: For making HTTP requests.
- **OpenAI**: For AI and machine learning functionalities.

## How to Use:

1. Clone the repository:
    ```sh
    git clone https://github.com/ArchismwanChatterjee/SightSyncHarmony.git
    ```

2. Install the required libraries:
    ```sh
    pip install streamlit pillow ipython gtts google-generativeai deep-translator firebase-admin requests openai
    ```
    or
   ```sh
   pip install -r requirements.txt
   ```
   
4. Set up Firebase:
    - Follow the instructions on the [Firebase website](https://firebase.google.com/docs/web/setup) to set up your Firebase project.
    - Download your `serviceAccountKey.json` file and place it in the root of the project.

5. Create a `.env` file and add your API keys and configurations:
    ```env
    OPENAI_API_KEY=your_openai_api_key
    GOOGLE_GENERATIVEAI_API_KEY=your_google_api_key
    FIREBASE_API_KEY=your_firebase_api_key
    ```

6. Run the Streamlit app:
    ```sh
    streamlit run app.py
    ```

7. Open your web browser and go to `http://localhost:8501` to use the application.

## Deployment:

The application is deployed using Streamlit Cloud. Follow these steps to deploy your own instance:

1. Push your code to a GitHub repository.
2. Go to [Streamlit Cloud](https://share.streamlit.io/) and sign in.
3. Click on "New app" and connect your GitHub repository.
4. Choose the main branch and the app file (e.g., `app.py`).
5. Deploy the app.

For more detailed instructions, refer to the [Streamlit Cloud documentation](https://docs.streamlit.io/streamlit-cloud).

## Contributing:

Contributions are welcome! Please fork the repository and use a feature branch. Pull requests are warmly welcome.

## License:

This project is licensed under the MIT License.

## Contact:

For any questions or suggestions, feel free to contact me at [archismwanchatterjee@gmail.com](mailto:archismwanchatterjee@gmail.com).

