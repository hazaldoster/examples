import os
import pathlib
import tempfile
import time
import random
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from PIL import Image
import streamlit as st
from playwright.sync_api import sync_playwright
from playwright.sync_api import Page
import streamlit.components.v1 as components
from hyperbrowser.client.sync import Hyperbrowser
from hyperbrowser.models.session import CreateSessionParams

from location_validator import validate_city
from chatgpt_parser import TravelDestination, extract_travel_data_from_image
from dataclasses import dataclass

MAX_DAYS = 2


@dataclass
class PlaceDetails:
    title: str
    description: str
    images: list[str]
    page_url: str
    address: str
    coordinates: tuple[float, float]


@dataclass
class DayPlan:
    day: int
    places: list[PlaceDetails]


# ----- CACHING FUNCTIONS -----


@st.cache_data(ttl=3600)
def cached_capture_explore_page(browser_ws_url, from_location):
    st.session_state.page_number = 1
    return capture_explore_page(browser_ws_url, from_location)


@st.cache_data(ttl=3600)
def cached_extract_travel_data(image_path):
    st.session_state.page_number = 1
    return extract_travel_data_from_image(image_path)


# Cache the browser ws url for 14 minutes, so that we don't have to create a new session every time
@st.cache_resource(ttl=14 * 60)
def cached_browser_ws_url():
    client = Hyperbrowser(api_key=os.getenv("HYPERBROWSER_API_KEY"))
    session = client.sessions.create(CreateSessionParams(use_proxy=True))
    return [session.id, session.ws_endpoint]


# ----- BROWSER AUTOMATION FUNCTIONS -----


def set_weekend_filter(page):
    """Set the filter to display weekend trips."""
    duration_filter = page.query_selector('div[jsname="Q641D"]')
    if not duration_filter:
        st.warning("Could not find the duration filter")
        return False

    duration_filter.click()

    # Find and click on the "Weekend" option
    duration_options = page.wait_for_selector('div[aria-label="Trip duration"]')
    if not duration_options:
        st.warning("Could not find Weekend filter option")
        return False

    weekend_option = duration_options.query_selector("span[role='gridcell'] span")
    if not weekend_option:
        st.warning("Could not find Weekend filter option")
        return False

    weekend_option.click()
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


def capture_explore_page(browser_ws_url, from_location):
    """Use Playwright to navigate to Google Travel Explore and capture results."""
    try:
        browser = sync_playwright.chromium.connect_over_cdp(browser_ws_url)
        all_contexts = browser.contexts
        if len(all_contexts) == 0:
            context = browser.new_context()
        else:
            context = all_contexts[0]

        all_pages = context.pages
        if len(all_pages) == 0:
            page = context.new_page()
        else:
            page = all_pages[0]

        # Navigate to Google Travel Explore
        page.goto("https://www.google.com/travel/explore")

        locations_element = page.wait_for_selector("main")
        if not locations_element:
            st.error("Could not get locations properly")
            return

        # Wait for the page to load
        inputElement = page.wait_for_selector('input[aria-label="Where from?"]')
        if not inputElement:
            st.error("Travel Explore page did not load properly")
            return

        # Enter the location
        inputElement.fill(from_location)
        time.sleep(2)  # Wait for autocomplete suggestions
        page.keyboard.press("Enter")
        time.sleep(2)

        # Set weekend filter
        if not set_weekend_filter(page):
            return

        # Adjust viewport
        original_viewport_size, _ = adjust_viewport(page, locations_element)
        if not original_viewport_size:
            return

        # Create a temporary file for the screenshot
        screenshot_path = create_screenshot(locations_element)
        if not screenshot_path:
            return None

        # Reset viewport size to original
        page.set_viewport_size(original_viewport_size)
        time.sleep(1)

        # Process the image if needed
        final_screenshot_path = process_screenshot(screenshot_path)

        browser.disconnect()

        return final_screenshot_path
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None


