from random import random
from urllib import response
from flask import Flask, request, redirect, render_template, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import Bookmark, Review, db, connect_db, User, Manga, Genre, GenreTag, Favorite
from forms import RegisterUserForm, LoginForm, QueryForm, BookmarkForm, ReviewForm
from sqlalchemy.exc import IntegrityError
import requests
import random
import os


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///mangashelfdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'shh')
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

@app.context_processor
def base():
    queryform=QueryForm()
    return dict(queryform=queryform)

####################################
## Homepage
####################################
@app.route('/', methods=["GET", "POST"])
def homepage():
    """Shows homepage
    if logged in displays a search bar or link to user's reviews
    if not logged in displays a prompt to sign up/login and a search bar
    """
    queryform = QueryForm()
    reviews= (Review.query.order_by(Review.id.desc()).limit(5).all())

    if "username" in session:
        username=session["username"]
        user = User.query.filter(User.username == f"{username}").first()
        

        
        if queryform.validate_on_submit():
            query = queryform.query.data

            return redirect(f"/queryresults?query={query}&page=1")

        else:
            return render_template("home.html", user=user,reviews=reviews)

    else:
            return render_template("anon-home.html",reviews=reviews)

################################
# User Routes
################################

@app.route("/register", methods=["GET", "POST"])
def register():
    """provides a form for a user to register and handles its submission"""
    if "username" in session:
        flash("User already logged in","danger")
        return redirect(f"/users/{session['username']}")

    form = RegisterUserForm()
    queryform = QueryForm()
    

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.register(username, password)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username already in use')
            return render_template("users/register_user.html", form=form)

        session["username"] = user.username
        flash("User registered","success")
        return redirect(f"/")
    else:
        return render_template("users/register_user.html", form=form)


@app.route("/users/<username>")
def user_details(username):
    """Example hidden page for logged-in users only."""
    queryform = QueryForm()
    list_of_favorites=[]
    list_of_genres=[]
    query="""query ($genre_in: String, $page: Int) {
    Page(page: $page, perPage: 10) {
    pageInfo {
      currentPage
      hasNextPage
    }
    media(search: $genre_in, type: MANGA, isAdult:false,sort:SCORE_DESC) {
      title {
        english
        native
        romaji
      }
      id
      genres
      coverImage {
        large
      }
    }
    }
    }"""
    
    url = 'https://graphql.anilist.co'
    if "username" not in session:
        flash("You must be logged in to view a profile","danger")
        return redirect("/login")
    if username != session['username']:
        flash("You can only view your own profile","danger")
        return redirect("/")
    user = User.query.filter(User.username == f"{username}").first()
    
    if user.favorites:
        for favorite in user.favorites:
            list_of_favorites.append(favorite.manga.id)
        random_favorite=Manga.query.get(random.choice(list_of_favorites))
        for genre in random_favorite.genres:
            list_of_genres.append(genre.genre)
        random_genre=random.choice(list_of_genres)

    else:
        random_favorite=None
        random_genre=None
    
    variables={
        'genre_in':random_genre,
        'page':1}
    try:
        jsonresponse = requests.post(url, json={'query': query, 'variables': variables})
    except requests.exceptions.RequestException as e:
        flash("Unable to connect to database","danger") 
        return redirect("/")
    response = jsonresponse.json()
    return render_template("users/user_details.html", user=user,random_favorite=random_favorite,random_genre=random_genre, response=response, queryform=queryform)

@app.route("/users/<username>/delete", methods=["POST"])
def delete_user(username):
    if "username" not in session:
        flash("Please login to delete your account","danger") 
        redirect("/login")                         
    if username != session['username']:
        flash("Access Unauthorized","danger") 
        redirect("/")      

    user = User.query.filter(User.username == f"{username}").first()
    db.session.delete(user)
    db.session.commit()
    session.pop("username")
    flash("Account Deleted","success")
    return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    """provides a form for a user to log in and handles its submission"""
    form = LoginForm()
    queryform = QueryForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            session["username"] = user.username
            flash("Login Successful","success")
            return redirect(f"/users/{session['username']}")
        else:
            form.username.errors = ["Invalid Username or Password"]

    return render_template("users/login_user.html", form=form, queryform=queryform)

@app.route("/logout")
def logout():
    """Logs user out and redirects to homepage."""

    session.pop("username")
    flash("Logout Successful","success")
    return redirect("/")

##########
#Manga routes
##########
@app.route("/query", methods=["POST"])
def query():
    """test route for querying"""

    queryform = QueryForm() 
    if queryform.validate_on_submit():
        query = queryform.query.data


        return redirect(f"/queryresults?query={query}&page=1")


