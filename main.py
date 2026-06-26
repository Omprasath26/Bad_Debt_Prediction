
## # Bad Debt Prediction

# Loading the datasets

import pandas as pd
import numpy as np

# loading the datasets:

def load_data():
    print("Loading datasets....")

    data_df = pd.read_excel("Data.xlsm",sheet_name="DataV2")
    additional_df = pd.read_excel("Additional Info.xlsx",sheet_name="Additional info")

    print("Datasets loaded successfully !")

    print(f"\n Data dataset")
    print(data_df.head())

    print(f"\n Additional Dataset")
    print(additional_df.head())
    return data_df, additional_df

# Merging the datasets :

def merge_data(data_df,additional_df):

    print("\nMerging datasets.....")

    merged_df = pd.merge(data_df,additional_df,on="Customer",how="left")
    print("Datasets merged successfully..")
    print("merged datasets shape:",merged_df.shape)

    return merged_df

# Load datasets
data_df, additional_df = load_data()

# Merge datasets
merged_df = merge_data(data_df,additional_df)

# View the merged data's
print("\n Merged datasets preview")
print(merged_df.head())    

def remove_rejected_records(df):

    print("Removing rejected records...")

    df = df[
        df["OUTCOME"] != "Rejected - Policy Decline"
    ]

    print("Rejected records removed successfully!")
    print(df["OUTCOME"].value_counts())

    return df

merged_df = merged_df[
    merged_df["OUTCOME"] != "Rejected - Policy Decline"]

# Removing the duplicates:

def remove_duplicates(merged_df):
    print("Removing the duplicates....")

    merged_df = merged_df.drop_duplicates()
    print("Duplicates removed sucessfully...")
    print(f"Dataset shape : {merged_df.shape}")

    return merged_df
merged_df = remove_duplicates(merged_df)
print("Remaining duplicates :",merged_df.duplicated().sum())

# View the column summary :

def column_summary(df):

    summary_df = pd.DataFrame({
        "Column_Name": df.columns,
        "Data_Type": df.dtypes.values,
        "Null_Count": df.isnull().sum().values,
        "Null_Percentage": round((df.isnull().sum() / len(df)) * 100, 2).values,
        "Unique_Values": df.nunique().values
    })

    summary_df = summary_df.sort_values(
        by="Null_Percentage",
        ascending=False
    )

    return summary_df


# Generate report
summary_df = column_summary(merged_df)

# View report
print(summary_df)

'''
#Save report
summary_df.to_csv(
    "Column_Summary_Report.csv",
    index=False
) '''

# Dropping the unwanted columns :

def drop_unwanted_columns(df):

    columns_to_drop = [
        "Customer",
        "WORST_3M",
        "WORST_1M",
        "WORST_18M",
        "WORST_12M",
        "WORST_24M",
        "MTH_TILL_AGENCY",
        "AGENCY_AMT"
    ]

    print("Dropping unwanted columns...")

    df = df.drop(columns =columns_to_drop,errors="ignore")

    print("Dropping the columns sucessfully..")
    print(f"Current shape : {df.shape}")
    return df

merged_df = drop_unwanted_columns(merged_df)
print(merged_df.columns.tolist())

# Imputing missing values using "Mode" and "Median" :

def impute_missing_values(df):
    print("Imputing the missing values")

    # Numeric columns:
    numerical_cols = df.select_dtypes(include=["int64","float64"]).columns

    for col in numerical_cols:
        df[col] = df[col].fillna(df[col].median())

    # categoriacal columns:
    categorical_cols = df.select_dtypes(include=["object"]).columns

    for col in categorical_cols:
        df[col] = df[col].fillna(df[col].mode()[0])

    print("Missiing values are Imputed successfully..")

    return df
merged_df = impute_missing_values(merged_df)
print(merged_df.isnull().sum().sum())

''''
merged_df.to_csv(
    "cleaned_data.csv",
    index=False
)

print("Cleaned dataset saved successfully.") '''

# Splitting the Target variable :

def split_features_target(df,target_column):

    print("Separating the feature and target variables...")

    x = df.drop(columns=[target_column])
    y= df[target_column]

    print("Features shape :",x.shape)
    print("Target shape :",y.shape)

    return x,y

x,y = split_features_target(merged_df,target_column="OUTCOME")

# EDA

# Target variable analysis :

