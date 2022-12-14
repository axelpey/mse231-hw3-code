# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
from sklearn import preprocessing
from sklearn.linear_model import LogisticRegression
import urllib.request, json

sns.set_context("notebook", font_scale=1, rc={"lines.linewidth": 2.5})


def assemble_original_and_extra_survey():
    url = "https://raw.githubusercontent.com/fivethirtyeight/data/master/comma-survey/comma-survey.csv"
    df = pd.read_csv(url)

    print(df.info())

    # Add survey results from Step 2 (22 Responses)
    extra_survey = pd.read_csv("new_comma_survey.csv")
    extra_survey = extra_survey.drop(["Timestamp"], axis=1)
    columns = {
        extra_survey.columns[i]: df.columns[i + 1]
        for i in range(len(extra_survey.columns))
    }
    extra_survey = extra_survey.rename(columns=columns)
    df = pd.concat([df, extra_survey])

    return df


# Function to ensure that x labels of plots do not overlap
def replace_every_nth_space(a_list, n):
    return_list = []
    for option in list(a_list):
        split_options = option.split()
        if len(option.split()) > 1:
            if len(option.split()) % n != 0:
                for _ in range(len(option.split()) % n):
                    split_options.append("")
            option = "\n".join(" ".join(s) for s in zip(*[iter(split_options)] * n))
        return_list.append(option)
    return return_list


# Investigate survey questions, answer options, and count of answers
def format_survey_data(df):
    demographic_groups = {}
    answers = {}
    for col in df.columns:
        if col == "RespondentID":
            continue
        values, counts = np.unique(df[col].astype(str, copy=True), return_counts=True)
        print(col)
        print()
        print("Options: ", values)
        print("Counts: ", counts)
        print("Pct: ", counts / sum(counts))
        print()
        print()

        if col in [
            "Gender",
            "Age",
            "Household Income",
            "Education",
            "Location (Census Region)",
        ]:
            demographic_groups[col] = [list(values), list(counts)]
        else:
            answers[col] = [list(values), list(counts)]

    income_order = [
        "$0 - $24,999",
        "$25,000 - $49,999",
        "$50,000 - $99,999",
        "$100,000 - $149,999",
        "$150,000+",
        "nan",
    ]
    age_order = ["18-29", "30-44", "45-60", "> 60", "nan"]
    education_order = [
        "Less than high school degree",
        "High school degree",
        "Some college or Associate degree",
        "Bachelor degree",
        "Graduate degree",
        "nan",
    ]
    demographic_groups["Household Income"] = [
        income_order,
        [
            demographic_groups["Household Income"][1][
                demographic_groups["Household Income"][0].index(income_order[i])
            ]
            for i in range(len(income_order))
        ],
    ]
    demographic_groups["Age"] = [
        age_order,
        [
            demographic_groups["Age"][1][
                demographic_groups["Age"][0].index(age_order[i])
            ]
            for i in range(len(age_order))
        ],
    ]
    demographic_groups["Education"] = [
        education_order,
        [
            demographic_groups["Education"][1][
                demographic_groups["Education"][0].index(education_order[i])
            ]
            for i in range(len(education_order))
        ],
    ]

    care_order = ["Not at all", "Not much", "Some", "A lot", "nan"]
    importance_order = [
        "Very unimportant",
        "Somewhat unimportant",
        "Neither important nor unimportant (neutral)",
        "Somewhat important",
        "Very important",
        "nan",
    ]
    col = "How much, if at all, do you care about the use (or lack thereof) of the serial (or Oxford) comma in grammar?"
    answers[col] = [
        care_order,
        [
            answers[col][1][answers[col][0].index(care_order[i])]
            for i in range(len(care_order))
        ],
    ]
    col = 'How much, if at all, do you care about the debate over the use of the word "data" as a singluar or plural noun?'
    answers[col] = [
        care_order,
        [
            answers[col][1][answers[col][0].index(care_order[i])]
            for i in range(len(care_order))
        ],
    ]
    col = "In your opinion, how important or unimportant is proper use of grammar?"
    answers[col] = [
        importance_order,
        [
            answers[col][1][answers[col][0].index(importance_order[i])]
            for i in range(len(importance_order))
        ],
    ]

    return demographic_groups, answers


