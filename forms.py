from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, PasswordField, SelectField, BooleanField
from wtforms.validators import InputRequired, Optional, Email, NumberRange, Length

class RegisterUserForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[InputRequired(), Length(min=1, max=20)],
    )
    password = PasswordField(
        "Password",
        validators=[InputRequired(), Length(min=1, max=20)],
    )

class LoginForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[InputRequired(), Length(min=1, max=20)],
    )
    password = PasswordField(
        "Password",
        validators=[InputRequired(), Length(min=1, max=20)],
    )

class QueryForm(FlaskForm):
    query = StringField(
        render_kw={"placeholder": "Search..."},
        validators=[InputRequired()]
    )

class BookmarkForm(FlaskForm):
    chapter= IntegerField(
        "Last Read Chapter:",
        validators=[InputRequired(), NumberRange(min=0, max=9999)]
    )
    
    status= SelectField(
        "Your reading status:",
        choices=[(""),("Interested"),("In Progress"),("Finished"),("Dropped")]
    )

class ReviewForm(FlaskForm):
    title = StringField(
        "Review Title",
        validators=[InputRequired(), Length(min=1, max=100)],
    )
    content = TextAreaField(
        "Review", render_kw={"rows": 20, "cols": 11},
        validators=[InputRequired()],
    )

    rating= SelectField(
        "Rating:",
        choices=[0,1,2,3,4,5],
        validators=[InputRequired()]
    )