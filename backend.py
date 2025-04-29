import sqlite3
import openai
import speech_recognition as sr
import requests
import tempfile
import pygame
import re
import os
from datetime import datetime
import pandas as pd
import platform
import subprocess
from fpdf import FPDF


openai.api_key = "API-Key"
eleven_api_key = "API-Key"

conn = sqlite3.connect("inventory.db", 
                       check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL COLLATE NOCASE,
        quantity INTEGER NOT NULL,
        unit TEXT NOT NULL)
               

""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        unit TEXT NOT NULL,
        sale_date TEXT NOT NULL)
""")

conn.commit()
recognizer = sr.Recognizer()

def save_conversation(role, message):
    with open("conversation_log.txt", "a", encoding="utf-8") as f:
        f.write(f"{role}: {message}\n")

def load_conversation():
    if not os.path.exists("conversation_log.txt"):
        return

    with open("conversation_log.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        if line.startswith("User: "):
            chat_history.append({"role": "user", "content": line[6:].strip()})
        elif line.startswith("Assistant: "):
            chat_history.append({"role": "assistant", "content": line[11:].strip()})

chat_history = []
load_conversation()


def speak(text):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/VR6AewLTigWG4xSOukaG"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": eleven_api_key,
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.7
        }
    }

    response = requests.post(url, json=data, headers=headers)
    if response.status_code != 200:
        print("Error from ElevenLabs:", response.text)
        return

    temp_file_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name

    with open(temp_file_path, "wb") as f:
        f.write(response.content)

    pygame.mixer.init()
    pygame.mixer.music.load(temp_file_path)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        continue

    pygame.mixer.quit()
    os.unlink(temp_file_path)


def speak_response(response):
    print(f"Assistant: {response}")
    speak(response)
    save_conversation("Assistant", response)

def classify_intent(command):
    prompt = f"""
You are a strict assistant helping in a shop's inventory system.

Rules:
- If the user asks anything related to checking stock, item availability, quantity, products, database, or inventory, classify it as "SQL".
- If the user talks about something else (greetings, jokes, general chat), classify it as "CHAT".

IMPORTANT:
- Only respond with exactly "SQL" or "CHAT". Nothing else.
- No explanation. Only one word.

User's input: "{command}"
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        classification = response["choices"][0]["message"]["content"].strip().upper()
        if classification not in ["SQL", "CHAT"]:
            classification = "CHAT"  
        return classification
    except Exception:
        return "CHAT"
def generate_update_stock_query(command):
    prompt = f"""
You are a professional SQL assistant specialized only in updating inventory stock.

Task:
- Translate the user's instruction into a valid SQLite UPDATE query.
- Only perform updates on the quantity of items in the inventory.

Database Table: 'inventory'
Columns: id (integer), name (text), quantity (integer), unit (text)

Rules:
- If the instruction indicates adding stock, generate:
  UPDATE inventory SET quantity = quantity + X WHERE LOWER(name) = LOWER('item_name');
- If the instruction indicates reducing stock (sold or removed), generate:
  UPDATE inventory SET quantity = quantity - X WHERE LOWER(name) = LOWER('item_name');
- X is the number of units mentioned in the instruction. If not mentioned, assume 1.
- Always match item names case-insensitively.
- Never generate SELECT, DELETE, or INSERT queries.
- If multiple operations are mentioned, only perform the first valid one.

Important:
- Assume quantities are always positive integers.
- Do not generate any text or explanation — only the SQL query.

Instruction: '{command}'
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        sql_query = response["choices"][0]["message"]["content"].replace("```sql", "").replace("```", "").strip()
        print(sql_query)
        return sql_query
    except Exception as e:
        return f"AI Error: {str(e)}"

def generate_check_stock_query(command):
    prompt = f"""
You are a professional SQL assistant specialized only in checking inventory stock.

Task:
- Translate the user's instruction into a valid SQLite query.
- Only generate a SELECT query to check quantity and unit for a specific item.
- Never generate UPDATE, DELETE, INSERT, or any modification queries.

Database Table: 'inventory'
Columns: id (integer), name (text), quantity (integer), unit (text)

Rules:
- Query must be: SELECT quantity, unit FROM inventory WHERE LOWER(name) = LOWER('item_name');
- Item name must be taken exactly as mentioned in the user's command (case-insensitive match).
- If multiple items are mentioned, only pick the first one.
- If no valid item name is found, return: SELECT 'Item not specified' as error;

