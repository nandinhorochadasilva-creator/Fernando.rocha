import asyncio
import subprocess
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ▼▼▼ COLOQUE SEU TOKEN E CHAT ID AQUI ▼▼▼
TOKEN = "8213294688:AAFvDn749s5K2sZ8xDBvMwomdPdLp66Vc3c"
CHAT_ID = "7408514634"

# --- FUNÇÕES DE COMANDO ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        f"Olá, {user.mention_html()}! Comandos disponíveis:\n"
        f"/status - Mostra o painel de controle.\n"
        f"/scan &lt;url&gt; - Inicia uma varredura de vulnerabilidades."
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f"Usuário {update.effective_user.name} pediu /status")
    try:
        home_dir = os.path.expanduser("~")
        script_path = os.path.join(home_dir, "painel.sh")
        resultado = subprocess.run(
            [script_path], capture_output=True, text=True, check=True, timeout=30
        )
        output = resultado.stdout
        await update.message.reply_text(f"--- Painel de Controle ---\n{output}")
    except Exception as e:
        await update.message.reply_text("Ocorreu um erro ao executar o script de status.")
        print(f"Erro ao executar painel.sh: {e}")

# --- LÓGICA PARA TAREFAS EM SEGUNDO PLANO ---

async def run_scan_task(update: Update, context: ContextTypes.DEFAULT_TYPE, target_url: str):
    chat_id = update.effective_chat.id
    print(f"Iniciando scan para {target_url} para o chat {chat_id}")

    if not target_url.startswith("http://") and not target_url.startswith("https://"):
        sanitized_url = "https://" + target_url
    else:
        sanitized_url = target_url
    
    domain_part = sanitized_url.split('//')[1]
    report_folder_name = "relatorio_" + domain_part.replace('/', '_').replace(':', '_')
    report_path = os.path.join(os.path.expanduser("~"), report_folder_name)
    
    command = ["wapiti", "-u", sanitized_url, "-o", report_path, "--scope", "domain"]

    process = await asyncio.create_subprocess_exec(
        *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        final_message = f"✅ Varredura de '{sanitized_url}' concluída!\n\nRelatório salvo em: {report_folder_name}"
    else:
        final_message = f"❌ A varredura de '{sanitized_url}' falhou.\n\nErro:\n{stderr.decode()}"
    
    await context.bot.send_message(chat_id=chat_id, text=final_message)
    print(f"Scan para {sanitized_url} concluído.")

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Uso: /scan <url>\nExemplo: /scan exemplo.com")
        return
    
    target_url = context.args[0]
    await update.message.reply_text(
        f"Entendido! 🚀\nIniciando varredura em {target_url}.\n"
        f"Este processo pode levar horas. Avisarei quando terminar."
    )
    asyncio.create_task(run_scan_task(update, context, target_url))

# --- FUNÇÃO PRINCIPAL ---

def main() -> None:
    print("Iniciando o bot...")
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("scan", scan))

    print("Bot iniciado. Pressione Ctrl+C para parar.")
    application.run_polling()

if __name__ == "__main__":
    main()
