import streamlit as st
import pandas as pd
import uuid
from datetime import datetime

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="LostLink - University Lost & Found",
    page_icon="🔎",
    layout="wide"
)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "items" not in st.session_state:
    st.session_state.items = [
        {
            "id": "L001",
            "type": "Lost",
            "item_name": "Black Wallet",
            "description": "Black leather wallet with school ID and cards",
            "category": "Personal Items",
            "location": "Library",
            "date": "September 20, 2026",
            "status": "Lost",
            "reported_by": "Juan Dela Cruz",
            "contact": "juan@email.com"
        },
        {
            "id": "F001",
            "type": "Found",
            "item_name": "Black Wallet",
            "description": "Black wallet found near the library entrance",
            "category": "Personal Items",
            "location": "Library",
            "date": "September 20, 2026",
            "status": "Found",
            "reported_by": "Maria Santos",
            "contact": "maria@email.com"
        },
        {
            "id": "L002",
            "type": "Lost",
            "item_name": "Blue Umbrella",
            "description": "Blue folding umbrella with black handle",
            "category": "Accessories",
            "location": "Cafeteria",
            "date": "September 19, 2026",
            "status": "Lost",
            "reported_by": "Pedro Reyes",
            "contact": "pedro@email.com"
        },
        {
            "id": "F002",
            "type": "Found",
            "item_name": "Student ID",
            "description": "University student identification card",
            "category": "Documents",
            "location": "Computer Laboratory",
            "date": "September 21, 2026",
            "status": "Found",
            "reported_by": "Anna Garcia",
            "contact": "anna@email.com"
        }
    ]

if "claims" not in st.session_state:
    st.session_state.claims = []

if "logged_in" not in st.session_state:
    st.session_state.logged_in = True

if "current_user" not in st.session_state:
    st.session_state.current_user = "Student User"


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def generate_id(prefix):
    """Generate a simple unique ID."""
    return prefix + str(uuid.uuid4())[:6].upper()


def clean_words(text):
    """
    Convert text into simple words for keyword matching.
    No NLP library is required.
    """
    if not text:
        return set()

    punctuation = ",.!?;:()[]{}\"'/-_"

    text = text.lower()

    for char in punctuation:
        text = text.replace(char, " ")

    return set(text.split())


def calculate_match_score(lost_item, found_item):
    """
    Calculate a simple matching score using:
    - Item name
    - Description keywords
    - Category
    - Location

    This is NOT NLP.
    """

    score = 0

    # -----------------------------
    # ITEM NAME MATCH
    # -----------------------------

    lost_name = clean_words(lost_item["item_name"])
    found_name = clean_words(found_item["item_name"])

    if lost_name and found_name:
        name_matches = lost_name.intersection(found_name)

        if name_matches:
            score += min(len(name_matches) * 20, 40)

    # -----------------------------
    # DESCRIPTION MATCH
    # -----------------------------

    lost_description = clean_words(lost_item["description"])
    found_description = clean_words(found_item["description"])

    common_words = lost_description.intersection(found_description)

    # Ignore very common words
    ignored_words = {
        "the",
        "and",
        "with",
        "for",
        "near",
        "found",
        "item",
        "this",
        "that",
        "has",
        "was",
        "is"
    }

    meaningful_words = common_words - ignored_words

    if meaningful_words:
        score += min(len(meaningful_words) * 5, 25)

    # -----------------------------
    # CATEGORY MATCH
    # -----------------------------

    if lost_item["category"] == found_item["category"]:
        score += 20

    # -----------------------------
    # LOCATION MATCH
    # -----------------------------

    if lost_item["location"] == found_item["location"]:
        score += 15

    return min(score, 100)


def find_matches(lost_item):
    """
    Find found items that may match the selected lost item.
    """

    matches = []

    for item in st.session_state.items:

        if item["type"] != "Found":
            continue

        if item["status"] != "Found":
            continue

        score = calculate_match_score(lost_item, item)

        if score >= 20:
            matches.append({
                "item": item,
                "score": score
            })

    matches.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return matches


def display_item_card(item, show_score=None):

    with st.container(border=True):

        col1, col2 = st.columns([3, 1])

        with col1:
            st.subheader(item["item_name"])

            st.write(
                f"**Description:** {item['description']}"
            )

            st.write(
                f"**Category:** {item['category']}"
            )

            st.write(
                f"**Location:** {item['location']}"
            )

            st.write(
                f"**Date:** {item['date']}"
            )

            st.write(
                f"**Reported by:** {item['reported_by']}"
            )

        with col2:

            if item["type"] == "Lost":
                st.error("🔴 LOST")
            else:
                st.success("🟢 FOUND")

            if show_score is not None:
                st.metric(
                    "Match Score",
                    f"{show_score}%"
                )


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("🔎 LostLink")

