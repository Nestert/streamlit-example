import streamlit as st
import spacy
import pandas as pd
import networkx as nx
import graphviz
import chardet
from collections import Counter


def upload_file():
    file = st.file_uploader("Загрузите файл книги в формате TXT", type=["txt"])
    return file

def process_text(file):
    raw_data = file.read()
    detected_encoding = chardet.detect(raw_data)
    text = raw_data.decode(detected_encoding["encoding"])
    return text

def extract_entities(text):
    nlp = spacy.load("ru_core_news_sm")
    doc = nlp(text)
    return doc

def count_characters(doc):
    characters = Counter()
    for ent in doc.ents:
        if ent.label_ == "PER":
            characters[ent.text] += 1

    character_df = pd.DataFrame(characters.items(), columns=["Персонаж", "Количество"])
    character_df = character_df.sort_values(by="Количество", ascending=False)

    return character_df

def display_characters(characters_count):
    st.write("Самые важные персонажи:")
    st.write(characters_count)

def create_graph(characters_count):
    G = nx.Graph()
    top_characters = characters_count.head(10)["Персонаж"].tolist()

    for char in top_characters:
        G.add_node(char)

    for i in range(len(top_characters)):
        for j in range(i + 1, len(top_characters)):
            G.add_edge(top_characters[i], top_characters[j])

    return G

def display_ui(G):
    st.write("Граф связей между персонажами:")

    dot = graphviz.Digraph()
    for node in G.nodes:
        dot.node(node)

    for edge in G.edges:
        dot.edge(edge[0], edge[1])

    st.graphviz_chart(dot)

if __name__ == "__main__":
    st.title("Анализ персонажей в книге")
    file = upload_file()
    if file:
        text = process_text(file)
        characters = extract_entities(text)
        characters_count = count_characters(characters)
        display_characters(characters_count)
        G = create_graph(characters_count)
        display_ui(G)
