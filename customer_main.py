## BOOKINGS.JSON (Internal user) 
##DB Path correct daalna hai

# import os
# import json
# import sqlite3
# from dotenv import load_dotenv
# import google.generativeai as genai

# # Load environment variables from .env file
# load_dotenv()
# GEMINI_API_KEY = "AIzaSyCS0E_uLpP6ay5y_G-0h4hjvcJRN2zPUY8"#os.getenv("GEMINI_API_KEY")

# # Configure Gemini API
# genai.configure(api_key=GEMINI_API_KEY)

# # Define Schema as Part of System Instruction7
# database_schema = """
# Database Schema:
# Table: bookings
# Columns:
# - _id: TEXT
# - platform: TEXT
# - listing_id: TEXT
# - confirmation_code: TEXT
# - check_in: TEXT (ISO8601 Date Format)
# - check_out: TEXT (ISO8601 Date Format)
# - listing_title: TEXT
# - guest_name: TEXT
# - commission: REAL
# """

# generation_config = {
#     "temperature": 1,
#     "top_p": 0.95,
#     "top_k": 40,
#     "max_output_tokens": 8192,
#     "response_mime_type": "text/plain",
# }

# model = genai.GenerativeModel(
#     model_name="gemini-1.5-flash",
#     generation_config=generation_config,
#     system_instruction=f"You are a chatbot that converts user questions into SQL queries. My database is in sqlite3 format. Here is the schema of the database:\n{database_schema}",
# )


# def clean_sql_query(sql_query):
#     # Remove markdown code block formatting
#     cleaned_query = sql_query.replace("```sql", "").replace("```", "").strip()

#     # Ensure proper SQL formatting with spaces
#     cleaned_query = " ".join(cleaned_query.split())

#     return cleaned_query






# def execute_sql(conn, sql_query):
#     try:
#         # Clean and properly format the SQL query
#         sql_query = clean_sql_query(sql_query)

#         cursor = conn.cursor()
#         print(f"Executing query: {sql_query}")  # Debug print

#         cursor.execute(sql_query)
#         results = cursor.fetchall()

#         return results
#     except sqlite3.Error as e:
#         print(f"SQL Error: {e}")
#         return f"SQL Error: {e}"


# # Main Chat Loop
# def chatbot_loop():
#     conn = sqlite3.connect("bookings.db")
#     print("Welcome to the Booking Chatbot! Type 'exit' to quit.")
#     while True:
#         user_query = input("You: ")
#         if user_query.lower() == 'exit':
#             break

#         try:
#             # Start chat session
#             chat_session = model.start_chat(history=[])
            
#             # Get SQL query from first response
#             response = chat_session.send_message(user_query)
#             generated_sql = response.text

#             if "SELECT" in generated_sql.upper():
#                 print(f"Generated SQL: {generated_sql}")  # For debugging
                
#                 # Execute SQL
#                 result = execute_sql(conn, generated_sql)
                
#                 if isinstance(result, list) and result:
#                     # Create a follow-up prompt to interpret the results
#                     interpretation_prompt = f"""
#                     The user asked: "{user_query}"
#                     The SQL query returned this result: {result}
#                     Please explain these results in natural language without showing actual result, in a clear and conversational way.
#                       and at last ask user is this what you were looking for?
#                     """
                    
#                     # Get natural language interpretation
#                     interpretation = chat_session.send_message(interpretation_prompt)
#                     print(f"Chatbot: {interpretation.text}")
#                 elif isinstance(result, str):  # SQL Error
#                     print(f"Chatbot: {result}")
#                 else:
#                     print("Chatbot: I couldn't find any matching data for your query.")
#             else:
#                 print(f"Chatbot: {response.text}")
                
#         except Exception as e:
#             print(f"Error: {e}")


# chatbot_loop()

import logging
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import google.generativeai as genai
from model import hash_password, verify_password, Guest_ChatRecord, SessionLocal
import chromadb
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging to write to a file
log_file_path = os.getenv("LOG_FILE_PATH", "customer_main.log")  # Default to 'customer_main.log' if not set
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a file handler
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.INFO)

# Create a logging format
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger = logging.getLogger()
logger.addHandler(file_handler)

GEMINI_API_KEY = "AIzaSyCS0E_uLpP6ay5y_G-0h4hjvcJRN2zPUY8"

genai.configure(api_key=GEMINI_API_KEY)

# Define generation configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

