# Usa uma imagem leve do Python
FROM python:3.10-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia os arquivos para dentro do container
COPY requirements.txt .
COPY app.py .

# Instala as dependências
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

# (Opcional) Define o Gradio para rodar em todas interfaces e na porta 7860 por padrão
ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=7860

# Comando para rodar seu app
CMD ["python", "app.py"]
