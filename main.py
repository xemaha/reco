import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import streamlit as st

# Beispiel-Bewertungsdatenbank (fiktive Nutzerdaten)
data = {
    'User': ['User1', 'User2', 'User3'],
    'Book1': [5, 4, np.nan],
    'Book2': [3, np.nan, 4],
    'Book3': [np.nan, 2, 5],
    'Book4': [4, 5, np.nan],
    'Book5': [np.nan, 3, 4],
    'Book6': [2, np.nan, 3]
}
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(data).set_index('User')

# Beispiel-Benutzerdatenbank (fiktive Nutzerdaten)
users = {
    'xenia': 'OMDI'
}

def recommend_books(user_ratings, df, top_n=3):
    df_copy = df.copy()
    if len(user_ratings) < len(df.columns):
        user_ratings.extend([np.nan] * (len(df.columns) - len(user_ratings)))
    df_copy.loc['NewUser'] = user_ratings
    filled_df = df_copy.fillna(0)
    similarity_matrix = cosine_similarity(filled_df)
    user_similarities = pd.Series(similarity_matrix[-1, :-1], index=filled_df.index[:-1])
    user_similarities = user_similarities.sort_values(ascending=False)
    similar_users = user_similarities.head(3).index
    recommended_books = filled_df.loc[similar_users].mean().sort_values(ascending=False)
    for book, rating in enumerate(user_ratings):
        if not np.isnan(rating):
            recommended_books = recommended_books.drop(filled_df.columns[book], errors='ignore')
    return recommended_books.head(top_n)

def main():
    df = st.session_state.df

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.title("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username in users and users[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Login successful")
            else:
                st.error("Invalid username or password")
    else:
        st.title("RECO")

        st.sidebar.subheader("Navigation")
        if st.sidebar.button("Bewertungen eingeben"):
            st.session_state.page = "Bewertungen eingeben"
        if st.sidebar.button("Empfehlungen anzeigen"):
            st.session_state.page = "Empfehlungen anzeigen"
        if st.sidebar.button("Datenbank anzeigen"):
            st.session_state.page = "Datenbank anzeigen"
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.page = "Login"

        page = st.session_state.get('page', "Bewertungen eingeben")

        if page == "Bewertungen eingeben":
            st.subheader("Gib deine Bewertungen ein")
            user_name = st.session_state.username

            book_title = st.text_input("Buchtitel eingeben:")

            # Custom star rating component
            rating = st.radio("Bewertung (1-5 Sterne):", [1, 2, 3, 4, 5], index=0, format_func=lambda x: '★' * x)

            if st.button("Bewertung speichern"):
                if book_title not in df.columns:
                    df[book_title] = np.nan
                if user_name not in df.index:
                    df.loc[user_name] = [np.nan] * len(df.columns)
                df.at[user_name, book_title] = rating
                st.session_state.df = df
                st.success("Bewertung wurde hinzugefügt!")
                st.write("Aktuelle Datenbank:")
                st.dataframe(df)

        elif page == "Empfehlungen anzeigen":
            st.subheader("Empfohlene Bücher anzeigen")
            user_name = st.session_state.username

            if user_name in df.index:
                user_ratings = df.loc[user_name].tolist()
                recommendations = recommend_books(user_ratings, df)
                st.write("Empfohlene Bücher:")
                st.table(recommendations)
            else:
                st.warning("Nutzer nicht gefunden. Bitte erst Bewertungen eingeben.")

        elif page == "Datenbank anzeigen":
            st.subheader("Aktuelle Datenbank")
            book_search = st.text_input("Suche nach einem Buch:")

            if book_search:
                if book_search in df.columns:
                    st.write(f"Bewertungen für {book_search}:")
                    book_ratings = df[book_search].dropna()
                    st.table(book_ratings)
                    avg_rating = book_ratings.mean()
                    st.write(f"Durchschnittliche Bewertung: {avg_rating:.2f}")
                else:
                    st.warning("Buch nicht gefunden.")
            else:
                st.dataframe(df)

if __name__ == "__main__":
    main()