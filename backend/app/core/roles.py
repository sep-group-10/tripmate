from enum import StrEnum


class Role(StrEnum):
    TOURIST = "TOURIST"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"


# Per docs/RABC.md: Super Admin inherits everything Admin can do.
# Admin does NOT inherit Tourist rights - it is an isolated staff role,
# not a "higher" version of Tourist. So this is not a simple ranked
# ladder; each role only grants access to itself plus roles that
# explicitly inherit from it.
_INHERITED_BY: dict[Role, set[Role]] = {
    Role.TOURIST: {Role.TOURIST},
    Role.ADMIN: {Role.ADMIN, Role.SUPER_ADMIN},
    Role.SUPER_ADMIN: {Role.SUPER_ADMIN},
}


def roles_satisfying(required_role: Role) -> set[Role]:
    return _INHERITED_BY[required_role]
