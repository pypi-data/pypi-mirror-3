username_and_roles = context.get_local_roles()
roles_and_usernames = {}
for username_and_role_set in username_and_roles:
    for role in username_and_role_set[1]:
        if not roles_and_usernames.has_key(role):
            roles_and_usernames[role] = []
        roles_and_usernames[role].append(username_and_role_set[0])

return roles_and_usernames