Important:
- Do not assume or create imaginary item names.
- Return only the pure SQL query without explanation.

Instruction: '{command}'
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        sql_query = response["choices"][0]["message"]["content"].replace("```sql", "").replace("```", "").strip()
        return sql_query
    except Exception as e:
        return f"AI Error: {str(e)}"
def generate_sql_query(command):
    prompt = f"""
You are an expert SQL assistant.

Convert the following instruction into a valid SQLite query:
Instruction: '{command}'

Database table 'inventory' has columns: id, name, quantity, unit.

Rules:
- If checking stock, generate: SELECT quantity, unit FROM inventory WHERE name = '...';
- If adding new stock, generate: UPDATE inventory SET quantity = quantity + X WHERE name = '...';
- If reducing stock (sold or removed), generate: UPDATE inventory SET quantity = quantity - X WHERE name = '...';
- Assume the quantity mentioned in instruction (e.g., "2 kg apples sold" means reduce 2).
- Please be serious about reducing the amount of items whenthey are updated through commands.
- Always use the item name exactly as given (case-insensitive match).
- If quantity is not specified, assume 1.
- Return only the SQL query. No explanation or extra text.
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        sql_query = response["choices"][0]["message"]["content"].replace("```sql", "").replace("```", "").strip()
        return sql_query
    except Exception as e:
        return f"AI Error: {str(e)}"

def execute_sql_query(sql_query, original_command):
    date, time, day = get_datetime_context()
    try:
        cursor.execute(sql_query)
        conn.commit()

        if sql_query.strip().lower().startswith("select"):
            result = cursor.fetchone()
            match = re.search(r"where name\s*=\s*'([^']+)'", sql_query, re.IGNORECASE)
            item_name = match.group(1) if match else "item"

            if result:
                quantity, unit = result
                if isinstance(quantity, int) and quantity <= 5:
                    alert = f"Warning: {item_name.title()} is running low ({quantity} {unit}).\n"
                else:
                    alert = ""
                gpt_prompt = (
                    f"Shopkeeper asked: '{original_command}'\n"
                    f"Inventory shows: {quantity} {unit} of {item_name}.\n"
                    "Reply shortly and friendly."
                )

                gpt_response = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "system", "content": "Short friendly inventory assistant."},
                              {"role": "user", "content": gpt_prompt}]
                )
                reply = gpt_response["choices"][0]["message"]["content"].strip()
                return alert + reply
            

            else:
                return "Item not found in inventory."
        else:
            return f"Inventory updated successfully!{date},{time},{day}"
        
    except sqlite3.Error as e:
        return f"SQLite Error: {e}"

def get_response(command, mode=None):
    date, time, day = get_datetime_context()

    prompt=f"""You are a smart assistant helping track inventory sales.
            Today's date is {date}, current time is {time}, and it's {day}.

            while reading the conversation_log file
            Rules:
            - If a sentence says "Inventory updated successfully!" followed by a date, time, and day, it means an item was sold or updated.
            - The item name is mentioned **in the user's command right before** this success message.
            - You have to extract that item name carefully.
            - Prepare a neat list of sold items with their name, quantity, unit, and sale date if possible.

            Example conversation:

            User: 5 kg sugar sold  
            Assistant: Inventory updated successfully! 2025-04-26, 23:29:10, Saturday

            User: 2 packets of flour sold  
            Assistant: Inventory updated successfully! 2025-04-26, 23:30:00, Saturday

            Your job is to:
            - Make a list:
                - 5 kg sugar (sold on 2025-04-26)
                - 2 packets flour (sold on 2025-04-26)

            Important:
            - If the user asks about "today's sales" or "sales on a specific date", use the latest updated items.
            - If no item was updated recently, reply "No sales recorded yet."

            Only respond with the list when asked. Otherwise, continue normal conversation.

            Start now!

            """
    date, time, day = get_datetime_context(

    )

    if mode == "update" or mode == "add":
        sql_query = generate_update_stock_query(command)
        if "AI Error" in sql_query:
            return sql_query
        return execute_sql_query(sql_query, command)
    else:
        intent = classify_intent(command)
        if intent == "SQL":
            sql_query = generate_sql_query(command)
            if "AI Error" in sql_query:
                return sql_query
            return execute_sql_query(sql_query, command)
        else:
            chat_history.append({"role": "user", "content": command})
            if len(chat_history) > 10:
                chat_history.pop(0)

            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": prompt}
                    ] + chat_history,
                    request_timeout=30)
                reply = response["choices"][0]["message"]["content"].strip()
                chat_history.append({"role": "assistant", "content": reply})
                save_conversation("User", command)
                return reply
            except Exception as e:
                return f"AI Error: {str(e)}"




def listen_and_recognize():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1
                                            )
        print("Listening...")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            command = recognizer.recognize_google(audio)
            save_conversation("User", command)  
            return command
        except sr.UnknownValueError:
            return "Could not understand audio."
        except sr.RequestError:
            return "Speech recognition request failed."
        except Exception as e:
            return f"Speech recognition error: {str(e)}"


def speech_input(mode=None):
    try:


        command = listen_and_recognize()
        return command
    except Exception as e:
        return f"Error capturing voice: {str(e)}"
    
def get_datetime_context():
    now = datetime.now(
        
    )
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    day_str = now.strftime("%A")
    return date_str, time_str, day_str


def view_stock():
    command = speech_input()
    if command:
        intent = classify_intent(command)
        if intent == "SQL":
            sql_query = generate_check_stock_query(command)
            if "AI Error" not in sql_query:
                response = execute_sql_query(sql_query, command)
                speak_response(response)
            else:
                speak_response("Sorry, I couldn't understand the item.")
        else:
            speak_response("I think you want to have general chat, so please click on the mic.")
    else:
        speak_response("Sorry, I didn't catch that.")


def update_stock():
    command = speech_input()  
    if command: 
        intent=classify_intent(command)
        if (intent == "SQL"):
            sql_query = generate_update_stock_query(command) 
            if "AI Error" not in sql_query: 
                response = execute_sql_query(sql_query, command) 

                speak_response(response)
            else:
                speak_response("Sorry, I couldn't understand the item.")
        else:
            speak_response("I think,you want to have genral chat,so you should click on mic.")
    else:
        speak_response("Sorry, I didn't catch that.")


def export_inventory_to_excel(database_path="inventory.db", output_file="database_xl.xlsx"):
    conn = sqlite3.connect(database_path)
    
    query = "SELECT * FROM inventory"
    df = pd.read_sql(query, conn)
    
    df.to_excel(output_file, index=False, engine='openpyxl')
    
    conn.close()
    print(f"Exported inventory to '{output_file}' successfully!")


def view_dataset(file_path="database_xl.xlsx"):
    export_inventory_to_excel()

    if not os.path.exists(file_path):
        print(f"File '{file_path}' does not exist.")
        return

    try:
        if platform.system() == "Windows":
            os.startfile(file_path)
        elif platform.system() == "Darwin": 
            subprocess.call(["open", file_path])
        else:
            subprocess.call(["xdg-open", file_path])
        
        print(f"Opened '{file_path}' successfully!")
    except Exception as e:
        print(f"Failed to open the file: {e}")



def view_report(log_file="conversation_log.txt", output_pdf="sales_report.pdf"):
    today = datetime.now().strftime("%Y-%m-%d")

    with open(log_file, "r", encoding="utf-8") as f:
        conversation = f.read()
    prompt = f"""
    You are an expert sales assistant.

    Here is a chat log between a user and an assistant:
    {conversation}

Your task:
- Find all sales (the user inputs just above where the assistant says "inventory updated {{date and time}}").
- Only consider sales where the date inside "inventory updated {{}}" matches today's date: {today}.
- Also show the time of selling of the item (just after the sales record)
- Summarize all these sales nicely into a report format.
- Include a short summary at the end like total number of sales.
- Write it clearly for a PDF.
- Don't give very large spaces between the lines keep it general

Give ONLY the report text. No explanations.
ALSO tell the most selling and lowest selling item on that date in the end .
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    report_text = response[
        "choices"][0]["message"]["content"
                                 ]
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for line in report_text.split('\n'):
        pdf.multi_cell(0, 10, line)

    pdf.output(output_pdf)
    print(f"Sales report generated: {output_pdf}")



    return output_pdf


def today_report():
    pdf_path = view_report()

    if pdf_path and os.path.exists(pdf_path):

        os.startfile(pdf_path)
        print(
            "Today's sales report opened!")
    else:
        print("No report found to open."
              )