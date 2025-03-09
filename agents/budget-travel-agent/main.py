from datetime import datetime
import tempfile
from typing import Optional
import streamlit as st
from playwright.sync_api import (
    sync_playwright,
    Page,
    ElementHandle,
)
import os
from openai import OpenAI
import base64
import time
from dotenv import load_dotenv
from PIL import Image


# Load environment variables from .env file
load_dotenv()

from hyperbrowser.client.sync import Hyperbrowser
from hyperbrowser.models.session import CreateSessionParams, ScreenConfig
from src.location_validator import validate_city
from src.chatgpt_parser import TravelDestination, extract_travel_data_from_image

# Get OpenAI API key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    st.error("OpenAI API key not found. Please set it in a .env file.")


def adjust_viewport(page, locations_element):
    """Adjust the viewport to capture the entire locations element."""
    location_element_bbox = locations_element.bounding_box()
    if not location_element_bbox:
        st.warning("Could not get the height of the locationsElement")
        return None, None

    original_viewport_size = page.viewport_size
    if not original_viewport_size:
        viewport_size_hack = page.evaluate(
            r"() => ({width:window.innerWidth, height:window.innerHeight})"
        )
        if not viewport_size_hack:
            st.warning("Could not get the viewport size")
            return None, None
        original_viewport_size = viewport_size_hack

    # Adjust viewport height
    new_height = max(
        original_viewport_size["height"],
        int(location_element_bbox["height"]) + 512,
    )
    page.set_viewport_size(
        {"width": original_viewport_size["width"], "height": new_height}
    )

    time.sleep(1)  # Wait for the page to adjust
    return original_viewport_size, location_element_bbox


def set_weekend_filter(page: Page, trip_duration):
    """Set the filter to display weekend trips."""
    duration_filter = page.query_selector('div[jsname="Q641D"]')
    if not duration_filter:
        st.warning("Could not find the duration filter")
        return False

    duration_filter.click()

    # Find and click on the "Weekend" option
    duration_options = page.wait_for_selector('div[aria-label*="Trip duration"]')
    if not duration_options:
        st.warning("Could not find Weekend filter option")
        return False

    weekend_options = duration_options.query_selector_all("span[role='gridcell'] span")
    if not weekend_options:
        st.warning("Could not find Weekend filter option")
        return False

    # Find the weekend option that matches the trip duration
    selected_weekend_option = None
    for option in weekend_options:
        option_text = option.text_content()
        if option_text and option_text.lower() == trip_duration.lower():
            selected_weekend_option = option
            break

    if not selected_weekend_option:
        st.warning("Could not find Weekend filter option")
        return False

    selected_weekend_option.click()
    time.sleep(2)

    # Click the Done button
    done_button = page.query_selector(
        "div.ZGEB9c.yRXJAe.P0ukfb.icWGef.bWstqf.iWO5td > div > div.ohKsQc > div:nth-child(1) > button"
    )
    if not done_button:
        st.warning("Could not set the duration filter")
        return False

    done_button.click()
    time.sleep(2)  # Wait for the page to update with weekend options
    return True


def create_screenshot(locations_element: ElementHandle):
    """Take a screenshot of the locations element and save to a temporary file."""

    # Take the screenshot
    return locations_element.screenshot(
        scale="css",  # Use CSS scaling for consistent size
    )


def crop_screenshot(screenshot_path: str, width, height, max_dimension) -> str:

    # Calculate the crop dimensions
    crop_width = min(width, max_dimension)
    crop_height = min(height, max_dimension)

    # Define crop box coordinates (crop from the top)
    left, top = 0, 0
    right = min(width, crop_width)
    bottom = min(height, crop_height)

    temp_file = tempfile.NamedTemporaryFile(
        delete=False, dir=tempfile.gettempdir(), suffix=".png"
    )
    temp_file.close()
    # Perform the crop
    with Image.open(screenshot_path) as img:
        cropped_img = img.crop((left, top, right, bottom))
        # Convert the cropped image to bytes instead of saving to a file

        cropped_img.save(temp_file.name, format=img.format or "PNG")
    os.unlink(screenshot_path)
    return temp_file.name