def get_place_details(page: Page, link: str, find_nearby_places: bool = False):
    """Extract details from an Atlas Obscura place page."""
    try:
        # Get the link to the place page

        # Visit the place page
        page.goto(link)
        page.wait_for_load_state("domcontentloaded")
        time.sleep(2)

        title_element = page.query_selector("h1")
        title_text: str = (
            (title_element.text_content() or "Unknown Place")
            if title_element
            else "Unknown Place"
        )

        if title_element is None:
            description = "No description available"
        else:
            # Get the parent element of the title to find the description
            parent_element = title_element.evaluate_handle(
                "el => el.parentElement.children[1]"
            ).as_element()
            description = (
                parent_element.inner_text()
                if parent_element
                else "No description available"
            )

        try:
            images: list[str] = page.evaluate(
                '()=>[...document.querySelector("div.swiper").querySelectorAll("picture")].map(p=>p.querySelector("img").src)'
            )
        except Exception as e:
            single_image = page.evaluate(
                '()=>document.querySelector("div.swiper").querySelector("picture").querySelector("img").src'
            )
            images = [single_image]

        coordinates: tuple[float, float] = page.evaluate(
            '()=>document.querySelector(\'div[data-clipboard-name-value="Coordinates"]\').innerText.split(",").map(parseFloat)'
        ) or (0, 0)

        address: str = (
            page.evaluate(
                "()=>document.querySelector('address[data-clipboard-name-value]').innerText"
            )
            or "Address Unknown"
        )

        places: list[PlaceDetails] = []
        places.append(
            PlaceDetails(
                title=title_text,
                description=(
                    description[:300] + "..." if len(description) > 300 else description
                ),
                images=images,
                page_url=page.url,
                address=address,
                coordinates=coordinates,
            )
        )

        if find_nearby_places:
            # Find nearby places
            nearby_places = page.evaluate(
                '()=>[...new Set([...document.querySelectorAll("article.aon--simple-card")].map(e=>e.querySelector("a").href))]'
            )
            for place_url in nearby_places:
                nested_place_details = get_place_details(page, place_url, False)
                if nested_place_details:
                    places.extend(nested_place_details)

        return places
    except Exception as e:
        print(f"Error getting place details: {e}")
        return []


def search_atlas_obscura(browser_ws_url, location) -> list[DayPlan] | None:
    """Search Atlas Obscura for the specified location."""
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(browser_ws_url)
        all_contexts = browser.contexts
        if len(all_contexts) == 0:
            context = browser.new_context()
        else:
            context = all_contexts[0]

        all_pages = context.pages
        if len(all_pages) == 0:
            page = context.new_page()
        else:
            page = all_pages[0]

        # Navigate to Atlas Obscura
        page.goto("https://www.atlasobscura.com/")
        page.wait_for_load_state("domcontentloaded")

        # Find and click the search button
        search_button = page.wait_for_selector(
            'button[aria-label="Search"]', timeout=10000
        )
        if search_button:
            search_button.click()

            # Wait for search input to appear
            search_input = page.wait_for_selector('input[type="search"]', timeout=10000)
            if not search_input:
                st.error("Could not find search input on Atlas Obscura")
                return None

            search_input.type(location)
            time.sleep(2)  # Wait for autocomplete suggestions
            search_submit_button = page.wait_for_selector('button[type="Submit"]')
            if not search_submit_button:
                st.error("Could not find search submit button on Atlas Obscura")
                return None

            search_submit_button.evaluate("(element) => element.click()")
            page.wait_for_load_state("domcontentloaded")
            time.sleep(1)

            url = page.evaluate("()=>window.location.href")
            places_url = f"{url}/places?sort=recent"
            page.goto(places_url)
            page.wait_for_load_state("domcontentloaded")
            time.sleep(1)

            places = page.query_selector_all("a.Card")
            if not places or len(places) == 0:
                st.error("Could not find places on Atlas Obscura")
                return None

            # Sample 2 random places
            selected_places = random.sample(places, min(MAX_DAYS, len(places)))
            selected_place_urls: list[str] = [
                place.evaluate("el=>el.href") for place in selected_places
            ]

            day_plans: list[DayPlan] = []

            for place_day in range(len(selected_place_urls)):
                place_details = get_place_details(
                    page, selected_place_urls[place_day], True
                )
                if place_details:
                    day_plans.append(DayPlan(day=place_day + 1, places=place_details))

            # Return the results
            return day_plans
        else:
            st.error("Could not find search button on Atlas Obscura")

    return None


