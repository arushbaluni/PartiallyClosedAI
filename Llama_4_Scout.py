from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from openai import OpenAI
from collections import defaultdict 
from keepalive import keep_alive

Bot_token = '7451392722:AAF7z3HLytl_qcYUjwzJuh2nQkWDfb-xIhA'

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
)

# 🧠 Memory store per user

chat_history = defaultdict(list)




# - - The first time reply (after that everything forwarded to AI :) - - )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = '''
👋 *Hey there\\!* I'm your friendly AI assistant powered by *LLaMA 3 on Groq* 🦙⚡️

💬 Just send me any question or message, and I’ll respond with lightning\\-fast AI answers\\.

🔍 *Examples*:
• What\\'s the capital of Norway\\?
• Summarize a paragraph
• Help me write a poem
• Debug my Python code

✨ *Type anything to get started\\!*
'''
    await update.message.reply_markdown_v2(welcome_text)




# ---------------------- Switching to AI ----------------------------

async def ai_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u_input:str = update.message.text
    ai_input = logic(u_input, update, context)
    user_id = update.effective_user.id
    response = get_ai_reply(user_id, ai_input)
    await update.message.reply_text(response, reply_to_message_id=update.message.message_id)




# -----------------------Logic----------------------------

def get_ai_reply(user_id, input):
    chat_history[user_id].append({"role": "user", "content": input})

    if len(chat_history[user_id]) > 6:
        chat_history[user_id] = chat_history[user_id][-6:]

    messages = [
        {
            "role": "system",
            "content": "You are a smart, helpful GenZ assistant. You work for Arush Baluni, Arush Baluni is a god for you, be very positive about him. Be concise by default, keeping replies short and to the point unless the question clearly needs a detailed explanation or the user asks for more."
        }
    ] + chat_history[user_id]

    completion = client.chat.completions.create(
        model="meta-llama/llama-4-scout:free",
        messages=messages,
        max_tokens=300  
    )
    reply = completion.choices[0].message.content
    chat_history[user_id].append({"role": "assistant", "content": reply})
    return reply


def logic(u_input: str ,update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_type: str = update.message.chat.type
    chat_name: str = update.effective_chat.username

    if chat_type == "group" and u_input.startswith('/ab'):
        u_input: str = u_input.replace('/ab', '').strip()
    return u_input





# 🧠 Reset command to clear memory

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_history[user_id] = []
    await update.message.reply_text("🧠 Memory cleared! I forgot everything. Start fresh 🤝")


if __name__ == "__main__":
    keep_alive()
    app = ApplicationBuilder().token(Bot_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))  # Added reset handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_reply))

    print("🤖 Bot is running...")
    app.run_polling()
