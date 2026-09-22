def lambda_handler(event, context):

    a = event["a"]
    b = event["b"]

    result = a + b

    print("a =", a)
    print("b =", b)
    print("result =", result)

    return {
        "a": a,
        "b": b,
        "result": result
    }
