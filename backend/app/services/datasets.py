from uuid import UUID

from app.schemas import Dataset, DatasetCreate, DatasetUpdate


class DatasetStore:
    """In-memory dataset storage used until the persistence milestone."""

    def __init__(self) -> None:
        self._datasets: dict[UUID, Dataset] = {}

    def create(self, dataset_data: DatasetCreate) -> Dataset:
        dataset = Dataset(**dataset_data.model_dump())
        self._datasets[dataset.id] = dataset
        return dataset

    def list(self) -> list[Dataset]:
        return list(self._datasets.values())

    def get(self, dataset_id: UUID) -> Dataset | None:
        return self._datasets.get(dataset_id)

    def update(self, dataset_id: UUID, dataset_data: DatasetUpdate) -> Dataset | None:
        dataset = self.get(dataset_id)
        if dataset is None:
            return None

        updated_fields = dataset_data.model_dump(exclude_unset=True)
        updated_dataset = dataset.model_copy(update=updated_fields)
        self._datasets[dataset_id] = updated_dataset
        return updated_dataset

    def delete(self, dataset_id: UUID) -> bool:
        return self._datasets.pop(dataset_id, None) is not None

    def clear(self) -> None:
        self._datasets.clear()


dataset_store = DatasetStore()