import redis
from redis.commands.search.field import VectorField, NumericField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from sklearn.metrics.pairwise import cosine_similarity

r = redis.Redis(
    host="redis-12644.c212.ap-south-1-1.ec2.redns.redis-cloud.com",
    port=12644,
    password="", #Safety
    decode_responses=False 
)
print('redis connected')

mentor_keys = r.keys("mentor:*")
subscription_keys = r.keys("subscription:*")

mentors = [r.json().get(k) for k in mentor_keys]
subscriptions = [r.json().get(k) for k in subscription_keys]
