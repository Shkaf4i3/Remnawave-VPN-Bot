from ..dto import TariffDto
from ..model import Tariff


def map_tariff(tariff: Tariff) -> TariffDto:
    return TariffDto(
        id=tariff.id,
        name=tariff.name,
        duration_days=tariff.duration_days,
        price=tariff.price,
        device_limit=tariff.device_limit,
        created_at=tariff.created_at,
        description=tariff.description,
        remnawave_squad_id=tariff.remnawave_squad_id,
        updated_at=tariff.updated_at,
    )
