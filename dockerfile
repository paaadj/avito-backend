FROM python:3.11

COPY req.txt ./
RUN pip install -r req.txt

COPY ./database database
COPY ./routing routing
COPY ./schemas schemas
COPY ./services services
COPY app.py ./

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]