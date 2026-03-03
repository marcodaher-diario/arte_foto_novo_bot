# -*- coding: utf-8 -*-

import os
from google import genai


class GeminiEngine:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)

    # ==========================================================
    # GERAR ARTIGO TÉCNICO EVERGREEN - FOTOGRAFIA
    # ==========================================================

    def gerar_artigo_tecnico_fotografia(self, modulo, tema):

        prompt = f"""
Atue como um Fotógrafo Profissional e Educador Técnico com mais de 20 anos de experiência em fotografia digital, analógica e produção audiovisual.

Seu objetivo é produzir um artigo técnico, didático e evergreen para um blog especializado em fotografia chamado "MD Arte Foto".

Módulo Editorial: {modulo}
Tema do Artigo: {tema}

Diretrizes Obrigatórias:

Tom e Estilo:
- Linguagem clara, técnica e educativa.
- Não utilizar primeira pessoa.
- Não emitir opiniões pessoais.
- Não usar linguagem sensacionalista.
- Manter postura profissional e instrutiva.

Extensão:
- Entre 900 e 1200 palavras.
- Parágrafos desenvolvidos com profundidade técnica.

Estrutura Obrigatória:

Título Principal (não repetir o módulo).
Introdução envolvente contextualizando o tema.
Seção explicando o conceito técnico detalhadamente.
Seção mostrando aplicação prática no mundo real.
Seção sobre erros comuns e como evitá-los.
Seção com dicas profissionais avançadas.
Considerações Finais com visão estratégica e educativa.

Regras:
- Usar subtítulos naturais no texto.
- Não escrever comentários fora do artigo.
- Não explicar o que está fazendo.
- Entregar apenas o artigo final estruturado.
"""

        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        return response.text.strip()

    # ==========================================================
    # GERAR QUERY VISUAL PARA BUSCA DE IMAGEM
    # ==========================================================

    def gerar_query_visual_fotografia(self, modulo, tema):

        prompt = f"""
Com base no módulo editorial e no tema abaixo, gere APENAS uma sequência de 3 a 5 palavras-chave em INGLÊS que representem uma imagem fotográfica ideal para ilustrar o artigo.

Módulo: {modulo}
Tema: {tema}

Diretrizes:
- Usar apenas termos visuais.
- Não usar frases completas.
- Não usar pontuação extra.
- Focar em câmera, luz, lente, cenário ou ação fotográfica.
- Retornar somente as palavras em inglês.
"""

        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            return response.text.strip().replace('"', '').replace("'", "")
        except:
            return None

    # ==========================================================
    # GERAR META DESCRIÇÃO SEO
    # ==========================================================

    def gerar_meta_descricao(self, titulo, texto):

        prompt = f"""
Crie uma meta descrição SEO otimizada entre 140 e 160 caracteres com base no título e no conteúdo abaixo.

Título: {titulo}

Conteúdo:
{texto[:1000]}

Regras:
- Linguagem profissional.
- Foco em fotografia.
- Alta taxa de clique.
- Não ultrapassar 160 caracteres.
- Retornar apenas a meta descrição.
"""

        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            return response.text.strip()
        except:
            return ""
