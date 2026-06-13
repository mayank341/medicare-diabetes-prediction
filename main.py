from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import pickle
import numpy as np

app = FastAPI(
    title="Diabetes Prediction API",
    version="1.0.0"
)

# Load Model
try:
    with open("diabetes_model.pkl", "rb") as file:
        diabetic_model = pickle.load(file)
except Exception as e:
    diabetic_model = None
    print(f"Model Loading Error: {e}")


class UserInput(BaseModel):
    Pregnancies: int = Field(..., ge=0, le=20)
    Glucose: int = Field(..., ge=0, le=300)
    BloodPressure: int = Field(..., ge=0, le=200)
    SkinThickness: int = Field(..., ge=0, le=100)
    Insulin: int = Field(..., ge=0, le=1000)
    BMI: float = Field(..., ge=0, le=100)
    DiabetesPedigreeFunction: float = Field(..., ge=0)
    Age: int = Field(..., ge=1, le=120)


@app.get("/")
def home():
    return {"message": "Welcome to Diabetes Prediction API"}


@app.post("/diabetes_prediction")
def diabetes_prediction(data: UserInput):
    if diabetic_model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")

    try:
        features = np.array([[
            data.Pregnancies,
            data.Glucose,
            data.BloodPressure,
            data.SkinThickness,
            data.Insulin,
            data.BMI,
            data.DiabetesPedigreeFunction,
            data.Age
        ]])

        prediction = diabetic_model.predict(features)

        if prediction[0] == 1:
            return {
                "prediction": "Diabetic",
                "risk_level": "High",
                "precautions": [
                    "Consult a doctor",
                    "Monitor blood sugar",
                    "Exercise daily",
                    "Avoid sugary foods"
                ],
                "diet_plan": {
                    "eat": [
                        "Oats",
                        "Brown Rice",
                        "Green Vegetables",
                        "Apple",
                        "Guava",
                        "Almonds"
                    ],
                    "avoid": [
                        "Soft Drinks",
                        "Sweets",
                        "Pastries",
                        "Deep Fried Foods"
                    ]
                }
            }

        return {
            "prediction": "Non-Diabetic",
            "risk_level": "Low",
            "recommendations": [
                "Maintain healthy diet",
                "Exercise regularly",
                "Stay hydrated"
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))