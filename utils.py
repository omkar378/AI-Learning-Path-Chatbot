from typing import Any, Callable, Dict, List, Optional

from google import genai
from googleapiclient.discovery import build

from prompt import user_goal_prompt


# -----------------------------------------
# Gemini Models (Automatic Fallback)
# -----------------------------------------

PREFERRED_MODELS = [
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]


# -----------------------------------------
# Parse Gemini Response
# -----------------------------------------

def parse_learning_topics(response_text: str) -> List[str]:
    """
    Extract topics from Gemini response.
    Expected format:

    Day 1
    Topic: Variables

    Day 2
    Topic: Loops
    """

    topics: List[str] = []

    for raw_line in response_text.splitlines():

        line = raw_line.strip()

        if not line:
            continue

        if line.lower().startswith("day"):
            continue

        if line.lower().startswith("topic:"):

            topic = line.split(":", 1)[1].strip()

            if topic:
                topics.append(topic)

    # Remove duplicates while preserving order

    unique_topics = []

    seen = set()

    for topic in topics:

        if topic not in seen:

            seen.add(topic)

            unique_topics.append(topic)

    return unique_topics[:7]


# -----------------------------------------
# YouTube Search
# -----------------------------------------

def search_youtube_videos(
    query: str,
    youtube_api_key: str,
    max_results: int = 3,
) -> List[Dict[str, str]]:

    if not youtube_api_key:
        return []

    youtube = build(
        "youtube",
        "v3",
        developerKey=youtube_api_key,
    )

    request = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        maxResults=max_results,
        order="relevance",
        videoEmbeddable="true",
    )

    try:
        response = request.execute()
    except Exception:
        return []

    videos: List[Dict[str, str]] = []

    for item in response.get("items", []):

        video_id = item.get("id", {}).get("videoId")

        if not video_id:
            continue

        snippet = item.get("snippet", {})

        videos.append(
            {
                "title": snippet.get("title", "YouTube Video"),
                "url": f"https://www.youtube.com/watch?v={video_id}",
            }
        )

    return videos


# -----------------------------------------
# Download Text Builder
# -----------------------------------------

def build_download_text(
    learning_path: Dict[str, Any],
) -> str:

    lines = [
        "Learning Path",
        "=" * 30,
        "",
    ]

    for topic in learning_path["topics"]:

        lines.append(f"{topic['day']}: {topic['topic']}")

        if topic["videos"]:

            for video in topic["videos"]:

                lines.append(
                    f"- {video['title']}"
                )

                lines.append(video["url"])

        lines.append("")

    return "\n".join(lines)

# -----------------------------------------
# Generate Learning Path
# -----------------------------------------

def generate_learning_path(
    google_api_key: str,
    user_goal: str,
    youtube_api_key: Optional[str] = None,
    progress_callback: Optional[Callable[[str], None]] = None,
) -> Dict[str, Any]:

    if progress_callback:
        progress_callback("Connecting to Gemini...")

    client = genai.Client(api_key=google_api_key)

    prompt = f"""
User Goal:

{user_goal}

{user_goal_prompt}
"""

    response = None
    last_error = None

    # Try models one by one
    for model_name in PREFERRED_MODELS:

        try:

            if progress_callback:
                progress_callback(f"Trying {model_name}...")

            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )

            break

        except Exception as e:
            last_error = e
            continue

    if response is None:
        raise RuntimeError(
            f"Unable to generate content.\nLast Error:\n{last_error}"
        )

    response_text = getattr(response, "text", "")

    if not response_text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    topics = parse_learning_topics(response_text)

    if not topics:
        raise RuntimeError(
            "Could not extract learning topics from Gemini response."
        )

    structured_topics = []

    for index, topic in enumerate(topics, start=1):

        if progress_callback:
            progress_callback(f"Searching YouTube for {topic}...")

        videos = search_youtube_videos(
            query=f"{topic} tutorial",
            youtube_api_key=youtube_api_key or "",
            max_results=3,
        )

        structured_topics.append(
            {
                "day": f"Day {index}",
                "topic": topic,
                "videos": videos,
            }
        )

    if progress_callback:
        progress_callback("Completed!")

    return {
        "response_text": response_text,
        "topics": structured_topics,
        "download_text": build_download_text(
            {
                "topics": structured_topics,
            }
        ),
    }