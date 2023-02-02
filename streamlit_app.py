import spacy
import networkx as nx
import streamlit as st

# Load the NER model
nlp = spacy.load("model\ru_core_news_md-3.5.0.tar.gz")

# Function to process the text and extract entities
def process_text(text):
    characters = {}
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PER":
            if ent.text not in characters:
                characters[ent.text] = []
            for i in range(ent.start, ent.end):
                for other_ent in doc.ents:
                    if other_ent.label_ == "PER" and other_ent.start < i < other_ent.end:
                        if other_ent.text not in characters[ent.text]:
                            characters[ent.text].append(other_ent.text)
    return characters

# Function to visualize the characters
def visualize_characters(characters):
    G = nx.Graph()
    for character, connections in characters.items():
        G.add_node(character)
        for connection in connections:
            G.add_edge(character, connection)
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color="skyblue", node_size=1500, alpha=0.7, linewidths=0.5, font_size=10)
    st.pyplot()

# Streamlit app
def app():
    st.set_page_config(page_title="Character Visualization", page_icon=":guardsman:", layout="wide")
    st.title("Character Visualization")

    # Upload the txt file
    uploaded_file = st.file_uploader("Upload a book in txt format", type=["txt"])
    if uploaded_file is not None:
        text = uploaded_file.read().decode("utf-8")
        characters = process_text(text)
        st.write("Number of characters:", len(characters))
        st.write("Connections between characters:", characters)
        st.pyplot(visualize_characters)

if __name__ == '__main__':
    app()
