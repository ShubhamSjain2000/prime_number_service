from fastapi import FastAPI

from celery_conf import celery_app

app = FastAPI()


@celery_app.task
def create_find_prime_task(number_of_primes: str):
    primes = []
    count = 0
    i = 2
    while True:
        if count >= number_of_primes:
            break
        is_prime = True
        for j in primes:
            if i % j == 0:
                is_prime = False
        if is_prime:
            primes.append(i)
            count += 1
        i += 1
    return {"prime_numbers": primes}


@app.post("/find-prime")
def calculate_prime(body: dict):
    task = create_find_prime_task.apply_async(args=[body.get("number_of_primes")])
    return {"task_id": task.id, "message": "Processing"}


@app.get("/get-result/{task_id}")
def get_result(task_id: str):
    task_result = celery_app.AsyncResult(task_id)
    if task_result.state == "PENDING":
        response = {"state": task_result.state, "status": "PENDING"}
    elif task_result.state == "SUCCESS":
        response = {"state": task_result.state, "status": task_result.info}
    else:
        response = {"state": task_result.state, "result": task_result.result}
    return response
