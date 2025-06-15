from typing import Any

from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import expression
from sqlalchemy.types import DateTime


class utcnow(expression.FunctionElement):  # type: ignore[type-arg]
    type = DateTime()
    inherit_cache = True


@compiles(utcnow, 'postgresql')
def pg_utcnow(element: utcnow, compiler: Any, **kwargs: Any) -> str:
    return 'TIMEZONE(\'utc\', CURRENT_TIMESTAMP)'
