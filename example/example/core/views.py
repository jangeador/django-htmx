import time
from dataclasses import dataclass

from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from faker import Faker

from django_htmx.views import HtmxListView
from example.core.forms import OddNumberForm


@require_http_methods(("GET",))
def index(request: HttpRequest) -> HttpResponse:
    return render(request, "index.html")


# CSRF Demo


@require_http_methods(("GET",))
def csrf_demo(request: HttpRequest) -> HttpResponse:
    return render(request, "csrf-demo.html")


@require_http_methods(("POST",))
def csrf_demo_checker(request: HttpRequest) -> HttpResponse:
    form = OddNumberForm(request.POST)
    if form.is_valid():
        number = form.cleaned_data["number"]
        number_is_odd = number % 2 == 1
    else:
        number_is_odd = False
    return render(
        request,
        "csrf-demo-checker.html",
        {"form": form, "number_is_odd": number_is_odd},
    )


# Error demo


@require_http_methods(("GET",))
def error_demo(request: HttpRequest) -> HttpResponse:
    return render(request, "error-demo.html")


@require_http_methods(("GET",))
def error_demo_trigger(request: HttpRequest) -> HttpResponse:
    1 / 0
    return render(request, "error-demo.html")  # unreachable


# Middleware tester

# This uses two views - one to render the form, and the second to render the
# table of attributes.


@require_http_methods(("GET",))
def middleware_tester(request: HttpRequest) -> HttpResponse:
    return render(request, "middleware-tester.html")


@require_http_methods(["DELETE", "POST", "PUT"])
def middleware_tester_table(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "middleware-tester-table.html",
        {"timestamp": time.time()},
    )


# Partial rendering example


# This dataclass acts as a stand-in for a database model - the example app
# avoids having a database for simplicity.


@dataclass
class Person:
    id: int
    name: str


faker = Faker()
people = [Person(id=i, name=faker.name()) for i in range(1, 235)]


@require_http_methods(("GET",))
def partial_rendering(request: HttpRequest) -> HttpResponse:
    # Standard Django pagination
    page_num = request.GET.get("page", "1")
    page = Paginator(object_list=people, per_page=10).get_page(page_num)

    # The htmx magic - use a different, minimal base template for htmx
    # requests, allowing us to skip rendering the unchanging parts of the
    # template.
    if request.htmx:
        base_template = "_partial.html"
    else:
        base_template = "_base.html"

    return render(
        request,
        "partial-rendering.html",
        {
            "base_template": base_template,
            "page": page,
        },
    )


# Class based view (CBV) example
class HtmxCBVListView(HtmxListView):
    queryset = people
    template_name = "cbv-full-rendering.html"
    partial_template_name = "cbv-partial-rendering.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        # the function-based example uses `page` as the paginator object name
        # here we switch the context key `page_obj` to `page` to keep things the same
        ctx = super().get_context_data(**kwargs)
        ctx["page"] = ctx.pop("page_obj")
        return ctx
