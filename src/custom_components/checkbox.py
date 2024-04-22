from dataclasses import dataclass, field
from typing import List, Optional

from dash import dcc, html


@dataclass
class CheckboxCustom:
    """Custom checkbox component using dcc.Checklist."""

    options: List[dict] = field(default_factory=list)
    value: List[str] = field(default_factory=list)
    label: Optional[str] = None
    help_text: str = ""
    error_message: str = ""
    instance_count: int = field(default=0, init=False, repr=False)

    def __post_init__(self):
        if not self.options:
            raise ValueError("Options must be provided.")

        type(self).instance_count += 1
        self.id = f"({self.__class__.__name__}-{self.instance_count})"
        self.help_text_id: str = f"{self.id}-help"
        self.error_message_id: str = f"{self.id}-error"
        self.label_id = f"{self.id}-label" if self.label is not None else None

    @property
    def layout(self) -> html.Div:
        """Generates the HTML layout for the custom checkbox component."""
        components = []

        if self.label is not None:
            components.append(
                html.Label(
                    self.label,
                    htmlFor=self.id,
                    className="text-sm font-medium text-gray-700",
                )
            )

        components.extend(
            [
                dcc.Checklist(
                    id=self.id,
                    options=self.options,
                    value=self.value,
                    className="block w-full rounded-md shadow-sm border-gray-300 focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 sm:text-sm",
                ),
                html.P(
                    self.help_text,
                    id=self.help_text_id,
                    className="mt-2 text-sm text-gray-500",
                ),
                html.Div(
                    self.error_message,
                    id=self.error_message_id,
                    className="mt-2 text-sm text-red-600",
                ),
            ]
        )

        return html.Div(components, className="m-4")
