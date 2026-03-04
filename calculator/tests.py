import json

from django.test import Client, TestCase
from django.urls import reverse

from .services import CalculationResult, calculate


class CalculationServiceTests(TestCase):
    def test_addition(self) -> None:
        result: CalculationResult = calculate("2", "3", "add")
        self.assertIsNone(result.error)
        self.assertEqual(result.value, 5)

    def test_subtraction(self) -> None:
        result = calculate("5", "8", "sub")
        self.assertIsNone(result.error)
        self.assertEqual(result.value, -3.0)

    def test_multiplication(self) -> None:
        result = calculate("2.5", "4", "mul")
        self.assertIsNone(result.error)
        self.assertEqual(result.value, 10.0)

    def test_division(self) -> None:
        result = calculate("9", "3", "div")
        self.assertIsNone(result.error)
        self.assertEqual(result.value, 3.0)

    def test_division_by_zero_returns_error(self) -> None:
        result = calculate("9", "0", "div")
        self.assertIsNone(result.value)
        self.assertEqual(result.error, "Cannot divide by zero.")

    def test_first_number_required(self) -> None:
        result = calculate("", "2", "add")
        self.assertIsNone(result.value)
        self.assertEqual(result.error, "First number is required.")

    def test_second_number_must_be_number(self) -> None:
        result = calculate("2", "abc", "add")
        self.assertIsNone(result.value)
        self.assertEqual(result.error, "Second number must be a number.")

    def test_unsupported_operation(self) -> None:
        result = calculate("2", "3", "pow")  # type: ignore[arg-type]
        self.assertIsNone(result.value)
        self.assertEqual(result.error, "Unsupported operation.")


class CalculatorViewTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_get_index_renders_template(self) -> None:
        url = reverse("calculator:index")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "calculator/index.html")
        self.assertIn("result", response.context)
        self.assertIn("error", response.context)

    def test_post_index_valid_addition_shows_result(self) -> None:
        url = reverse("calculator:index")
        response = self.client.post(
            url,
            data={"a": "2", "b": "3", "op": "add"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["result"], 5.0)
        self.assertIsNone(response.context["error"])

    def test_post_index_divide_by_zero_shows_error(self) -> None:
        url = reverse("calculator:index")
        response = self.client.post(
            url,
            data={"a": "9", "b": "0", "op": "div"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context["result"])
        self.assertEqual(response.context["error"], "Cannot divide by zero.")


class CalculatorApiTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.url = reverse("calculator:calculate_api")

    def test_get_not_allowed(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_valid_addition_returns_json_result(self) -> None:
        payload = {"a": 2, "b": 3, "op": "add"}
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["result"], 5.0)

    def test_divide_by_zero_returns_400_error(self) -> None:
        payload = {"a": 9, "b": 0, "op": "div"}
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["error"], "Cannot divide by zero.")

    def test_invalid_json_returns_400(self) -> None:
        response = self.client.post(
            self.url,
            data="this is not json",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("error", data)

