# medicare-diabetes-prediction
# Diabetes Prediction API using FastAPI & Machine Learning

## Overview

This project is a Machine Learning powered REST API built using FastAPI that predicts whether a person is diabetic or non-diabetic based on medical attributes.

The API uses a trained Support Vector Machine (SVM) model and accepts patient health data as input.

---

## Features

* FastAPI REST API
* Machine Learning Model Integration
* Input Validation using Pydantic
* Interactive Swagger Documentation
* JSON Request/Response Support
* Diabetes Prediction
* Health Recommendations
* Deployment Ready

---

## Technology Stack

* Python
* FastAPI
* Scikit-Learn
* NumPy
* Pydantic
* Uvicorn

---

## Project Structure

```text
Diabetes-Prediction/
│
├── diabetes_model.pkl
├── main.py
├── requirements.txt
├── README.md
│
└── dataset/
    └── diabetes.csv
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/your-username/Diabetes-Prediction.git

cd Diabetes-Prediction
```

Create Virtual Environment:

```bash
python -m venv myenv
```

Activate Environment:

Windows:

```bash
myenv\Scripts\activate
```

Linux/Mac:

```bash
source myenv/bin/activate
```

Install Dependencies:

```bash
pip install -r requirements.txt
```

---

## Running the API

```bash
uvicorn main:app --reload
```

Server:

```text
http://127.0.0.1:8000
```

Swagger Documentation:

```text
http://127.0.0.1:8000/docs
```

Redoc Documentation:

```text
http://127.0.0.1:8000/redoc
```

---

## API Endpoint

### Predict Diabetes

Endpoint:

```http
POST /diabetes_prediction
```

Request Body:

```json
{
  "Pregnancies": 5,
  "Glucose": 166,
  "BloodPressure": 72,
  "SkinThickness": 19,
  "Insulin": 175,
  "BMI": 25.8,
  "DiabetesPedigreeFunction": 0.587,
  "Age": 51
}
```

Response Example:

```json
{
  "prediction": "Diabetic",
  "risk_level": "High"
}
```

---

## Input Parameters

| Feature                  | Description                  |
| ------------------------ | ---------------------------- |
| Pregnancies              | Number of pregnancies        |
| Glucose                  | Plasma glucose concentration |
| BloodPressure            | Diastolic blood pressure     |
| SkinThickness            | Triceps skin fold thickness  |
| Insulin                  | 2-Hour serum insulin         |
| BMI                      | Body Mass Index              |
| DiabetesPedigreeFunction | Genetic diabetes likelihood  |
| Age                      | Age of patient               |

---

## Machine Learning Model

Algorithm Used:

* Support Vector Machine (SVM)

Accuracy Achieved:

```text
77.27%
```

---

## Future Improvements

* Database Integration
* User Authentication
* Prediction History
* Docker Support
* Cloud Deployment
* Model Monitoring
* CI/CD Pipeline

---

## Author

Mayank Kumar

B.Tech Student
Machine Learning & FastAPI Developer