def analyze_target(y):
    print("Target variable distribution..")
    print("-" * 40)

    print(y.value_counts())

    print("\nPercentage Distribution")
    print(round(y.value_counts(normalize=True) * 100, 2 ))



def analyze_numerical_features(x):
    """
    Analyze numerical columns.
    """

    print("\n" + "=" * 50)
    print("NUMERICAL FEATURE ANALYSIS")
    print("=" * 50)

    numerical_df = x.select_dtypes(
        include=["int64", "float64"]
    )

    print(numerical_df.describe().T)


def analyze_categorical_features(x):
    """
    Analyze categorical columns.
    """

    print("\n" + "=" * 50)
    print("CATEGORICAL FEATURE ANALYSIS")
    print("=" * 50)

    categorical_cols = x.select_dtypes(
        include=["object"]
    ).columns

    for col in categorical_cols:

        print("\n" + "-" * 50)
        print(f"Column : {col}")
        print("-" * 50)

        print(x[col].value_counts())


def target_correlation_analysis(x, y):
    """
    Correlation of numerical features
    with target variable.
    """

    print("\n" + "=" * 50)
    print("TARGET CORRELATION ANALYSIS")
    print("=" * 50)

    temp_df = x.copy()

    temp_df["OUTCOME"] = y

    correlation_df = (
        temp_df.corr(
            numeric_only=True
        )["OUTCOME"]
        .sort_values(
            ascending=False
        )
    )

    print(correlation_df)

    return correlation_df


def run_eda(x, y):
    """
    Execute complete EDA workflow.
    """

    analyze_target(y)

    analyze_numerical_features(x)

    analyze_categorical_features(x)

    correlation_df = target_correlation_analysis(x,y)

    return correlation_df

x, y = split_features_target(
    merged_df,
    target_column="OUTCOME")

y = y.map({
    "Good": 0,
    "Bad": 1})

correlation_df = run_eda(x, y)

# Check Remaining Categorical Columns

categorical_cols = x.select_dtypes(include = ["object"]).columns
print("Categorical Columns.")
print(categorical_cols.to_list())

# Analyze Cardinality
# Checking how many unique values each categorical column contains.

def analyze_categorical_columns(x):

    categorical_cols = x.select_dtypes(include=["object"])

    for col in categorical_cols:
        print("\n" + "=" * 50)
        print(f"Column : {col}")
        print("=" * 50)

        print(
            x[col].value_counts()
        )

        print(
            f"Unique Values : {x[col].nunique()}"
        )

analyze_categorical_columns(x)

#Next Step: Create a Feature Engineering Report

#Don't encode immediately.

#First create a report.


def categorical_feature_report(x):

    categorical_cols = x.select_dtypes(
        include=["object"]
    ).columns

    report = []

    for col in categorical_cols:

        report.append({
            "Column_Name": col,
            "Unique_Values": x[col].nunique(),
            "Most_Frequent_Value": x[col].mode()[0]
        })

    return pd.DataFrame(report)


cat_report = categorical_feature_report(x)

print(cat_report)

#Create an encoding function.

def encode_categorical_features(x):

    print("Encoding categorical features...")

    x_encoded = pd.get_dummies(
        x,
        drop_first=True
    )

    print("Encoding completed.")
    print(f"Shape Before Encoding : {x.shape}")
    print(f"Shape After Encoding  : {x_encoded.shape}")

    return x_encoded

x_encoded = encode_categorical_features(x)

print(
    x_encoded.select_dtypes(
        include=["object","string"]
    ).columns.tolist())

# removing CR 21 features
def identify_cr21_score_features(df):

    print("=" * 60)
    print("Identifying CR21 Score-related Features")
    print("=" * 60)

    keywords = [
        "SCORE_CR21",
        "RISK_SCORE_CR21",
        "NO_SCORE_CR21",
        "SCORECARD_CR21",
        "SCORE_BAND_CR21",
        "SCORE_INDICATOR_CR21"
    ]

    cr21_score_features = [
        col for col in df.columns
        if any(keyword in col for keyword in keywords)
    ]

    print(f"\nTotal Features Found : {len(cr21_score_features)}\n")

    for feature in cr21_score_features:
        print(feature)

    return cr21_score_features

cr21_score_features = identify_cr21_score_features(x_encoded)

def remove_cr21_score_features(df, features):

    print("\nRemoving CR21 Score-related Features...")

    updated_df = df.drop(columns=features)

    print("Removal Completed Successfully.")
    print(f"Old Shape : {df.shape}")
    print(f"New Shape : {updated_df.shape}")

    return updated_df
