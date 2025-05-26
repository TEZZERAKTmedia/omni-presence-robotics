# --- Backend Stage ---
    FROM python:3.11-slim AS backend

    WORKDIR /app
    
    COPY requirements.txt .
    RUN pip install --upgrade pip && pip install -r requirements.txt
    
    COPY Backend/ ./Backend/
    COPY params.json .
    
    # --- Frontend Stage (build-only) ---
    FROM node:18 AS frontend
    
    WORKDIR /Frontend
    
    COPY Frontend/package*.json ./
    COPY Frontend/ ./
    
    RUN npm install
    RUN npm run build
    
    # --- Final Runtime Stage ---
    FROM python:3.11-slim
    
    WORKDIR /app
    
    # Copy backend code only
    COPY --from=backend /app /app
    
    # Install dependencies again for final container
    COPY requirements.txt .
    RUN pip install --upgrade pip && pip install -r requirements.txt
    
    EXPOSE 8000
    
    CMD ["python", "Backend/Server/main.py"]
    

    # Copy and make script executable
COPY start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]