st.sidebar.write(
    "University Lost & Found System"
)

st.sidebar.divider()

menu = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "🔍 Search Items",
        "📢 Report Lost Item",
        "📦 Report Found Item",
        "📋 All Reports",
        "🤝 Claims",
        "👤 Profile",
        "⚙️ Admin Dashboard"
    ]
)

st.sidebar.divider()

st.sidebar.write(
    f"Logged in as: **{st.session_state.current_user}**"
)


# ==================================================
# DASHBOARD
# ==================================================

if menu == "🏠 Dashboard":

    st.title("🏠 LostLink Dashboard")

    st.write(
        "A university system for reporting, searching, and "
        "matching lost and found items."
    )

    st.divider()

    lost_items = [
        item for item in st.session_state.items
        if item["type"] == "Lost"
    ]

    found_items = [
        item for item in st.session_state.items
        if item["type"] == "Found"
    ]

    resolved_items = [
        item for item in st.session_state.items
        if item["status"] == "Claimed"
    ]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Lost Items",
            len(lost_items)
        )

    with col2:
        st.metric(
            "Found Items",
            len(found_items)
        )

    with col3:
        st.metric(
            "Claims",
            len(st.session_state.claims)
        )

    with col4:
        st.metric(
            "Resolved",
            len(resolved_items)
        )

    st.divider()

    st.subheader("📌 Recent Reports")

    recent_items = st.session_state.items[-5:]

    for item in reversed(recent_items):
        display_item_card(item)


# ==================================================
# SEARCH ITEMS
# ==================================================

elif menu == "🔍 Search Items":

    st.title("🔍 Search Lost & Found Items")

    st.write(
        "Search for items using keywords, category, location, "
        "or item status."
    )

    col1, col2 = st.columns(2)

    with col1:
        search_text = st.text_input(
            "Search item",
            placeholder="Example: black wallet"
        )

    with col2:
        search_type = st.selectbox(
            "Item Type",
            [
                "All",
                "Lost",
                "Found"
            ]
        )

    col3, col4 = st.columns(2)

    with col3:
        category_filter = st.selectbox(
            "Category",
            [
                "All",
                "Electronics",
                "Personal Items",
                "Documents",
                "Accessories",
                "Clothing",
                "Others"
            ]
        )

    with col4:
        location_filter = st.selectbox(
            "Location",
            [
                "All",
                "Library",
                "Cafeteria",
                "Computer Laboratory",
                "Gymnasium",
                "Classroom",
                "Student Center",
                "Others"
            ]
        )

    st.divider()

    results = []

    for item in st.session_state.items:

        # Type filter
        if search_type != "All":
            if item["type"] != search_type:
                continue

        # Category filter
        if category_filter != "All":
            if item["category"] != category_filter:
                continue

        # Location filter
        if location_filter != "All":
            if item["location"] != location_filter:
                continue

        # Keyword search
        if search_text:

            search_words = clean_words(search_text)

            item_text = (
                item["item_name"]
                + " "
                + item["description"]
            )

            item_words = clean_words(item_text)

            if not search_words.intersection(item_words):
                continue

        results.append(item)

    st.write(
        f"**{len(results)} item(s) found.**"
    )

    if results:

        for item in results:
            display_item_card(item)

    else:

        st.info(
            "No matching items were found."
        )


# ==================================================
# REPORT LOST ITEM
# ==================================================

