from collections import Counter
import math

def recommender(base_topic):
    def get_all_topics_from_supabase():
        # Only want 50 topics
        response = SUPABASE_CLIENT.table('topics').select('*').limit(50).execute()
        return response.data
    
    def get_info_about_topic(id: str, *columns):
        # Fetch specified columns from the 'topics' table in Supabase.
        if not columns:
            select_str = "*"
        else:
            select_str = ",".join(columns)
        response = SUPABASE_CLIENT.table('topics').select("id", select_str).eq("id", id).execute()
        return response.data

    topics_data = get_all_topics_from_supabase()

    topics = {}  # dictionary where key = topic name, value = summary + info
    for item in topics_data:
        topic_name = item.get("topic")
        summary = item.get("summary", "")

        # Fetch additional info for this topic (customize columns as needed)
        extra_info_data = get_info_about_topic(item["id"], "description", "examples")

        # Combine all extra info fields into one text string
        extra_info = ""
        if extra_info_data and len(extra_info_data) > 0:
            extra_item = extra_info_data[0]
            extra_info = " ".join(str(v) for v in extra_item.values() if v)

        # Merge summary and info
        combined_summary = f"{summary} {extra_info}".strip()

        topics[topic_name] = combined_summary

    for item in topics_data:
        topic_name = item.get("topic")
        summary = item.get("summary")
        topics[topic_name] = summary

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
    top_results = score_topic_list[:3]

    print("Base topic:", base_topic)
    print("Top related topics:")
    for item in top_results:
        score = item[0]
        topic_name = item[1]
        print(f"-{topic_name} | similarity: {score:.2f})")
