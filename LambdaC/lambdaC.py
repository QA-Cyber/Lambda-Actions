# lambdaC.py
import typer
import json
import logging
import ruamel.yaml
import importlib
import os
from transformer import to_general_lambda
from ai_transformer import cached_transform
from validators.validate_xsoar import validate_xsoar_playbook
from exporters.xsoar_exporter import export_xsoar
from exporters.fortisoar_exporter import export_fortisoar
from parsers import fortisoar_parser, xsoar_parser, ai_parser
import importlib.util
import io

app = typer.Typer()
logging.basicConfig(filename="conversion.log", level=logging.INFO)

@app.command()
def convert(
    input_file: str = typer.Option(..., "--input-file", "-f", help="Path to the input playbook file"),
    input_vendor: str = 'xsoar',
    output_vendor: str = 'lambda',
    output_dir: str = None,
    ai_fallback: bool = False,
    sdk_validate: bool = False
):
    """
    Convert between SOAR playbook formats, via Lambda-Actions as an intermediate.
    """
    input_vendor = input_vendor.lower()
    output_vendor = output_vendor.lower()

    playbook_repo_base = "Playbooks_Repo"
    cache_base = "cache"

    if not output_dir:
        output_dir = os.path.join(playbook_repo_base, output_vendor)

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(playbook_repo_base, output_vendor), exist_ok=True)
    os.makedirs(os.path.join(cache_base, input_vendor), exist_ok=True)

    # Choose parser
    try:
        spec = importlib.util.find_spec(f"parsers.{input_vendor}_parser")
        if spec is not None:
            parser_module = importlib.import_module(f"parsers.{input_vendor}_parser")
            parser = parser_module
            typer.echo(f"📦 Using built-in parser: {input_vendor}_parser")
        else:
            typer.echo("🔮 No built-in parser found—using AI to parse into Lambda-Actions schema…")
            parser = ai_parser
    except Exception as e:
        typer.echo(f"❌ Failed to load parser for {input_vendor}: {e}")
        raise typer.Exit(1)

    try:
        if input_vendor == 'xsoar':
            lambda_pb = xsoar_parser.parse_xsoar_yaml(input_file)
        elif input_vendor == 'fortisoar':
            lambda_pb = fortisoar_parser.parse_fortisoar(input_file)
        else:
            lambda_pb = parser.parse_with_ai(input_file)
    except Exception as e:
        logging.error(f"Failed parsing {input_vendor} file: {input_file} – {e}")
        typer.echo(f"❌ Error parsing {input_vendor} input: {e}")
        raise typer.Exit(1)

    out_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(input_file))[0]}")

    if output_vendor == 'xsoar':
        try:
            raw = export_xsoar(lambda_pb)
            vendor_playbook = ai_fallback and cached_transform(raw, output_vendor) or raw
        except Exception as e:
            logging.error(f"XSOAR export failed: {e}")
            typer.echo(f"❌ Error during XSOAR conversion: {e}")
            raise typer.Exit(1)

        try:
            validate_xsoar_playbook(vendor_playbook)
        except Exception as e:
            logging.error(f"XSOAR validation error: {e}")
            typer.echo(f"❌ XSOAR validation error: {e}")
            raise typer.Exit(1)

        out_path += ".yml"
        yaml = ruamel.yaml.YAML()
        yaml.default_flow_style = False

        import io
        stream = io.StringIO()
        yaml.dump(vendor_playbook, stream)
        new_content = stream.getvalue()

        if not os.path.exists(out_path) or open(out_path).read().strip() == new_content.strip():
            with open(out_path, "w") as f:
                f.write(new_content)
            typer.echo(f"✅ XSOAR playbook saved to: {out_path}")
        else:
            typer.echo(f"⚠️ XSOAR file already exists with different content, skipping: {out_path}")

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

    elif output_vendor == 'fortisoar':
        try:
            fs_json = export_fortisoar(lambda_pb)
        except Exception as e:
            logging.error(f"FortiSOAR export failed: {e}")
            typer.echo(f"❌ Error during FortiSOAR conversion: {e}")
            raise typer.Exit(1)

        out_path += ".json"
        new_content = json.dumps(fs_json, indent=2)
        if not os.path.exists(out_path) or open(out_path).read().strip() == new_content.strip():
            with open(out_path, "w") as f:
                f.write(new_content)
            typer.echo(f"✅ FortiSOAR playbook saved to: {out_path}")
        else:
            typer.echo(f"⚠️ File already exists with different content, skipping: {out_path}")

    elif output_vendor == 'lambda':
        vendor_playbook = to_general_lambda(lambda_pb).model_dump()
        out_path += ".yml"
        yaml = ruamel.yaml.YAML()
        yaml.default_flow_style = False
        stream = io.StringIO()
        yaml.dump(vendor_playbook, stream)
        new_content = stream.getvalue()

        if not os.path.exists(out_path) or open(out_path).read().strip() == new_content.strip():
            with open(out_path, "w") as f:
                f.write(new_content)
            typer.echo(f"✅ Lambda-Actions YAML saved to: {out_path}")
        else:
            typer.echo(f"⚠️ File already exists with different content, skipping: {out_path}")
        return

    lambda_dir = os.path.join(playbook_repo_base, "lambda")
    os.makedirs(lambda_dir, exist_ok=True)
    safe = "".join(c for c in lambda_pb.name or "" if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_")
    lambda_out = os.path.join(lambda_dir, f"LA - {safe or 'playbook'}.yml")
    yaml = ruamel.yaml.YAML()
    yaml.default_flow_style = False
    stream = io.StringIO()
    yaml.dump(to_general_lambda(lambda_pb).model_dump(), stream)
    new_content = stream.getvalue()

    if not os.path.exists(lambda_out) or open(lambda_out).read().strip() == new_content.strip():
        with open(lambda_out, "w") as ly:
            ly.write(new_content)
        typer.echo(f"✅ Intermediate Lambda YAML saved to: {lambda_out}")
    else:
        typer.echo(f"⚠️ Intermediate Lambda YAML already exists with different content, skipping: {lambda_out}")

if __name__ == "__main__":
    app()
