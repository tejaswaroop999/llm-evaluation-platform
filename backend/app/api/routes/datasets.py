from uuid import UUID

from fastapi import APIRouter, HTTPException, Response, status

from app.schemas import Dataset, DatasetCreate, DatasetUpdate
from app.services.datasets import dataset_store

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.post("", response_model=Dataset, status_code=status.HTTP_201_CREATED)
def create_dataset(dataset_data: DatasetCreate) -> Dataset:
    return dataset_store.create(dataset_data)


@router.get("", response_model=list[Dataset])
def list_datasets() -> list[Dataset]:
    return dataset_store.list()


@router.get("/{dataset_id}", response_model=Dataset)
def get_dataset(dataset_id: UUID) -> Dataset:
    dataset = dataset_store.get(dataset_id)
    if dataset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    return dataset


@router.put("/{dataset_id}", response_model=Dataset)
def update_dataset(dataset_id: UUID, dataset_data: DatasetUpdate) -> Dataset:
    dataset = dataset_store.update(dataset_id, dataset_data)
    if dataset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    return dataset


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dataset(dataset_id: UUID) -> Response:
    if not dataset_store.delete(dataset_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)