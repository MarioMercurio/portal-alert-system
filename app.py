import streamlit as st
from tweet_parser import extract_player_name
from superfile_loader import load_superfile, find_player

st.set_page_config(page_title="Portal Alert System", page_icon="🚨")

st.title("Portal Alert System")

tweet_text = st.text_area(
    "Paste a sample portal tweet",
    "A.J. Storr has entered the transfer portal, source tells @GoodmanHoops."
)

if st.button("Test Tweet Parser"):
    
    player_name = extract_player_name(tweet_text)

    if player_name is None:
        st.write("Detected player: None")
    else:
        st.write("Detected player:", player_name)

        df = load_superfile()

        if df is None:
            st.error("SuperFile not loaded")
        else:
            player = find_player(player_name, df)

            if player is None:
                st.warning("Player not found in SuperFile")
            else:
                st.success("Player found!")

                st.write("Player:", player["Player"])
                st.write("School:", player["School"])
                st.write("HDI:", round(player["HDI"]))
