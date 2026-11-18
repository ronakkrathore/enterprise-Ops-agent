
from sqlalchemy.engine import Engine

from shared.database.schema_inspector import (
    get_table_names,
    get_foreign_keys
)

from shared.semantic.models.relationships import (
    SemanticRelationship,
    RelationshipType,
    RelationshipOrigin
)

from shared.semantic.models.mappings import ApprovalStatus

from shared.semantic.catalog.relationship_catalog import (
    RelationshipCatalog
)

from collections import deque

def discover_relationships(
    engine: Engine,
    source_id: str
) -> list[SemanticRelationship]:
    """
    Discover relationships using database foreign-key metadata.

    Discovered relationships remain proposed until reviewed.
    """

    tables = get_table_names(engine)

    discovered_relationships = []

    for table in tables:

        # Views are not considered for FK discovery.
        if table["object_type"] != "BASE TABLE":
            continue

        schema_name = table["schema"]
        table_name = table["name"]

        foreign_keys = get_foreign_keys(
            engine,
            table_name,
            schema_name
        )

        for foreign_key in foreign_keys:

            columns = foreign_key["columns"]
            referenced_columns = foreign_key["referenced_columns"]

            # The current model supports single-column relationships.
            if len(columns) != 1 or len(referenced_columns) != 1:
                raise NotImplementedError(
                    "Composite foreign keys are not yet supported: "
                    f"{table_name} -> {foreign_key['referenced_table']}"
                )

            relationship = SemanticRelationship(
                source_id=source_id,

                left_schema=schema_name,
                left_table=table_name,
                left_column=columns[0],

                right_schema=foreign_key["referenced_schema"],
                right_table=foreign_key["referenced_table"],
                right_column=referenced_columns[0],

                relationship_type=RelationshipType.MANY_TO_ONE,
                relationship_origin=RelationshipOrigin.SCHEMA_DISCOVERED,
                confidence=1.0,
                approval_status=ApprovalStatus.PROPOSED
            )

            discovered_relationships.append(relationship)

    return discovered_relationships

def discover_and_store_relationships(
    engine: Engine,
    source_id: str,
    catalog: RelationshipCatalog
) -> tuple[SemanticRelationship, ...]:
    """
    Discover database relationships and store them
    in the supplied relationship catalog.
    """

    if not isinstance(catalog, RelationshipCatalog):
        raise TypeError(
            "catalog must be a RelationshipCatalog instance."
        )

    relationships = discover_relationships(
        engine,
        source_id
    )

    for relationship in relationships:
        catalog.add_relationship(relationship)

    return tuple(relationships)



def resolve_join_path(
    catalog: RelationshipCatalog,
    source_id: str,
    start_schema: str,
    start_table: str,
    target_schema: str,
    target_table: str
) -> tuple[SemanticRelationship, ...]:
    """
    Find the unique shortest approved relationship path
    between two tables using BFS.

    Raises:
        TypeError: If the catalog has an invalid type.
        ValueError: If required identifiers are invalid.
        ValueError: If no approved path exists.
        ValueError: If multiple shortest paths exist.
    """

    if not isinstance(catalog, RelationshipCatalog):
        raise TypeError(
            "catalog must be a RelationshipCatalog instance."
        )

    identifiers = {
        "source_id": source_id,
        "start_schema": start_schema,
        "start_table": start_table,
        "target_schema": target_schema,
        "target_table": target_table
    }

    for name, value in identifiers.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"{name} must be a non-empty string."
            )

    start = (start_schema, start_table)
    target = (target_schema, target_table)

    if start == target:
        return ()

    relationships = catalog.get_approved_relationships(source_id)

    # Build an undirected graph.
    graph = {}

    for relationship in relationships:

        left = (
            relationship.left_schema,
            relationship.left_table
        )

        right = (
            relationship.right_schema,
            relationship.right_table
        )

        graph.setdefault(left, []).append(
            (right, relationship)
        )

        graph.setdefault(right, []).append(
            (left, relationship)
        )

    # BFS state.
    queue = deque([start])

    distances = {start: 0}

    # Number of shortest paths to each table.
    # Values are capped at 2 because we only need to
    # distinguish unique paths from ambiguous paths.
    path_counts = {start: 1}

    # Stores the previous table and relationship
    # for reconstructing a unique shortest path.
    predecessors = {}

    target_distance = None

    while queue:

        current = queue.popleft()
        current_distance = distances[current]

        # Continue processing all nodes one level
        # before the target, but do not explore beyond it.
        if (
            target_distance is not None
            and current_distance >= target_distance
        ):
            continue

        for next_table, relationship in graph.get(
            current,
            []
        ):

            next_distance = current_distance + 1

            if next_table not in distances:

                distances[next_table] = next_distance

                path_counts[next_table] = path_counts[current]

                predecessors[next_table] = (
                    current,
                    relationship
                )

                queue.append(next_table)

                if next_table == target:
                    target_distance = next_distance

            elif distances[next_table] == next_distance:

                # Another equally short route was found.
                path_counts[next_table] = min(
                    2,
                    path_counts[next_table] + path_counts[current]
                )

    if target not in distances:
        raise ValueError(
            f"No approved relationship path exists between "
            f"{start_schema}.{start_table} and "
            f"{target_schema}.{target_table}."
        )

    if path_counts[target] > 1:
        raise ValueError(
            "Multiple shortest relationship paths exist. "
            "The join path is ambiguous."
        )

    # Reconstruct the unique shortest path.
    path = []
    current = target

    while current != start:

        previous, relationship = predecessors[current]

        path.append(relationship)
        current = previous

    path.reverse()

    return tuple(path)
