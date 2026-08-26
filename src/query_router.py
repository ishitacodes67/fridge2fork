from constraint_parser import parse_constraints

def route_query(query):
    """
    Decides how to handle a query based on its parsed constraints.
    Returns the constraints dict plus a routing decision.
    """
    constraints = parse_constraints(query)

    # Determine if any real constraints (beyond raw_query) were found
    constraint_keys = [k for k in constraints.keys() if k != "raw_query"]

    if constraint_keys:
        route = "search_with_filters"
    else:
        route = "simple_search"

    print(f"\nQuery: {query}")
    print(f"Route: {route}")
    print(f"Constraints found: {constraint_keys}")

    return constraints, route


if __name__ == "__main__":
    test_queries = [
        "chicken, garlic, rice",
        "vegetarian pasta without nuts, budget-friendly, under 15 minutes",
        "shrimp and rice",
    ]
    for q in test_queries:
        route_query(q)