x_encoded = remove_cr21_score_features(
    x_encoded,
    cr21_score_features)

remaining_features = [
    col for col in x_encoded.columns
    if any(keyword in col for keyword in [
        "SCORE_CR21",
        "RISK_SCORE_CR21",
        "NO_SCORE_CR21",
        "SCORECARD_CR21",
        "SCORE_BAND_CR21",
        "SCORE_INDICATOR_CR21"
    ])
]

print(remaining_features)

# checking dtypes of the columns
print( x_encoded.dtypes.value_counts())

print(x_encoded.head(10))
print("Shape:", x_encoded.shape)

# EDA Visualization :

# Target variable distribution :

import matplotlib.pyplot as plt
import seaborn as sns

plt.figure(figsize=(8,5))

sns.countplot(
    data=merged_df,
    x="OUTCOME"
)

plt.title("Target Variable Distribution")
plt.show()

# Risk score distribution ;

plt.figure(figsize=(10,5))

sns.histplot(
    merged_df["RISK_SCORE"],
    bins=30,
    kde=True
)

plt.title("Risk Score Distribution")
plt.show()

# Risk score VS Outcome :

plt.figure(figsize=(8,5))

sns.boxplot(
    data=merged_df,
    x="OUTCOME",
    y="RISK_SCORE"
)

plt.title("Risk Score vs Outcome")
plt.show()

# Feature Engineering :

# Feature selection :

from sklearn.ensemble import RandomForestClassifier


def create_feature_subsets(x, y):

    print("Training Random Forest for Feature Selection...")

    # Train Random Forest
    rf_selector = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        n_jobs=-1
    )

    rf_selector.fit(x, y)

    print("Feature Selection Model Trained Successfully.")

    # Feature Importance
    feature_importance = pd.DataFrame({
        "Feature": x.columns,
        "Importance": rf_selector.feature_importances_
    })

    feature_importance = feature_importance.sort_values(
        by="Importance",
        ascending=False
    ).reset_index(drop=True)

    # Create Feature Lists
    top_10_features = feature_importance.head(10)["Feature"].tolist()

    top_20_features = feature_importance.head(20)["Feature"].tolist()

    top_30_features = feature_importance.head(30)["Feature"].tolist()

    top_40_features = feature_importance.head(40)["Feature"].tolist()

    top_50_features = feature_importance.head(50)["Feature"].tolist()

    # Create Feature Subsets
    x_top10 = x[top_10_features]

    x_top20 = x[top_20_features]

    x_top30 = x[top_30_features]

    x_top40 = x[top_40_features]

    x_top50 = x[top_50_features]

    return {
        "Feature_Importance": feature_importance,
        "Top10": x_top10,
        "Top20": x_top20,
        "Top30": x_top30,
        "Top40": x_top40,
        "Top50": x_top50
    }


# Run Feature Selection
results = create_feature_subsets(
    x_encoded,
    y
)

# Extract Outputs
feature_importance = results["Feature_Importance"]

x_top10 = results["Top10"]

x_top20 = results["Top20"]

x_top30 = results["Top30"]

x_top40 = results["Top40"]

x_top50 = results["Top50"]


# View Top Features
print("\nTop 20 Important Features")
print(feature_importance.head(20))


# Verify Shapes
print("\nDataset Shapes")

print("Top 10 :", x_top10.shape)

print("Top 20 :", x_top20.shape)

print("Top 30 :", x_top30.shape)

print("Top 40 :", x_top40.shape)

print("Top 50 :", x_top50.shape)


# Mutual Information Feature Selection..


from sklearn.feature_selection import mutual_info_classif


def create_mi_feature_subsets(x, y):

    print("Calculating Mutual Information Scores...")

    # Calculate MI Scores
    mi_scores = mutual_info_classif(
        x,
        y,
        random_state=42
    )

    print("Mutual Information Calculation Completed.")

    # Create Importance DataFrame
    feature_importance = pd.DataFrame({
        "Feature": x.columns,
        "Importance": mi_scores
    })

    feature_importance = feature_importance.sort_values(
        by="Importance",
        ascending=False
    ).reset_index(drop=True)

    # Create Feature Lists
    top_10_features = feature_importance.head(10)["Feature"].tolist()

    top_20_features = feature_importance.head(20)["Feature"].tolist()

    top_30_features = feature_importance.head(30)["Feature"].tolist()

    top_40_features = feature_importance.head(40)["Feature"].tolist()

    top_50_features = feature_importance.head(50)["Feature"].tolist()

    # Create Feature Subsets
    x_top10 = x[top_10_features]

    x_top20 = x[top_20_features]

    x_top30 = x[top_30_features]

    x_top40 = x[top_40_features]

    x_top50 = x[top_50_features]

    return {
        "Feature_Importance": feature_importance,
        "Top10": x_top10,
        "Top20": x_top20,
        "Top30": x_top30,
        "Top40": x_top40,
        "Top50": x_top50
    }


