from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.routes.datasets import dataset_store
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_datasets() -> None:
    dataset_store.clear()


def test_dataset_crud_lifecycle() -> None:
    create_response = client.post(
        "/datasets",
        json={
            "name": "Arithmetic",
            "description": "Basic math cases",
            "cases": [
                {"input": "2 + 2", "expected_output": "4"},
            ],
        },
    )

    assert create_response.status_code == 201
    dataset = create_response.json()
    dataset_id = dataset["id"]
    assert dataset["name"] == "Arithmetic"
    assert len(dataset["cases"]) == 1

    list_response = client.get("/datasets")
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [dataset_id]

    get_response = client.get(f"/datasets/{dataset_id}")
    assert get_response.status_code == 200
    assert get_response.json()["description"] == "Basic math cases"

    update_response = client.put(
        f"/datasets/{dataset_id}",
        json={"name": "Updated arithmetic"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated arithmetic"
    assert update_response.json()["description"] == "Basic math cases"

    delete_response = client.delete(f"/datasets/{dataset_id}")
    assert delete_response.status_code == 204
    assert client.get(f"/datasets/{dataset_id}").status_code == 404


def test_missing_dataset_returns_not_found() -> None:
    response = client.get(f"/datasets/{uuid4()}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Dataset not found"}


def test_dataset_input_is_validated() -> None:
    response = client.post("/datasets", json={"name": ""})

    assert response.status_code == 422