# ----- IMAGE PROCESSING FUNCTIONS -----


def create_screenshot(locations_element):
    """Take a screenshot of the locations element and save to a temporary file."""
    screenshot_file = tempfile.NamedTemporaryFile(
        suffix=".png", delete=False, dir=tempfile.gettempdir()
    )
    screenshot_path = pathlib.Path(screenshot_file.name)
    screenshot_file.close()

    # Take the screenshot
    locations_element.screenshot(
        path=screenshot_path,
        scale="css",  # Use CSS scaling for consistent size
        mask=[],  # No masking needed
    )

    return screenshot_path


def process_screenshot(screenshot_path):
    """Process the screenshot if it exceeds the maximum dimensions."""
    with Image.open(screenshot_path) as img:
        width, height = img.size
        max_dimension = 2048

        # Only resize if the image exceeds the maximum dimension
        if width > max_dimension or height > max_dimension:
            return crop_screenshot(screenshot_path, width, height, max_dimension)

        return screenshot_path


def crop_screenshot(screenshot_path, width, height, max_dimension):
    """Crop the screenshot to the maximum allowed dimensions."""
    new_screenshot_file = tempfile.NamedTemporaryFile(
        suffix=".png", delete=False, dir=tempfile.gettempdir()
    )
    new_screenshot_path = pathlib.Path(new_screenshot_file.name)
    new_screenshot_file.close()

    # Calculate the crop dimensions
    crop_width = min(width, max_dimension)
    crop_height = min(height, max_dimension)

    # Define crop box coordinates (crop from the top)
    left, top = 0, 0
    right = min(width, crop_width)
    bottom = min(height, crop_height)

    # Perform the crop
    with Image.open(screenshot_path) as img:
        cropped_img = img.crop((left, top, right, bottom))
        cropped_img.save(new_screenshot_path)

    # Remove the original screenshot
    if screenshot_path.exists():
        os.unlink(screenshot_path)
        print(f"Removed temporary screenshot file: {screenshot_path}")

    return new_screenshot_path


# ----- UI DISPLAY FUNCTIONS -----


def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    if "from_location" not in st.session_state:
        st.session_state.from_location = ""

    if "page_number" not in st.session_state:
        st.session_state.page_number = 1

    if "selected_destination" not in st.session_state:
        st.session_state.selected_destination = None

    if "show_atlas_obscura_modal" not in st.session_state:
        st.session_state.show_atlas_obscura_modal = False


def display_travel_data(
    travel_data: list[TravelDestination], browser_ws_url: str, from_location: str
):
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
        # Update the session state when number_input changes
        st.session_state.page_number = page_number
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

            # Add button to open Atlas Obscura search
            if st.button(
                f"Discover Things to do in {destination.location}", key=f"guide_btn_{i}"
            ):
                st.session_state.selected_destination = destination.location
                st.session_state.show_atlas_obscura_modal = True
                st.rerun()  # Trigger a rerun to show the modal

    # Show the Atlas Obscura modal if needed
    if (
        st.session_state.show_atlas_obscura_modal
        and st.session_state.selected_destination
    ):
        with st.spinner(
            f"Searching Atlas Obscura for {st.session_state.selected_destination}..."
        ):
            # Search Atlas Obscura for the selected destination
            ao_results = search_atlas_obscura(
                browser_ws_url, st.session_state.selected_destination
            )
            if ao_results is None:
                st.error(
                    f"Could not find things to do in {st.session_state.selected_destination}"
                )
                return False

            # Display the results
            display_atlas_obscura_results(
                ao_results, st.session_state.selected_destination
            )

    return True


