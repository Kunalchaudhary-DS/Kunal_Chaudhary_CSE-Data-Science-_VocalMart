# VocalMart: An AI Driven Inventory Managment assistant aka. chhotu

### Project Video Link
[Watch the video on Google Drive](https://drive.google.com/file/d/14QuJ6K5qESMuJS6EojRXK5eD3sakbTXZ/view?usp=drive_link)

# Team Leader: Kunal Chaudhary - 2401420049
Team Members:
Utsav Singhal - 2401420041,
  Dhruv Sharma - 2401410050,
  Md Anas Khan - 2401420035,


# Project Description:
Bringing AI to Local Shops:
This project is a voice-enabled Inventory Management Assistant built with Python, designed to empower local shopkeepers with the power of AI — without the complexity. Whether it’s updating stock, checking inventory, or generating reports, this assistant does it all through natural voice commands and a simple, intuitive interface.

For many small businesses, this could be their first dive into AI, making everyday inventory tasks faster, easier, and smarter — without needing to be tech-savvy

Simple Steps:

i) Voice Commands – Just speak, and the assistant handles the rest.

ii) Natural Language Understanding – No need to learn commands. Talk like you normally would.

iii) Local Database Integration – Fast and secure data handling using SQLite.

iv) Real-time Insights – Get instant feedback and stock updates without lifting a finger.

"Revolutionizing local retail with smart, AI-powered inventory management."


# Technologies Used:

*Frontend:
- Kivy
  - Lightweight Python GUI framework.
  - Mobile and desktop cross-platform compatibility.

*Backend:
- Python: Core language for backend scripting.
- SQLite3: Embedded, zero-configuration database.
- Pandas: Data manipulation and Excel handling.
- Openpyxl: For direct Excel file interactions.
- Fpdf2: PDF generation for reports.
- SpeechRecognition: Speech-to-text interface.
- ElevenLabs API: Natural-sounding Text-to-Speech.
- OpenAI API (GPT-4o-mini): Intent analysis, query formulation.


# Steps to Run/Execute the Project

1. Environment Setup
i) Install Python:
  Ensure that Python 3.9 or higher is installed on your system.
  download from here: https://www.python.org/downloads/

ii) Create a Virtual Environment (Recommended):
  Open the terminal or command prompt and run:
  python -m venv inventory_env

iii) Activate the environment:
  Windows:
  inventory_env\Scripts\activate
  Mac/Linux:
  source inventory_env/bin/activate



2. Install Required Libraries
  Install all the necessary dependencies using pip:
  
  pip install kivy openai speechrecognition elevenlabs pandas fpdf2
  
  (You may also use a provided requirements.txt file if available.)



3. Set Up API Keys and Configuration
  i) OpenAI API Key:
  Sign up on [OpenAI](https://platform.openai.com/signup) and get your API key.

  ii) ElevenLabs API Key (for Voice Output):
  Sign up on [ElevenLabs](https://elevenlabs.io/) to access realistic text-to-speech services.

  iii) Configure Keys in the Project:
  Insert your API keys inside the configuration section of the script, typically in config.py or directly in the main.py file:
  OPENAI_API_KEY = "your-openai-api-key" as I can't upload mine.
  ELEVENLABS_API_KEY = "your-elevenlabs-api-key" as I can't upload mine.



4. Prepare Database and Files
  Ensure the SQLite database (inventory.db) is present in the project directory.
  If missing, run the provided database initialization script to create the required tables for inventory and sales tracking.



5. Launch the Application
  Navigate to the project directory using terminal/command prompt.

  Run the main application file:
  python main.py



6. Interacting with the Assistant
  After launching, speak your inventory or sales commands clearly into the microphone.
  
  The assistant will:
  
  Update stock automatically.
  
  Record the sales with timestamp.
  
  Generate sales reports in PDF format when requested.
  
  Open inventory or sales data in Excel directly from the app.
  
  Respond with human-like natural speech via ElevenLabs.



7. System Requirements
  Microphone: Ensure your system microphone is working properly for voice commands.
  
  Internet Connection: Required for accessing AI APIs (OpenAI and ElevenLabs).
  
  Storage: Minimal space needed for local database and reports.



8. Additional Notes
  If ElevenLabs service is unavailable, you can configure fallback offline text-to-speech using pyttsx3.
  
  The application is designed for offline-first use (for local database) but online API access for AI features.
  
  All generated reports are saved automatically in a reports/ folder inside the project directory.


