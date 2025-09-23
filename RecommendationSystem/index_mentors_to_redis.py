import redis
from redis.commands.search.field import VectorField, NumericField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from sklearn.metrics.pairwise import cosine_similarity

df = pd.read_csv("cleaned_mentor_dataset.csv")

text_columns = [
    'state','city', 'skills', 'specialities_x', 'tags',
    'features', 'combinations', 'persona', 'description'
]

weights = {
    'state': 3,
    'city' : 3,
    'skills': 2,
    'specialities_x': 2,
    'tags': 2,
    'features': 1,
    'combinations': 1,
    'persona': 1,
    'description': 1
}

def weighted_text(row):
    combined = []
    for col in text_columns:
        weight = weights.get(col, 1)
        value = str(row[col])
        if pd.isna(value) or value.strip() == "":
            continue
        combined.append((value + ' ') * weight) 
    return ' '.join(combined)

df['combined_text'] = df.apply(weighted_text, axis=1)

model = SentenceTransformer('all-MiniLM-L6-v2') 

mentor_embeddings = model.encode(df['combined_text'].tolist(), convert_to_tensor=True)

r = redis.Redis(
    host="redis-12644.c212.ap-south-1-1.ec2.redns.redis-cloud.com",
    port=12644,
    password="",#Safety
    decode_responses=False 
)
print('redis connected')

DIM = 384
INDEX_NAME = "mentors_index"
schema = [
    NumericField("$.mentorId", as_name="mentorId"),
    NumericField("$.subscriptionId", as_name="subscriptionId"),
    VectorField("$.embedding", "FLAT", {
        "TYPE": "FLOAT32",
        "DIM": DIM,
        "DISTANCE_METRIC": "COSINE"
    }, as_name="embedding") 
]

try:
    r.ft(INDEX_NAME).create_index(
        fields=schema,
        definition=IndexDefinition(prefix=["mentor:subscription:"], index_type=IndexType.JSON)
    )
except Exception as e:
    print(f"Index might already exist: {e}")

for idx, row in df.iterrows():
    vec = mentor_embeddings[idx].cpu().numpy().astype(np.float32).tolist()
    r.json().set(f"mentor:profile:subscription:{idx}", "$", {
        "embedding": vec
    })
print("done")

