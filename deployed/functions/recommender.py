""" Recommender integration funciton """

# Dependencies
from collections import Counter
import math
from database import get_all_topics_from_supabase, find_topic_by_name, find_topic_by_id
from dataclasses import dataclass, field

@dataclass
class Recommendation:
    id: str
    name: str
    similarity: float
    internal_relevance_score: int
    date_added: str

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "similarity": self.similarity,
            "internal_relevance_score": self.internal_relevance_score,
            "date_added": self.date_added
        }

def recommender(base_topic, num_results: int):

    def text_to_vector(text):
        # Turn text into a word-count vector (Counter) - dictionary
        # Lowercase and split on whitespace.
        words = text.lower().split()
        return Counter(words)

    def dot_product(vector1, vector2):
        total = 0
        for a, b in vector1.items():
            if a in vector2:
                total += b * vector2[a]
        return total

    def magnitude(vector):
        total = 0.0
        for x in vector.values():
            total += x * x
        return math.sqrt(total)

    def cosine_similarity(vec1, vec2):
        # Cosine similarity = dot(vec1 · vec2) / (|vec1| * |vec2|)
        # Return 0.0 if either vector has zero magnitude.
        num = dot_product(vec1, vec2)
        magnitude1 = magnitude(vec1)
        magnitude2 = magnitude(vec2)
        if magnitude1 == 0.0 or magnitude2 == 0.0:
            return 0
        return num / (magnitude1 * magnitude2)
    
    # Get all topics
    topics_data = get_all_topics_from_supabase()
    topics = {}
    for item in topics_data:
        topic_name = item.get("name") # type: ignore
        summary = item.get("summary") # type: ignore
        topics[topic_name] = summary
    base_text = topics[base_topic]
    base_vector = text_to_vector(base_text)
    # Compute similarity scores for all other topics
    similarities = {}  # maps topic -> score
    for topic_name in topics:
        if topic_name == base_topic:
            continue
        summary_text = topics[topic_name]
        test_vector = text_to_vector(summary_text)
        score = cosine_similarity(base_vector, test_vector)
        similarities[topic_name] = score
    score_topic_list = []
    for t, s in similarities.items():
        # store as (score, topic) so default sort sorts by score first
        score_topic_list.append((s, t))
    # Sort descending by score (highest similarity first)
    score_topic_list.sort(reverse=True)
    # Take top 3 results (or fewer if not enough topics)
    top_results = score_topic_list[:num_results]
    # print("Base topic:", base_topic)
    # print("Top related topics:")
    processed_results = []
    for item in top_results:
        score = item[0]
        topic_name = item[1]
        topic_exists, topic_id = find_topic_by_name(topic_name)
        if topic_exists:
            topic_retrieved, topic_object = find_topic_by_id(id=topic_id) # type: ignore
            if topic_retrieved:
                processed_results.append(
                    Recommendation(
                        id=topic_object["id"], # type: ignore
                        name=topic_object["name"], # type: ignore
                        similarity=score,
                        internal_relevance_score=topic_object["internal_relevance_score"], # type: ignore
                        date_added=topic_object["date_added"] # type: ignore
                    ).to_dict()
                )
    return processed_results