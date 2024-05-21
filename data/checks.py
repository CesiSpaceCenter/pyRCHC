def check(item_value: any, checks_list: dict, item_name: str) -> list:
    error_messages = []
    for check_name, check_value in checks_list.items():
        # if a check does not pass, define the error message
        if check_name == 'min_length' and len(item_value) < check_value:
            error_messages.append(f'{item_name} is not long enough ({len(item_value)} < {check_value})')

        if check_name == 'max_length' and len(item_value) > check_value:
            error_messages.append(f'{item_name} is too long ({len(item_value)} > {check_value})')

        if check_name == 'min' and item_value < check_value:
            error_messages.append(f'{item_name} is below min ({item_value} < {check_value})')

        if check_name == 'max' and item_value > check_value:
            error_messages.append(f'{item_name} is above max ({item_value} > {check_value})')

        if check_name == 'values_enum' and item_value not in check_value:
            error_messages.append(f'{item_name}\'s value is not in defined enum {check_value}')

    return error_messages
