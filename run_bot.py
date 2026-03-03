# -*- coding: utf-8 -*-

import os
import random
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from configuracoes import (
    BLOG_ID,
    MODULOS_EDITORIAIS,
    DIAS_REPETICAO_TEMA,
    DIAS_REPETICAO_MODULO,
    TAGS_FIXAS_FOTOGRAFIA,
    BLOCO_FIXO_FINAL
)

from template_blog import obter_esqueleto_html
from gemini_engine import GeminiEngine
from imagem_engine import ImageEngine


# ==========================================================
# CONFIGURAÇÃO
# ==========================================================

HORARIO_PUBLICACAO = "19:00"
JANELA_MINUTOS = 59

ARQUIVO_CONTROLE_DIARIO = "controle_diario.txt"
ARQUIVO_CONTROLE_MODULOS = "controle_modulos.txt"
ARQUIVO_CONTROLE_TEMAS = "controle_temas.txt"


# ==========================================================
# UTILIDADES DE TEMPO
# ==========================================================

def obter_horario_brasilia():
    return datetime.utcnow() - timedelta(hours=3)


def horario_para_minutos(hhmm):
    h, m = map(int, hhmm.split(":"))
    return h * 60 + m


def dentro_da_janela(min_atual, min_agenda):
    return abs(min_atual - min_agenda) <= JANELA_MINUTOS


# ==========================================================
# CONTROLE DIÁRIO
# ==========================================================

