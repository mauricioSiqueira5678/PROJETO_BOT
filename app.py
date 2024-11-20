import os
import openai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext
from telegram.ext import filters
from dotenv import load_dotenv

# Carregar variáveis do arquivo .env
load_dotenv()

# Obter as chaves das variáveis de ambiente
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configurar OpenAI
openai.api_key = OPENAI_API_KEY

# Carrega o prompt base do arquivo de texto
def carregar_prompt_arquivo(caminho_arquivo):
    with open(caminho_arquivo, 'r') as arquivo:
        prompt_base = arquivo.read()
    return prompt_base

# Função para responder usando GPT-3.5
async def responder_com_gpt(update: Update, context: CallbackContext) -> None:
    pergunta = update.message.text
    prompt_base = carregar_prompt_arquivo('prompts.txt')  # Carrega o prompt personalizado

    prompt_completo = f"{prompt_base}\nPergunta do usuário: {pergunta}"

    # Faz a chamada para o GPT-3.5 usando o endpoint de chat
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Usando o modelo de chat
        messages=[
            {"role": "system", "content": "Você é um assistente virtual especializado em saúde."},
            {"role": "user", "content": prompt_completo},
        ],
        max_tokens=150,
        temperature=0.7
    )

    resposta_gpt = response['choices'][0]['message']['content'].strip()

    # Envia a resposta para o usuário
    await update.message.reply_text(resposta_gpt)

# Função de lembrete
async def enviar_lembrete(context: CallbackContext):
    job = context.job
    await context.bot.send_message(job.chat_id, text='Lembre-se de beber água! Manter-se hidratado é essencial para sua saúde.')

# Função para agendar lembretes
async def agendar_lembrete(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id

    # Agenda um lembrete para ser enviado a cada 2 horas (7200 segundos)
    context.job_queue.run_repeating(enviar_lembrete, interval=7200, first=10, chat_id=chat_id)

    await update.message.reply_text('Lembretes de saúde ativados! Você receberá lembretes a cada 2 horas.')

# Função de início
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Bem-vindo ao Bot de Saúde Preventiva! Pergunte algo sobre saúde ou ative lembretes de saúde.')

# Configuração do bot
def main():
    # Substitua pelo seu token do Telegram
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    application = Application.builder().token(token).build()

    # Comandos do bot
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("lembrete", agendar_lembrete))

    # Responde a mensagens de texto usando GPT-3.5
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder_com_gpt))

    try:
        # Inicia o bot
        application.run_polling()
    except KeyboardInterrupt:
        print("Bot interrompido manualmente. Encerrando...")

if __name__ == '__main__':
    main()
