import subprocess
import sys
import requests

# --- CONFIGURAÇÃO ---
TARGET_DOMAIN = "google.com" 

# ▼▼▼ COLOQUE SUAS INFORMAÇÕES DO TELEGRAM AQUI ▼▼▼
BOT_TOKEN = "8213294688:AAFvDn749s5K2sZ8xDBvMwomdPdLp66Vc3c"
CHAT_ID = "7408514634"

# --- NOVA FUNÇÃO "TRADUTORA" ---
def escape_markdown(text: str) -> str:
    """Protege os caracteres especiais para o modo MarkdownV2 do Telegram."""
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)

def send_telegram_alert(found_domain):
    """Envia um alerta para o Telegram."""
    safe_found_domain = escape_markdown(found_domain)
    safe_target_domain = escape_markdown(TARGET_DOMAIN)

    message = (
        f"🚨 *ALERTA \\- SENTINELA PHISHGUARD* 🚨\n\n"
        f"Domínio suspeito registrado:\n`{safe_found_domain}`\n\n"
        f"Pode ser usado para atacar:\n`{safe_target_domain}`"
    )
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    # A LINHA CORRIGIDA ESTÁ AQUI (CHAT_ID em vez de CH_ID)
    params = {"chat_id": CHAT_ID, "text": message, "parse_mode": "MarkdownV2"}
    
    try:
        response = requests.get(url, params=params)
        if response.json().get('ok'):
            sys.stdout.write("\n[+] Alerta enviado com sucesso para o Telegram!\n")
        else:
            sys.stdout.write(f"\n[-] Falha ao enviar alerta: {response.text}\n")
    except Exception as e:
        sys.stdout.write(f"\n[-] Erro de conexão com a API do Telegram: {e}\n")

def generate_typos(domain):
    print(f"[*] Gerando variações para {domain}...")
    parts = domain.split('.')
    if len(parts) < 2: return []
    domain_name = parts[0]
    tld = '.'.join(parts[1:])
    typos = set()
    for i in range(len(domain_name)):
        typos.add(domain_name[:i] + domain_name[i+1:] + '.' + tld)
    for i in range(len(domain_name) - 1):
        typos.add(domain_name[:i] + domain_name[i+1] + domain_name[i] + domain_name[i+2:] + '.' + tld)
    typos.add(f"suporte-{domain_name}.{tld}")
    typos.add(f"login-{domain_name}.{tld}")
    typos.add(f"acesso-{domain_name}.{tld}")
    print(f"[+] {len(typos)} variações geradas.")
    return list(typos)

def is_domain_registered(domain):
    try:
        command = ["dig", "+short", "A", domain]
        result = subprocess.run(command, capture_output=True, text=True, timeout=5)
        return bool(result.stdout.strip())
    except Exception:
        return False

def main():
    print("--- Iniciando Sentinela PhishGuard (com Alertas Telegram) ---")
    variations = generate_typos(TARGET_DOMAIN)
    if not variations: return

    print("\n[*] Iniciando verificação de domínios...")
    found_count = 0
    for domain in sorted(variations):
        sys.stdout.write(f"    -> Verificando {domain.ljust(30)}...")
        sys.stdout.flush()
        
        if is_domain_registered(domain):
            sys.stdout.write(f"\r✅ [ALERTA! REGISTRADO!] {domain.ljust(30)}\n")
            found_count += 1
            send_telegram_alert(domain)
        else:
            sys.stdout.write(f"\r❌ [Não Registrado] {domain.ljust(30)}\n")

    print("\n--- Verificação Concluída ---")
    if found_count > 0:
        print(f"🚨 Encontrados e reportados {found_count} domínios suspeitos!")
    else:
        print("👍 Nenhum domínio suspeito com base nas nossas variações foi encontrado.")

if __name__ == "__main__":
    main()
