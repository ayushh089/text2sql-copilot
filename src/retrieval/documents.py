
from langchain_core.documents import Document

from src.database.schema_extractor import get_database_schema


def build_schema_documents():
    """
    Convert database schema into separate LangChain
    documents, one document per table.
    """

    schema = get_database_schema()

    documents = []

    for table in schema["tables"]:

        table_name = table["table_name"]

        # Build column descriptions
        column_lines = []

        for column in table["columns"]:
            column_lines.append(
                f"- {column['column_name']} "
                f"({column['data_type']})"
            )

        # Find relationships connected to this table
        relationship_lines = []

        for relation in schema["relationships"]:

            if relation["from_table"] == table_name:
                relationship_lines.append(
                    f"- {relation['from_column']} references "
                    f"{relation['to_table']}.{relation['to_column']}"
                )

            elif relation["to_table"] == table_name:
                relationship_lines.append(
                    f"- {relation['to_table']}.{relation['to_column']} "
                    f"is referenced by "
                    f"{relation['from_table']}.{relation['from_column']}"
                )

        # Build document content
        content = f"""
Table: {table_name}

Columns:
{chr(10).join(column_lines)}

Relationships:
{chr(10).join(relationship_lines) if relationship_lines else "No direct relationships defined."}
"""

        document = Document(
            page_content=content.strip(),
            metadata={
                "table_name": table_name,
                "source": "olist_database_schema"
            }
        )

        documents.append(document)

    return documents


if __name__ == "__main__":

    documents = build_schema_documents()

    print(f"Total schema documents created: {len(documents)}")

    for document in documents:

        print("\n" + "=" * 60)
        print("TABLE:", document.metadata["table_name"])
        print("=" * 60)

        print(document.page_content)