# Run Feature Selection
results_mi = create_mi_feature_subsets(
    x_encoded,
    y
)

# Extract Outputs
mi_feature_importance = results_mi["Feature_Importance"]

x_top10_mi = results_mi["Top10"]

x_top20_mi = results_mi["Top20"]

x_top30_mi = results_mi["Top30"]

x_top40_mi = results_mi["Top40"]

x_top50_mi = results_mi["Top50"]


# View Top Features
print("\nTop 20 Mutual Information Features")
print(mi_feature_importance.head(20))


# Verify Shapes
print("\nDataset Shapes")

print("Top 10 :", x_top10_mi.shape)

print("Top 20 :", x_top20_mi.shape)

print("Top 30 :", x_top30_mi.shape)

print("Top 40 :", x_top40_mi.shape)

print("Top 50 :", x_top50_mi.shape)

#XGBoost Feature Selection

from xgboost import XGBClassifier


def create_xgb_feature_subsets(x, y):

    print("Training XGBoost for Feature Selection...")

    xgb_selector = XGBClassifier(
        n_estimators=100,
        random_state=42,
        n_jobs=-1,
        eval_metric="logloss"
    )

    xgb_selector.fit(x, y)

    print("XGBoost Feature Selection Completed.")

    # Feature Importance
    feature_importance = pd.DataFrame({
        "Feature": x.columns,
        "Importance": xgb_selector.feature_importances_
    })

    feature_importance = feature_importance.sort_values(
        by="Importance",
        ascending=False
    ).reset_index(drop=True)

    # Create Feature Lists
    top_10_features = feature_importance.head(10)["Feature"].tolist()

    top_20_features = feature_importance.head(20)["Feature"].tolist()

    top_30_features = feature_importance.head(30)["Feature"].tolist()

    top_40_features = feature_importance.head(40)["Feature"].tolist()

    top_50_features = feature_importance.head(50)["Feature"].tolist()

    # Create Feature Subsets
    x_top10 = x[top_10_features]

    x_top20 = x[top_20_features]

    x_top30 = x[top_30_features]

    x_top40 = x[top_40_features]

    x_top50 = x[top_50_features]

    return {
        "Feature_Importance": feature_importance,
        "Top10": x_top10,
        "Top20": x_top20,
        "Top30": x_top30,
        "Top40": x_top40,
        "Top50": x_top50
    }


# Run Feature Selection
results_xgb = create_xgb_feature_subsets(
    x_encoded,
    y
)

# Extract Outputs
xgb_feature_importance = results_xgb["Feature_Importance"]

x_top10_xgb = results_xgb["Top10"]

x_top20_xgb = results_xgb["Top20"]

x_top30_xgb = results_xgb["Top30"]

x_top40_xgb = results_xgb["Top40"]

x_top50_xgb = results_xgb["Top50"]

# View Results
print("\nTop 20 XGBoost Features")
print(xgb_feature_importance.head(20))

print("\nDataset Shapes")
print("Top10 :", x_top10_xgb.shape)
print("Top20 :", x_top20_xgb.shape)
print("Top30 :", x_top30_xgb.shape)
print("Top40 :", x_top40_xgb.shape)
print("Top50 :", x_top50_xgb.shape)

# RFE (Recursive Feature Elimination) Feature Selection

from sklearn.feature_selection import RFE
from sklearn.linear_model import LogisticRegression


