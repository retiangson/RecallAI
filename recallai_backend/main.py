from mangum import Mangum
from app.main import app
import sys
print("DEBUG: sys.path =", sys.path)
print("DEBUG: main.py loaded OK")

handler = Mangum(app)