def plot_distributions(plot_dict):
    for col, options in plot_dict.items():
        if (
            col
            == "In your opinion, how important or unimportant is proper use of grammar?"
        ):
            adj_options = replace_every_nth_space(options[0], 2)
            plt.figure(figsize=(6, 4))
            plt.bar(adj_options, options[1])
            plt.title(col)
            plt.ylabel("Number of responses")

            print()
            plt.figure(figsize=(14, 10))
            # plt.pie(options[1], labels=adj_options,autopct='%1.1f%%')
            plt.pie(
                [options[1][i] for i in [0, 3, 1, 4, 2, 5]],
                labels=[adj_options[i] for i in [0, 3, 1, 4, 2, 5]],
                autopct="%1.1f%%",
            )
            plt.title(col)

            plt.savefig(f"distribution_{col.replace(' ', '')}")
            plt.close()
            print()


def plot_distributions(plot_dict):
    for col, options in plot_dict.items():
        adj_options = replace_every_nth_space(options[0], 2)
        plt.figure(figsize=(6, 4))
        plt.bar(adj_options, options[1])
        plt.title(col)
        plt.ylabel("Number of responses")

        print()
        plt.figure(figsize=(14, 10))
        plt.pie(options[1], labels=adj_options, autopct="%1.1f%%")
        plt.title(col)

        plt.savefig(f"distribution_{col.replace(' ', '')}")
        plt.close()
        print()


def plot_bivariate(df, col1, col2, col2_keys=None):
    d = {}
    col1_keys = list(df[col1].dropna().unique())
    if col2_keys is None:
        col2_keys = sorted(list(df[col2].dropna().unique()))

    d_sums = [0] * len(col2_keys)

    for col1_key in col1_keys:
        d[col1_key] = []
        for idx, col2_key in enumerate(col2_keys):
            count = len(df[(df[col1] == col1_key) & (df[col2] == col2_key)])
            d[col1_key].append(count)
            d_sums[idx] += count
        if d[col1_key] == []:
            del d[col1_key]

    ind = np.arange(len(col2_keys))
    width = 0.35
    bottoms = [0] * ind

    fig, ax = plt.subplots(figsize=(10, 6))
    for col1_key in d.keys():
        counts = [100 * v / s for v, s in zip(d[col1_key], d_sums)]
        ax.bar(ind, counts, width=width, bottom=bottoms, label=col1_key)
        bottoms = [bottoms[idx] + val for idx, val in enumerate(counts)]
    ax.legend()
    plt.xticks(ticks=ind, labels=list(col2_keys))
    plt.savefig(f"bivariate_{col1.replace(' ', '')}_{col2.replace(' ', '')}")
    plt.close()
    return d


def analyze_assembled_survey(df, demographic_groups, answers):
    sns.set_context("notebook", font_scale=1.5, rc={"lines.linewidth": 2.5})
    plot_distributions(demographic_groups)

    plot_distributions(answers)

    sns.set_context("notebook", font_scale=0.8, rc={"lines.linewidth": 2.5})

    plot_bivariate(
        df,
        "Education",
        "Household Income",
        [
            "$0 - $24,999",
            "$25,000 - $49,999",
            "$50,000 - $99,999",
            "$100,000 - $149,999",
            "$150,000+",
        ],
    )

    plot_bivariate(
        df,
        "In your opinion, how important or unimportant is proper use of grammar?",
        "How much, if at all, do you care about the use (or lack thereof) of the serial (or Oxford) comma in grammar?",
        ["Not at all", "Not much", "Some", "A lot"],
    )

    plot_bivariate(
        df,
        "In your opinion, how important or unimportant is proper use of grammar?",
        "Education",
        [
            "Less than high school degree",
            "High school degree",
            "Bachelor degree",
            "Some college or Associate degree",
            "Graduate degree",
        ],
    )