def create_rfe_feature_subsets(x, y):

    print("Running Recursive Feature Elimination...")

    base_model = LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=42
    )

    selector = RFE(
        estimator=base_model,
        n_features_to_select=50,
        step=5
    )

    selector.fit(x, y)

    print("RFE Completed Successfully.")

    feature_ranking = pd.DataFrame({
        "Feature": x.columns,
        "Rank": selector.ranking_
    })

    feature_ranking = (
        feature_ranking
        .sort_values(
            by="Rank",
            ascending=True
        )
        .reset_index(drop=True)
    )

    # Create Feature Lists
    top_10_features = (
        feature_ranking
        .head(10)["Feature"]
        .tolist()
    )

    top_20_features = (
        feature_ranking
        .head(20)["Feature"]
        .tolist()
    )

    top_30_features = (
        feature_ranking
        .head(30)["Feature"]
        .tolist()
    )

    top_40_features = (
        feature_ranking
        .head(40)["Feature"]
        .tolist()
    )

    top_50_features = (
        feature_ranking
        .head(50)["Feature"]
        .tolist()
    )

    return {
        "Feature_Ranking": feature_ranking,
        "Top10": x[top_10_features],
        "Top20": x[top_20_features],
        "Top30": x[top_30_features],
        "Top40": x[top_40_features],
        "Top50": x[top_50_features]
    }


# Run RFE
results_rfe = create_rfe_feature_subsets(
    x_encoded,
    y
)

# Extract Outputs
rfe_feature_ranking = results_rfe["Feature_Ranking"]

x_top10_rfe = results_rfe["Top10"]

x_top20_rfe = results_rfe["Top20"]

x_top30_rfe = results_rfe["Top30"]

x_top40_rfe = results_rfe["Top40"]

x_top50_rfe = results_rfe["Top50"]

# View Results
print("\nTop 20 RFE Features")
print(rfe_feature_ranking.head(20))

print("\nDataset Shapes")

print("Top10 :", x_top10_rfe.shape)
print("Top20 :", x_top20_rfe.shape)
print("Top30 :", x_top30_rfe.shape)
print("Top40 :", x_top40_rfe.shape)
print("Top50 :", x_top50_rfe.shape)
rfe_feature_ranking.head(20)

#LightGBM Feature Importance.

from lightgbm import LGBMClassifier


def create_lgbm_feature_subsets(x, y):

    print("Training LightGBM for Feature Selection...")

    lgbm_selector = LGBMClassifier(
        n_estimators=100,
        random_state=42,
        n_jobs=-1,
        verbosity=-1
    )

    lgbm_selector.fit(x, y)

    print("LightGBM Feature Selection Completed.")

    # Feature Importance
    feature_importance = pd.DataFrame({
        "Feature": x.columns,
        "Importance": lgbm_selector.feature_importances_
    })

    feature_importance = (
        feature_importance
        .sort_values(
            by="Importance",
            ascending=False
        )
        .reset_index(drop=True)
    )

    # Top Feature Lists
    top_10_features = feature_importance.head(10)["Feature"].tolist()

    top_20_features = feature_importance.head(20)["Feature"].tolist()

    top_30_features = feature_importance.head(30)["Feature"].tolist()

    top_40_features = feature_importance.head(40)["Feature"].tolist()

    top_50_features = feature_importance.head(50)["Feature"].tolist()

    return {
        "Feature_Importance": feature_importance,
        "Top10": x[top_10_features],
        "Top20": x[top_20_features],
        "Top30": x[top_30_features],
        "Top40": x[top_40_features],
        "Top50": x[top_50_features]
    }


# Run Feature Selection
results_lgbm = create_lgbm_feature_subsets(
    x_encoded,
    y
)

# Extract Outputs
lgbm_feature_importance = results_lgbm["Feature_Importance"]

x_top10_lgbm = results_lgbm["Top10"]

x_top20_lgbm = results_lgbm["Top20"]

x_top30_lgbm = results_lgbm["Top30"]

x_top40_lgbm = results_lgbm["Top40"]

x_top50_lgbm = results_lgbm["Top50"]

# View Results
print("\nTop 20 LightGBM Features")
print(lgbm_feature_importance.head(20))

print("\nDataset Shapes")

print("Top10 :", x_top10_lgbm.shape)
print("Top20 :", x_top20_lgbm.shape)
print("Top30 :", x_top30_lgbm.shape)
print("Top40 :", x_top40_lgbm.shape)
print("Top50 :", x_top50_lgbm.shape)

# Highest Importance
feature_importance.head(10)

#Lowest Importance
feature_importance.tail(10)

# Model Evaluvation :

from sklearn.model_selection import train_test_split