def display_atlas_obscura_results(ao_results: list[DayPlan], destination: str):
    """Display Atlas Obscura search results in the modal."""
    if not ao_results:
        st.error(f"Could not find things to do in {destination}")
        return

    # Show search results page
    st.subheader(f"Things to do in {destination}")

    # Create tabs for each day
    day_tabs = st.tabs([f"Day {day_plan.day}" for day_plan in ao_results])

    # Display each day's plan
    for day_idx, (tab, day_plan) in enumerate(zip(day_tabs, ao_results)):
        with tab:
            st.subheader(f"Day {day_plan.day} Itinerary")

            # Display each place for this day
            for place_idx, place in enumerate(day_plan.places):
                with st.expander(f"Place {place_idx+1}: {place.title}"):
                    col1, col2 = st.columns([1, 1])

                    with col1:
                        if place.images and len(place.images) > 0:
                            st.image(
                                place.images[0],
                                caption=place.title,
                                use_container_width=True,
                            )

                    with col2:
                        st.subheader(place.title)
                        st.write(f"**Address:** {place.address}")
                        lat, lng = place.coordinates
                        maps_url = f"https://www.google.com/maps?q={lat},{lng}"
                        st.write(f"**Coordinates:** [{lat}, {lng}]({maps_url})")
                        st.write(place.description)
                        if place.page_url:
                            st.markdown(
                                f"[Read more on Atlas Obscura]({place.page_url})",
                                unsafe_allow_html=True,
                            )

            # Display summary of places for this day
            st.write(f"**Total Places for Day {day_plan.day}:** {len(day_plan.places)}")

            # Add a map showing all locations for this day
            if any(place.coordinates != (0, 0) for place in day_plan.places):
                st.write("**Map of Today's Locations:**")
                map_data = [
                    [place.coordinates[0], place.coordinates[1], place.title]
                    for place in day_plan.places
                    if place.coordinates != (0, 0)
                ]

                if map_data:
                    # Create a simple map with markers
                    locations_df = {
                        "lat": [loc[0] for loc in map_data],
                        "lon": [loc[1] for loc in map_data],
                        "data": [{"name": loc[2]} for loc in map_data],
                    }
                    st.map(locations_df)


# ----- MAIN APPLICATION FUNCTION -----


def main():
    client = Hyperbrowser(api_key=os.getenv("HYPERBROWSER_API_KEY"))

    """Main application function."""
    st.title("Weekend Getaway Planner")
    st.write("Find weekend trip destinations from your city!")

    # Initialize session state
    initialize_session_state()

    # Get starting location from user
    from_location = st.text_input(
        "Enter your starting city:",
        value=st.session_state.from_location,
    )

    if from_location is not None and (
        st.button("Find Weekend Getaways") or from_location != ""
    ):
        # Validate city
        if not validate_city(from_location):
            st.error(
                f"'{from_location}' doesn't appear to be a valid city. Please try again."
            )
            return
        else:
            if from_location != st.session_state.from_location:
                st.session_state.from_location = from_location
                st.session_state.page_number = 1
                st.session_state.show_atlas_obscura_modal = False
                st.session_state.selected_destination = None

        # Capture screenshot
        screenshot_tmp_path = None
        with st.spinner("Searching for destinations..."):
            try:
                session_id, browser_ws_url = cached_browser_ws_url()
                if not (browser_ws_url):
                    st.error("Could not create session")
                    return
                screenshot_tmp_path = cached_capture_explore_page(
                    browser_ws_url, from_location.lower()
                )
                if screenshot_tmp_path is None:
                    st.error("Could not get screenshot")
                    return

                # Display the screenshot in an expander
                with st.expander("Travel Options"):
                    st.image(
                        screenshot_tmp_path,
                        caption="Google Travel Results",
                        use_container_width=True,
                    )

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                import traceback

                st.error(traceback.format_exc())
                return

        # Extract and display travel data
        with st.spinner("Fetching locations results..."):
            travel_data = cached_extract_travel_data(screenshot_tmp_path)
            st.subheader(f"Weekend Getaways from {from_location}")
            session_id, browser_ws_url = cached_browser_ws_url()
            if not (browser_ws_url):
                st.error("Could not create session")
                return
            if travel_data is None:
                st.error("Could not get travel data")
                return
            display_travel_data(
                travel_data,
                browser_ws_url,
                from_location,
            )


if __name__ == "__main__":
    main()
