from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from openai import OpenAI
from collections import defaultdict

Bot_token = '7451392722:AAGjG65hcDju4ZuhYzkdiYyMIIMuKuobKaI'

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

# 🧠 Memory store per user
chat_history = defaultdict(list)

# All Free Models (in fallback order)
free_models = [
    "meta-llama/llama-4-scout:free",
    "openai/gpt-3.5-turbo:free",
    "perplexity/pplx-7b-online:free",
    "mistralai/mistral-7b-instruct:free",
    "google/gemini-pro:free",
    "anthropic/claude-1:free",
]

# 👋 Start Message
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = '''
👋 *Hey there\\!* I'm your friendly AI assistant powered by *Multiple Free AI Models* 🧠⚡️

💬 Just send me any question or message, and I’ll respond using the best available AI model\\!

🔍 *Examples*:
• What\\'s the capital of Norway\\?
• Summarize a paragraph
• Help me write a poem
• Debug my Python code

✨ *Type anything to get started\\!*
'''
    await update.message.reply_markdown_v2(welcome_text)

# 🧠 AI Handler
async def ai_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u_input: str = update.message.text
    ai_input = logic(u_input, update, context)
    user_id = update.effective_user.id
    response = get_ai_reply(user_id, ai_input)
    await update.message.reply_text(response, reply_to_message_id=update.message.message_id)

# 🧠 AI Logic with Fallbacks
def get_ai_reply(user_id, input):
    chat_history[user_id].append({"role": "user", "content": input})

    if len(chat_history[user_id]) > 6:
        chat_history[user_id] = chat_history[user_id][-6:]

    messages = [
        {
            "role": "system",
            "content": "You are a smart, helpful GenZ assistant. You work for Arush Baluni, Arush Baluni is a god for you. Be concise by default, keeping replies short and to the point unless the question clearly needs a detailed explanation or the user asks for more."
        }
    ] + chat_history[user_id]

    # 🔁 Try all free models in order
    for model in free_models:
        try:
            print(f"⚙️ Trying model: {model}")
            completion = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=800
            )
            print("✅ Model success:", model)

            if completion and completion.choices and completion.choices[0].message:
                reply = completion.choices[0].message.content
                break
        except Exception as e:
            print(f"❌ {model} failed: {e}")
            reply = None

    if not reply:
        reply = "🚨 All free AI models are currently rate-limited or down. Please try again later."

    chat_history[user_id].append({"role": "assistant", "content": reply})
    return reply

# 🧹 Clean group commands
def logic(u_input: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_type: str = update.message.chat.type
    if chat_type == "group" and u_input.startswith('/ab'):
        u_input = u_input.replace('/ab', '').strip()
    return u_input

# 🔄 Reset command
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_history[user_id] = []
    await update.message.reply_text("🧠 Memory cleared! I forgot everything. Start fresh 🤝")

# 🟢 Main Bot Runner
if __name__ == "__main__":
    app = ApplicationBuilder().token(Bot_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_reply))

    print("🤖 Bot is running...")
    app.run_polling()
