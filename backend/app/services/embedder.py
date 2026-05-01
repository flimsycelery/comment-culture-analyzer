from sentence_transformers import SentenceTransformer
from bertopic import BERTopic
import numpy as np

print("Loading embedding model...")
model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
print("Model loaded!")

def embed_comments(comments: list[str]) -> list[list[float]]:
    """Convert comments to vector embeddings"""
    embeddings = model.encode(comments, show_progress_bar=True)
    return embeddings.tolist()

def cluster_topics(comments: list[str], embeddings: list[list[float]]) -> list[str]:
    """Use BERTopic to find themes in comments"""
    import numpy as np
    
    if len(comments) < 10:
        return ["general"] * len(comments)
    
    embeddings_array = np.array(embeddings)
    
    topic_model = BERTopic(
        nr_topics=5,           # find top 5 themes
        min_topic_size=3,      # minimum 3 comments per theme
        verbose=False
    )
    
    topics, _ = topic_model.fit_transform(comments, embeddings_array)
    topic_info = topic_model.get_topic_info()
    
    topic_labels = {}
    for _, row in topic_info.iterrows():
        if row['Topic'] == -1:
            topic_labels[-1] = "other"
        else:
            words = topic_model.get_topic(row['Topic'])
            if words:
                topic_labels[row['Topic']] = "_".join([w[0] for w in words[:3]])
            else:
                topic_labels[row['Topic']] = f"theme_{row['Topic']}"
    
    return [topic_labels.get(t, "other") for t in topics]