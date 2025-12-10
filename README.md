# SportHurt analysis: Project analysis 

This project is designed to analyse the effect an ingury has on a football player during a leauge, it anlaysies the performance drop of the player while he is ingured, and it also analyses the the teams performance when the player is off the feild injured, and what their performance is after the ingury. It also clacluates which ingury has the higest performance drop for both 


### Key fetures

Barchart for team performance drop: using the avrage GD per match befroe and after ingury, and based on ingury the highest goal diffrnece with that ingury will get recorded. 

Intractive line graph: showing a line graph for each player in the leauge for their performance before and after ingury

Heatmap of clubs and inguries per month: analyses the ingury fequrency in diffrent clubs

Scatter plot of every player: alnalyses the avrage performance drop of all players

Leaderboard of Combacks: list of players and how good they came back after ingury

### Live link

[steramlit app](https://sporthurt-analysis-bgjddtw22ev.streamlit.app)

### Scereenshots

avaible in the scereenshot folder


### Delployment instructions for local machine 


1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

2. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```


### Intragration details

this project intracts with steramlit with 

* pandas to manage the databases

* matplotlib for graphs

* seaborn fro advanced graphs

* plotly for intractable graphs on steramlit

