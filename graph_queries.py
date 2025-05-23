def apply_persona_to_graph(graph, persona_rule):
    matched_users = set()

    for node, data in graph.nodes(data=True):
        if data.get("type") != "user":
            continue

        match = True

        # Apply each field if it exists
        for field, condition in persona_rule.items():
            value = data.get(field)
            
            if field == "age" and isinstance(condition, dict):
                op = condition.get("operator")
                val = condition.get("value", 0)
                value = data.get("age", None)  # ← updated

                if value is None:
                    match = False
                    break

                if op == ">" and not value > val:
                    match = False
                elif op == "<" and not value < val:
                    match = False
                elif op == "=" and not value == val:
                    match = False

            elif isinstance(condition, list):
                if value not in condition:
                    match = False

            elif isinstance(condition, str):
                if value != condition:
                    match = False

            # Future: handle zip, tag, genre → via relationships

        if match:
            matched_users.add(node)

    # Now check graph relationships if tags or genres are in persona
    for rel_field in ["tag", "genre"]:
        if rel_field in persona_rule:
            values = set(persona_rule[rel_field])
            valid_users = set()
            for u, node, edge_data in graph.edges(data=True):
                if edge_data.get("relation") in ["purchased", "watched"]:
                    for _, target, tdata in graph.out_edges(node, data=True):
                        if tdata.get("relation") in ["tagged_as", "about"] and target.lower() in values:
                            valid_users.add(u)
            matched_users = matched_users & valid_users if matched_users else valid_users

    return matched_users

def evaluate_condition(user_data, condition, matcher=None, field=None, graph=None, user_node=None):
    if field is None:
        field = condition.get("field")

    # Special case: tag or genre → check through graph relationships
    if field in ["tag", "genre"] and matcher and graph and user_node:
        values = condition.get("in", [])
        expanded_vals = []
        for val in values:
            expanded_vals.extend(matcher.expand(val))

        found = False
        for _, mid_node, edge_data in graph.out_edges(user_node, data=True):
            if edge_data.get("relation") in ["purchased", "watched"]:
                for _, target_node, rel_data in graph.out_edges(mid_node, data=True):
                    if rel_data.get("relation") in ["tagged_as", "about"]:
                        if target_node.lower() in expanded_vals:
                            found = True
                            break
            if found:
                break
        return found

    # Standard direct field checks
    value = user_data.get(field)
    if value is None:
        return False

    if "operator" in condition:
        op = condition.get("operator")
        val = condition.get("value")
        try:
            value = int(value)
            val = int(val)
            if op == ">" and value > val: return True
            if op == "<" and value < val: return True
            if op == ">=" and value >= val: return True
            if op == "<=" and value <= val: return True
            if op == "=" and value == val: return True
            if op == "==" and value == val: return True
        except:
            return False

    if "equals" in condition:
        return value == condition["equals"]

    if "in" in condition:
        values = condition["in"]
        if value in values:
            return True

    return False



def evaluate_logic_block(user_data, logic_block, matcher=None, graph=None, user_node=None):
    if "and" in logic_block:
        return all(
            evaluate_logic_block(user_data, cond, matcher, graph, user_node)
            if isinstance(cond, dict) and ("and" in cond or "or" in cond)
            else evaluate_condition(user_data, cond, matcher, cond.get("field"), graph, user_node)
            for cond in logic_block["and"]
        )

    elif "or" in logic_block:
        return any(
            evaluate_logic_block(user_data, cond, matcher, graph, user_node)
            if isinstance(cond, dict) and ("and" in cond or "or" in cond)
            else evaluate_condition(user_data, cond, matcher, cond.get("field"), graph, user_node)
            for cond in logic_block["or"]
        )

    return False


def apply_logical_rule(graph, rule, matcher=None):
    matched_users = set()

    for node, data in graph.nodes(data=True):
        if data.get("type") != "user":
            continue

        if evaluate_logic_block(data, rule["conditions"], matcher, graph, node):
            matched_users.add(node)

    return matched_users