elif menu == "📢 Report Lost Item":

    st.title("📢 Report Lost Item")

    st.write(
        "Provide information about the item you lost."
    )

    with st.form("lost_item_form"):

        item_name = st.text_input(
            "Item Name *",
            placeholder="Example: Black Wallet"
        )

        description = st.text_area(
            "Description *",
            placeholder=(
                "Describe the item, color, brand, "
                "identifying marks, etc."
            )
        )

        col1, col2 = st.columns(2)

        with col1:

            category = st.selectbox(
                "Category",
                [
                    "Electronics",
                    "Personal Items",
                    "Documents",
                    "Accessories",
                    "Clothing",
                    "Others"
                ]
            )

        with col2:

            location = st.selectbox(
                "Last Seen Location",
                [
                    "Library",
                    "Cafeteria",
                    "Computer Laboratory",
                    "Gymnasium",
                    "Classroom",
                    "Student Center",
                    "Others"
                ]
            )

        date_lost = st.date_input(
            "Date Lost"
        )

        contact = st.text_input(
            "Contact Information *",
            placeholder="Email or phone number"
        )

        submitted = st.form_submit_button(
            "Submit Lost Item Report"
        )

        if submitted:

            if not item_name or not description or not contact:

                st.error(
                    "Please complete all required fields."
                )

            else:

                new_item = {
                    "id": generate_id("L"),
                    "type": "Lost",
                    "item_name": item_name,
                    "description": description,
                    "category": category,
                    "location": location,
                    "date": str(date_lost),
                    "status": "Lost",
                    "reported_by": st.session_state.current_user,
                    "contact": contact
                }

                st.session_state.items.append(
                    new_item
                )

                st.success(
                    "Lost item report submitted successfully!"
                )

                st.info(
                    "You can check the Search Items page "
                    "for possible found items."
                )


# ==================================================
# REPORT FOUND ITEM
# ==================================================

elif menu == "📦 Report Found Item":

    st.title("📦 Report Found Item")

    st.write(
        "Report an item that you found inside the university."
    )

    with st.form("found_item_form"):

        item_name = st.text_input(
            "Item Name *",
            placeholder="Example: Black Wallet"
        )

        description = st.text_area(
            "Description *",
            placeholder=(
                "Describe the item, color, brand, "
                "and other identifying details."
            )
        )

        col1, col2 = st.columns(2)

        with col1:

            category = st.selectbox(
                "Category",
                [
                    "Electronics",
                    "Personal Items",
                    "Documents",
                    "Accessories",
                    "Clothing",
                    "Others"
                ]
            )

        with col2:

            location = st.selectbox(
                "Found Location",
                [
                    "Library",
                    "Cafeteria",
                    "Computer Laboratory",
                    "Gymnasium",
                    "Classroom",
                    "Student Center",
                    "Others"
                ]
            )

        date_found = st.date_input(
            "Date Found"
        )

        contact = st.text_input(
            "Your Contact Information *",
            placeholder="Email or phone number"
        )

        submitted = st.form_submit_button(
            "Submit Found Item Report"
        )

        if submitted:

            if not item_name or not description or not contact:

                st.error(
                    "Please complete all required fields."
                )

            else:

                new_item = {
                    "id": generate_id("F"),
                    "type": "Found",
                    "item_name": item_name,
                    "description": description,
                    "category": category,
                    "location": location,
                    "date": str(date_found),
                    "status": "Found",
                    "reported_by": st.session_state.current_user,
                    "contact": contact
                }

                st.session_state.items.append(
                    new_item
                )

                st.success(
                    "Found item report submitted successfully!"
                )


# ==================================================
# ALL REPORTS
# ==================================================

elif menu == "📋 All Reports":

    st.title("📋 All Lost & Found Reports")

    if st.session_state.items:

        df = pd.DataFrame(
            st.session_state.items
        )

        display_df = df[
            [
                "id",
                "type",
                "item_name",
                "category",
                "location",
                "date",
                "status"
            ]
        ]

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No reports available."
        )


# ==================================================
# CLAIMS
# ==================================================

elif menu == "🤝 Claims":

    st.title("🤝 Item Claims")

    st.write(
        "Select a found item that you believe belongs to you."
    )

    found_items = [
        item for item in st.session_state.items
        if item["type"] == "Found"
        and item["status"] == "Found"
    ]

    if not found_items:

        st.info(
            "There are currently no found items available for claims."
        )

    else:

        selected_item_id = st.selectbox(
            "Select Found Item",
            [
                item["id"]
                + " - "
                + item["item_name"]
                for item in found_items
            ]
        )

        selected_id = selected_item_id.split(" - ")[0]

        selected_item = next(
            item for item in found_items
            if item["id"] == selected_id
        )

        st.divider()

        display_item_card(selected_item)

        st.divider()

        st.subheader("Claim Information")

        claim_reason = st.text_area(
            "Why do you believe this item belongs to you?",
            placeholder=(
                "Provide identifying details such as "
                "color, contents, brand, serial number, "
                "or other information."
            )
        )

        contact = st.text_input(
            "Your Contact Information"
        )

        if st.button(
            "Submit Claim",
            type="primary"
        ):

            if not claim_reason or not contact:

                st.error(
                    "Please provide the required information."
                )

            else:

                claim = {
                    "claim_id": generate_id("C"),
                    "item_id": selected_item["id"],
                    "item_name": selected_item["item_name"],
                    "claimed_by": st.session_state.current_user,
                    "reason": claim_reason,
                    "contact": contact,
                    "status": "Pending",
                    "date": str(datetime.now().date())
                }

                st.session_state.claims.append(
                    claim
                )

                st.success(
                    "Your claim has been submitted!"
                )


