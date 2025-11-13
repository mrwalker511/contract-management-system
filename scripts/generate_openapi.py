"""
Script to generate OpenAPI specification and save to /shared
"""
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.main import app

def generate_openapi_spec():
    """Generate OpenAPI specification and save to shared directory"""
    openapi_schema = app.openapi()

    # Save as JSON
    shared_dir = Path(__file__).parent.parent / "shared"
    shared_dir.mkdir(exist_ok=True)

    output_file = shared_dir / "openapi.json"
    with open(output_file, "w") as f:
        json.dump(openapi_schema, f, indent=2)

    print(f"✓ OpenAPI specification generated: {output_file}")
    print(f"  Title: {openapi_schema.get('info', {}).get('title')}")
    print(f"  Version: {openapi_schema.get('info', {}).get('version')}")
    print(f"  Endpoints: {len(openapi_schema.get('paths', {}))}")

if __name__ == "__main__":
    generate_openapi_spec()
