# Relatórios de Anúncios

Este é um servidor local desenvolvido em **Python+Flask** para consumir dados de uma API de anúncios e gerar relatórios em formato **CSV**. O projeto permite a geração de relatórios em tempo real, acessíveis através de endpoints organizados por plataforma e tipo de relatório.

---

## 📋 Funcionalidades

O servidor consome dados de anúncios de várias plataformas e gera relatórios em tempo real, acessíveis através dos seguintes endpoints:  

- **`/`** - Exibe informações pessoais (nome, e-mail e LinkedIn).  
- **`/{{plataforma}}`** - Relatório detalhado de anúncios para uma plataforma específica.  
- **`/{{plataforma}}/resumo`** - Resumo consolidado dos anúncios por conta para a plataforma específica.  
- **`/geral`** - Relatório geral de anúncios de todas as plataformas.  
- **`/geral/resumo`** - Resumo consolidado dos anúncios por plataforma.  

---

## 🚀 Tecnologias Utilizadas

- **Python** (versão 3.8+)
- **Flask** - Framework para construção da API.
- **Requests** - Para consumir os dados da API de anúncios.
- **CSV** - Formato de saída para os relatórios.

---

## ⚙️ Instalação e Configuração

### Pré-requisitos

- Tenha o **Python 3.8** (ou superior) instalado na sua máquina.
- Recomenda-se o uso de um ambiente virtual para isolamento de dependências.

### 1. Clonar o Repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd <PASTA_DO_REPOSITORIO>
