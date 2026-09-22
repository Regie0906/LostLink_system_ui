
import streamlit as st
import pandas as pd
import uuid
from datetime import datetime
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="LostLink | University Lost & Found",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 40px;
        font-weight: 700;
        margin-bottom: 0px;
    }

    .subtitle {
        font-size: 17px;
        color: #6b7280;
        margin-bottom: 25px;
    }

    .section-title {
        font-size: 25px;
        font-weight: 650;
    }

    .info-card {
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        background-color: #f8fafc;
        margin-bottom: 15px;
    }

    .match-card {
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #dbeafe;
        background-color: #eff6ff;
        margin-bottom: 12px;
    }

    .footer {
        text-align: center;
        color: #6b7280;
        padding: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# NLP MODEL
# ============================================================

@st.cache_resource
def load_nlp_model():
    """
    Loads the Sentence Transformer model.

    The model converts item descriptions into numerical
    embeddings that can be compared semantically.
    """

    return SentenceTransformer("all-MiniLM-L6-v2")


# Load the NLP model
nlp_model = load_nlp_model()


# ============================================================
# SESSION STATE
# ============================================================

if "items" not in st.session_state:

    st.session_state.items = [

        {
            "id": "LL-1001",
            "type": "Lost",
            "name": "Black Laptop",
            "category": "Electronics",
            "description": (
                "I lost my black Lenovo laptop with a small "
                "sticker on the back. I may have left it "
                "near the university library."
            ),
            "location": "University Library",
            "date": "September 18, 2026",
            "owner": "Juan Dela Cruz",
            "contact": "juan@university.edu",
            "status": "Pending",
            "image": None,
            "claimed_by": None
        },

        {
            "id": "LL-1002",
            "type": "Found",
            "name": "Lenovo Notebook Computer",
            "category": "Electronics",
            "description": (
                "A dark colored Lenovo notebook computer was "
                "found beside the campus library. It has a "
                "small sticker on its back."
            ),
            "location": "University Library",
            "date": "September 19, 2026",
            "owner": "Maria Santos",
            "contact": "maria@university.edu",
            "status": "Found",
            "image": None,
            "claimed_by": None
        },

        {
            "id": "LL-1003",
            "type": "Lost",
            "name": "Black Wallet",
            "category": "Wallet",
            "description": (
                "Black leather wallet containing my student "
                "ID and several cards. I last remember having "
                "it at the student center."
            ),
            "location": "Student Center",
            "date": "September 20, 2026",
            "owner": "Alex Reyes",
            "contact": "alex@university.edu",
            "status": "Pending",
            "image": None,
            "claimed_by": None
        },

        {
            "id": "LL-1004",
            "type": "Found",
            "name": "Leather Wallet",
            "category": "Wallet",
            "description": (
                "A black leather wallet was found at the "
                "student center. It contains several cards "
                "and a university identification card."
            ),
            "location": "Student Center",
            "date": "September 20, 2026",
            "owner": "Mark Garcia",
            "contact": "mark@university.edu",
            "status": "Found",
            "image": None,
            "claimed_by": None
        },

        {
            "id": "LL-1005",
            "type": "Found",
            "name": "Blue Umbrella",
            "category": "Personal Item",
            "description": (
                "A blue foldable umbrella was found near "
                "the university cafeteria."
            ),
            "location": "Cafeteria",
            "date": "September 21, 2026",
            "owner": "Student Volunteer",
            "contact": "volunteer@university.edu",
            "status": "Found",
            "image": None,
            "claimed_by": None
        }
    ]


if "claims" not in st.session_state:
    st.session_state.claims = []


if "current_user" not in st.session_state:
    st.session_state.current_user = "Student User"


if "current_email" not in st.session_state:
    st.session_state.current_email = "student@university.edu"


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def generate_id():
    """
    Generates a unique LostLink report ID.
    """

    return "LL-" + str(uuid.uuid4())[:6].upper()


def create_item_text(item):
    """
    Combines important item information into one text.

    This text will be converted into a semantic embedding
    by the Sentence Transformer model.
    """

    return (
        f"Item name: {item['name']}. "
        f"Category: {item['category']}. "
        f"Description: {item['description']}. "
        f"Location: {item['location']}."
    )


def semantic_similarity(item1, item2):
    """
    Calculates semantic similarity between two items.

    Returns a value between 0 and 100.
    """

    text1 = create_item_text(item1)
    text2 = create_item_text(item2)

    embeddings = nlp_model.encode(
        [text1, text2],
        convert_to_numpy=True
    )

    similarity = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]]
    )[0][0]

    # Prevent unusual negative values
    similarity = max(0, similarity)

    return round(similarity * 100, 2)


