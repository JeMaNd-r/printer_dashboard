from typing import Any, Dict, Optional, Union

from rest_framework.renderers import BaseRenderer


class BinaryRenderer(BaseRenderer):
    """Renderer for binary content like Excel files."""

    media_type = "application/vnd.ms-excel"
    format = "bin"

    def render(
        self, data: Any, accepted_media_type: Optional[str] = None, renderer_context: Optional[Dict[str, Any]] = None
    ) -> Union[bytes, str, None]:
        return data