def process_screenshot(screenshot_bytes: bytes) -> str:
    temp_file = tempfile.NamedTemporaryFile(
        delete=False, dir=tempfile.gettempdir(), suffix=".png"
    )
    temp_file.write(screenshot_bytes)
    temp_file.close()
    with Image.open(temp_file.name) as img:
        width, height = img.size
        max_dimension = 2048

        # Only resize if the image exceeds the maximum dimension
        if width > max_dimension or height > max_dimension:
            return crop_screenshot(temp_file.name, width, height, max_dimension)

        return temp_file.name


@st.cache_data(show_spinner=False)
def take_screenshot(
    start_location: str, end_location: Optional[str], trip_duration
) -> Optional[str]:
    """
    Use Playwright to navigate to Google Travel, set parameters, and take a screenshot
    """
    client = Hyperbrowser(api_key=os.getenv("HYPERBROWSER_API_KEY"))
    session = client.sessions.create(
        CreateSessionParams(
            screen=ScreenConfig(
                width=1920,
                height=1080,
            )
        )
    )
    print(session.live_url)
    if not session.ws_endpoint:
        st.error("Could not create a session")
        return

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(session.ws_endpoint)
        context = browser.new_context()
        page = context.new_page()

        try:
            # Navigate to Google Travel Explore
            page.goto("https://www.google.com/travel/explore", wait_until="load")
            time.sleep(1)

            locations_element = page.wait_for_selector("main")
            if not locations_element:
                st.error("Could not get locations properly")
                return

            # Wait for the page to load
            fromInputElement = page.wait_for_selector(
                'input[aria-label*="Where from?"]'
            )
            if not fromInputElement:
                st.error("Travel Explore page did not load properly")
                return

            # Enter the location
            fromInputElement.fill(start_location)
            time.sleep(2)  # Wait for autocomplete suggestions
            page.keyboard.press("Enter")

            toInputElement = page.wait_for_selector('input[aria-label*="Where to?"]')
            if not toInputElement:
                st.error("Travel Explore page did not load properly")
                return

            if end_location:
                # Enter the location
                toInputElement.fill(end_location)
                time.sleep(2)  # Wait for autocomplete suggestions
                page.keyboard.press("Enter")

            if not set_weekend_filter(page, trip_duration):
                st.error("Could not set the duration filter")
                return

            spinner_element = locations_element.query_selector('div[jsname="aZ2wEe"]')
            if spinner_element is None:
                st.error("Could not capture the screenshot")
                return

            isVisible = True
            for i in range(10):
                isVisible = spinner_element.is_visible()
                if not isVisible:
                    break
                else:
                    time.sleep(0.5)

            if isVisible:
                print("Spinner element is still visible,timing out")
                st.error("Could not capture the screenshot")
                return

            # Adjust viewport
            original_viewport_size, _ = adjust_viewport(page, locations_element)
            if not original_viewport_size:
                st.error("Could not get the screenshot for the travel options")
                return

            # Create a temporary file for the screenshot
            screenshot_path = create_screenshot(locations_element)
            if not screenshot_path:
                st.error("Could not get the screenshot for the travel options")
                return

            # Reset viewport size to original
            page.set_viewport_size(original_viewport_size)
            time.sleep(0.5)

            # Process the image if needed
            final_screenshot_bytes = process_screenshot(screenshot_path)

            return final_screenshot_bytes
        except Exception as e:
            st.error(f"Error during browser automation: {str(e)}")
            # Return screenshot of current state for debugging
            return None
        finally:
            client.sessions.stop(session.id)


