import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from datetime import date, time, timedelta


"# The baby is born!"

winner=st.empty()

"Enter the information below to update the winner"

date_answer = st.date_input("Date of the birth")
time_answer = st.slider("Time of the birth", min_value=time(0,0), max_value=time(23,59), step=timedelta(minutes=1), format="h:mm a")
with st.container():
    "Weight of the baby"
    lbs = st.number_input("pounds", min_value=0, step=1)
    oz = st.number_input("ounces", min_value=0, max_value=15, step=1)
weight_answer = oz + 16*lbs
length_answer = st.number_input("Length of the baby in inches", min_value=0, step=1)



guesses = (l.split('\t') for l in """
Name	Turned in?	Sex	Weight (lbs)	Length	Date	Time of Day
Nana	10	Male	8 lbs 3 oz	21 in	June 5th	2:36 PM
Papa Smith	10	Female	9 lbs 3 oz	19.5 in	June 19th	4:45 PM
Skjelse	10	Female	6 lbs 7 oz	19.5 in	June 16th	1:11 AM
Gavin	10	Male	8 lbs 4 oz	22.5 in	June 8th	3:30 AM
Chandler	10	Female	8 lbs 4 oz	21 in	June 3rd	8:00 PM
Teikn	10	Female	7 lbs 15 oz	18.5 in	May 30th	3:17 AM
Lysi	10	Male	8 lbs 2 oz	21.5 in	June 3rd	6:24 PM
Garrett	10	Male	8 lbs 7 oz	23 in	June 1st	9:00 PM
G-mama	10	Male	8 lbs 10 oz	21 in	May 30	6:30 PM
Papa McCord	10	Female 	9 lbs 0 oz	22 in	June 3	3:00 AM
Jack	10	Male				
Jessica	10	Female	8 lbs 5 oz	21 inches 	June 7	7:30 AM
Ryan	10	Male	7 lbs 10 oz	20.6 inches	June 1st	2:45 PM
Brooke	10	Female	8 lbs 3 oz	21.5 inches	May 28	9:58 PM
Mallory	10	Female	7 lbs 15 oz	20.75 inches	June 2nd	3:46 AM
Brenden	10	Male	7 lbs 4 oz	20 inches	June 12th	9:37 PM
Matt	10	Female	9 lbs 1 oz	22 in	June 4th	7:46 AM
Oog	10	Male	6 lbs 7 oz	20 in	June 10th	12:00 PM
""".strip().split('\n'))
guesses = {name: tuple(answers) for name, *answers in guesses if name != "Name"}

# Turned in
scores = {name: 10 for name in guesses}

# Twins/triplets
scores['Garrett'] -= .50

# Sex
for name, answers in guesses.items():
    if answers[1] == "Male":
        scores[name] += 10

def rank_score(answer, guesses, category, delta_fun=None):
    if delta_fun is None:
        delta_fun = lambda tru, ges: abs(tru-ges) if ges is not None else float('inf')
    guesses = [(delta_fun(answer, guess), name, guess_str) for name, guess, guess_str in guesses]
    guesses.sort()

    last_delta = 0
    last_score = 20
    for i, (delta, name, guess_str) in enumerate(guesses):
        score = 20 - i
        if delta == last_delta:
            score = last_score
        last_delta = delta
        last_score = score
        scores[name] += score

# Weight
weight_guesses = []
for name, answers in guesses.items():
    weight_str = answers[2]
    oz = None
    if weight_str:
        lbs, _, oz, *rest = weight_str.split()
        oz = int(oz) + 16*int(lbs)
    weight_guesses.append((name, oz, weight_str))

rank_score(weight_answer, weight_guesses, "weight")

# Length
length_guesses = []
for name, answers in guesses.items():
    length_str = answers[3]
    inches = None
    if length_str:
        inches = float(length_str.split()[0])
    length_guesses.append((name, inches, length_str))

rank_score(length_answer, length_guesses, "length")

# Date
for name, answers in guesses.items():
    date_str = answers[4]
    score = 0
    if date_str:
        month, day = date_str.split()
        month = 5 if month == "May" else 6
        day = int(''.join(c for c in day if c.isdigit()))
        guess = date(2024, month, day)
        score = max(0, 20 - abs((date_answer - guess).days))
    scores[name] += score

# Time of day
time_answer = time_answer.hour*60 + time_answer.minute

time_guesses = []
for name, answers in guesses.items():
    time_str = answers[5]
    time_guess = None
    if time_str:
        hm, i = time_str.split()
        hour, minute = map(int, hm.split(':'))
        if hour == 12:
            hour = 0
        if i[0].lower() == 'p':
            hour += 12
        time_guess = hour*60 + minute
    time_guesses.append((name, time_guess, time_str))

def time_dif(tru, ges):
    if ges is None:
        return float('inf')
    dif = min(abs(tru-ges), 24*60 - abs(tru-ges))
    return dif

rank_score(time_answer, time_guesses, "time of day", time_dif)


scores = sorted(((score,name) for name,score in scores.items()), reverse=True)
# for name, answers in guesses.items():
#     print(name)
#     for guess in answers:
#         print("    ", guess)

with winner:
    f'## WINNER: {scores[0][1]}'
