import secrets

# Generate a secure secret key
secret_key = secrets.token_hex(32)

print("=" * 60)
print("QuickLine LLC - Environment Configuration")
print("=" * 60)
print("\nGenerated SECRET_KEY:")
print(secret_key)
print("\nCopy this to your .env file!")
print("=" * 60)
