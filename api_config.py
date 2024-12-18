import os
import google.generativeai as genai
#from sqlalchemy.orm import Session
from model import SessionLocal
from fastapi import FastAPI
# Load the API key from environment variables
GEMINI_API_KEY = "AIzaSyDUeSSceuRmQkke4LPusoTJFumddJJAKMk"

