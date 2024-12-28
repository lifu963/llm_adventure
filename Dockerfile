FROM python:3.10-slim

WORKDIR /usr/src/app
COPY main.py ./
RUN pip install --no-cache-dir -U gradio openai
EXPOSE 7860
ENV GRADIO_SERVER_NAME="0.0.0.0"

CMD ["python", "main.py"]