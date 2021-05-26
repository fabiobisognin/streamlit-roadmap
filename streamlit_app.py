import streamlit as st
from notion.client import NotionClient

DB_URL = "https://www.notion.so/streamlit/fdd164419a79454f993984b1f8e21f66"

@st.cache(allow_output_mutation=True, ttl=12*60*60)
def get_data(token_v2, db_url):
    client = NotionClient(token_v2=token_v2)
    cv = client.get_collection_view(db_url)
    orig_rows = cv.default_query().execute()

    in_progress_rows = []
    early_stage_rows = []

    for row in orig_rows:
        # Skip things that aren't coming any time soon.

        if not row.stage: continue
        stage = row.stage.lower()

        if "needs triage" in stage: continue
        if "upcoming" in stage: continue
        if not row.schedule: continue

        # Skip things that are done.

        if "done" in stage: continue

        # Sort rows into buckets.

        if (
            "scoping" in stage or
            "speccing" in stage or
            "ready for" in stage
        ):
            early_stage_rows.append(row)

        else:
            in_progress_rows.append(row)

    in_progress_rows.sort(key=lambda r: row.schedule.end)
    early_stage_rows.sort(key=lambda r: row.schedule.start)

    return in_progress_rows, early_stage_rows

in_progress_rows, early_stage_rows = get_data(
    st.secrets["notion"]["token_v2"],
    DB_URL)


def display_project(row):
    end = row.schedule.end
    if end:
        date_out = f"{row.schedule.start}–{row.schedule.end}"
    else:
        date_out = f"{row.schedule.start}–?"

    st.markdown(
        f"{row.icon} {row.name} <small style='color: #aaa'>{date_out}</small>",
        unsafe_allow_html=True
    )

"""
# Streamlit roadmap

### In progress
"""

for row in in_progress_rows:
    display_project(row)

"""
### In early stages
"""

for row in early_stage_rows:
    display_project(row)
