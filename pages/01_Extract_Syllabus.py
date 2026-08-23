# ============================================================
# FIX FOR pages/01_Extract_Syllabus.py
# Topic rendering compatible with STRING and DICT topics
# ============================================================

def _safe_topic_value(topic, key="name", default=""):
    """
    Safely read a topic regardless of whether the extractor returns:

        "Python programming for data science"

    or:

        {"name": "Python programming for data science"}

    or an object exposing attributes.
    """
    if topic is None:
        return default

    if isinstance(topic, str):
        return topic.strip()

    if isinstance(topic, dict):
        value = topic.get(key)

        if value is None and key == "name":
            value = (
                topic.get("topic_name")
                or topic.get("title")
                or topic.get("text")
                or topic.get("topic")
            )

        if value is None:
            return default

        return str(value).strip()

    value = getattr(topic, key, None)

    if value is None and key == "name":
        value = (
            getattr(topic, "topic_name", None)
            or getattr(topic, "title", None)
            or getattr(topic, "text", None)
            or getattr(topic, "topic", None)
        )

    if value is None:
        return default

    return str(value).strip()


def _safe_topic_concepts(topic):
    """
    Return concepts as a list regardless of extractor representation.
    """
    if isinstance(topic, dict):
        concepts = topic.get("concepts", [])
    else:
        concepts = getattr(topic, "concepts", [])

    if concepts is None:
        return []

    if isinstance(concepts, str):
        return [concepts]

    if not isinstance(concepts, list):
        return [str(concepts)]

    return concepts


# ============================================================
# REPLACE THE OLD CODE AROUND LINE ~1594
# ============================================================

for topic_index, topic in enumerate(
    module_topics,
    start=1,
):

    # --------------------------------------------------------
    # Topic name
    # --------------------------------------------------------
    topic_name = _safe_topic_value(
        topic,
        key="name",
        default=f"Topic {topic_index}",
    )

    st.markdown(
        f"**{topic_index}. {topic_name}**"
    )

    # --------------------------------------------------------
    # Optional concepts
    # --------------------------------------------------------
    concepts = _safe_topic_concepts(topic)

    if concepts:
        for concept_index, concept in enumerate(
            concepts,
            start=1,
        ):

            concept_name = _safe_topic_value(
                concept,
                key="name",
                default=f"Concept {concept_index}",
            )

            st.markdown(
                f"&nbsp;&nbsp;&nbsp;• {concept_name}"
            )


# ============================================================
# IMPORTANT:
#
# DO NOT use:
#
# topic.get("name")
#
# directly.
#
# The extractor may return a topic as a plain string.
#
# ============================================================
