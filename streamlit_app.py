import spacy
import networkx as nx
import streamlit as st
import ru_core_news_md
import matplotlib as plt
import re
import pymorphy2
import pandas as pd


# Load the NER model
nlp = ru_core_news_md.load()
morph = pymorphy2.MorphAnalyzer()

# Function to process the text and extract entities
def process_text(text):

    doc = nlp(text)

    sent_entity_df = []

    # Loop through sentences, store named entity list for each sentence
    for sent in doc.sents:
        entity_list = [morph.parse(re.sub('\n', '', ent.text))[0].normal_form for ent in sent.ents if ent.label_ == 'PER']
        sent_entity_df.append({"sentence": sent, "entities": entity_list})
    
    sent_entity_df = pd.DataFrame(sent_entity_df)


    relationships = []

    for i in range(sent_entity_df.index[-1]):
        end_i = min(i+5, sent_entity_df.index[-1])
        char_list = sum((sent_entity_df.loc[i: end_i].entities), [])
        
        # Remove duplicated characters that are next to each other
        char_unique = [char_list[i] for i in range(len(char_list)) 
                    if (i==0) or char_list[i] != char_list[i-1]]
        
        if len(char_unique) > 1:
            for idx, a in enumerate(char_unique[:-1]):
                b = char_unique[idx + 1]
                relationships.append({"source": a, "target": b})
        
    relationship_df = pd.DataFrame(relationships)
    relationship_df["value"] = 1
    relationship_df = relationship_df.groupby(["source","target"], sort=False, as_index=False).sum()


    return relationship_df

# Function to visualize the characters
def visualize_characters(characters):
    G = nx.from_pandas_edgelist(characters, 
                            source = "source", 
                            target = "target", 
                            edge_attr = "value", 
                            create_using = nx.Graph())
    plt.figure(figsize=(10,10))
    pos = nx.kamada_kawai_layout(G)
    nx.draw(G, with_labels=True, node_color='skyblue', edge_cmap=plt.cm.Blues, pos = pos)
    plt.show()


# Streamlit app
def app():
    st.set_page_config(page_title="Character Visualization", page_icon=":guardsman:", layout="wide")
    st.title("Character Visualization")

    # Upload the txt file
    uploaded_file = st.file_uploader("Upload a book in txt format", type=["txt"])
    if uploaded_file is not None:
        text = uploaded_file.read().decode("cp1251")
        characters = process_text(text)
        st.write("Number of characters:", len(characters))
        st.write("Connections between characters:", characters)
        st.pyplot(visualize_characters)

if __name__ == '__main__':
    app()
