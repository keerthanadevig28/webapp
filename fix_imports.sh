#!/bin/bash

echo "Fixing all imports..."

# Fix app/__init__.py
echo '__version__ = "1.0.0"' > app/__init__.py

# Fix main.py
sed -i '' 's/^from routes import/from app.routes import/g' app/main.py
sed -i '' 's/^from routes\./from app.routes./g' app/main.py
sed -i '' 's/^from database import/from app.database import/g' app/main.py
sed -i '' 's/^from models import/from app.models import/g' app/main.py
sed -i '' 's/^from schemas import/from app.schemas import/g' app/main.py
sed -i '' 's/^from auth import/from app.auth import/g' app/main.py
sed -i '' 's/^from config import/from app.config import/g' app/main.py

# Fix database.py
sed -i '' 's/^from config import/from app.config import/g' app/database.py
sed -i '' 's/^from models import/from app.models import/g' app/database.py

# Fix models.py
sed -i '' 's/^from database import/from app.database import/g' app/models.py
sed -i '' 's/^from config import/from app.config import/g' app/models.py

# Fix schemas.py
sed -i '' 's/^from models import/from app.models import/g' app/schemas.py

# Fix auth.py if exists
sed -i '' 's/^from database import/from app.database import/g' app/auth.py 2>/dev/null
sed -i '' 's/^from models import/from app.models import/g' app/auth.py 2>/dev/null
sed -i '' 's/^from config import/from app.config import/g' app/auth.py 2>/dev/null

# Fix route files
sed -i '' 's/^from models import/from app.models import/g' app/routes/*.py 2>/dev/null
sed -i '' 's/^from database import/from app.database import/g' app/routes/*.py 2>/dev/null
sed -i '' 's/^from schemas import/from app.schemas import/g' app/routes/*.py 2>/dev/null
sed -i '' 's/^from auth import/from app.auth import/g' app/routes/*.py 2>/dev/null
sed -i '' 's/^from config import/from app.config import/g' app/routes/*.py 2>/dev/null

echo "All imports fixed!"
