# ML-TP
## Project Objective
Recommend Diabete Diet for day, including preferences of each user.

### Input
- exercise: 0 ~ 2, 0 for low exercise, 2 for high exercise
- gender: 'Male' or 'Female'
- height: cm
- weight: kg
- like: the food name must be in 'food_unit.csv'
- hate: the food name must be in 'food_unit.csv'

### Output
- needed kcal for a day
- diet recommendation

For detail, please read <code>Diet_Recommendation.ipynb</code>


## Team Member
- 202035509 Kim Yeeun
- 202035510 Kim Jisoo
- 202035518 Noh Hyungju
- 202035519 Ma Sunghee

## Files
- <code>data</code>: data repository
- <code>Diet_Recommendation.ipynb</code>: ipynb file for code example (with sample input)
- <code> Diet_Recommendation.py</code>: python file with input/output

### Data
- data.csv
<br>User data<br>
columns: *exercise, gender, age, height, weight, like food, hate food*

- food_unit.csv
<br>Food unit, volume for planning diet<br>
columns: *품목(food), 용량(g) (volume), 식품군(unit)* <br>
data from Korean Diabetes Association (대한당뇨병학회): https://www.diabetes.or.kr/general/dietary/dietary_03.php?con=3

