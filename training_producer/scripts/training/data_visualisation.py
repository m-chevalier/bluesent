from training_producer.scripts.training.data_preparation import connect_to_mongodb_and_load_data

if __name__ == "__main__":
    df = connect_to_mongodb_and_load_data("is_llm_related")

    df = df.head(5000)
    df = df[['text', 'is_llm_related']]

    print(df.head())
    print(df.describe())
    print(df.info())
    print(df.groupby('is_llm_related').count())