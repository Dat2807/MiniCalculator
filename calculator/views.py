import json
from json import JSONDecodeError

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

from .services import CalculationResult, calculate


def index(request: HttpRequest) -> HttpResponse:
    context: dict[str, object] = {
        "a": "",
        "b": "",
        "op": "add",
        "result": None,
        "error": None,
    }

    if request.method == "POST":
        a = request.POST.get("a", "")
        b = request.POST.get("b", "")
        op = request.POST.get("op", "add")

        result: CalculationResult = calculate(a_raw=a, b_raw=b, op=op)  # type: ignore[arg-type]

        context.update(
            {
                "a": a,
                "b": b,
                "op": op,
                "result": result.value,
                "error": result.error,
            }
        )

    return render(request, "calculator/index.html", context)


def calculate_api(request: HttpRequest) -> JsonResponse:
    if request.method != "POST":
        return JsonResponse({"error": "Only POST is allowed."}, status=405)

    try:
        body = request.body.decode("utf-8") if request.body else ""
        data = json.loads(body) if body else None
    except (UnicodeDecodeError, JSONDecodeError):
        data = None

    if not isinstance(data, dict):
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    a = str(data.get("a", ""))
    b = str(data.get("b", ""))
    op = str(data.get("op", "add"))

    result = calculate(a_raw=a, b_raw=b, op=op)  # type: ignore[arg-type]

    if result.error:
        return JsonResponse({"error": result.error}, status=400)

    return JsonResponse({"result": result.value})

