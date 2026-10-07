from app.retrieval.table_retriever import TableRetriever


def main():

    retriever = TableRetriever()

    results = retriever.retrieve(
        query="baseline characteristics"
    )

    print("\n" + "=" * 70)
    print("TABLE RETRIEVAL TEST")
    print("=" * 70)

    print(f"Found {len(results)} table(s)\n")

    for table in results:

        print("TABLE:")
        print(f"  ID: {table['table_id']}")
        print(f"  Trial: {table['trial_id']}")
        print(f"  Title: {table['title']}")
        print(f"  Page: {table['page']}")

        print("\nHeaders:")
        print(table["headers"])

        print("\nFirst 5 rows:")

        for row in table["rows"][:5]:
            print(row)

        print("\n" + "-" * 70)


if __name__ == "__main__":
    main()