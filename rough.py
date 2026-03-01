from app.security import pwd_context # Or wherever your CryptContext is defined

password = "admin123"
hashed = pwd_context.hash(password)
print(f"Your Hashed Password: {hashed}")