def preprocess_data(data, test_data=None):
    demographics = [
        "Gender",
        "Age",
        "Household Income",
        "Education",
        "Location (Census Region)",
    ]
    X_demographics = data[demographics]
    enc_gender = preprocessing.OrdinalEncoder()
    X_demographics["Gender"] = enc_gender.fit_transform(
        np.squeeze(X_demographics["Gender"].array).reshape(-1, 1)
    )

    age_str_to_value = {
        "30-44": 37.0,
        "18-29": 23.5,
        "> 60": 70.0,
        "45-60": 52.0,
        np.nan: np.nan,
    }
    X_demographics["Age"] = X_demographics["Age"].apply(lambda s: age_str_to_value[s])

    income_str_to_value = {
        "$50,000 - $99,999": 75000,
        np.nan: np.nan,
        "$25,000 - $49,999": 37500,
        "$0 - $24,999": 12500,
        "$150,000+": 200000,
        "$100,000 - $149,999": 125000,
    }
    X_demographics["Household Income"] = X_demographics["Household Income"].apply(
        lambda s: income_str_to_value[s]
    )

    # Check the order here (of)
    enc_edu = preprocessing.OrdinalEncoder()
    X_demographics["Education"] = enc_edu.fit_transform(
        np.squeeze(X_demographics["Education"].array).reshape(-1, 1)
    )

    enc_loc = preprocessing.OneHotEncoder(sparse=False)
    locations = enc_loc.fit_transform(
        np.squeeze(X_demographics["Location (Census Region)"].array).reshape(-1, 1)
    )
    X_demographics[enc_loc.get_feature_names(["location"])] = locations

    # Now we should have everything in the right type (float)
    # To finish, we standardize everything
    scaler = preprocessing.StandardScaler()
    X_demographics[["Household Income", "Age", "Education"]] = scaler.fit_transform(
        X_demographics[["Household Income", "Age", "Education"]].to_numpy()
    )
    X_demographics = X_demographics.drop(columns=["Location (Census Region)"])

    if test_data is not None:
        X_test = test_data[demographics]
        X_test["Gender"] = enc_gender.transform(
            np.squeeze(X_test["Gender"].array).reshape(-1, 1)
        )
        X_test["Age"] = X_test["Age"].apply(lambda s: age_str_to_value[s])
        X_test["Household Income"] = X_test["Household Income"].apply(
            lambda s: income_str_to_value[s]
        )
        X_test["Education"] = enc_edu.transform(
            np.squeeze(X_test["Education"].array).reshape(-1, 1)
        )
        locations_test = enc_loc.transform(
            np.squeeze(X_test["Location (Census Region)"].array).reshape(-1, 1)
        )
        X_test[enc_loc.get_feature_names(["location"])] = locations_test

        X_test[["Household Income", "Age", "Education"]] = scaler.transform(
            X_test[["Household Income", "Age", "Education"]].to_numpy()
        )
        X_test = X_test.drop(columns=["Location (Census Region)"])
    else:
        X_test = test_data

    return X_demographics, X_test


def make_models(df):
    df_plain = df.dropna()
    X_demographics, _ = preprocess_data(df_plain)

    questions = answers.keys()

    models_for_questions = {}

    for question in questions:
        m = LogisticRegression(multi_class="multinomial")
        y = df_plain[question]
        m.fit(X_demographics, y)

        print("Most import coefficients for question:", question)
        print(list(zip(X_demographics.columns, m.coef_[0])))
        print()
        models_for_questions[question] = m

    return questions, models_for_questions


