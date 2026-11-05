#!/usr/bin/env bash
# ==============================================================================
# Script de Configuração da Instância Amazon EC2 (Ubuntu 22.04 / 24.04 LTS)
# Disciplina: Integração DevOps
# ==============================================================================
set -e

echo "=== 1. Atualizando pacotes do sistema ==="
sudo apt-get update -y
sudo apt-get upgrade -y

echo "=== 2. Instalando pré-requisitos (curl, unzip, ca-certificates) ==="
sudo apt-get install -y ca-certificates curl gnupg lsb-release unzip

echo "=== 3. Instalando Docker ==="
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg --yes
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

echo "=== 4. Habilitando Docker e adicionando usuário ubuntu ao grupo docker ==="
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker ubuntu

echo "=== 5. Instalando AWS CLI v2 ==="
if ! command -v aws &> /dev/null; then
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip -q awscliv2.zip
    sudo ./aws/install
    rm -rf aws awscliv2.zip
fi

echo "=== 6. Validando instalações ==="
docker --version
aws --version

echo "=========================================================="
echo " Configuração concluída com sucesso!"
echo " AVISO: Se você estiver conectado via SSH, desconecte e"
echo " conecte-se novamente para atualizar as permissões do grupo docker."
echo "=========================================================="