def calculate_match_score(item1, item2):
    """
    Calculates a combined match score using:

    1. NLP semantic similarity
    2. Category similarity
    3. Location similarity

    NLP receives the largest weight.
    """

    semantic_score = semantic_similarity(
        item1,
        item2
    )

    # Category score
    if item1["category"] == item2["category"]:
        category_score = 100
    else:
        category_score = 0

    # Location score
    if item1["location"] == item2["location"]:
        location_score = 100
    else:
        location_score = 0

    # Weighted score
    final_score = (
        semantic_score * 0.70
        + category_score * 0.15
        + location_score * 0.15
    )

    return round(final_score, 2)


def find_semantic_matches(item, threshold=45):
    """
    Finds possible matching reports.

    Lost items are compared only with Found items.
    Found items are compared only with Lost items.
    """

    matches = []

    for existing in st.session_state.items:

        # Don't compare an item with itself
        if existing["id"] == item["id"]:
            continue

        # Lost should match Found
        # Found should match Lost
        if existing["type"] == item["type"]:
            continue

        score = calculate_match_score(
            item,
            existing
        )

        if score >= threshold:

            matches.append(
                {
                    "item": existing,
                    "score": score
                }
            )

    # Highest score first
    matches.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return matches


def match_description(score):
    """
    Returns a human-readable description
    for the similarity score.
    """

    if score >= 80:
        return "Very Strong Possible Match"

    elif score >= 65:
        return "Strong Possible Match"

    elif score >= 50:
        return "Possible Match"

    else:
        return "Weak Possible Match"


def show_match_results(matches):

    if not matches:

        st.info(
            "🤖 No possible matching reports were found."
        )

        return

    st.subheader(
        "🤖 NLP-Based Possible Matches"
    )

    st.write(
        "The system compared the item description with "
        "other reports using semantic similarity."
    )

    for match in matches[:5]:

        existing = match["item"]
        score = match["score"]

        with st.container(border=True):

            col1, col2 = st.columns(
                [1, 3]
            )

            with col1:

                if existing["image"] is not None:

                    st.image(
                        existing["image"],
                        use_container_width=True
                    )

                else:

                    st.markdown(
                        "### 📦"
                    )

            with col2:

                st.markdown(
                    f"### {existing['name']}"
                )

                st.write(
                    existing["description"]
                )

                st.write(
                    f"📍 **Location:** {existing['location']}"
                )

                st.write(
                    f"🏷️ **Category:** {existing['category']}"
                )

                st.write(
                    f"📅 **Date:** {existing['date']}"
                )

                if score >= 80:

                    st.success(
                        f"🟢 Match Score: {score}% — "
                        f"{match_description(score)}"
                    )

                elif score >= 65:

                    st.warning(
                        f"🟡 Match Score: {score}% — "
                        f"{match_description(score)}"
                    )

                else:

                    st.info(
                        f"🔵 Match Score: {score}% — "
                        f"{match_description(score)}"
                    )

                st.caption(
                    f"Report ID: {existing['id']}"
                )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🔎 LostLink")

    st.caption(
        "University Lost & Found System"
    )

    st.divider()

    menu = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "🔎 Search Items",
            "📌 Report Lost Item",
            "📦 Report Found Item",
            "📋 All Reports",
            "🤖 Find Possible Matches",
            "📨 My Claims",
            "👤 My Profile",
            "🛡️ Admin Dashboard"
        ]
    )

    st.divider()

    st.markdown("### 👤 Current User")

    st.write(
        st.session_state.current_user
    )

    st.caption(
        st.session_state.current_email
    )

    st.divider()

    st.info(
        "LostLink uses NLP-based semantic matching "
        "to identify possible relationships between "
        "lost and found item descriptions."
    )


# ============================================================
# DASHBOARD
# ============================================================