system_instruction = """
    Persona: You are Neovis Chatbot, representing Neovis Consulting, a leading firm specializing in business transformation, strategy, human capital development, technology, and operations. You are professional, knowledgeable, and formal in tone, delivering comprehensive and detailed responses.
    Task: Answer questions about Neovis Consulting, its services, values, and related information. Provide detailed responses in a kind, conversational manner.
        If a question is outside Neovis Consulting’s scope, politely inform the user that you do not have the answer.
        At the end of each response, direct the user to visit https://neovisconsulting.co.mz/contacts/ or contact via WhatsApp at +258 9022049092.
        Inform users that you can transfer the conversation to a real representative if required.
    Format: Respond formally and please keep your response as consise as consie as Possible. If you do not know the answer, state so professionally. Avoid formatting; use plain text only.At last .
    Function Call: You can transfer the chat to the customer service team. If the user requests a transfer, respond professionally and execute the transfer_to_customer_service function.
"""

# Function to handle the chat transfer
def transfer_to_customer_service(
    name: str = None, email: str = None, phone_number: str = None
):
    """Simulates transferring the chat to the customer service team."""
    message = "Call transferred to the customer service team successfully!"
    logging.info(message)  # Log the message
    return message

# Register the function with the model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    tools=[transfer_to_customer_service],  # Register the transfer function
    system_instruction=system_instruction,
)

chat = model.start_chat()

client = chromadb.PersistentClient(path="UNITS_INFO_CHUNCK")

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

def validate_collection_id(collection_id: str) -> bool:
    """Validates if a collection ID exists in ChromaDB."""
    try:
        collection = client.get_collection("collection_" + collection_id)
        return True
    except Exception:
        logging.error(f"Collection ID {collection_id} not found.")
        return False

class QueryRequest(BaseModel):
    id: str
    query: str
    name: str  
    email: str 

class IDValidationRequest(BaseModel):
    id: str

def retrieve_chunks(query, collection_name, top_k=5):
    try:
        collection = client.get_collection("collection_" + collection_name)
        results = collection.query(query_texts=[query], n_results=top_k)
        return " ".join(doc for doc in results["documents"][0])
    except Exception as e:
        error_message = f"Error retrieving context: {e}"
        logging.error(error_message)
        return error_message

def chatbot(query, collection_name, name=None, email=None, phone_number=None):
    # Retrieve context from ChromaDB
    context = retrieve_chunks(query, collection_name)
    if context.startswith("Error"):
        return context

    # Augment query with retrieved context
    augmented_query = f"Context: {context}\nQuestion: {query}"
    response = chat.send_message(augmented_query)

    # Check for function call in the response
    for part in response.candidates[0].content.parts:
        if hasattr(part, "function_call") and part.function_call is not None and part.function_call.name == "transfer_to_customer_service":
            return transfer_to_customer_service(name, email, phone_number)

    return response.text

@app.post("/validate-id")
async def validate_id(request: IDValidationRequest):
    collection_id = request.id
    is_valid = validate_collection_id(collection_id)

    if not is_valid:
        raise HTTPException(status_code=404, detail="Collection ID not found")

    return {"message": "Collection ID is valid"}

@app.post("/Chat(Registered)")
async def chat_endpoint(request: QueryRequest, db: Session = Depends(get_db)):
    collection_id = request.id
    query = request.query

    # Validate collection ID
    if not validate_collection_id(collection_id):
        raise HTTPException(status_code=404, detail="Invalid Collection ID")

    # Search for the user in the database
    user = db.query(Guest_ChatRecord).filter_by(name=request.name, email=request.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found. Please register.")

    # Retrieve and augment context
    response = chatbot(query, collection_id, name=request.name, email=request.email)

    # Append conversation history
    user.user_message = (user.user_message or "") + f"\n USER-> {query}"
    user.model_response = (user.model_response or "") + f"\n RESPONSE-> {response}"

    # Commit changes to the database
    db.commit()
    db.refresh(user)

    logging.info(f"User {request.name} queried: {query}")
    logging.info(f"Response: {response}")

    return {"response": response}

@app.post('/Sign-Up')
async def registered_user(name: str, email: str, mob_no: str, password: str, Repeat_password: str, db: Session = Depends(get_db)):
    """Function for Registered User"""
    try:
        if password != Repeat_password:
            logging.warning("Password mismatch during registration.")
            return "Your Password is not matching"
        hashed_password = hash_password(password)
        user = db.query(Guest_ChatRecord).filter_by(name=name, password=hashed_password, email=email).first()

        if not user:
            # Add new user if not already registered
            new_user = Guest_ChatRecord(name=name, email=email, password=hashed_password, phone_number=mob_no)
            new_user.Role = "Guest"
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            logging.info(f"User {name} registered successfully.")
            return {"message": f"User {name} has been Registered In successfully!"}

        logging.info(f"User {name} logged in as an authorized registered user.")
        return {"message": f"Welcome back, {name}! You are an authorized registered user!"}
    except Exception as e:
        error_message = f"Database error: {e}"
        logging.error(error_message)
        raise HTTPException(status_code=500, detail=error_message)

# ... existing code ...
