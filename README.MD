1. Mangashelf, located at: https://mangashelf.herokuapp.com/
2. My website allows users to search manga using the Anilist api. A user can then favorite, review and bookmark those manga. Other users read thos reviews. The website will also give reccomendations based on the genres of the user's favorited manga
3. Features: 
Search manga - implmented because it's required for the other features, and its fun to browse manga
bookmark manga- as someone that reads a lot of manga it's always nice to have a record of what you read, how you felt about it, and how far you got in it, especially when they can go on hiatus for months
Favorite manga- it's useful to have a list of your favorites, it was also needed to make reccomendations
Review manga- it's human nature to want to talk about what we read so reviews are a natural feature to add allow users to voice their opinion
Reccomend manga- it's always good to have a source of new things you haven't read and for me reccomendations are the number one way I hear about new manga.
4. The standard user flow is to either sign up or search a manga. After signing up the user can search manga and read their descriptions, other reviews and add the to their favorites. A user can see a list of their favorites and reviews on their profile. Their profile will also give suggestions for new manga based on their favorites.
5. The api is https://anilist.gitbook.io/anilist-apiv2-docs/. It was pretty fun to work with after I understood what was going on with it. The interactive editor was super useful at helping me craft my queries and the docs were relatively easy to understand.
6. I used flask, jinja, sqlalchemy, postgresql, and hosted it on heroku
7. I know I need to go back and write tests, the main reason I hadn't was because the design of the website was changing as I worked on it and I wanted a more finalized version before I started working on tests. I intend to go back and add them now along with any criticisms and suggestions about the application.