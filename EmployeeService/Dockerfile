FROM python:3.12-slim

# Set a default value for PORT if not provided
ARG PORT=8080
ENV PORT=$PORT
ENV PYTHONPATH=/app
# Create a non-root user and group
RUN addgroup --system appgroup && adduser --system appuser --ingroup appgroup

WORKDIR /app

COPY EmployeeService/requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY core /app/core
COPY EmployeeService/app/. /app
COPY EmployeeService/start.sh /app
# Change ownership of /app to appuser
RUN chown -R appuser:appgroup /app

# Ensure the start script is executable
RUN chmod +x /app/start.sh

# Change to the non-root user
USER appuser

# Expose the port
EXPOSE $PORT

# Command to run the application
CMD ["/app/start.sh"]