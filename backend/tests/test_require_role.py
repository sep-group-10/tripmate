import pytest

from app.core.dependencies import require_role
from app.core.errors import ApiError
from app.core.roles import Role


class _FakeUser:
    def __init__(self, role: str):
        self.role = role


@pytest.mark.parametrize(
    ("required_role", "actual_role", "should_be_allowed"),
    [
        (Role.TOURIST, "TOURIST", True),
        (Role.TOURIST, "ADMIN", False),
        (Role.TOURIST, "SUPER_ADMIN", False),
        (Role.ADMIN, "TOURIST", False),
        (Role.ADMIN, "ADMIN", True),
        (Role.ADMIN, "SUPER_ADMIN", True),
        (Role.SUPER_ADMIN, "TOURIST", False),
        (Role.SUPER_ADMIN, "ADMIN", False),
        (Role.SUPER_ADMIN, "SUPER_ADMIN", True),
    ],
)
def test_require_role_matches_rbac_hierarchy(
    required_role, actual_role, should_be_allowed
):
    check = require_role(required_role)
    user = _FakeUser(role=actual_role)

    if should_be_allowed:
        assert check(current_user=user) is user
    else:
        with pytest.raises(ApiError) as exc_info:
            check(current_user=user)
        assert exc_info.value.code == "FORBIDDEN"
        assert exc_info.value.status_code == 403
