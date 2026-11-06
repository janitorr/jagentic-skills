from fastapi import FastAPI

app = FastAPI(title="orders-api")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/orders/{order_id}")
def get_order(order_id: str) -> dict[str, str]:
    return {"id": order_id, "status": "pending"}