@st.cache_data(show_spinner=False)
def analyze_screenshot_with_openai(screenshot_path):
    """
    Analyze the screenshot using OpenAI's Vision capabilities
    """
    client = OpenAI(api_key=openai_api_key)

    # Read the image and encode it to base64
    with open(screenshot_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

    # Create the prompt for analysis
    prompt = """
    Analyze this screenshot from Google Travel and extract the following information:
    1. Travel start and end dates
    2. Cost of travel (flight prices, train tickets, etc.)
    3. Travel time (separate plane travel from other modes if multiple options are shown)
    4. Approximate stay cost (hotels, accommodations)
    
    Format your response in a structured way with clear sections for each type of information.
    If any information is not visible in the screenshot, indicate that it's not available.
    Be precise with numbers and dates that you can clearly read.
    """

    # Call the API
    try:
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encoded_image}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=1000,
        )

        return response.choices[0].message.content
    except Exception as e:
        return f"Error analyzing image with OpenAI: {str(e)}"


def display_travel_data(travel_data: list[TravelDestination], from_location: str):
    """Display the extracted travel destinations with pagination."""
    if not travel_data:
        st.warning("No destinations could be extracted from the results.")
        return False

    # Pagination settings
    page_size = 5
    total_destinations = len(travel_data)
    num_pages = (total_destinations + page_size - 1) // page_size  # Ceiling division

    # Handle pagination
    if num_pages > 1:
        page_number = st.number_input(
            "Page",
            min_value=1,
            max_value=num_pages,
            value=st.session_state.page_number,
            step=1,
            key="page_input",
        )
        if page_number != st.session_state.page_number:
            st.session_state.page_number = page_number
            st.rerun()
    else:
        page_number = 1
        st.session_state.page_number = 1

    # Calculate range of destinations to display
    start_idx = (page_number - 1) * page_size
    end_idx = min(start_idx + page_size, total_destinations)

    if num_pages > 1:
        st.write(
            f"Showing {start_idx + 1}-{end_idx} of {total_destinations} destinations"
        )

    # Create tabs for destinations
    destination_tabs = st.tabs(
        [f"{d.location} - ${d.price}" for d in travel_data[start_idx:end_idx]]
    )

    # Display each destination in its own tab
    for i, (tab, destination) in enumerate(
        zip(destination_tabs, travel_data[start_idx:end_idx])
    ):
        with tab:
            # Convert string dates to datetime objects
            start_date = datetime.strptime(destination.start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(destination.end_date, "%Y-%m-%d").date()

            start_date_cleaned = destination.start_date.replace(" ", "%20")
            end_date_cleaned = destination.end_date.replace(" ", "%20")
            location_cleaned = destination.location.replace(" ", "%20")
            from_location_cleaned = from_location.replace(" ", "%20")

            # Format dates for display
            formatted_start_date = start_date.strftime("%B %d, %Y")
            formatted_end_date = end_date.strftime("%B %d, %Y")

            st.write(f"**Start Date:** {formatted_start_date}")
            st.write(f"**End Date:** {formatted_end_date}")
            st.write(f"**Travel Time:** {destination.travel_time}")
            st.write(f"**Approximate Stay Cost:** ${destination.stay_cost}")
            st.markdown(
                f"Google Flights: [link](https://www.google.com/travel/flights?q=Flights%20to%20{location_cleaned}%20from%20{from_location_cleaned}%20on%20{start_date_cleaned}%20through%20{end_date_cleaned})"
            )


def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    if "from_location" not in st.session_state:
        st.session_state.from_location = ""

    if "end_location" not in st.session_state:
        st.session_state.end_location = None

    if "page_number" not in st.session_state:
        st.session_state.page_number = 1

    if "search_button_clicked" not in st.session_state:
        st.session_state.search_button_clicked = False


def main():
    initialize_session_state()
    st.set_page_config(
        layout="centered",  # Can be "centered" or "wide". In the future also "dashboard", etc.
        initial_sidebar_state="auto",  # Can be "auto", "expanded", "collapsed"
        page_title="Changelog Builder - Hyperbrowser",  # String or None. Strings get appended with "• Streamlit".
        page_icon="https://hyperbrowser-assets-bucket.s3.us-east-1.amazonaws.com/favicon.ico",  # String, anything supported by st.image, or None.
    )

    # Create two columns for the header
    col1, col2 = st.columns([3, 2])

    # Add logo in the left column - using local file
    with col1:
        st.image(
            "https://hyperbrowser-assets-bucket.s3.us-east-1.amazonaws.com/wordmark-dark.png",
            width=200,
        )

    # Add hyperbrowser link in the right column, aligned to the right
    with col2:
        st.html(
            """
        <div style="text-align: right; display: flex; justify-content: flex-end; height: 100%; align-items: center;">
            <p style="margin: 0px;">
                Powered by <a href="https://hyperbrowser.ai" target="_blank">hyperbrowser.ai</a>
            </p>
        </div>
        """,
        )

    st.title("Travel Explorer")
    st.write("This app automates searches on Google Travel and analyzes the results.")

    # Input fields
    col1, col2 = st.columns(2)
    with col1:
        start_location = st.text_input(
            "Starting Location",
            value=st.session_state.from_location,
            key="from_location_input",
            help="Enter the starting location",
        )
        if start_location != st.session_state.from_location:

            st.session_state.search_button_clicked = False
        st.session_state.from_location = start_location
    with col2:
        end_location = st.text_input(
            "Destination",
            key="destination_input",
            placeholder="Leave blank to search for any destination",
            help="Optional: Leave blank to search for any destination",
            value=st.session_state.end_location,
        )
        if end_location != st.session_state.end_location:
            st.session_state.search_button_clicked = False
        st.session_state.end_location = end_location
    trip_duration = st.selectbox("Trip Duration", ["Weekend", "1 Week", "2 Weeks"])

    if st.button("Search Travel Options") or st.session_state.search_button_clicked:
        if not start_location:
            st.error("Please enter starting location.")
            return
        st.session_state.search_button_clicked = True
        if not st.session_state.search_button_clicked:
            location_reset = False
            valid_start_location, valid_start_location_name = validate_city(
                start_location
            )
            if not valid_start_location:
                st.error(
                    "Invalid starting location. Please enter a valid location name."
                )
                return
            else:
                if valid_start_location_name != start_location:
                    if valid_start_location_name is not None:
                        location_reset = True
                        st.info(
                            f"Start location modified to : {valid_start_location_name}"
                        )
                        st.session_state.from_location = valid_start_location_name
                        start_location = valid_start_location_name

            if end_location is not None:
                valid_end_location, valid_end_location_name = validate_city(
                    end_location
                )
                if not valid_end_location:
                    st.error(
                        "Invalid destination location. Please enter a valid location name."
                    )
                    return
                else:
                    if valid_end_location_name != end_location:
                        if valid_end_location_name is not None:
                            location_reset = True
                            st.info(
                                f"End location modified to : {valid_end_location_name}"
                            )
                            st.session_state.end_location = valid_end_location_name
                            end_location = valid_end_location_name

            if location_reset:
                st.rerun()

        with st.spinner("Searching for travel options..."):
            try:
                # Take screenshot
                screenshot_path = take_screenshot(
                    start_location, end_location, trip_duration
                )

                if not screenshot_path:
                    st.error("Could not get the screenshot for the travel options")
                    return
                with st.expander("Locations Screenshot"):
                    # Display the screenshot
                    st.image(
                        screenshot_path, caption="Screenshot of Google Travel results"
                    )

                # Check if OpenAI API key is available
                if openai_api_key:
                    with st.spinner("Analyzing the results with OpenAI..."):
                        # Analyze screenshot with OpenAI
                        analysis = extract_travel_data_from_image(screenshot_path)

                        if analysis:
                            # Display the analysis
                            st.subheader("Travel Analysis")
                            display_travel_data(analysis, start_location)
                        else:
                            st.error(
                                "Could not extract travel data from the screenshot"
                            )
                else:
                    st.warning(
                        "OpenAI API key not provided. Please add it to the .env file to enable analysis."
                    )

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