@app.route("/queryresults", methods=["GET", "POST"])
def queryresults():
    queryform = QueryForm()
    querytext= request.args.get('query')
    page= request.args.get('page')
    query="""query($title:String, $page:Int){
        Page(page:$page, perPage:10){
            pageInfo{
                currentPage,
                hasNextPage}
                media(search:$title,type:MANGA,isAdult:false){
                    title{
                        english
                        native
                        romaji}
                    id
                    coverImage{
                        large} 
                }

            } 
        }"""
    variables={
        'title':querytext,
        'page':page}
    url = 'https://graphql.anilist.co'
    try:
        jsonresponse = requests.post(url, json={'query': query, 'variables': variables})
    except requests.exceptions.RequestException as e:
        flash("Unable to connect to database","danger") 
        return redirect("/")
    response = jsonresponse.json()
    return render_template("manga/queryresults.html",response=response, querytext=querytext, queryform=queryform)

@app.route("/manga/<int:manga_id>", methods=["GET","POST"])
def manga(manga_id):
    #if "username" in session:
    #   username=session["username"]
    #   user = User.query.filter(User.username == f"{username}").first()
    #   existing_bookmark=Bookmark.query.get((user.id,manga_id))
    #   if existing_bookmark:
    #       bookmark_form=BookmarkForm(obj=existing_bookmark)
    #   else:
    #       bookmark_form=BookmarkForm()
    #else:
    #        bookmark_form=BookmarkForm()
    manga=Manga.query.get(manga_id)
    query="""query($id:Int){
        Media(id:$id,type:MANGA){
            title{
                english
                native}
            id
            bannerImage
            coverImage{
                extraLarge
                large
                medium}
            chapters
            volumes
            status
            description(asHtml: true)
            genres
            staff(sort:[ROLE]) {
                    edges {
                        node{
                            name {
                                full
                                native
                                }
                            }
                                 id
                                role
                            }
                        }
                    }
                }"""
    variables={'id':manga_id}
    url = 'https://graphql.anilist.co'
    try:
        jsonresponse = requests.post(url, json={'query': query, 'variables': variables})
    except requests.exceptions.RequestException as e:
        flash("Unable to connect to database","danger") 
        return redirect("/")
    response = jsonresponse.json()
    
    if Manga.query.get(manga_id) == None:
        id= manga_id
        native_title=response["data"]["Media"]["title"]["native"]
        english_title=response["data"]["Media"]["title"]["english"]
        large_image=response["data"]["Media"]["coverImage"]["large"]
        medium_image=response["data"]["Media"]["coverImage"]["medium"]
        manga=Manga(
            id=id, 
            native_title= native_title, 
            english_title=english_title,
            large_image=large_image,
            medium_image=medium_image)
        db.session.add(manga)
        db.session.commit()
       
        for genre_data in response["data"]["Media"]["genres"]:
            if Genre.query.get(genre_data)==None:
                genre=Genre(
                genre=genre_data
            )
                db.session.add(genre)
                db.session.commit()

        for genre_data in response["data"]["Media"]["genres"]:
            if GenreTag.query.get((genre_data,manga_id))==None:
                genretag=GenreTag(
                    genre_name=genre_data,
                    manga_id=manga_id
                    )
                db.session.add(genretag)
                db.session.commit()
            
    else:
        manga=Manga.query.get(manga_id)
    
    if "username" not in session:
        return render_template("manga/manga.html",response=response, manga=manga)
    
    username=session["username"]
    user = User.query.filter(User.username == f"{username}").first()
    bookmark_form=BookmarkForm()
    existing_bookmark=Bookmark.query.get((user.id,manga_id))
    if existing_bookmark:
           bookmark_form=BookmarkForm(obj=existing_bookmark)
    else:
           bookmark_form=BookmarkForm()
    
    if existing_bookmark:
        if bookmark_form.validate_on_submit():
            existing_bookmark.chapter = bookmark_form.chapter.data
            existing_bookmark.status= bookmark_form.status.data
            db.session.commit()
            flash(f"Bookmark Updated","success")
            return redirect(f"/manga/{manga_id}")
    
    if bookmark_form.validate_on_submit():
        chapter = bookmark_form.chapter.data
        status= bookmark_form.status.data

        bookmark= Bookmark(
            user_id=user.id,
            manga_id=manga_id,
            chapter=chapter,
            status= status,
        )
        db.session.add(bookmark)
        db.session.commit()
        flash(f"Bookmark Created","success")
        return redirect(f"/manga/{manga_id}")

    return render_template("manga/manga.html",response=response, form=bookmark_form,manga=manga)

#######
## Opinions
########

