# lambdaC.py
import typer
import json
import logging
import ruamel.yaml
import importlib
import os
import glob
from internal_model import LambdaPlaybook
from transformer import to_general_lambda
from ai_transformer import cached_transform
from validators.validate_xsoar import validate_xsoar_playbook
from exporters.xsoar_exporter import export_xsoar
from exporters.fortisoar_exporter import export_fortisoar
from parsers import fortisoar_parser, xsoar_parser, ai_parser
import importlib.util

app = typer.Typer()
logging.basicConfig(filename="conversion.log", level=logging.INFO)

@app.command()
def convert(
    input_file: str,
    output_dir: str = "xsoar_outputs",
    vendor: str = 'xsoar',
    ai_fallback: bool = False,
    sdk_validate: bool = False
):
    """
    Convert between SOAR playbook formats, via Lambda-Actions as an intermediate.
    """
    playbook_repo_base = "Playbooks_Repo"
    cache_base = "cache"
    vendor = vendor.lower()

    if output_dir == "xsoar_outputs":
        output_dir = os.path.join(playbook_repo_base, vendor)

    # Ensure vendor-specific folders exist
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(playbook_repo_base, vendor), exist_ok=True)
    os.makedirs(os.path.join(cache_base, vendor), exist_ok=True)

    # Choose parser: {vendor}_parser if present, else AI
    parser = None
    try:
        spec = importlib.util.find_spec(f"parsers.{vendor}_parser")
        if spec is not None:
            parser_module = importlib.import_module(f"parsers.{vendor}_parser")
            parser = parser_module
            typer.echo(f"📦 Using built-in parser: {vendor}_parser")
        else:
            typer.echo("🔮 No built-in parser found—using AI to parse into Lambda-Actions schema…")
            parser = ai_parser
    except Exception as e:
        typer.echo(f"❌ Failed to load parser for {vendor}: {e}")
        raise typer.Exit(1)

    # Parse input into LambdaPlaybook
    try:
        if vendor == 'xsoar':
            lambda_pb = xsoar_parser.parse_xsoar_yaml(input_file)
        elif vendor == 'fortisoar':
            lambda_pb = fortisoar_parser.parse_fortisoar(input_file)
        else:
            lambda_pb = parser.parse_with_ai(input_file)
    except Exception as e:
        logging.error(f"Failed parsing {vendor} file: {input_file} – {e}")
        typer.echo(f"❌ Error parsing {vendor} input: {e}")
        raise typer.Exit(1)

    # Export to target format
    if vendor == 'xsoar':
        try:
            raw = export_xsoar(lambda_pb)
            vendor_playbook = ai_fallback and cached_transform(raw, vendor) or raw
        except Exception as e:
            logging.error(f"XSOAR export failed: {e}")
            typer.echo(f"❌ Error during XSOAR conversion: {e}")
            raise typer.Exit(1)

        # Validate XSOAR
        try:
            validate_xsoar_playbook(vendor_playbook)
        except Exception as e:
            logging.error(f"XSOAR validation error: {e}")
            typer.echo(f"❌ XSOAR validation error: {e}")
            raise typer.Exit(1)

        out_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(input_file))[0]}.json")
        with open(out_path, "w") as f:
            json.dump(vendor_playbook, f, indent=2)
        typer.echo(f"✅ XSOAR playbook saved to: {out_path}")

        # demisto-sdk validation for XSOAR
        if sdk_validate:
            import subprocess
            typer.echo("🔍 Running demisto-sdk validate…")
            cmd = ["demisto-sdk", "validate", "--insecure", "-i", out_path]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode != 0:
                typer.echo("❌ demisto-sdk validation failed:\n" + proc.stdout + proc.stderr)
                if typer.confirm("Regenerate via AI fallback?"):
                    vendor_playbook = cached_transform(raw)
                    with open(out_path, "w") as f:
                        json.dump(vendor_playbook, f, indent=2)
                    typer.echo("🔍 Re-running demisto-sdk validate…")
                    proc2 = subprocess.run(cmd, capture_output=True, text=True)
                    if proc2.returncode == 0:
                        typer.echo("✅ Now passes demisto-sdk validation.")
                    else:
                        typer.echo("❌ Still invalid after AI pass.")
                        raise typer.Exit(1)
                else:
                    raise typer.Exit(1)

    elif vendor == 'fortisoar':
        try:
            fs_json = export_fortisoar(lambda_pb)
        except Exception as e:
            logging.error(f"FortiSOAR export failed: {e}")
            typer.echo(f"❌ Error during FortiSOAR conversion: {e}")
            raise typer.Exit(1)

        out_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(input_file))[0]}.json")
        with open(out_path, "w") as f:
            json.dump(fs_json, f, indent=2)
        typer.echo(f"✅ FortiSOAR playbook saved to: {out_path}")

    else:
        vendor_playbook = to_general_lambda(lambda_pb).model_dump()
        out_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(input_file))[0]}.yml")
        yaml = ruamel.yaml.YAML()
        yaml.default_flow_style = False
        with open(out_path, "w") as f:
            yaml.dump(vendor_playbook, f)
        typer.echo(f"✅ Lambda-Actions YAML saved to: {out_path}")
        return

    lambda_dir = os.path.join(playbook_repo_base, "lambda")
    os.makedirs(lambda_dir, exist_ok=True)
    safe = "".join(c for c in lambda_pb.name or "" if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_")
    lambda_out = os.path.join(lambda_dir, f"{safe or 'playbook'}.yml")
    yaml = ruamel.yaml.YAML()
    yaml.default_flow_style = False
    with open(lambda_out, "w") as ly:
        yaml.dump(to_general_lambda(lambda_pb).model_dump(), ly)
    typer.echo(f"✅ Intermediate Lambda YAML saved to: {lambda_out}")

if __name__ == "__main__":
    app()
