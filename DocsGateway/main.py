from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
import httpx
import asyncio
import copy

# Optional: Set up Swagger UI and ReDoc endpoints
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html


merged_spec = {}


async def fetch_openapi_specs(services):
    specs = []
    async with httpx.AsyncClient() as client:
        tasks = []
        for service in services:
            tasks.append(client.get(service["url"]))
        responses = await asyncio.gather(*tasks)
        for i, response in enumerate(responses):
            spec = response.json()
            # Ensure the 'servers' field is set correctly
            if not spec.get("servers"):
                spec["servers"] = [{"url": services[i]["base_url"]}]
            specs.append(spec)
    return specs


def merge_openapi_specs(specs):
    merged_spec = {
        "openapi": "3.0.0",
        "info": {"title": "Aggregated API", "version": "1.0.0"},
        # We can omit the root 'servers' field or include all servers
        # "servers": [],  # Optional
        "paths": {},
        "components": {
            "schemas": {},
            "parameters": {},
            "responses": {},
            "securitySchemes": {},
        },
        "tags": [],
    }

    for spec in specs:
        spec_servers = spec.get("servers", [])
        # Iterate over each path in the spec
        for path, path_item in spec.get("paths", {}).items():
            # Make a deep copy to avoid modifying the original path_item
            path_item_copy = copy.deepcopy(path_item)
            # Set the 'servers' field at the path level
            if "servers" not in path_item_copy:
                path_item_copy["servers"] = spec_servers
            else:
                # Combine servers if already present
                path_item_copy["servers"].extend(
                    [
                        server
                        for server in spec_servers
                        if server not in path_item_copy["servers"]
                    ]
                )
            # Add the path to the merged spec
            merged_spec["paths"][path] = path_item_copy

        # Merge components
        for component in ["schemas", "parameters", "responses", "securitySchemes"]:
            comp = spec.get("components", {}).get(component, {})
            merged_spec["components"][component].update(comp)

        # Merge tags (avoid duplicates)
        existing_tags = {tag["name"] for tag in merged_spec["tags"]}
        for tag in spec.get("tags", []):
            if tag["name"] not in existing_tags:
                merged_spec["tags"].append(tag)
                existing_tags.add(tag["name"])

    return merged_spec


@asynccontextmanager
async def lifespan(app: FastAPI):
    global merged_spec
    services = [
        {
            "url": f"http://localhost:{port}/openapi.json",
            "base_url": f"http://localhost:{port}",
        }
        for port in range(8001, 8004)
    ]
    specs = await fetch_openapi_specs(services)
    merged_spec = merge_openapi_specs(specs)
    yield


app = FastAPI(title="Aggregated API Documentation", lifespan=lifespan)


@app.get("/openapi.json", include_in_schema=False)
async def custom_openapi(request: Request):
    return merged_spec


def custom_openapi_schema():
    return merged_spec


app.openapi = custom_openapi_schema


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Aggregated API Docs")


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(openapi_url="/openapi.json", title="Aggregated API Docs")
