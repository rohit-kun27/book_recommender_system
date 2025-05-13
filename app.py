from flask import Flask, render_template, request
import pickle
import numpy as np


popular_df = pickle.load(open('popular.pkl','rb'))
pt = pickle.load(open('pt.pkl','rb'))
books = pickle.load(open('books.pkl','rb'))
similarity_score = pickle.load(open('similarity_score.pkl','rb'))
demographic_df = pickle.load(open('demographic_df.pkl','rb'))

app = Flask(__name__)

@app.route('/')
def home():
    top_books = popular_df[['book_title','book_author', 'avg_rating']].head(50).values.tolist()
    return render_template('index.html', books=top_books)

@app.route('/collaborative', methods=['GET', 'POST'])
def recommend():
    if request.method == 'POST':
        user_input = request.form.get('user_input')

        if user_input not in pt.index:
            return render_template('collaborative.html', books=[], message="Book not found in dataset.")

        index = np.where(pt.index == user_input)[0][0]
        similar_items = sorted(list(enumerate(similarity_score[index])), key=lambda x: x[1], reverse=True)[1:5]

        data = []
        for i in similar_items:
            item = []
            temp_df = books[books['book_title'] == pt.index[i[0]]]
            item.extend(list(temp_df.drop_duplicates('book_title')['book_title'].values))
            item.extend(list(temp_df.drop_duplicates('book_author')['book_author'].values))
            data.append(item)

        return render_template('collaborative.html', books=data)

    return render_template('collaborative.html', books=[])


@app.route('/demographic', methods=['GET', 'POST'])
def demographic():
    books = []
    if request.method == 'POST':
        try:
            age = int(request.form.get('age'))
            if age < 10 or age > 100:
                books = []
            else:
                age_group = demographic_df[demographic_df['Age'] == age]['age_group'].values
                if len(age_group) == 0:
                    books = []
                else:
                    group = age_group[0]
                    group_df = demographic_df[demographic_df['age_group'] == group]

                    book_stats = group_df.groupby(['isbn', 'book_title']).agg(
                        avgg_rating=('rating', 'mean'),
                        rating_count=('rating', 'count')
                    ).reset_index()

                    popular_books = book_stats[book_stats['rating_count'] >= 10]
                    top_books = popular_books.sort_values('avgg_rating', ascending=False).head(10)
                    top_books['avgg_rating'] = top_books['avgg_rating'].round(1)
                    books = top_books[['book_title', 'avgg_rating']].values.tolist()
        except:
            books = []

    return render_template('demographic.html', books=books)




if __name__ == '__main__':
    app.run(debug=True)
    
