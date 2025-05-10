# YouTube Chat AI

import os
import re
import requests
import gradio as gr
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from google.genai import Client
from google.genai import types
from dotenv import load_dotenv  # ADICIONADO

# Mapeamento de códigos para nomes em PT-BR
COMMON_TRANSLATIONS = {
    "pt": "Português",
    "en": "Inglês",
    "es": "Espanhol",
    # Adicione outros se desejar
}

def extrair_id_video(url_ou_id: str):
    """Extrai ID do YouTube da URL ou ID puro."""
    padrao = (
        r'(?:youtube\.com/(?:[^/\n\s]+/\S+/|(?:v|e(?:mbed)?)/|.*[?&]v=)|youtu\.be/)'
        r'([A-Za-z0-9_-]{11})'
    )
    m = re.search(padrao, url_ou_id)
    if m:
        return m.group(1)
    if re.match(r'^[A-Za-z0-9_-]{11}$', url_ou_id):
        return url_ou_id
    return None

def obter_thumbnail_url(video_id: str):
    """Busca URL da thumbnail usando a API oEmbed do YouTube."""
    if not video_id:
        return None
    try:
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        oembed_url = f"https://www.youtube.com/oembed?url={youtube_url}&format=json"
        response = requests.get(oembed_url)
        response.raise_for_status()
        data = response.json()
        return data.get("thumbnail_url")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar thumbnail via oEmbed: {e}")
        return None
    except Exception as e:
        print(f"Erro inesperado ao buscar thumbnail: {e}")
        return None

def listar_legendas(video_id):
    """Lista legendas disponíveis."""
    try:
        tl = YouTubeTranscriptApi.list_transcripts(video_id)
        manuais, automatics = [], []
        for t in tl:
            label = f"{t.language} ({t.language_code})"
            if t.is_generated:
                automatics.append((label, t.language_code))
            else:
                manuais.append((label, t.language_code))
        return manuais, automatics, tl
    except Exception as e:
        print(f"Erro ao listar legendas: {e}")
        return [], [], None

def obter_texto_legenda(video_id, legenda_info):
    """Obtém o texto da legenda."""
    codigo, tipo = legenda_info
    try:
        tl = YouTubeTranscriptApi.list_transcripts(video_id)
        tr = None
        if tipo == "manual":
            tr = tl.find_manually_created_transcript([codigo])
        elif tipo == "auto":
            tr = tl.find_generated_transcript([codigo])

        if tr is None:
            if tl:
                 tr = tl.find_transcript([t.language_code for t in tl])
            else:
                 return "❌ Nenhuma legenda disponível para este vídeo."

        data = tr.fetch()
        formatter = TextFormatter()
        texto = formatter.format_transcript(data)
        return texto
    except Exception as e:
        return f"❌ Erro ao obter texto da legenda: {str(e)}"


