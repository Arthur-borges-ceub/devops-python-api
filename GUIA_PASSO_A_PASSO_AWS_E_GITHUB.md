# Guia Completo de Execução — AWS, GitHub Actions e Entrega Moodle

Este guia contém o passo a passo exato e detalhado para configurar a AWS, configurar o GitHub, executar o fluxo de branches exigido pelo professor e capturar todas as evidências para obter nota **10/10** no trabalho.

---

## Sumário
1. [Configuração na AWS (ECR, IAM, EC2 e Security Group)](#1-configuração-na-aws)
2. [Configuração do Repositório no GitHub e Secrets](#2-configuração-do-repositório-no-github-e-secrets)
3. [Executando o Fluxo de Branches e Pull Requests (Etapas 1 a 6)](#3-executando-o-fluxo-de-branches-e-pull-requests)
4. [Executando a Atualização Automática (Etapa 7)](#4-executando-a-atualização-automática-etapa-7)
5. [Checklist Completo de Evidências para Entrega no Moodle](#5-checklist-completo-de-evidências-para-entrega-no-moodle)
6. [Destruição dos Recursos da AWS (Evitar Cobranças)](#6-destruição-dos-recursos-da-aws)

---

## 1. Configuração na AWS

### Passo 1.1: Criar o Repositório no Amazon ECR
1. Acesse o **AWS Console** e pesquise por **Elastic Container Registry (ECR)**.
2. Certifique-se de estar na região desejada (por exemplo: `us-east-1` - N. Virginia).
3. Clique em **Create repository** (Criar repositório).
4. Selecione a visibilidade: **Private** (Privado).
5. Nome do repositório: `devops-python-api`.
6. Deixe as demais opções como padrão e clique em **Create repository**.
7. Guarde a URI gerada (exemplo: `123456789012.dkr.ecr.us-east-1.amazonaws.com/devops-python-api`).

---

### Passo 1.2: Criar a IAM Role para a Instância EC2
> *Exigência da Etapa 5 do trabalho: "A instância deverá utilizar uma IAM Role para obter as permissões de leitura do ECR."*

1. No console da AWS, pesquise por **IAM** > **Roles** (Funções) > **Create role**.
2. Tipo de entidade confiável: **AWS service** (Serviço da AWS).
3. Caso de uso: Selecione **EC2** e clique em **Next**.
4. Em permissões, pesquise e marque:
   - `AmazonEC2ContainerRegistryReadOnly`
5. Clique em **Next**.
6. Nome da Role: `EC2-ECR-ReadOnly-Role`.
7. Clique em **Create role**.

---

### Passo 1.3: Criar Usuário IAM para o GitHub Actions
Para que o GitHub Actions consiga enviar as imagens construídas para o Amazon ECR:
1. No menu do **IAM**, vá em **Users** (Usuários) > **Create user**.
2. Nome: `github-actions-deployer`.
3. Não marque acesso ao console (apenas acesso programático). Clique em **Next**.
4. Selecione **Attach policies directly** (Anexar políticas diretamente) e adicione:
   - `AmazonEC2ContainerRegistryPowerUser` (permite autenticar, puxar e enviar imagens ao ECR).
5. Clique em **Next** e depois em **Create user**.
6. Clique no usuário criado > aba **Security credentials** (Credenciais de segurança).
7. Vá na seção **Access keys** (Chaves de acesso) > **Create access key**.
8. Selecione o caso de uso **Application running outside AWS** (ou Third-party service).
9. Copie e guarde em um local seguro:
   - `Access key ID` (ex: `AKIA...`)
   - `Secret access key` (ex: `wJalrXUtn...`)

---

### Passo 1.4: Criar o Par de Chaves (Key Pair)
1. Vá para o console do **EC2** > no menu lateral esquerdo, clique em **Key Pairs** (Pares de chaves).
2. Clique em **Create key pair**.
3. Nome: `devops-ec2-key`.
4. Tipo: **RSA**, formato: `.pem`.
5. Clique em **Create key pair** e o arquivo `devops-ec2-key.pem` será baixado no seu computador. Guarde-o com cuidado.

---

### Passo 1.5: Criar o Security Group
1. No menu lateral do **EC2**, clique em **Security Groups** > **Create security group**.
2. Nome: `devops-python-api-sg`.
3. Descrição: `Security group para permitir SSH e HTTP`.
4. Em **Inbound rules** (Regras de entrada), adicione:
   - **Regra 1:** Tipo `SSH` | Porta `22` | Origem `Anywhere-IPv4` (`0.0.0.0/0`)
   - **Regra 2:** Tipo `HTTP` | Porta `80` | Origem `Anywhere-IPv4` (`0.0.0.0/0`)
5. Clique em **Create security group**.

---

### Passo 1.6: Criar e Iniciar a Instância EC2
1. No menu lateral do **EC2**, clique em **Instances** > **Launch instances**.
2. Nome: `devops-python-api-server`.
3. Imagem do Sistema (AMI): Selecione **Ubuntu Server 24.04 LTS** (ou 22.04 LTS) - *Eligible for free tier*.
4. Tipo de instância: `t2.micro` ou `t3.micro`.
5. Key pair: Selecione `devops-ec2-key`.
6. Configurações de rede: Clique em **Edit**, selecione a sua VPC e escolha o Security Group `devops-python-api-sg` criado no passo 1.5. Garanta que **Auto-assign public IP** esteja **Enable** (Habilitado).
7. Expanda a seção **Advanced details** (Detalhes avançados):
   - No campo **IAM instance profile**, selecione a role criada: `EC2-ECR-ReadOnly-Role`.
   - No campo **User data**, cole o conteúdo do arquivo `scripts/setup-ec2.sh` para instalar Docker e AWS CLI automaticamente na inicialização.
8. Clique em **Launch instance**.
9. Aguarde a instância mudar para status `Running` e anote o **Public IPv4 address** (ex: `54.210.12.34`).

---

## 2. Configuração do Repositório no GitHub e Secrets

### Passo 2.1: Criar Repositório no GitHub
1. Acesse seu perfil no [GitHub](https://github.com/) e clique em **New repository**.
2. Nome do repositório: `devops-python-api`.
3. Visibilidade: Pode ser **Public** (ou Private, se for compartilhar com o professor).
4. **Não marque** a opção de inicializar com README (pois já temos o código pronto localmente).
5. Clique em **Create repository**.

---

### Passo 2.2: Cadastrar os GitHub Secrets
No seu novo repositório no GitHub:
1. Vá na aba **Settings** > no menu lateral esquerdo clique em **Secrets and variables** > **Actions**.
2. Clique no botão **New repository secret** e cadastre cada uma das variáveis abaixo:

| Nome do Secret | Valor / Onde obter |
| :--- | :--- |
| `AWS_ACCESS_KEY_ID` | Chave de acesso do usuário `github-actions-deployer` (Passo 1.3) |
| `AWS_SECRET_ACCESS_KEY` | Chave secreta do usuário `github-actions-deployer` (Passo 1.3) |
| `AWS_REGION` | Região da sua conta AWS (ex: `us-east-1`) |
| `ECR_REPOSITORY` | `devops-python-api` |
| `EC2_HOST` | Endereço IP Público da sua EC2 (ex: `54.210.12.34`) |
| `EC2_USER` | `ubuntu` |
| `EC2_SSH_KEY` | Todo o conteúdo textual do arquivo de chave privada `devops-ec2-key.pem` (incluindo as linhas `-----BEGIN RSA PRIVATE KEY-----` e `-----END RSA PRIVATE KEY-----`) |

---

## 3. Executando o Fluxo de Branches e Pull Requests

> *Atenção aos critérios do professor: "Não serão considerados suficientes trabalhos que realizem todas as alterações diretamente na branch main, sem demonstrar o processo de desenvolvimento por branches e Pull Requests."*

Execute os passos a seguir no seu terminal dentro do diretório do projeto:

### 3.1 Inicializar o repositório local e publicar a base
```powershell
cd C:\Users\arthur.borgess\.gemini\antigravity\scratch\devops-python-api

# Inicializar o git
git init -b main

# Configurar seu usuário git (se ainda não configurado)
git config user.name "Seu Nome"
git config user.email "seu.email@exemplo.com"

# Adicionar o código base inicial (app.py, requirements, tests)
git add app.py requirements.txt tests/ .gitignore
git commit -m "feat: implementacao inicial da API Flask e testes unitarios"

# Conectar ao seu repositorio remoto no GitHub
git remote add origin https://github.com/Arthur-borges-ceub/devops-python-api.git

# Enviar para a main
git push -u origin main
```

---

### 3.2 Criar a branch `feature/ci-cd-ec2` e adicionar a esteira (Etapa 1)
```powershell
# 1. Criar e mudar para a branch requerida
git checkout -b feature/ci-cd-ec2

# 2. Adicionar os arquivos de Docker, Workflows de CI/CD, scripts e documentação
git add Dockerfile .dockerignore .github/ README.md scripts/
git commit -m "feat(devops): adicao de Dockerfile, pipelines CI/CD e configuracao de deploy EC2"

# 3. Enviar a branch para o GitHub
git push -u origin feature/ci-cd-ec2
```

---

### 3.3 Abrir e Validar o Pull Request (Etapa 2)
1. Vá até o GitHub no seu repositório.
2. Você verá o aviso sugerindo abrir um PR: clique em **Compare & pull request**.
3. Destino (base): `main` <- De (compare): `feature/ci-cd-ec2`.
4. Título: `feat: Implementação de Pipeline CI/CD, Docker e Deploy na AWS EC2`.
5. Descrição: `Adiciona workflow de CI com pytest, Dockerfile otimizado e workflow de CD integrado ao Amazon ECR e EC2.`
6. Clique em **Create pull request**.
7. **Observe o GitHub Actions:** O workflow `ci.yml` será acionado automaticamente!
8. Aguarde os testes com `pytest` serem concluídos com sucesso (símbolo verde `✔`).
9. **📸 TIRE O PRINT 01 AQUI:** Screenshot do Pull Request com os testes do GitHub Actions aprovados (*Evidência B*).
10. Clique em **Merge pull request** e depois em **Confirm merge**.

---

### 3.4 Acompanhar o Deploy Automatizado (Etapas 4, 5 e 6)
1. Após o merge na `main`, clique na aba **Actions** no GitHub.
2. Veja o workflow `Continuous Deployment (CD)` sendo executado.
3. Ele passará pelas etapas:
   - *Test* (pytest)
   - *Configure AWS Credentials*
   - *Login to Amazon ECR*
   - *Build, tag, and push image to Amazon ECR*
   - *Deploy to Amazon EC2 via SSH*
4. **📸 TIRE O PRINT 02 AQUI:** Console do Amazon ECR exibindo as imagens com a tag do commit e a tag latest (*Evidência C*).
5. **📸 TIRE O PRINT 03 AQUI:** Workflow `deploy.yml` finalizado com sucesso no GitHub Actions (*Evidência D - parte 1*).
6. Acesse a EC2 via SSH ou abra o navegador:
   - No navegador, acesse: `http://<IP_PUBLICO_EC2>/`
   - Acesse: `http://<IP_PUBLICO_EC2>/health`
   - Acesse: `http://<IP_PUBLICO_EC2>/api/v1/version`
7. **📸 TIRE O PRINT 04 AQUI:** Terminal da EC2 executando `docker ps` (*Evidência D - parte 2*).
8. **📸 TIRE O PRINT 05 AQUI:** Navegador exibindo a resposta JSON da API rodando no IP público da EC2 (*Evidência D - parte 3*).

---

## 4. Executando a Atualização Automática (Etapa 7)

> *Exigência da Etapa 7: Modificar alguma característica visível da aplicação (ex: versão v1.0.0 para v1.1.0) e demonstrar que a atualização ocorre de forma 100% automatizada.*

### 4.1 Criar a branch de atualização
```powershell
# Voltar para a main e atualizar com o merge anterior
git checkout main
git pull origin main

# Criar nova branch para a versao 1.1.0
git checkout -b feature/atualizacao-v1.1.0
```

### 4.2 Alterar a versão no código
No arquivo `app.py`, altere o valor padrão da versão:
```python
# Em app.py:
APP_VERSION = os.getenv("APP_VERSION", "1.1.0")
```

No arquivo `app.py`, você também pode adicionar uma mensagem comemorativa no endpoint `/`:
```python
"message": "DevOps Python API v1.1.0 - Atualização Automática Concluída!",
```

### 4.3 Testar localmente e commitar
```powershell
# Testar localmente
pytest -v

# Registrar o commit
git add app.py
git commit -m "feat(api): atualiza versao da aplicacao para v1.1.0"
git push -u origin feature/atualizacao-v1.1.0
```

### 4.4 Abrir o 2º Pull Request e realizar o Merge
1. No GitHub, abra o Pull Request da branch `feature/atualizacao-v1.1.0` para a `main`.
2. Aguarde a validação do `ci.yml`.
3. Realize o **Merge**.
4. Acompanhe a pipeline `deploy.yml`. Ela irá construir a nova imagem com o novo commit SHA, enviar ao ECR e substituir o container na EC2 automaticamente.
5. Recarregue no navegador `http://<IP_PUBLICO_EC2>/api/v1/version` ou `http://<IP_PUBLICO_EC2>/`.
6. Veja a nova versão `1.1.0` refletida em tempo real!
7. **📸 TIRE O PRINT 06 AQUI:** Comparativo ou print da tela com a versão atualizada v1.1.0 (*Evidência E*).

---

## 5. Checklist Completo de Evidências para Entrega no Moodle

Verifique se você possui todos os itens do relatório final:

- [ ] **A. Link do Repositório GitHub:** `https://github.com/<seu-usuario>/devops-python-api`
- [ ] **B. Evidência de Integração Contínua (CI):**
  - Print do GitHub Actions mostrando a execução dos testes com sucesso na abertura do PR.
- [ ] **C. Evidência de Publicação Docker (ECR):**
  - Print da tela do Amazon ECR com a imagem listada, exibindo as tags do commit e latest.
- [ ] **D. Evidências do Deploy (EC2):**
  - Print da pipeline `deploy.yml` finalizada em verde.
  - Print do terminal da EC2 rodando `docker ps` mostrando o container ativo.
  - Print do navegador acessando a API no IP público da EC2.
- [ ] **E. Evidência de Atualização Automática (Etapa 7):**
  - Print da versão 1.0.0 antes do merge.
  - Print da versão 1.1.0 após o merge na main, comprovando o ciclo contínuo sem intervenção manual.
- [ ] **F. Links dos Pull Requests:**
  - Link do 1º PR (`feature/ci-cd-ec2` -> `main`).
  - Link do 2º PR (`feature/atualizacao-v1.1.0` -> `main`).

---

## 6. Destruição dos Recursos da AWS (Evitar Cobranças)

> *Lembrete obrigatório da Seção 8 do trabalho: "Os alunos deverão interromper ou excluir os recursos da AWS após a conclusão e avaliação da atividade, evitando cobranças desnecessárias."*

Após a apresentação/avaliação do professor:
1. **EC2:** Selecione a instância `devops-python-api-server` > **Instance state** > **Terminate instance**.
2. **ECR:** Vá em Repositories > selecione `devops-python-api` > clique em **Delete**.
3. **IAM:** Exclua as chaves de acesso do usuário `github-actions-deployer` e a Role `EC2-ECR-ReadOnly-Role`.

