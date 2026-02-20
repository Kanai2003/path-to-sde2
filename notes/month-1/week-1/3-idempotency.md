# Idempotency

# Idempotency

In backend development, idempotency is a fancy word for a very simple, critical concept: "No matter how many times you perform an action, the result should be exactly the same as if you did it once."

## Why do we need it? (The "Double Charge" Problem)

Idempotency is the only thing standing between a happy customer and a customer who was accidentally charged twice for the same order because their Wi-Fi flickered.

In a distributed system, network failures happen:

1. The client sends a request (e.g., "Pay $50").
2. The server processes it successfully.
3. The network dies before the server can send the "Success" message back.
4. The client (or a retry logic) thinks the request failed and sends "Pay $50" again.

**Without idempotency**: The user pays $100.

**With idempotency**: The server recognizes the second request and says, "I already did this, here is the original success message."

### HTTP Methods: Which are Idempotent?

| Method | Idempotent?  | Why?                                                                                       |
| ------ | ------------ | ------------------------------------------------------------------------------------------ |
| GET    | ✅ Yes       | Reading data doesn't change anything.                                                      |
| PUT    | ✅ Yes       | Replacing a resource with the same data results in the same state.                         |
| DELETE | ✅ Yes       | Once a resource is gone, deleting it again doesn't change the fact that it's gone.         |
| POST   | ❌ No        | Usually creates a new resource every time. 2 POSTs = 2 new items.                          |
| PATCH  | ⚠️ Sometimes | It depends on the logic (e.g., "Set age to 30" is idempotent; "Increase age by 1" is NOT). |

## How to implement it (The "Idempotency Key")

The most common way to make a POST request idempotent (like in Stripe or PayPal) is using an Idempotency Key.

1. Client generates a unique string (a UUID) for the transaction: `idempotency-key: "gitcash-order-123"`.

2. Server receives the request and checks the database: "Have I seen this key before?"

3. **If NO**: Process the request and save the result in a table (Key + Response).

4. **If YES**: Don't run the logic again. Just return the saved response from the first time.

```python
from fastapi import FastAPI, Header, HTTPException

app = FastAPI()

processed_keys = {}

@app.post("/payments")
async def process_payment(amount: int, x_idempotency_key: str = Header(None)):
    if not x_idempotency_key:
        raise HTTPException(status_code=400, detail="Idempotency key missing")

    # 1. Check if we've seen this key
    if x_idempotency_key in processed_keys:
        return processed_keys[x_idempotency_key]

    # 2. Perform the "Expensive" logic
    result = {"status": "success", "amount": amount, "transaction_id": "txn_987"}

    # 3. Store the result
    processed_keys[x_idempotency_key] = result

    return result
```
