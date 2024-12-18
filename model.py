from sqlalchemy import Column, String, Integer, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import bcrypt



DATABASE_URL = "mysql+pymysql://root:#1Krishna@localhost:3306/Conversations"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Guest_ChatRecord(Base):
    __tablename__ = "Registered_user_chat"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Role=Column(String(255), nullable=True)
    user_message = Column(Text, nullable=True)
    model_response = Column(Text, nullable=True)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone_number = Column(String(20), nullable=True)
    password = Column(String(255))

    transfer_call_user_message = Column(Text, nullable=True)
    transfer_call_response = Column(Text, nullable=True)
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))



print("Tables to be created:")
Base.metadata.create_all(bind=engine)
print("Tables created successfully.")