def carregar_video_e_chat(api_key, url):
    """Processa o vídeo, obtém legenda, thumbnail e inicia o chat."""
    chatbox_update = gr.update(value=[], visible=False)
    textbox_pergunta_update = gr.update(visible=False)
    enviar_btn_update = gr.update(visible=False)
    thumbnail_update = gr.update(value=None, visible=False)
    status_update = gr.update(value="Insira a API Key e a URL do vídeo.")

    if not api_key or api_key.strip() == "":
        status_update = gr.update("❌ Por favor, insira sua Google GenAI API Key.")
        return status_update, thumbnail_update, chatbox_update, None, textbox_pergunta_update, enviar_btn_update
        
    if not url or url.strip() == "":
         status_update = gr.update("❌ Por favor, insira a URL ou ID do vídeo.")
         return status_update, thumbnail_update, chatbox_update, None, textbox_pergunta_update, enviar_btn_update

    status_update = gr.update("▶️ Processando vídeo...")

    vid = extrair_id_video(url)
    if not vid:
        status_update = gr.update("❌ Vídeo inválido. Verifique a URL ou ID.")
        return status_update, thumbnail_update, chatbox_update, None, textbox_pergunta_update, enviar_btn_update

    thumb_url = obter_thumbnail_url(vid)
    if thumb_url:
        thumbnail_update = gr.update(value=thumb_url, visible=True)
    else:
        thumbnail_update = gr.update(value=None, visible=False)

    status_update = gr.update("▶️ Buscando legendas disponíveis...")

    manuais, automatics, tl = listar_legendas(vid)
    if tl is None or (not manuais and not automatics):
         status_update = gr.update("❌ Não foi possível obter legendas ou nenhuma legenda disponível.")
         return status_update, thumbnail_update, chatbox_update, None, textbox_pergunta_update, enviar_btn_update

    legenda_escolhida = None
    if manuais:
        legenda_escolhida = manuais[0]
        tipo = 'manual'
    elif automatics:
        legenda_escolhida = automatics[0]
        tipo = 'auto'

    if legenda_escolhida is None:
         status_update = gr.update("❌ Nenhuma legenda manual ou automática encontrada.")
         return status_update, thumbnail_update, chatbox_update, None, textbox_pergunta_update, enviar_btn_update

    codigo_legenda = legenda_escolhida[1]
    status_update = gr.update(f"Legenda encontrada: {legenda_escolhida[0]} ({tipo}). Obtendo texto...")

    texto_legenda = obter_texto_legenda(vid, (codigo_legenda, tipo))
    if texto_legenda.startswith("❌"):
        status_update = gr.update(texto_legenda)
        return status_update, thumbnail_update, chatbox_update, None, textbox_pergunta_update, enviar_btn_update

    status_update = gr.update("✅ Texto obtido. Iniciando sessão de chat...")

    try:
        client = Client(api_key=api_key)
        session = client.chats.create(model="gemini-2.0-flash-001")
        system_content = f"Você é um assistente que responde perguntas estritamente baseadas NO SEGUINTE CONTEÚDO de legenda do vídeo do YouTube. NÃO USE CONHECIMENTO PRÉVIO que não esteja neste texto. Se a informação não estiver no texto, diga que não sabe. Conteúdo da legenda:\n\n{texto_legenda}"
        session.send_message(system_content)
        chat_history = []
        status_update = gr.update(f"✨ Chat pronto! Legenda usada: {legenda_escolhida[0]} ({tipo}).")

        chatbox_update = gr.update(value=chat_history, visible=True)
        textbox_pergunta_update = gr.update(visible=True)
        enviar_btn_update = gr.update(visible=True)
        
        return status_update, thumbnail_update, chatbox_update, session, textbox_pergunta_update, enviar_btn_update

    except Exception as e:
        error_message = f"❌ Erro ao iniciar GenAI ou chat: {str(e)}"
        status_update = gr.update(error_message)
        return status_update, thumbnail_update, gr.update(visible=False), None, gr.update(visible=False), gr.update(visible=False)

def chat_com_video(mensagem, chat_history, session):
    """Envia mensagem para o chat e retorna histórico atualizado."""
    if session is None:
         return chat_history, session
    if not mensagem.strip():
        return chat_history, session
    try:
        chat_history = chat_history + [(mensagem, None)]
        resp = session.send_message(mensagem)
        resposta = resp.text
        chat_history[-1] = (mensagem, resposta)
        return chat_history, session
    except Exception as e:
        error_message = f"❌ Erro no chat: {str(e)}"
        chat_history = chat_history + [(mensagem, error_message)]
        return chat_history, session

def update_font_css(size):
    """Gera o CSS para atualizar o tamanho da fonte do chat."""
    # O seletor pode precisar de ajuste dependendo da versão do Gradio
    # Inspecione o HTML gerado pelo Chatbot para confirmar as classes/ids
    # `#chatbox-component .message-bubble p` ou `#chatbox-component .message p` são comuns
    # Usaremos um seletor mais genérico que tende a funcionar:
    css = f"""
    <style>
    #chatbox-component .message p {{ 
        font-size: {size}px !important; 
        line-height: {size * 1.3}px !important; /* Ajusta altura da linha */
    }}
    </style>
    """
    return css

# Gradio interface
# Carrega variáveis do .env
load_dotenv()  # ADICIONADO

