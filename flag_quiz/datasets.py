from dataclasses import dataclass, field
from pathlib import Path

FLAGS_BASE = Path(__file__).parent.parent / "flags"


@dataclass
class Dataset:
    id: str
    label: str
    entries: list[dict]          # each: {"code": str, "name": str}
    prompt: str = "Which country does this flag belong to?"

    @property
    def flags_dir(self) -> Path:
        return FLAGS_BASE / self.id

    def is_available(self) -> bool:
        d = self.flags_dir
        return d.is_dir() and any(d.glob("*.png"))

    @property
    def names(self) -> list[str]:
        return [e["name"] for e in self.entries]


# ---------------------------------------------------------------------------
# World countries
# ---------------------------------------------------------------------------
from flag_quiz.countries import COUNTRIES as _COUNTRIES  # noqa: E402

_COUNTRIES_DATASET = Dataset(
    id="countries",
    label="World Countries",
    entries=_COUNTRIES,
    prompt="Which country does this flag belong to?",
)

# ---------------------------------------------------------------------------
# US States
# ---------------------------------------------------------------------------
US_STATES: list[dict] = [
    {"code": "us-al", "name": "Alabama"},
    {"code": "us-ak", "name": "Alaska"},
    {"code": "us-az", "name": "Arizona"},
    {"code": "us-ar", "name": "Arkansas"},
    {"code": "us-ca", "name": "California"},
    {"code": "us-co", "name": "Colorado"},
    {"code": "us-ct", "name": "Connecticut"},
    {"code": "us-de", "name": "Delaware"},
    {"code": "us-fl", "name": "Florida"},
    {"code": "us-ga", "name": "Georgia"},
    {"code": "us-hi", "name": "Hawaii"},
    {"code": "us-id", "name": "Idaho"},
    {"code": "us-il", "name": "Illinois"},
    {"code": "us-in", "name": "Indiana"},
    {"code": "us-ia", "name": "Iowa"},
    {"code": "us-ks", "name": "Kansas"},
    {"code": "us-ky", "name": "Kentucky"},
    {"code": "us-la", "name": "Louisiana"},
    {"code": "us-me", "name": "Maine"},
    {"code": "us-md", "name": "Maryland"},
    {"code": "us-ma", "name": "Massachusetts"},
    {"code": "us-mi", "name": "Michigan"},
    {"code": "us-mn", "name": "Minnesota"},
    {"code": "us-ms", "name": "Mississippi"},
    {"code": "us-mo", "name": "Missouri"},
    {"code": "us-mt", "name": "Montana"},
    {"code": "us-ne", "name": "Nebraska"},
    {"code": "us-nv", "name": "Nevada"},
    {"code": "us-nh", "name": "New Hampshire"},
    {"code": "us-nj", "name": "New Jersey"},
    {"code": "us-nm", "name": "New Mexico"},
    {"code": "us-ny", "name": "New York"},
    {"code": "us-nc", "name": "North Carolina"},
    {"code": "us-nd", "name": "North Dakota"},
    {"code": "us-oh", "name": "Ohio"},
    {"code": "us-ok", "name": "Oklahoma"},
    {"code": "us-or", "name": "Oregon"},
    {"code": "us-pa", "name": "Pennsylvania"},
    {"code": "us-ri", "name": "Rhode Island"},
    {"code": "us-sc", "name": "South Carolina"},
    {"code": "us-sd", "name": "South Dakota"},
    {"code": "us-tn", "name": "Tennessee"},
    {"code": "us-tx", "name": "Texas"},
    {"code": "us-ut", "name": "Utah"},
    {"code": "us-vt", "name": "Vermont"},
    {"code": "us-va", "name": "Virginia"},
    {"code": "us-wa", "name": "Washington"},
    {"code": "us-wv", "name": "West Virginia"},
    {"code": "us-wi", "name": "Wisconsin"},
    {"code": "us-wy", "name": "Wyoming"},
]

_US_STATES_DATASET = Dataset(
    id="us_states",
    label="US States",
    entries=US_STATES,
    prompt="Which US state does this flag belong to?",
)

# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------
ALL_DATASETS: dict[str, Dataset] = {
    "countries": _COUNTRIES_DATASET,
    "us_states": _US_STATES_DATASET,
}


def get_available_datasets() -> list[Dataset]:
    """Return datasets that have at least one PNG in their flags folder."""
    return [ds for ds in ALL_DATASETS.values() if ds.is_available()]
