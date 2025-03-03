import streamlit as st
from hyperbrowser import ClientConfig, Hyperbrowser
from hyperbrowser.models.extract import StartExtractJobParams
from hyperbrowser.models.session import CreateSessionParams
from elevenlabs.client import ElevenLabs
from typing import Dict

import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Configure the page
st.set_page_config(
    page_title="WebWhisper - Web to Voice", page_icon="🎧", layout="wide"
)


HYPERBROWSER_API_KEY = str(os.getenv("HYPERBROWSER_API_KEY", ""))
ELEVENLABS_API_KEY = str(os.getenv("ELEVENLABS_API_KEY", ""))

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class ArticleContent:
    """
    Dataclass to store extracted article content.
    """

    title: str
    full_content: str
    author: Optional[str] = None
    abstract: Optional[str] = None

    @staticmethod
    def from_json(data: Dict) -> "ArticleContent":
        json_data = data

        title: str = json_data.get("title", "")
        full_content: str = json_data.get("fullContent", "")
        author: Optional[str] = json_data.get("author", None)
        abstract: Optional[str] = json_data.get("abstract", None)

        return ArticleContent(
            title=title, full_content=full_content, author=author, abstract=abstract
        )


def extract_content(
    url: str,
    hb_key: str,
) -> Optional[ArticleContent]:
    try:
        client = Hyperbrowser(api_key=hb_key)

        extraction_config = StartExtractJobParams(
            urls=[url],
            schema={
                "type": "object",
                "properties": {
                    "author": {"type": "string"},
                    "title": {"type": "string"},
                    "abstract": {"type": "string"},
                    "fullContent": {"type": "string"},
                },
                "required": [
                    "title",
                    "fullContent",
                ],
            },
            session_options=CreateSessionParams(
                use_stealth=True,
                accept_cookies=True,
            ),
        )
        content = client.extract.start_and_wait(extraction_config)
        client.close()

        article_content = ArticleContent.from_json(content.data)  # type: ignore
        return article_content
    except Exception as e:
        print(f"Error: {e}")
        return None


def main():
    st.title("🎧 WebWhisper")
    st.subheader("Transform Web Content into Natural Speech")

    # Initialize session state for content if it doesn't exist
    if "article_content" not in st.session_state:
        st.session_state.article_content = None

    # API Configuration Section
    with st.sidebar:
        st.header("API Configuration")

        # ElevenLabs API Key
        elevenlabs_key = st.text_input(
            "ElevenLabs API Key",
            placeholder="sk_...",
            value=ELEVENLABS_API_KEY,
            type="password",
            help="Get your API key from https://elevenlabs.io",
        )

        # Validate ElevenLabs API key by checking remaining credits
        if elevenlabs_key:
            try:
                client = ElevenLabs(api_key=elevenlabs_key)
                user_data = client.user.get()
                remaining_credits = (
                    user_data.subscription.character_limit
                    - user_data.subscription.character_count
                )
                st.success(
                    f"ElevenLabs API key valid! Remaining credits: {remaining_credits:,} characters"
                )
            except Exception as e:
                st.error(f"Invalid ElevenLabs API key: {str(e)}")
                elevenlabs_key = None

        # Hyperbrowser API Key
        hb_key = st.text_input(
            "Hyperbrowser API Key",
            value=HYPERBROWSER_API_KEY,
            placeholder="hb_...",
            type="password",
            help="Enter your Hyperbrowser API key",
        )

        if not elevenlabs_key:
            st.sidebar.warning("Please enter your ElevenLabs API key")
        if not hb_key:
            st.sidebar.warning("Please enter your Hyperbrowser API key")

    # Main content
    if not elevenlabs_key or not hb_key:
        st.warning(
            "Please configure your API keys in the sidebar to use the application"
        )
        st.stop()

    # Input fields
    url = st.text_input("Enter webpage URL:", placeholder="https://example.com")

    # Advanced options
    with st.expander("Voice Options"):
        voice = st.selectbox(
            "Select voice:",
            [
                "Rachel",
                "Domi",
                "Bella",
                "Antoni",
                "Elli",
                "Josh",
                "Arnold",
                "Adam",
                "Sam",
            ],
        )
        model = st.selectbox(
            "Select model:", ["eleven_monolingual_v1", "eleven_multilingual_v1"]
        )

    content: Optional[ArticleContent] = st.session_state.article_content

    if st.button("Extract", key="extract_button"):
        if url:
            st.write(f"Extracting content from {url}...")
            with st.spinner("Extracting content..."):
                content = extract_content(url, hb_key)
                # Store content in session state
                st.session_state.article_content = content
        else:
            st.warning("Please enter a URL")

    if content is not None:
        st.success("Content extracted successfully!")
        # Show extracted text
        with st.expander("Show extracted text", expanded=True):
            st.write(content)

        if st.button("Convert to speech", key="convert_to_speech"):
            st.write(f"Converting content to speech...")
            with st.spinner("Converting to speech...") as spinner:
                try:
                    text_for_speech = (
                        f"{content.title}\nby {content.author}\n{content.full_content}"
                    )
                    client = ElevenLabs(api_key=elevenlabs_key)
                    audio_iterator = client.generate(
                        text=text_for_speech, voice=voice, model=model
                    )
                    audio = b"".join(
                        audio_iterator
                    )  # Convert iterator of bytes to a single bytes object
                    st.audio(audio, format="audio/mp3")
                    # Download option
                    st.download_button(
                        label="Download Audio",
                        data=audio,
                        file_name="webwhisper_audio.mp3",
                        mime="audio/mp3",
                    )
                except Exception as e:
                    st.error(f"Error generating speech: {str(e)}")


if __name__ == "__main__":
    main()