def get_census_data():
    url = "https://api.census.gov/data/2021/acs/acs1/pums?tabulate=weight(PWGTP)&col+SCHL_RC1&col+HINCP_RC1&col+AGEP_RC1&col+SEX&row+ucgid&ucgid=0300000US1,0300000US2,0300000US3,0300000US4,0300000US5,0300000US6,0300000US7,0300000US8,0300000US9&recode+SCHL_RC1=%7B%22b%22:%22SCHL%22,%22d%22:%5B%5B%220%22,%2201%22,%2202%22,%2203%22,%2204%22,%2205%22,%2206%22,%2207%22,%2208%22,%2209%22,%2210%22,%2211%22,%2212%22,%2213%22,%2214%22,%2215%22%5D,%5B%2216%22,%2217%22%5D,%5B%2218%22,%2219%22,%2220%22%5D,%5B%2221%22%5D,%5B%2222%22,%2223%22,%2224%22%5D%5D%7D&recode+HINCP_RC1=%7B%22b%22:%22HINCP%22,%22d%22:%5B%5B%7B%22mn%22:1,%22mx%22:24999%7D,%220%22%5D,%5B%7B%22mn%22:25000,%22mx%22:49999%7D%5D,%5B%7B%22mn%22:50000,%22mx%22:99999%7D%5D,%5B%7B%22mn%22:100000,%22mx%22:149999%7D%5D,%5B%7B%22mn%22:150000,%22mx%22:9999999%7D%5D%5D%7D&recode+AGEP_RC1=%7B%22b%22:%22AGEP%22,%22d%22:%5B%5B%7B%22mn%22:18,%22mx%22:29%7D%5D,%5B%7B%22mn%22:30,%22mx%22:44%7D%5D,%5B%7B%22mn%22:45,%22mx%22:60%7D%5D,%5B%7B%22mn%22:61,%22mx%22:99%7D%5D%5D%7D"
    with urllib.request.urlopen(url) as url:
        data = json.load(url)
    with open("data.json", "w") as f:
        json.dump(data, f)

    feature_dictionary = {
        "SCHL_RC1": {
            "1": "Less than high school degree",
            "2": "High school degree",
            "3": "Some college or Associate degree",
            "4": "Bachelor degree",
            "5": "Graduate degree",
        },
        "SEX": {"1": "Male", "2": "Female"},
        "HINCP_RC1": {
            "1": "$0 - $24,999",
            "2": "$25,000 - $49,999",
            "3": "$50,000 - $99,999",
            "4": "$100,000 - $149,999",
            "5": "$150,000+",
        },
        "AGEP_RC1": {"1": "18-29", "2": "30-44", "3": "45-60", "4": "> 60"},
    }

    geography_dict = {
        "0300000US1": "New England",
        "0300000US2": "Middle Atlantic",
        "0300000US3": "East North Central",
        "0300000US4": "West North Central",
        "0300000US5": "South Atlantic",
        "0300000US6": "East South Central",
        "0300000US7": "West South Central",
        "0300000US8": "Mountain",
        "0300000US9": "Pacific",
    }

    for idx, datapoint in enumerate(data[0][:-1]):
        data[0][idx]["SCHL_RC1"] = feature_dictionary["SCHL_RC1"][datapoint["SCHL_RC1"]]
        data[0][idx]["SEX"] = feature_dictionary["SEX"][datapoint["SEX"]]
        data[0][idx]["HINCP_RC1"] = feature_dictionary["HINCP_RC1"][
            datapoint["HINCP_RC1"]
        ]
        data[0][idx]["AGEP_RC1"] = feature_dictionary["AGEP_RC1"][datapoint["AGEP_RC1"]]

    with open("data.json", "w") as f:
        json.dump(data, f)

    census_dict = {
        "Gender": [],
        "Age": [],
        "Household Income": [],
        "Education": [],
        "Location (Census Region)": [],
        "Count": [],
    }

    for idx_loc, row in enumerate(data[1:]):
        for idx_other, count in enumerate(row[:-1]):
            feature_dict = data[0][idx_other]
            census_dict["Gender"].append(feature_dict["SEX"])
            census_dict["Age"].append(feature_dict["AGEP_RC1"])
            census_dict["Household Income"].append(feature_dict["HINCP_RC1"])
            census_dict["Education"].append(feature_dict["SCHL_RC1"])
            census_dict["Location (Census Region)"].append(
                geography_dict[data[idx_loc + 1][-1]]
            )
            census_dict["Count"].append(count)

    census_df = pd.DataFrame.from_dict(census_dict)

    print("The census contains data for", census_df.Count.sum(), "people")

    return census_df


def create_pie_plots(df, col):
    col_df = df.groupby([col])["Count"].sum()
    plt.figure(figsize=(14, 8))
    plt.pie(col_df.to_numpy(), labels=list(col_df.index), autopct="%1.1f%%")
    plt.title(col)

    plt.savefig(f"pie_{col.replace(' ', '')}.png")
    plt.close()
    print()


def plot_pie_in_pie(survey_dict, census_dataframe, feature):
    fig, ax = plt.subplots(figsize=(12, 12))
    size = 0.35
    outer = census_dataframe.groupby([feature])["Count"].sum()

    inner = survey_dict[feature][1][:-1]  # Remove Nan
    labels = survey_dict[feature][0][:-1]  # Remove Nan

    outer = [outer[label] for label in labels]

    ax.pie(
        outer,
        radius=1,
        colors=mcolors.TABLEAU_COLORS,
        autopct="%1.1f%%",
        pctdistance=0.8,
        wedgeprops=dict(width=size, edgecolor="w"),
    )

    ax.pie(
        inner,
        radius=1 - size,
        colors=mcolors.TABLEAU_COLORS,
        autopct="%1.1f%%",
        pctdistance=0.7,
        wedgeprops=dict(width=size, edgecolor="w"),
    )

    ax.legend(labels, loc="lower left")

    ax.set(
        aspect="equal",
        title=f"\n{feature}\n Outer chart: Census Data\n Inner chart: Survey Data",
    )

    plt.savefig(f"pie_in_pie_{feature.replace(' ','')}.png")
    plt.close()


