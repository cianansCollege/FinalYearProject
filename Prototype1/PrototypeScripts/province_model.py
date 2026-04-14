from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import pandas as pd

df = pd.read_csv("/Users/cianan/Documents/GitHub/FYP/Prototype1/features/mfcc_features.csv")

X = df[[f"mfcc_{i+1}" for i in range(13)]]
y = df["province"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))