def create_train_test_splits(feature_sets, y, test_size=0.2, random_state=42):

    print("=" * 70)
    print("Creating Train-Test Splits")
    print("=" * 70)

    split_datasets = {}

    for dataset_name, X in feature_sets.items():

        print(f"\nProcessing {dataset_name} Dataset...")

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=test_size,
            random_state=random_state,
            stratify=y
        )

        split_datasets[dataset_name] = {
            "X_train": X_train,
            "X_test": X_test,
            "y_train": y_train,
            "y_test": y_test
        }

        print(f"Training Shape : {X_train.shape}")
        print(f"Testing Shape  : {X_test.shape}")

    print("\nTrain-Test Split Completed Successfully.")

    return split_datasets

feature_sets = {

    "Top10": x_top10,

    "Top20": x_top20,

    "Top30": x_top30,

    "Top40": x_top40,

    "Top50": x_top50

}
split_datasets = create_train_test_splits(
    feature_sets,
    y
)
print(split_datasets.keys())

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier

models = {

    "Logistic Regression": LogisticRegression(
        random_state=42,
        max_iter=1000,
        class_weight="balanced"
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        n_jobs=-1
    ),

    "XGBoost": XGBClassifier(
        random_state=42,
        eval_metric="logloss"
    ),

    "LightGBM": LGBMClassifier(
        random_state=42
    ),

    "CatBoost": CatBoostClassifier(
        random_state=42,
        verbose=0
    )

}

results = []

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)

def evaluate_model(model, X_train, X_test, y_train, y_test):

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:,1]

    return {

        "Accuracy": accuracy_score(y_test, y_pred),

        "Precision": precision_score(y_test, y_pred),

        "Recall": recall_score(y_test, y_pred),

        "F1 Score": f1_score(y_test, y_pred),

        "ROC AUC": roc_auc_score(y_test, y_prob)

    }

for dataset_name, dataset in split_datasets.items():

    print("\n" + "="*70)
    print(f"Dataset : {dataset_name}")
    print("="*70)

    X_train = dataset["X_train"]
    X_test = dataset["X_test"]
    y_train = dataset["y_train"]
    y_test = dataset["y_test"]

    for model_name, model in models.items():

        print(f"Training {model_name}...")

        metrics = evaluate_model(
            model,
            X_train,
            X_test,
            y_train,
            y_test
        )

        metrics["Dataset"] = dataset_name
        metrics["Model"] = model_name

        results.append(metrics)

        print("Completed.")

results_df = pd.DataFrame(results)
results_df

results_df = results_df.sort_values(
    by="ROC AUC",
    ascending=False
)

results_df

# Comparing the models which is best :

comparison_table = results_df.copy()

comparison_table = comparison_table[
    [
        "Dataset",
        "Model",
        "Accuracy",
        "Precision",
        "Recall",
        "F1 Score",
        "ROC AUC"
    ]
]

comparison_table

## Find the Best Model for Each Metric
## Highest Accuracy

print("="*60)
print("Best Accuracy")
print("="*60)

display(
    comparison_table.sort_values(
        by="Accuracy",
        ascending=False
    ).head(5)
)

## Highest Precision

print("="*60)
print("Best Precision")
print("="*60)

display(
    comparison_table.sort_values(
        by="Precision",
        ascending=False
    ).head(5)
)

## Highest Recall

print("="*60)
print("Best Recall")
print("="*60)

display(
    comparison_table.sort_values(
        by="Recall",
        ascending=False
    ).head(5)
)

## Highest F1 Score

print("="*60)
print("Best F1 Score")
print("="*60)

display(
    comparison_table.sort_values(
        by="F1 Score",
        ascending=False
    ).head(5)
)

## Highest ROC-AUC

print("="*60)
print("Best ROC-AUC")
print("="*60)

display(
    comparison_table.sort_values(
        by="ROC AUC",
        ascending=False
    ).head(5)
)

# Calculate the class Imbalance ratio :

# Calculate Class Imbalance Ratio

negative_class = (y == 0).sum()
positive_class = (y == 1).sum()

scale_pos_weight = negative_class / positive_class

print(f"Negative Class : {negative_class}")
print(f"Positive Class : {positive_class}")
print(f"Scale Pos Weight : {scale_pos_weight:.2f}")

## Re defining the models again

models = {

    "Logistic Regression": LogisticRegression(
        random_state=42,
        max_iter=1000,
        class_weight="balanced"
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1
    ),

    "XGBoost": XGBClassifier(
        random_state=42,
        eval_metric="logloss",
        scale_pos_weight=scale_pos_weight
    ),

    "LightGBM": LGBMClassifier(
        random_state=42,
        class_weight="balanced"
    ),

    "CatBoost": CatBoostClassifier(
        random_state=42,
        auto_class_weights="Balanced",
        verbose=0
    )

}

