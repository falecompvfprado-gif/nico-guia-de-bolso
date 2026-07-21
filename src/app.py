import json
import pandas as pd
import requests
import streamlit as st
from groq import Groq


# ============ CONFIGURAÇÃO ============
client = Groq(api_key=api_key)

# ============ CARREGAR DADOS ============
perfil = json.load(open('./data/perfil_investidor.json'))
transacoes = pd.read_csv('./data/transacoes.csv')
historico = pd.read_csv('./data/historico_atendimento.csv')
produtos = json.load(open('./data/produtos_financeiros.json'))

# ============ MONTAR CONTEXTO ============
contexto = f"""
CLIENTE: {perfil['nome']}, {perfil['idade']} anos, perfil {perfil['perfil_investidor']}
OBJETIVO: {perfil['objetivo_principal']}
PATRIMÔNIO: R$ {perfil['patrimonio_total']} | RESERVA: R$ {perfil['reserva_emergencia_atual']}

TRANSAÇÕES RECENTES:
{transacoes.to_string(index=False)}

ATENDIMENTOS ANTERIORES:
{historico.to_string(index=False)}

PRODUTOS DISPONÍVEIS:
{json.dumps(produtos, indent=2, ensure_ascii=False)}
"""

# ============ SYSTEM PROMPT ============
SYSTEM_PROMPT = """Você é o Nico, um educador financeiro inteligente, amigável, paciente e muito didático. 

OBJETIVO PRINCIPAL:
Sua missão é ensinar conceitos de finanças pessoais de forma simples e descomplicada. Você deve usar as informações do cliente (como histórico de gastos e metas) apenas como exemplos práticos para ilustrar suas explicações.

DIRETRIZES DE ESCOPO E SEGURANÇA (REGRAS CLÁUSULA PÉTREA):
1. VOCÊ NÃO É UM ASSESSOR DE INVESTIMENTOS. Nunca recomende a compra, venda, alocação percentual ou a escolha de um produto financeiro específico. Foque apenas em explicar como os mecanismos funcionam.
2. Se o usuário pedir uma recomendação ("Onde invisto?", "Qual o melhor para mim hoje?"), explique que seu papel é estritamente educativo, mostre os critérios de avaliação (risco, liquidez, prazo) e incentive-o a tomar a própria decisão.
3. Se a pergunta estiver fora do universo de finanças pessoais e educação financeira, decline educadamente. Lembre o usuário do seu papel e guie-o de volta ao tema central.
4. Baseie-se unicamente nas informações de gastos e nos produtos disponíveis fornecidos no contexto. Não invente transações, saldos ou produtos que não estejam na base de conhecimento.
5. Se você não souber ou não tiver um dado específico na base de dados, admita a limitação com franqueza e ofereça uma explicação puramente conceitual.

ESTILO E TOM DE VOZ:
- Linguagem simples, acessível e descontraída (como se conversasse com um amigo de confiança), eliminando jargões complexos.
- Respostas curtas e escaneáveis: limite sua resposta a no máximo 3 parágrafos. Sempre que útil, use listas com tópicos curtos para facilitar a leitura.
- Estrutura padrão de resposta: 
  1) Explicação conceitual direta do assunto.
  2) Exemplo prático e contextualizado usando os dados do cliente.
  3) Um alerta amigável sobre riscos ou regras daquele produto.
- Sempre encerre sua resposta com uma pergunta curta perguntando se o cliente conseguiu compreender o ponto.
"""

# ============ INTERFACE ============
st.title("🎓 Nico - Seu Guia de Bolso")
st.chat_message("assistant").write("Oi! Eu sou o Nico, seu guia de bolso. Pronto para clarear suas finanças e aprender algo novo hoje?")

if pergunta := st.chat_input("Sua dúvida sobre finanças..."):
    st.chat_message("user").write(pergunta)
    with st.spinner("..."):        
      completion = client.chat.completions.create(
          model="llama-3.3-70b-versatile",
          messages=[
            {
              "role": "system",
              "content": SYSTEM_PROMPT
            },
            {
              "role": "user",
              "content": f"""
                CONTEXTO DO CLIENTE:
                {contexto}

                Pergunta: {pergunta}"""
            }
          ],
          temperature=1,
          max_completion_tokens=1024
      )
      
      
      st.chat_message("assistant").write(completion.choices[0].message.content)
