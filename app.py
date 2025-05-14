import streamlit as st
import pickle
import pandas as pd
import numpy as np

# Load pickled files
popular_df = pickle.load(open('popular.pkl', 'rb'))
pt = pickle.load(open('pt.pkl', 'rb'))
books = pickle.load(open('books.pkl', 'rb'))
similarity_score = pickle.load(open('similarity_score.pkl', 'rb'))
demographic_df = pickle.load(open('demographic_df.pkl', 'rb'))


popular_df['avg_rating'] = popular_df['avg_rating'].round(2)

# App title
st.title("📖 Book Recommender System")

# Sidebar navigation
option = st.sidebar.radio("Choose Recommender Type", 
    ["📚 Popular Books", "🤝 Collaborative Filtering", "👤 Demographic-Based"]
)

# 1. Popular Books
if option == "📚 Popular Books":
    st.header("Top 50 Popular Books")
    st.dataframe(popular_df[['book_title', 'book_author', 'avg_rating']].head(50))

# 2. Collaborative Filtering
elif option == "🤝 Collaborative Filtering":
    st.header("Book Recommendation by Book Name")

    book_name = st.text_input("Enter a book title")

    if st.button("Recommend"):
        if book_name in pt.index:
            index = np.where(pt.index == book_name)[0][0]
            similar_items = sorted(
                list(enumerate(similarity_score[index])),
                key=lambda x: x[1],
                reverse=True
            )[1:6]

            data = []
            for i in similar_items:
                temp_df = books[books['book_title'] == pt.index[i[0]]]
                title = temp_df.drop_duplicates('book_title')['book_title'].values[0]
                author = temp_df.drop_duplicates('book_author')['book_author'].values[0]
                data.append([title, author])

            st.subheader("Recommended Books")
            st.dataframe(pd.DataFrame(data, columns=['Book Title', 'Author']))
        else:
            st.error("Book not found in dataset.")

# 3. Demographic-Based
elif option == "👤 Demographic-Based":
    st.header("Book Recommendation by Age")

    age = st.number_input("Enter your age (10-100)", min_value=10, max_value=100, step=1)

    if st.button("Get Recommendations"):
        age_group = demographic_df[demographic_df['Age'] == age]['age_group'].values
        if len(age_group) == 0:
            st.warning("No users found in this age group.")
        else:
            group = age_group[0]
            group_df = demographic_df[demographic_df['age_group'] == group]

            book_stats = group_df.groupby(['isbn', 'book_title']).agg(
                avgg_rating=('rating', 'mean'),
                rating_count=('rating', 'count')
            ).reset_index()

            popular_books = book_stats[book_stats['rating_count'] >= 10]
            top_books = popular_books.sort_values('avgg_rating', ascending=False).head(10)
            top_books['avgg_rating'] = top_books['avgg_rating'].round(2)

            st.subheader(f"Top Books for Age Group: {group}")
            st.dataframe(top_books[['book_title', 'avgg_rating']])
