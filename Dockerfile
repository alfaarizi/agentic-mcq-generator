FROM python:3.11-slim

WORKDIR /app

# Copy dependency files
COPY pyproject.toml requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py ./
COPY api/ ./api/
COPY src/ ./src/
COPY templates/ ./templates/
COPY static/ ./static/

# Create quizzes directory (will be mounted at runtime)
RUN mkdir -p /app/quizzes && chmod 755 /app/quizzes

# Expose port
EXPOSE 8080

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