def multi_barplot(survey_dict, census_dataframe, feature):
    census = (
        census_dataframe.groupby([feature])["Count"].sum()
        / census_dataframe.Count.sum()
        * 100
    )
    survey = (
        survey_dict[feature][1][:-1] / sum(survey_dict[feature][1][:-1]) * 100
    )  # Remove Nan
    labels = survey_dict[feature][0][:-1]  # Remove Nan
    census = [census[label] for label in labels]
    labels = replace_every_nth_space(labels, 2)

    X_axis = np.arange(len(labels))

    fig, ax = plt.subplots(figsize=(14, 8))
    ax.bar(X_axis - 0.2, census, 0.4, label="Census", color="lightblue")
    ax.bar(X_axis + 0.2, survey, 0.4, label="Survey", color="bisque")
    for p in ax.patches:
        ax.annotate(
            f"{p.get_height():.1f}%",
            (p.get_x() + 0.02, p.get_height() + 0.2),
            textcoords="data",
        )

    plt.xticks(X_axis, labels)
    plt.ylabel("Percent")
    plt.title(feature)
    ax.legend()

    plt.savefig(f"multi_barplot_{feature.replace(' ', '')}")
    plt.close()


def barh(results, category_names, title):
    category_names = replace_every_nth_space(category_names, 3)
    labels = list(results.keys())
    data = np.array(list(results.values())) * 100
    data_cum = data.cumsum(axis=1)

    fig, ax = plt.subplots(figsize=(10, 2))
    ax.invert_yaxis()
    ax.xaxis.set_visible(False)
    ax.set_xlim(0, np.sum(data, axis=1).max())

    for i, colname in enumerate(category_names):
        widths = data[:, i]
        starts = data_cum[:, i] - widths
        rects = ax.barh(labels, widths, left=starts, height=0.5, label=colname)
        if (
            title
            != "In your opinion, how important or unimportant is proper use of grammar?"
            or i > 2
        ):
            ax.bar_label(rects, label_type="center", fmt="%1.1f%%")

    if (
        title
        == "In your opinion, how important or unimportant is proper use of grammar?"
    ):
        ax.legend(ncol=2, bbox_to_anchor=(0, 1), loc="lower left", fontsize="small")
    else:
        ax.legend(
            ncol=len(category_names),
            bbox_to_anchor=(0, 1),
            loc="lower left",
            fontsize="small",
        )
    plt.savefig(f"barh_{title.replace(' ', '')}")
    plt.close()
    return fig, ax



if __name__ == "__main__":
    """ Steps 1 and 2 """
    df = assemble_original_and_extra_survey()
    demographic_groups, answers = format_survey_data(df)

    analyze_assembled_survey(df, demographic_groups, answers)

    """ Section 3 """

    questions, models = make_models(df)

    """ Section 4 """

    census_df = get_census_data()
    create_pie_plots(census_df, "Household Income")
    plot_pie_in_pie(demographic_groups, census_df, "Location (Census Region)")
    multi_barplot(demographic_groups, census_df, "Household Income")

    """ Section 5 """

    df_plain = df.dropna()
    _, census_preprocessed = preprocess_data(df_plain, census_df)

    counts = census_df.Count / census_df.Count.sum()

    census_df.Count.sum()


    for question in questions:
        print(question)
        answer_options = answers[question][0]
        answer_counts = answers[question][1]
        print(answers[question][0])
        predictions = models[question].predict_proba(census_preprocessed)

        weighted_predictions = predictions.transpose() @ counts
        if question != "In your opinion, which sentence is more gramatically correct?":
            answer_options = answers[question][0][:-1]
            answer_counts = answers[question][1][:-1]

        weighted_predictions = [
            weighted_predictions[np.where(models[question].classes_ == option)][0]
            for option in answer_options
        ]
        survey_probs = answer_counts / sum(answer_counts)
        results = {"Census": weighted_predictions, "Post-Strat": survey_probs}
        print("survey probs: ", survey_probs)
        print("Probabilities: ", weighted_predictions)
        print()

        barh(results, answer_options, question)


    print(results)