def ja_postou(data_str, horario_agenda):
    if not os.path.exists(ARQUIVO_CONTROLE_DIARIO):
        return False
    with open(ARQUIVO_CONTROLE_DIARIO, "r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if not linha or "|" not in linha: continue
            partes = linha.split("|")
            if len(partes) == 2:
                data, hora = partes
                if data == data_str and hora == horario_agenda:
                    return True
    return False

def registrar_postagem(data_str, horario_agenda):
    linhas = []
    if os.path.exists(ARQUIVO_CONTROLE_DIARIO):
        with open(ARQUIVO_CONTROLE_DIARIO, "r", encoding="utf-8") as f:
            linhas = f.readlines()

    # Adiciona o novo registro e mantém apenas os últimos 15
    nova_linha = f"{data_str}|{horario_agenda}\n"
    if nova_linha not in linhas:
        linhas.append(nova_linha)
    
    linhas = linhas[-100:] # Mantém o arquivo leve (aprox. 100 dias de histórico)

    with open(ARQUIVO_CONTROLE_DIARIO, "w", encoding="utf-8") as f:
        f.writelines(linhas)


# ==========================================================
# CONTROLE DE REPETIÇÃO DE MÓDULO
# ==========================================================

def modulo_usado_recentemente(modulo):

    if not os.path.exists(ARQUIVO_CONTROLE_MODULOS):
        return False

    hoje = datetime.utcnow()

    with open(ARQUIVO_CONTROLE_MODULOS, "r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if not linha or "|" not in linha:
                continue

            data_str, modulo_salvo = linha.split("|")

            try:
                data_mod = datetime.strptime(data_str, "%Y-%m-%d")
            except:
                continue

            if modulo_salvo == modulo:
                if (hoje - data_mod).days < DIAS_REPETICAO_MODULO:
                    return True

    return False


def registrar_modulo(modulo):
    hoje = datetime.utcnow().strftime("%Y-%m-%d")
    with open(ARQUIVO_CONTROLE_MODULOS, "a", encoding="utf-8") as f:
        f.write(f"{hoje}|{modulo}\n")


# ==========================================================
# CONTROLE DE REPETIÇÃO DE TEMA
# ==========================================================

def tema_usado_recentemente(tema):

    if not os.path.exists(ARQUIVO_CONTROLE_TEMAS):
        return False

    hoje = datetime.utcnow()

    with open(ARQUIVO_CONTROLE_TEMAS, "r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if not linha or "|" not in linha:
                continue

            data_str, tema_salvo = linha.split("|")

            try:
                data_tema = datetime.strptime(data_str, "%Y-%m-%d")
            except:
                continue

            if tema_salvo == tema:
                if (hoje - data_tema).days < DIAS_REPETICAO_TEMA:
                    return True

    return False


def registrar_tema(tema):
    hoje = datetime.utcnow().strftime("%Y-%m-%d")
    with open(ARQUIVO_CONTROLE_TEMAS, "a", encoding="utf-8") as f:
        f.write(f"{hoje}|{tema}\n")


# ==========================================================
# ESCOLHER MÓDULO E TEMA
# ==========================================================

def escolher_modulo_e_tema():

    modulos_disponiveis = list(MODULOS_EDITORIAIS.keys())
    random.shuffle(modulos_disponiveis)

    modulo_escolhido = None

    for modulo in modulos_disponiveis:
        if not modulo_usado_recentemente(modulo):
            modulo_escolhido = modulo
            break

    if not modulo_escolhido:
        modulo_escolhido = random.choice(modulos_disponiveis)

    temas = MODULOS_EDITORIAIS[modulo_escolhido].copy()
    random.shuffle(temas)

    tema_escolhido = None

    for tema in temas:
        if not tema_usado_recentemente(tema):
            tema_escolhido = tema
            break

    if not tema_escolhido:
        tema_escolhido = random.choice(temas)

    return modulo_escolhido, tema_escolhido


# ==========================================================
# GERAR TAGS SEO
# ==========================================================

def gerar_tags_seo(modulo, tema):

    tags = TAGS_FIXAS_FOTOGRAFIA.copy()

    tags.append(modulo.capitalize())
    tags.append(tema)

    resultado = []
    tamanho_atual = 0

    for tag in tags:
        if tamanho_atual + len(tag) + 2 <= 200:
            resultado.append(tag)
            tamanho_atual += len(tag) + 2
        else:
            break

    return resultado


# ==========================================================
# MODO TESTE
# ==========================================================

def executar_modo_teste(modulo_forcado=None, tema_forcado=None, publicar=False):

    print("=== MODO TESTE ATIVADO ===")

    if not modulo_forcado:
        modulo_forcado = random.choice(list(MODULOS_EDITORIAIS.keys()))

    if not tema_forcado:
        tema_forcado = random.choice(MODULOS_EDITORIAIS[modulo_forcado])

    print(f"Módulo: {modulo_forcado}")
    print(f"Tema: {tema_forcado}")

    gemini = GeminiEngine()
    imagem_engine = ImageEngine()

    texto_ia = gemini.gerar_artigo_tecnico_fotografia(modulo_forcado, tema_forcado)
    query_visual = gemini.gerar_query_visual_fotografia(modulo_forcado, tema_forcado)

    imagem_final = imagem_engine.obter_imagem(modulo_forcado, tema_forcado, query_visual)

    tags = gerar_tags_seo(modulo_forcado, tema_forcado)

    dados = {
        "titulo": tema_forcado,
        "imagem": imagem_final,
        "texto_completo": texto_ia,
        "assinatura": BLOCO_FIXO_FINAL
    }

    html = obter_esqueleto_html(dados)

    service = Credentials.from_authorized_user_file("token.json")
    service = build("blogger", "v3", credentials=service)

    service.posts().insert(
        blogId=BLOG_ID,
        body={
            "title": tema_forcado,
            "content": html,
            "labels": tags
        },
        isDraft=not publicar
    ).execute()

    print("Postagem de teste concluída.")


# ==========================================================
# EXECUÇÃO PRINCIPAL
# ==========================================================

if __name__ == "__main__":

    # VERIFICA MODO TESTE
    if os.getenv("TEST_MODE") == "true":

        modulo_teste = os.getenv("TEST_MODULO")
        tema_teste = os.getenv("TEST_TEMA")
        publicar_teste = os.getenv("TEST_PUBLICAR", "false") == "true"

        executar_modo_teste(
            modulo_forcado=modulo_teste,
            tema_forcado=tema_teste,
            publicar=publicar_teste
        )

        exit()

    agora = obter_horario_brasilia()
    min_atual = agora.hour * 60 + agora.minute
    min_agenda = horario_para_minutos(HORARIO_PUBLICACAO)

    data_hoje = agora.strftime("%Y-%m-%d")

    if not dentro_da_janela(min_atual, min_agenda):
        print("Fora da janela de publicação.")
        exit()

    if ja_postou_hoje(data_hoje):
        print("Postagem já realizada hoje.")
        exit()

    modulo, tema = escolher_modulo_e_tema()

    gemini = GeminiEngine()
    imagem_engine = ImageEngine()

    texto_ia = gemini.gerar_artigo_tecnico_fotografia(modulo, tema)
    query_visual = gemini.gerar_query_visual_fotografia(modulo, tema)

    imagem_final = imagem_engine.obter_imagem(modulo, tema, query_visual)

    tags = gerar_tags_seo(modulo, tema)

    dados = {
        "titulo": tema,
        "imagem": imagem_final,
        "texto_completo": texto_ia,
        "assinatura": BLOCO_FIXO_FINAL
    }

    html = obter_esqueleto_html(dados)

    service = Credentials.from_authorized_user_file("token.json")
    service = build("blogger", "v3", credentials=service)

    service.posts().insert(
        blogId=BLOG_ID,
        body={
            "title": tema,
            "content": html,
            "labels": tags
        },
        isDraft=False
    ).execute()

    registrar_postagem(data_hoje)
    registrar_modulo(modulo)
    registrar_tema(tema)

    print("Post publicado com sucesso.")
