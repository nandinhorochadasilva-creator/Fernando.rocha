#!/data/data/com.termux/files/usr/bin/bash

# Função para verificar e instalar pacotes se necessário
ensure_pkg() {
    if ! command -v $1 &> /dev/null; then
        echo "Ferramenta '$1' não encontrada. Instalando..."
        pkg install $2 -y
    fi
}

# Garante que as dependências estão instaladas
ensure_pkg jq jq
ensure_pkg termux-battery-status termux-api

echo "====================================="
echo " BEM-VINDO AO SEU PAINEL DE CONTROLE "
echo "====================================="
echo ""
echo "Hoje é: $(date +'%A, %d de %B de %Y')"
echo "Hora atual: $(date +'%H:%M:%S')"
echo ""

echo "--- STATUS DO SISTEMA ---"
BATERIA_INFO=$(termux-battery-status)
BATERIA_PCT=$(echo $BATERIA_INFO | jq '.percentage')
BATERIA_STATUS=$(echo $BATERIA_INFO | jq -r '.status')
echo "Bateria: ${BATERIA_PCT}% (${BATERIA_STATUS})"
echo "-------------------------"

echo -n "Clima em São Paulo: "
curl -s wttr.in/Sao_Paulo?format=3
echo ""
echo "-------------------------------------"