if menu == "🏠 Dashboard":

    st.markdown(
        '<div class="main-title">🔎 LostLink</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'University Lost & Found System'
        '</div>',
        unsafe_allow_html=True
    )

    st.info(
        "Lost something on campus? Report it on LostLink. "
        "Found an item? Help return it to its owner."
    )

    # --------------------------------------------------------
    # STATISTICS
    # --------------------------------------------------------

    total_reports = len(
        st.session_state.items
    )

    total_lost = len(
        [
            item for item in st.session_state.items
            if item["type"] == "Lost"
        ]
    )

    total_found = len(
        [
            item for item in st.session_state.items
            if item["type"] == "Found"
        ]
    )

    total_claimed = len(
        [
            item for item in st.session_state.items
            if item["status"] == "Claimed"
        ]
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Reports",
            total_reports
        )

    with col2:
        st.metric(
            "Lost Items",
            total_lost
        )

    with col3:
        st.metric(
            "Found Items",
            total_found
        )

    with col4:
        st.metric(
            "Claimed Items",
            total_claimed
        )

    st.divider()

    # --------------------------------------------------------
    # HOW IT WORKS
    # --------------------------------------------------------

    st.subheader(
        "🤖 How LostLink Works"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(
            "### 1️⃣ Report"
        )

        st.write(
            "Students report a lost or found item "
            "with its description, category, and location."
        )

    with col2:

        st.markdown(
            "### 2️⃣ Analyze"
        )

        st.write(
            "The NLP model analyzes the meaning of "
            "the item descriptions."
        )

    with col3:

        st.markdown(
            "### 3️⃣ Match"
        )

        st.write(
            "The system displays possible matching "
            "lost and found reports."
        )

    st.divider()

    # --------------------------------------------------------
    # RECENT REPORTS
    # --------------------------------------------------------

    st.subheader(
        "🕒 Recent Reports"
    )

    recent_items = st.session_state.items[-5:]

    for item in reversed(recent_items):

        with st.container(border=True):

            col1, col2, col3 = st.columns(
                [1, 4, 1]
            )

            with col1:

                if item["type"] == "Lost":
                    st.error("LOST")

                else:
                    st.success("FOUND")

            with col2:

                st.write(
                    f"### {item['name']}"
                )

                st.caption(
                    f"{item['category']} • "
                    f"{item['location']}"
                )

            with col3:

                st.caption(
                    item["status"]
                )


# ============================================================
# SEARCH ITEMS
# ============================================================

elif menu == "🔎 Search Items":

    st.title(
        "🔎 Search Lost & Found Items"
    )

    st.write(
        "Search reported items using keywords, "
        "category, location, or report type."
    )

    col1, col2 = st.columns(2)

    with col1:

        keyword = st.text_input(
            "🔍 Search Keyword",
            placeholder="Example: laptop, wallet, phone"
        )

    with col2:

        item_type = st.selectbox(
            "Report Type",
            [
                "All",
                "Lost",
                "Found"
            ]
        )

    col1, col2 = st.columns(2)

    with col1:

        category = st.selectbox(
            "Category",
            [
                "All",
                "Electronics",
                "Documents",
                "Wallet",
                "Personal Item",
                "Clothing",
                "School Supplies",
                "Keys",
                "Others"
            ]
        )

    with col2:

        location = st.selectbox(
            "Location",
            [
                "All",
                "Main Building",
                "University Library",
                "Student Center",
                "Cafeteria",
                "Gymnasium",
                "Laboratory",
                "Parking Area",
                "Other"
            ]
        )

    st.divider()

    results = []

    for item in st.session_state.items:

        match = True

        if keyword:

            search_text = (
                item["name"]
                + " "
                + item["description"]
            ).lower()

            if keyword.lower() not in search_text:

                match = False

        if item_type != "All":

            if item["type"] != item_type:
                match = False

        if category != "All":

            if item["category"] != category:
                match = False

        if location != "All":

            if item["location"] != location:
                match = False

        if match:

            results.append(item)

    st.subheader(
        f"Search Results: {len(results)}"
    )

    if not results:

        st.warning(
            "No matching reports were found."
        )

    for item in results:

        with st.container(border=True):

            col1, col2 = st.columns(
                [1, 4]
            )

            with col1:

                if item["image"] is not None:

                    st.image(
                        item["image"],
                        use_container_width=True
                    )

                else:

                    st.markdown(
                        "### 📦"
                    )

            with col2:

                if item["type"] == "Lost":
                    st.error("LOST ITEM")
                else:
                    st.success("FOUND ITEM")

                st.subheader(
                    item["name"]
                )

                st.write(
                    item["description"]
                )

                st.caption(
                    f"📍 {item['location']} | "
                    f"🏷️ {item['category']} | "
                    f"📅 {item['date']}"
                )

                st.caption(
                    f"Report ID: {item['id']}"
                )

                if (
                    item["type"] == "Found"
                    and item["status"] != "Claimed"
                ):

                    if st.button(
                        "📨 Claim This Item",
                        key="claim_search_" + item["id"]
                    ):

                        new_claim = {

                            "claim_id": generate_id(),

                            "item_id": item["id"],

                            "claimant":
                                st.session_state.current_user,

                            "date":
                                datetime.now().strftime(
                                    "%B %d, %Y %I:%M %p"
                                ),

                            "status": "Pending"
                        }

                        st.session_state.claims.append(
                            new_claim
                        )

                        st.success(
                            "Claim request submitted!"
                        )


# ============================================================
# REPORT LOST ITEM
# ============================================================

elif menu == "📌 Report Lost Item":

    st.title(
        "📌 Report a Lost Item"
    )

    st.write(
        "Provide as much accurate information as possible. "
        "The NLP matching system will compare your description "
        "with found item reports."
    )

    with st.form(
        "lost_item_form",
        clear_on_submit=True
    ):

        name = st.text_input(
            "Item Name *",
            placeholder="Example: Black Lenovo Laptop"
        )

        category = st.selectbox(
            "Category *",
            [
                "Electronics",
                "Documents",
                "Wallet",
                "Personal Item",
                "Clothing",
                "School Supplies",
                "Keys",
                "Others"
            ]
        )

        description = st.text_area(
            "Detailed Description *",
            placeholder=(
                "Describe the item, color, brand, "
                "identifying marks, and other details."
            ),
            height=150
        )

        location = st.selectbox(
            "Where did you lose it? *",
            [
                "Main Building",
                "University Library",
                "Student Center",
                "Cafeteria",
                "Gymnasium",
                "Laboratory",
                "Parking Area",
                "Other"
            ]
        )

        date = st.date_input(
            "Date Lost"
        )

        contact = st.text_input(
            "University Email *",
            value=st.session_state.current_email
        )

        image = st.file_uploader(
            "Upload an Image",
            type=[
                "jpg",
                "jpeg",
                "png"
            ]
        )

        submit = st.form_submit_button(
            "📌 Submit Lost Item",
            use_container_width=True
        )

    if submit:

        if not name:

            st.error(
                "Please enter the item name."
            )

        elif not description:

            st.error(
                "Please provide a detailed description."
            )

        elif not contact:

            st.error(
                "Please provide your university email."
            )

        else:

            new_item = {

                "id": generate_id(),

                "type": "Lost",

                "name": name,

                "category": category,

                "description": description,

                "location": location,

                "date":
                    date.strftime(
                        "%B %d, %Y"
                    ),

                "owner":
                    st.session_state.current_user,

                "contact": contact,

                "status": "Pending",

                "image": image,

                "claimed_by": None
            }

            st.session_state.items.append(
                new_item
            )

            st.success(
                "✅ Lost item report submitted successfully!"
            )

            st.write(
                f"Your Report ID is **{new_item['id']}**"
            )

            st.divider()

            # NLP MATCHING

            st.write(
                "🤖 **Running NLP semantic matching...**"
            )

            with st.spinner(
                "Analyzing item description..."
            ):

                matches = find_semantic_matches(
                    new_item
                )

            show_match_results(
                matches
            )


# ============================================================
# REPORT FOUND ITEM
# ============================================================

elif menu == "📦 Report Found Item":

    st.title(
        "📦 Report a Found Item"
    )

    st.write(
        "Found an item on campus? Report it so the "
        "possible owner can be identified."
    )

    with st.form(
        "found_item_form",
        clear_on_submit=True
    ):

        name = st.text_input(
            "Item Name *",
            placeholder="Example: Black Laptop"
        )

        category = st.selectbox(
            "Category *",
            [
                "Electronics",
                "Documents",
                "Wallet",
                "Personal Item",
                "Clothing",
                "School Supplies",
                "Keys",
                "Others"
            ]
        )

        description = st.text_area(
            "Detailed Description *",
            placeholder=(
                "Describe the item, color, brand, "
                "visible markings, and other details."
            ),
            height=150
        )

        location = st.selectbox(
            "Where was it found? *",
            [
                "Main Building",
                "University Library",
                "Student Center",
                "Cafeteria",
                "Gymnasium",
                "Laboratory",
                "Parking Area",
                "Other"
            ]
        )

        date = st.date_input(
            "Date Found"
        )

        contact = st.text_input(
            "University Email *",
            value=st.session_state.current_email
        )

        image = st.file_uploader(
            "Upload an Image",
            type=[
                "jpg",
                "jpeg",
                "png"
            ]
        )

        submit = st.form_submit_button(
            "📦 Submit Found Item",
            use_container_width=True
        )

    if submit:

        if not name:

            st.error(
                "Please enter the item name."
            )

        elif not description:

            st.error(
                "Please provide a detailed description."
            )

        elif not contact:

            st.error(
                "Please provide your university email."
            )

        else:

            new_item = {

                "id": generate_id(),

                "type": "Found",

                "name": name,

                "category": category,

                "description": description,

                "location": location,

                "date":
                    date.strftime(
                        "%B %d, %Y"
                    ),

                "owner":
                    st.session_state.current_user,

                "contact": contact,

                "status": "Found",

                "image": image,

                "claimed_by": None
            }

            st.session_state.items.append(
                new_item
            )

            st.success(
                "✅ Found item report submitted successfully!"
            )

            st.write(
                f"Your Report ID is **{new_item['id']}**"
            )

            st.divider()

            st.write(
                "🤖 **Running NLP semantic matching...**"
            )

            with st.spinner(
                "Analyzing item description..."
            ):

                matches = find_semantic_matches(
                    new_item
                )

            show_match_results(
                matches
            )


# ============================================================
# ALL REPORTS
# ============================================================

elif menu == "📋 All Reports":

    st.title(
        "📋 All Lost & Found Reports"
    )

    if st.session_state.items:

        report_data = []

        for item in st.session_state.items:

            report_data.append(
                {
                    "Report ID": item["id"],
                    "Type": item["type"],
                    "Item": item["name"],
                    "Category": item["category"],
                    "Location": item["location"],
                    "Date": item["date"],
                    "Status": item["status"]
                }
            )

        df = pd.DataFrame(
            report_data
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No reports available."
        )


# ============================================================
# FIND POSSIBLE MATCHES
# ============================================================

elif menu == "🤖 Find Possible Matches":

    st.title(
        "🤖 NLP-Based Semantic Matching"
    )

    st.write(
        "Select a lost or found report to find "
        "possible matching reports."
    )

    if not st.session_state.items:

        st.warning(
            "No reports available."
        )

    else:

        item_options = {}

        for item in st.session_state.items:

            label = (
                f"{item['id']} | "
                f"{item['type']} | "
                f"{item['name']}"
            )

            item_options[label] = item

        selected_label = st.selectbox(
            "Select a report",
            list(item_options.keys())
        )

        selected_item = item_options[
            selected_label
        ]

        st.divider()

        st.subheader(
            "Selected Report"
        )

        with st.container(border=True):

            st.write(
                f"### {selected_item['name']}"
            )

            st.write(
                selected_item["description"]
            )

            st.caption(
                f"Type: {selected_item['type']} | "
                f"Category: {selected_item['category']} | "
                f"Location: {selected_item['location']}"
            )

        if st.button(
            "🤖 Find Semantic Matches",
            use_container_width=True
        ):

            with st.spinner(
                "Comparing item descriptions using NLP..."
            ):

                matches = find_semantic_matches(
                    selected_item
                )

            show_match_results(
                matches
            )


# ============================================================
# MY CLAIMS
# ============================================================

elif menu == "📨 My Claims":

    st.title(
        "📨 My Claim Requests"
    )

    user_claims = [

        claim

        for claim in st.session_state.claims

        if claim["claimant"]
        == st.session_state.current_user
    ]

    if not user_claims:

        st.info(
            "You have no claim requests."
        )

    for claim in user_claims:

        item = next(
            (
                x
                for x in st.session_state.items

                if x["id"]
                == claim["item_id"]
            ),
            None
        )

        if item:

            with st.container(
                border=True
            ):

                st.subheader(
                    item["name"]
                )

                st.write(
                    f"Claim ID: {claim['claim_id']}"
                )

                st.write(
                    f"Report ID: {item['id']}"
                )

                st.write(
                    f"Claim Date: {claim['date']}"
                )

                if claim["status"] == "Pending":

                    st.warning(
                        "⏳ Claim is pending admin verification."
                    )

                elif claim["status"] == "Approved":

                    st.success(
                        "✅ Claim approved."
                    )

                else:

                    st.error(
                        "❌ Claim rejected."
                    )


# ============================================================
# MY PROFILE
# ============================================================

elif menu == "👤 My Profile":

    st.title(
        "👤 My Profile"
    )

    st.write(
        "Update your university information."
    )

    name = st.text_input(
        "Full Name",
        value=st.session_state.current_user
    )

    email = st.text_input(
        "University Email",
        value=st.session_state.current_email
    )

    student_id = st.text_input(
        "Student ID",
        value="2026-00001"
    )

    course = st.selectbox(
        "Program",
        [
            "BS Information Technology",
            "BS Computer Science",
            "BS Information Systems",
            "Other"
        ]
    )

    year_level = st.selectbox(
        "Year Level",
        [
            "1st Year",
            "2nd Year",
            "3rd Year",
            "4th Year"
        ]
    )

    if st.button(
        "💾 Save Profile",
        use_container_width=True
    ):

        st.session_state.current_user = name

        st.session_state.current_email = email

        st.success(
            "✅ Profile updated successfully."
        )


# ============================================================
# ADMIN DASHBOARD
# ============================================================

elif menu == "🛡️ Admin Dashboard":

    st.title(
        "🛡️ Admin Dashboard"
    )

    st.warning(
        "This is a prototype admin panel. "
        "Authentication should be added before actual deployment."
    )

    # --------------------------------------------------------
    # ADMIN STATISTICS
    # --------------------------------------------------------

    total_reports = len(
        st.session_state.items
    )

    pending_reports = len(
        [
            item
            for item in st.session_state.items
            if item["status"] == "Pending"
        ]
    )

    found_reports = len(
        [
            item
            for item in st.session_state.items
            if item["type"] == "Found"
        ]
    )

    total_claims = len(
        st.session_state.claims
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Total Reports",
            total_reports
        )

    with col2:

        st.metric(
            "Pending",
            pending_reports
        )

    with col3:

        st.metric(
            "Found Items",
            found_reports
        )

    with col4:

        st.metric(
            "Claim Requests",
            total_claims
        )

    st.divider()

    # --------------------------------------------------------
    # MANAGE REPORTS
    # --------------------------------------------------------

    st.subheader(
        "📋 Manage Reports"
    )

    for item in st.session_state.items:

        with st.container(
            border=True
        ):

            col1, col2, col3 = st.columns(
                [4, 2, 1]
            )

            with col1:

                st.write(
                    f"### {item['name']}"
                )

                st.caption(
                    f"{item['id']} | "
                    f"{item['type']} | "
                    f"{item['location']}"
                )

            with col2:

                status_options = [
                    "Pending",
                    "Found",
                    "Matched",
                    "Claimed",
                    "Closed"
                ]

                current_index = status_options.index(
                    item["status"]
                )

                new_status = st.selectbox(
                    "Status",
                    status_options,
                    index=current_index,
                    key="status_" + item["id"]
                )

            with col3:

                if st.button(
                    "Update",
                    key="update_" + item["id"]
                ):

                    item["status"] = new_status

                    st.success(
                        "Updated."
                    )

    st.divider()

    # --------------------------------------------------------
    # CLAIM REQUESTS
    # --------------------------------------------------------

    st.subheader(
        "📨 Claim Requests"
    )

    if not st.session_state.claims:

        st.info(
            "There are no claim requests."
        )

    for claim in st.session_state.claims:

        item = next(
            (
                x
                for x in st.session_state.items

                if x["id"]
                == claim["item_id"]
            ),
            None
        )

        if item:

            with st.container(
                border=True
            ):

                st.write(
                    f"### {item['name']}"
                )

                st.write(
                    f"Claimant: {claim['claimant']}"
                )

                st.write(
                    f"Claim ID: {claim['claim_id']}"
                )

                st.write(
                    f"Claim Status: {claim['status']}"
                )

                if claim["status"] == "Pending":

                    col1, col2 = st.columns(2)

                    with col1:

                        if st.button(
                            "✅ Approve Claim",
                            key="approve_" + claim["claim_id"]
                        ):

                            claim["status"] = "Approved"

                            item["status"] = "Claimed"

                            item["claimed_by"] = (
                                claim["claimant"]
                            )

                            st.success(
                                "Claim approved."
                            )

                    with col2:

                        if st.button(
                            "❌ Reject Claim",
                            key="reject_" + claim["claim_id"]
                        ):

                            claim["status"] = "Rejected"

                            st.warning(
                                "Claim rejected."
                            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    <div class="footer">
        🔎 <b>LostLink</b> — University Lost & Found System
        <br>
        NLP-Based Semantic Matching Prototype
    </div>
    """,
    unsafe_allow_html=True
)