with gr.Blocks() as app:
    # Componente HTML invisível para injetar CSS
    css_injector = gr.HTML(visible=False) 
    
    gr.Markdown("# 🎥 Chat com vídeos do YouTube Gemini")
    gr.Markdown("Insira sua API Key e a URL do vídeo para iniciar um chat baseado no conteúdo da legenda.")

    # Verifica se a chave está definida via .env
    api_key_env = os.getenv("GOOGLE_GENAI_API_KEY")  # ADICIONADO

    with gr.Row():
        with gr.Column(scale=3):
            api_key_input = gr.Textbox(
                label="Google GenAI API Key",
                type="password",
                placeholder="Insira sua API Key aqui...",
                value=api_key_env if api_key_env else "",
                interactive=False if api_key_env else True  # DESATIVA SE HÁ VARIÁVEL
            )
            url_input = gr.Textbox(label="URL ou ID do vídeo YouTube", placeholder="https://youtu.be/XXXXXXXXXXX ou ID puro")
            carregar_btn = gr.Button("Carregar Vídeo e Iniciar Chat", variant="primary")
            status_md = gr.Markdown("Insira a API Key e a URL do vídeo acima.")
        with gr.Column(scale=1):
            thumbnail_img = gr.Image(label="Thumbnail", visible=False, height=180, interactive=False)
            # Adiciona o Slider para tamanho da fonte aqui
            font_size_slider = gr.Slider(minimum=10, maximum=24, step=1, value=16, label="Tamanho da Fonte (px)", interactive=True)

    # Componentes do chat (inicialmente ocultos)
    # Adiciona elem_id ao Chatbot para ser alvo do CSS
    chatbox = gr.Chatbot(label="Chat do vídeo", visible=False, height=400, elem_id="chatbox-component") 
    with gr.Row():
        textbox_pergunta = gr.Textbox(placeholder="Digite sua pergunta aqui...", visible=False, show_label=False, scale=7)
        enviar_btn = gr.Button("Enviar", visible=False, scale=1)

    # Estados internos
    chat_session_state = gr.State(None)

    # Evento do botão carregar
    def carregar_video_e_chat_env(api_key, url):
        # Usa a chave do .env se existir
        api_key_final = api_key_env if api_key_env else api_key
        return carregar_video_e_chat(api_key_final, url)

    carregar_btn.click(
        carregar_video_e_chat_env,  # ALTERADO PARA USAR A FUNÇÃO ENV
        inputs=[api_key_input, url_input],
        outputs=[status_md, thumbnail_img, chatbox, chat_session_state, textbox_pergunta, enviar_btn]
    )
    
    # Evento do slider de tamanho da fonte
    font_size_slider.change(
        fn=update_font_css, 
        inputs=font_size_slider, 
        outputs=css_injector
    )

    # Evento para enviar mensagem (botão)
    enviar_btn.click(
        chat_com_video,
        inputs=[textbox_pergunta, chatbox, chat_session_state],
        outputs=[chatbox, chat_session_state]
    ).then(lambda: gr.update(value=""), outputs=[textbox_pergunta])

    # Evento para enviar mensagem (Enter no textbox)
    textbox_pergunta.submit(
        chat_com_video,
        inputs=[textbox_pergunta, chatbox, chat_session_state],
        outputs=[chatbox, chat_session_state]
    ).then(lambda: gr.update(value=""), outputs=[textbox_pergunta])

    # Aplica o CSS inicial ao carregar a aplicação
    app.load(
        fn=update_font_css, 
        inputs=font_size_slider, # Usa o valor padrão do slider
        outputs=css_injector
    )

    gr.Markdown(
        """
        ---
        Desenvolvido por **Alex Breno** ([https://github.com/alexlivre](https://github.com/alexlivre)) membro do **Inteligência Versátil** ([https://inteligenciaversatil.com.br/](https://inteligenciaversatil.com.br/))
        """
    )

if __name__ == "__main__":
    print("\n" + "="*40)
    print("Acesse o app em: http://localhost:7860")
    print("="*40 + "\n")
    # Lembre-se de ter 'requests' no requirements.txt
    app.launch(inbrowser=True)
