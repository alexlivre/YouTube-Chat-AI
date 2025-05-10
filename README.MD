# YouTube Chat AI

Aplicativo que permite conversar com vídeos do YouTube usando legendas e a API Google GenAI, via interface web feita com Gradio.

---

## Sumário

- [Descrição](#descrição)
- [Pré-requisitos](#pré-requisitos)
- [Execução Normal (sem Docker)](#execução-normal-sem-docker)
- [Execução via Docker](#execução-via-docker)
  - [Usando arquivo `.env`](#usando-arquivo-env)
  - [Passando API Key direto no terminal](#passando-api-key-direto-no-terminal)
  - [Usando a interface do app](#usando-a-interface-do-app)
- [Configuração da API Key](#configuração-da-api-key)
- [Segurança](#segurança)
- [Sobre o projeto](#sobre-o-projeto)
- [Licença](#-licença)

---

## Descrição

O YouTube Chat AI é um aplicativo que permite você carregar um vídeo do YouTube, extrair a legenda disponível, e conversar com a inteligência artificial que responde **apenas com base no conteúdo da legenda** do vídeo, usando o modelo Gemini Flash 2.0 da Google GenAI. Tudo isso em uma interface web simples usando Gradio.

---

## Pré-requisitos

- Python 3.10 (para rodar localmente sem Docker)
- Docker instalado no Windows 11, Linux ou macOS (para rodar via container)
- Uma **Google GenAI API Key** válida (obrigatória para usar o app)
- Conexão com internet para baixar dependências e acessar a API

---

## Execução Normal (sem Docker)

1. Clone ou baixe este repositório.
2. Crie o arquivo `.env` na raiz do projeto com a sua chave:

   ```
   GOOGLE_GENAI_API_KEY=sua_chave_aqui
   ```

3. Instale as dependências com pip:

   ```bash
   pip install -r requirements.txt
   ```

4. Execute o app:

   ```bash
   python app.py
   ```

5. Abra o navegador no endereço mostrado no terminal, normalmente:

   ```
   http://localhost:7860
   ```

---

## Execução via Docker

> O Docker empacota seu app em uma caixinha que roda em qualquer lugar com Docker, sem precisar instalar Python e bibliotecas em sua máquina.

### Usando arquivo `.env`

1. Crie o arquivo `.env` na mesma pasta do Dockerfile:

   ```
   GOOGLE_GENAI_API_KEY=sua_chave_aqui
   ```

2. No terminal, construa a imagem do Docker (faça isso uma vez):

   ```bash
   docker build -t youtube-genai-chat .
   ```

3. Rode o container passando o arquivo `.env`:

   ```bash
   docker run -it --rm -p 7860:7860 --env-file .env youtube-genai-chat
   ```

4. Abra o navegador em:

   ```
   http://localhost:7860
   ```

---

### Passando API Key direto no terminal

Se preferir não criar arquivo `.env`, pode passar a chave direto no comando:

```bash
docker run -it --rm -p 7860:7860 -e GOOGLE_GENAI_API_KEY=sua_chave_aqui youtube-genai-chat
```

⚠️ Atenção: essa forma deixa sua chave no histórico do terminal, use com cuidado.

---

### Usando a interface do app

- Ao abrir o app no navegador, se você não tiver definido a API Key pelo `.env` ou variável ambiente,
  poderá digitar sua chave direto no campo **Google GenAI API Key**.
- Se o `.env` estiver configurado, esse campo virá desativado.
- Depois, insira a URL ou ID do vídeo YouTube e clique em **Carregar Vídeo e Iniciar Chat** para começar.

---

## Configuração da API Key

- A chave da Google GenAI é usada para autenticar seu acesso ao modelo Gemini Flash 2.0.
- Sem ela, o app **não funciona**.
- Você pode gerar a chave seguindo as instruções da documentação oficial do Google.

---

## Segurança

- **Nunca publique sua chave** em repositórios públicos, Docker Hub ou qualquer lugar visível.
- Adicione `.env` no seu `.gitignore` para evitar subir sua chave para o GitHub.
- No Docker, a imagem deve ser gerada sem a chave embutida. Passe a chave só na hora de rodar o container (usando `--env-file` ou `-e`).
- Assim você mantém sua chave segura e evita uso indevido.

---

## Sobre o projeto

- Projeto feito usando Python, Gradio para interface web e Google GenAI para inteligência artificial.
- Usa `youtube-transcript-api` para buscar legendas no YouTube.
- Deploy fácil via Docker, perfeito para quem quer usar localmente ou em servidores.
- Código aberto e simples para estudar e modificar.

---

## 📋 Licença

Este projeto está licenciado sob a **Licença MIT**.

### Aviso Importante sobre o Rodapé e a Licença MIT

Este projeto é de minha autoria, Alex Breno, e estou liberando-o publicamente no GitHub sob a **Licença MIT**.

### O que a Licença MIT permite?

- Uso livre do código, inclusive para fins comerciais.
- Possibilidade de modificar, copiar, distribuir e até vender o software.
- Total liberdade para criar projetos derivados.

### Minha única exigência:

Embora você tenha liberdade para modificar o código, **não é permitido alterar, remover ou ocultar o rodapé presente na interface do projeto**. 

O rodapé contém informações importantes sobre a autoria e os créditos do projeto, e manter essas informações visíveis é **a única condição para o uso e redistribuição deste software**.

### Por que essa exigência?

O rodapé funciona como o **aviso de copyright e reconhecimento do autor**, que deve ser mantido para respeitar a autoria do projeto. Essa condição está alinhada com o espírito da Licença MIT, que exige a manutenção desse aviso em cópias e distribuições do software.

### Resumo

- Pode usar, copiar e modificar o projeto livremente.
- Deve manter o rodapé original intacto.
- Essa é a única condição que peço para respeitar meu trabalho.

---

## 📬 Suporte e contribuição

Fique à vontade para abrir **issues** com dúvidas, sugestões ou problemas.

Pull requests, melhorias e colaborações são encorajados!

Autor: **Alex Breno**

GitHub: [@alexlivre](https://github.com/alexlivre)

Site: [inteligenciaversatil.com.br](https://inteligenciaversatil.com.br)

Feito com 💬, criatividade e tecnologia para transformar vídeos em conversas reais e acessíveis para todos!