## Evaluation Function



def evaluate_model(model, X_train, X_test, y_train, y_test):

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    y_prob = model.predict_proba(X_test)[:, 1]

    accuracy = accuracy_score(y_test, y_pred)

    precision = precision_score(
        y_test,
        y_pred,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        y_pred,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        y_pred,
        zero_division=0
    )

    roc_auc = roc_auc_score(
        y_test,
        y_prob
    )

    return {

        "Accuracy": accuracy,

        "Precision": precision,

        "Recall": recall,

        "F1 Score": f1,

        "ROC AUC": roc_auc

    }

##Initialize Results List

results = []

## Retrain all the models



for dataset_name, dataset in split_datasets.items():

    print("\n" + "="*60)
    print(f"Dataset : {dataset_name}")
    print("="*60)

    X_train = dataset["X_train"]
    X_test = dataset["X_test"]

    y_train = dataset["y_train"]
    y_test = dataset["y_test"]

    for model_name, model in models.items():

        print(f"Training {model_name}...")

        metrics = evaluate_model(
            model,
            X_train,
            X_test,
            y_train,
            y_test
        )

        metrics["Dataset"] = dataset_name
        metrics["Model"] = model_name

        results.append(metrics)

        print("Completed.")

## Re-Create Results DataFrame

results_df = pd.DataFrame(results)

print(results_df.head())

print("\nColumns in Results DataFrame")
print(results_df.columns)


## Sort by ROC-AUC

results_df = results_df.sort_values(
    by="ROC AUC",
    ascending=False
)

results_df.reset_index(drop=True, inplace=True)

results_df

results_df.to_csv("Model_Comparison_Results.csv", index=False)

print("Model comparison results saved successfully.")

# Load the Top50 datastes:

X_train = split_datasets["Top50"]["X_train"]
X_test = split_datasets["Top50"]["X_test"]

y_train = split_datasets["Top50"]["y_train"]
y_test = split_datasets["Top50"]["y_test"]

# Selecting the  Final LightGBM Model

from lightgbm import LGBMClassifier

final_model = LGBMClassifier(
    random_state=42,
    class_weight="balanced")

# Train the Final Model

print("="*60)
print("Training Final LightGBM Model")
print("="*60)

final_model.fit(
    X_train,
    y_train)

print("Final Model Trained Successfully.")

# Save the Model

import joblib

joblib.dump(
    final_model,
    "Best_LightGBM_Model.pkl")

print("Best LightGBM Model Saved Successfully.")

## Verifing the Saved Model

loaded_model = joblib.load(
    "Best_LightGBM_Model.pkl")

print(loaded_model)

# SHAP Analysis:

import shap
import matplotlib.pyplot as plt

explainer = shap.TreeExplainer(final_model)
print("SHAP Explainer Created Successfully.")

# Calculating the SHAP values
shap_values = explainer.shap_values(X_test)
print("SHAP Values Calculated Successfully.")
print(type(shap_values))

plt.figure(figsize=(12, 8))

shap.summary_plot(
    shap_values,
    X_test,
    show=False)

plt.title("SHAP Summary Plot")
plt.tight_layout()
plt.show()

# SHAP Feature Importance :

plt.figure(figsize=(12,8))

shap.summary_plot(
    shap_values,
    X_test,
    plot_type="bar",
    show=False
)

plt.title("SHAP Feature Importance")
plt.tight_layout()
plt.show()

# ROC Curve :

from sklearn.metrics import roc_curve, roc_auc_score
import matplotlib.pyplot as plt

# Predict probabilities
y_prob = final_model.predict_proba(X_test)[:, 1]

# Calculate ROC
fpr, tpr, thresholds = roc_curve(y_test, y_prob)

auc_score = roc_auc_score(y_test, y_prob)

# Plot ROC Curve
plt.figure(figsize=(8,6))

plt.plot(
    fpr,
    tpr,
    label=f"LightGBM (AUC = {auc_score:.4f})",
    linewidth=2
)

plt.plot(
    [0,1],
    [0,1],
    linestyle="--",
    color="red"
)

plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve - LightGBM")
plt.legend(loc="lower right")

plt.grid(True)

plt.show()