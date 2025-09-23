import redis
import numpy as np
from sentence_transformers import SentenceTransformer
from redis.commands.search.query import Query

model = SentenceTransformer('all-MiniLM-L6-v2')

r = redis.Redis(
    host="redis-12644.c212.ap-south-1-1.ec2.redns.redis-cloud.com",
    port=12644,
    password="", #Safety
    decode_responses=False 
)
print('redis connected')

INDEX_NAME = "mentors_index"

def rec_from_redis(keywords, top_n=10):
    query_str = ' '.join(keywords)
    query_vec = model.encode(query_str).astype(np.float32).tobytes()

    q = Query(f'*=>[KNN {top_n} @embedding $vec_param AS score]') \
        .sort_by("score", asc=True) \
        .return_fields("mentorId", "subscriptionId", "score") \
        .dialect(2)

    results = r.ft(INDEX_NAME).search(q, query_params={"vec_param": query_vec})

    seen = set()
    print("\nTop Recommendations:")
    for doc in results.docs:
        sub_id = str(doc.subscriptionId)
        if sub_id not in seen:
            print(f"(Score: {float(doc.score):.4f})")
            print(f"SubscriptionId: {doc.subscriptionId}")
            print(f"MentorId: {doc.mentorId}\n")
            seen.add(sub_id)
        if len(seen) >= top_n:
            break

if __name__ == "__main__":
    rec_from_redis(["fundamental analysis","equity","24", "bangalore"])

