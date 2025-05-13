import streamlit as st
import pickle
import numpy as np
import pandas as pd

# Load your pickle files
popular_df = pickle.load(open('popular.pkl','rb'))
pt = pickle.load(open('pt.pkl','rb'))
books = pickle.load(open('books.pkl','rb'))
similarity_score = pickle.load(open('similarity_score.pkl','rb'))
demographic_df = pickle.load(open('demographic_df.pkl','rb'))

popular_df['avg_rating'] = popular_df['avg_rating'].round(2)

st.title("📚 Book Recommender System")

# Sidebar navigation
option = st.sidebar.radio("Choose Recommender", ["Top Books", "Collaborative", "Demographic"])

# Top 50 books
if option == "Top Books":
    st.header("🔥 Top 50 Popular Books")
    st.table(popular_df[['book_title','book_author','avg_rating']].head(50))

# Collaborative Filtering
elif option == "Collaborative":
    st.header("🤝 Collaborative Filtering")
    book_name = st.text_input("Enter a Book Name")

    if st.button("Recommend"):
        try:
            index = np.where(pt.index == book_name)[0][0]
            similar_items = sorted(list(enumerate(similarity_score[index])), key=lambda x: x[1], reverse=True)[1:6]

            for i in similar_items:
                temp_df = books[books['book_title'] == pt.index[i[0]]]
                st.write(f"**{temp_df['book_title'].values[0]}** by *{temp_df['book_author'].values[0]}*")
        except:
            st.warning("Book not found. Please enter an exact name.")

# Demographic Filtering
elif option == "Demographic":
    st.header("👤 Demographic Based Recommendations")
    age = st.slider("Select Age", 10, 100, 25)

    age_group = demographic_df[demographic_df['Age'] == age]['age_group'].values
    if len(age_group) > 0:
        group = age_group[0]
        group_df = demographic_df[demographic_df['age_group'] == group]

        book_stats = group_df.groupby(['isbn', 'book_title']).agg(
            avgg_rating=('rating', 'mean'),
            rating_count=('rating', 'count')
        ).reset_index()

        popular_books = book_stats[book_stats['rating_count'] >= 10]
        top_books = popular_books.sort_values('avgg_rating', ascending=False).head(10)
        
        
        top_books['avgg_rating'] = top_books['avgg_rating'].round(2)
        
        st.write("Top Books for your age group:")
        st.table(top_books[['book_title', 'avgg_rating']])
    else:
        st.warning("No data for this age.")