@app.route("/manga/<manga_id>/review", methods=["GET","POST"])
def review_manga(manga_id):
    if "username" not in session:
        flash(f"Please login to leave reviews","danger")
        return redirect("/login")
    manga=Manga.query.get(manga_id)
    form=ReviewForm()
    username=session["username"]
    user = User.query.filter(User.username == f"{username}").first()
    existing_review= Review.query.filter(Review.user_id == f"{user.id}",
                                         Review.manga_id == f"{manga_id}").first()

    if existing_review != None:
        flash("Existing review detected, please edit it instead","info")
        return redirect(f"/manga/{manga_id}/review/update")

    if form.validate_on_submit():
        title=form.title.data
        content=form.content.data
        rating=form.rating.data

        review= Review(
            user_id=user.id,
            manga_id=manga.id,
            title=title,
            content= content,
            rating=rating
        )
        db.session.add(review)
        db.session.commit()
        flash("Review added","success")
        return redirect(f"/manga/{manga_id}")
    else:
        return render_template("manga/review.html",manga=manga, form=form)

@app.route("/manga/<manga_id>/review/update", methods=["GET","POST"])
def update_review(manga_id):
    if "username" not in session:
        flash(f"Please login to edit reviews","danger")
        return redirect("/login")
    manga=Manga.query.get(manga_id)
    username=session["username"]
    user = User.query.filter(User.username == f"{username}").first()
    existing_review= Review.query.filter(Review.user_id == f"{user.id}",
                                         Review.manga_id == f"{manga_id}").first()

    form=ReviewForm(obj=existing_review)

    if existing_review==None:
        flash("No review detected, please create a review first","danger")
        return redirect(f"/manga/{manga_id}/review")

    if form.validate_on_submit():
        existing_review. title=form.title.data
        existing_review.content=form.content.data
        existing_review.rating=form.rating.data

        db.session.commit()
        flash(f"Review updated","success")
        return redirect(f"/manga/{manga_id}")
    else:
        return render_template("manga/review.html",manga=manga, form=form)

@app.route("/manga/<manga_id>/review/delete", methods=["POST"])
def delete_review(manga_id):
    if "username" not in session:
        flash(f"Please login to delete reviews","danger")
        return redirect("/login")
    username=session["username"]
    user = User.query.filter(User.username == f"{username}").first()
    existing_review= Review.query.filter(Review.user_id == f"{user.id}",
                                         Review.manga_id == f"{manga_id}").first()

    if existing_review==None:
        flash("No review to delete","danger")
        return redirect(f"/manga/{manga_id}")

    db.session.delete(existing_review)
    db.session.commit()
    
    flash(f"Review deleted","success")
    return redirect(f"/manga/{manga_id}")

@app.route("/manga/<manga_id>/bookmark/delete", methods=["POST"])
def delete_bookmark(manga_id):
    if "username" not in session:
        flash(f"Please login to delete bookmarks","danger")
        return redirect("/login")
    username=session["username"]
    user = User.query.filter(User.username == f"{username}").first()
    bookmark= Bookmark.query.get((user.id,manga_id))

    if bookmark==None:
        flash("No bookmark to delete","danger")
        return redirect(f"/manga/{manga_id}")

    db.session.delete(bookmark)
    db.session.commit()
    
    flash(f"Bookmark deleted","success")
    return redirect(f"/")

@app.route('/manga/<int:manga_id>/favorite',  methods=["GET","POST"])
def handle_favorite(manga_id):
    """toggles the favorite status."""
    if "username" not in session:
        flash(f"Please login to edit favorites","danger")
        return redirect("/login")
    username=session["username"]
    user = User.query.filter(User.username == f"{username}").first()
    existing_favorite=Favorite.query.get((user.id,manga_id))

    favorited_manga = Manga.query.get(manga_id)

    if existing_favorite:
        db.session.delete(existing_favorite)
        db.session.commit()
        flash("Favorite removed","success")
        return redirect(f"/manga/{manga_id}")
    
    else:
        favorite = Favorite(user_id=user.id,manga_id=favorited_manga.id)
        db.session.add(favorite)
        db.session.commit()
        flash("Favorite added","success")
        return redirect(f"/manga/{manga_id}")
    
@app.route('/manga/<int:manga_id>/bookmark', methods=["GET","POST"])
def handle_bookmark(manga_id):
    if "username" not in session:
        flash(f"Please login to leave bookmarks","danger")
        return redirect("/login")
    username=session["username"]
    user = User.query.filter(User.username == f"{username}").first()
    bookmark_form=BookmarkForm()
    existing_bookmark=Bookmark.query.get((user.id,manga_id))
    
    if existing_bookmark:
        if bookmark_form.validate_on_submit():
            existing_bookmark.chapter = bookmark_form.chapter.data
            existing_bookmark.status= bookmark_form.status.data
            db.session.commit()
            flash(f"Bookmark Updated","success")
            return redirect(f"/manga/{manga_id}")
    
    if bookmark_form.validate_on_submit():
        chapter = bookmark_form.chapter.data
        status= bookmark_form.status.data

        bookmark= Bookmark(
            user_id=user.id,
            manga_id=manga_id,
            chapter=chapter,
            status= status,
        )
        db.session.add(bookmark)
        db.session.commit()
        flash(f"Bookmark Created","success")
        return redirect(f"/manga/{manga_id}")