# ==================================================
# PROFILE
# ==================================================

elif menu == "👤 Profile":

    st.title("👤 My Profile")

    st.subheader(
        st.session_state.current_user
    )

    st.write(
        "Student Account"
    )

    st.divider()

    my_reports = [
        item for item in st.session_state.items
        if item["reported_by"]
        == st.session_state.current_user
    ]

    my_claims = [
        claim for claim in st.session_state.claims
        if claim["claimed_by"]
        == st.session_state.current_user
    ]

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "My Reports",
            len(my_reports)
        )

    with col2:
        st.metric(
            "My Claims",
            len(my_claims)
        )

    st.divider()

    st.subheader("My Reports")

    if my_reports:

        for item in my_reports:
            display_item_card(item)

    else:

        st.info(
            "You have not submitted any reports yet."
        )


# ==================================================
# ADMIN DASHBOARD
# ==================================================

elif menu == "⚙️ Admin Dashboard":

    st.title("⚙️ Admin Dashboard")

    st.write(
        "Manage lost and found reports and claims."
    )

    st.divider()

    # Statistics

    total_items = len(
        st.session_state.items
    )

    total_lost = len([
        x for x in st.session_state.items
        if x["type"] == "Lost"
    ])

    total_found = len([
        x for x in st.session_state.items
        if x["type"] == "Found"
    ])

    total_claims = len(
        st.session_state.claims
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Reports",
            total_items
        )

    with col2:
        st.metric(
            "Lost",
            total_lost
        )

    with col3:
        st.metric(
            "Found",
            total_found
        )

    with col4:
        st.metric(
            "Claims",
            total_claims
        )

    # ----------------------------------------------
    # ITEM MANAGEMENT
    # ----------------------------------------------

    st.divider()

    st.subheader("📋 Item Management")

    for index, item in enumerate(
        st.session_state.items
    ):

        with st.expander(
            f"{item['id']} - {item['item_name']} ({item['type']})"
        ):

            st.write(
                f"**Description:** {item['description']}"
            )

            st.write(
                f"**Category:** {item['category']}"
            )

            st.write(
                f"**Location:** {item['location']}"
            )

            st.write(
                f"**Status:** {item['status']}"
            )

            new_status = st.selectbox(
                "Update Status",
                [
                    "Lost",
                    "Found",
                    "Claimed",
                    "Resolved"
                ],
                index=[
                    "Lost",
                    "Found",
                    "Claimed",
                    "Resolved"
                ].index(item["status"]),
                key=f"status_{index}"
            )

            if st.button(
                "Update Status",
                key=f"update_{index}"
            ):

                st.session_state.items[index][
                    "status"
                ] = new_status

                st.success(
                    "Status updated successfully."
                )

                st.rerun()

    # ----------------------------------------------
    # CLAIM MANAGEMENT
    # ----------------------------------------------

    st.divider()

    st.subheader("🤝 Claim Management")

    if not st.session_state.claims:

        st.info(
            "No claims have been submitted."
        )

    else:

        for index, claim in enumerate(
            st.session_state.claims
        ):

            with st.expander(
                f"{claim['claim_id']} - "
                f"{claim['item_name']}"
            ):

                st.write(
                    f"**Claimed by:** {claim['claimed_by']}"
                )

                st.write(
                    f"**Reason:** {claim['reason']}"
                )

                st.write(
                    f"**Contact:** {claim['contact']}"
                )

                st.write(
                    f"**Status:** {claim['status']}"
                )

                new_claim_status = st.selectbox(
                    "Claim Status",
                    [
                        "Pending",
                        "Approved",
                        "Rejected"
                    ],
                    index=[
                        "Pending",
                        "Approved",
                        "Rejected"
                    ].index(claim["status"]),
                    key=f"claim_status_{index}"
                )

                if st.button(
                    "Update Claim",
                    key=f"claim_update_{index}"
                ):

                    st.session_state.claims[index][
                        "status"
                    ] = new_claim_status

                    st.success(
                        "Claim status updated."
                    )

                    st.rerun()
