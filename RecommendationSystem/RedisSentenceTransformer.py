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
    'state', 'skills', 'specialities_x', 'tags',
    'features', 'combinations', 'persona', 'description'
]

weights = {
    'state': 1,
    'skills': 3,
    'specialities_x': 3,
    'tags': 2,
    'features': 1,
    'combinations': 2,
    'persona': 2,
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

def rec_ment(keywords, top_n=10):
    keyword_query = ' '.join(keywords)
    query_embedding = model.encode(keyword_query, convert_to_tensor=True)
    
    similarities = util.cos_sim(query_embedding, mentor_embeddings)[0]
    
    top_indices = similarities.argsort(descending=True)[:top_n]
    
    print("Top Recommendations:")
    seen_subs = set()
    count = 0
    for idx_tensor in top_indices:
        idx = idx_tensor.item()  
        sub_id = df.loc[idx]['subscriptionId']
        if sub_id not in seen_subs:
            seen_subs.add(sub_id)
            print(f"(Score: {similarities[idx]:.2f})")
            print(f"SubscriptionId: {sub_id}")
            print(f"MentorId: {df.iloc[idx]['mentorId']}\n")
            count += 1
        if count >= top_n:
            break

r = redis.Redis(
    host="redis-12644.c212.ap-south-1-1.ec2.redns.redis-cloud.com",
    port=12644,
    password="", #Safety
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
    r.json().set(f"mentor:subscription:{idx}", "$", {
        "mentorId": int(row["mentorId"]),
        "subscriptionId": int(row["subscriptionId"]),
        "embedding": vec
    })

def rec_from_redis(keywords, top_n=10):
    query_str = ' '.join(keywords)
    query_vec = model.encode(query_str).astype(np.float32).tobytes()

    q = Query(f'*=>[KNN {top_n} @embedding $vec_param AS score]') \
        .sort_by("score") \
        .return_fields("mentorId", "subscriptionId", "score") \
        .dialect(2)

    params = {"vec_param": query_vec}

    results = r.ft(INDEX_NAME).search(q, query_params=params)

    seen = set()
    for doc in results.docs:
        if doc.subscriptionId not in seen:
            print(f"(Score: {float(doc.score):.4f})")
            print(f"SubscriptionId: {doc.subscriptionId}")
            print(f"MentorId: {doc.mentorId}\n")
            seen.add(doc.subscriptionId)
        if len(seen) >= top_n:
            break


if __name__ == "__main__":
    rec_from_redis(["jharkhand", "technical analysis"])
    rec_ment(["jharkhand", "technical analysis"])



