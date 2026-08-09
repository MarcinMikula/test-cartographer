"""Export JSON Schema for Sprint 15 ProjectProfile contract."""

from test_cartographer.project_profile.io import export_project_profile_schema

if __name__ == "__main__":
    export_project_profile_schema("schemas/project-profile-v0.1.schema.json")
    print("Exported schemas/project-profile-v0.1.schema.json")
