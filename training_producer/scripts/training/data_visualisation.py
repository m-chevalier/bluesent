import pandas as pd

from training_producer.scripts.training.data_preparation import connect_to_mongodb_and_load_data

if __name__ == "__main__":
    llm_posts_df = connect_to_mongodb_and_load_data("is_llm_related")
    random_posts_df = connect_to_mongodb_and_load_data("is_llm_related", "random_posts")
    llm_posts_df = llm_posts_df.head(5000)

    df = pd.concat([llm_posts_df, random_posts_df], ignore_index=True)
    df = df[['text', 'is_llm_related']]

    print(df.head())
    print(df.describe())
    print(df.info())
    print(df.groupby('is_llm_related').count())