#!/usr/bin/env bash
# Writes the Python and TypeScript message types from mimir-server's proto
# files, at the server version go.mod pins, so all three SDKs speak the same
# version. Run it after bumping github.com/gsoultan/mimir-server in go.mod.
#
# Needs Go, uv and npm (run `npm ci` in js/ first).
set -euo pipefail

root=$(cd "$(dirname "$0")/.." && pwd)
cd "$root"

server=github.com/gsoultan/mimir-server
dir=$(go mod download -json "$server" | sed -n 's/^[[:space:]]*"Dir": "\(.*\)",$/\1/p')
version=$(go list -m -f '{{.Version}}' "$server")
proto="$dir/proto"
if [ ! -d "$proto/mimir/v1" ]; then
	echo "no proto files in $proto" >&2
	exit 1
fi
echo "generating from $server $version"

# TypeScript, with protoc-gen-es.
(cd js && npx --no-install buf generate "$proto" --template buf.gen.yaml)

# Python, with protoc from grpcio-tools. The imports are rewritten to live
# under mimirsdk._gen, so they can't clash with another package's protos.
out=python/src/mimirsdk/_gen
rm -rf "$out"
mkdir -p "$out"
uv run --quiet --no-project --with 'grpcio-tools==1.75.0' -- \
	python -m grpc_tools.protoc -I "$proto" --python_out="$out" --pyi_out="$out" "$proto"/mimir/v1/*.proto
find "$out" -name '*.py' -o -name '*.pyi' | while read -r f; do
	sed -i.bak -e 's/^from mimir\.v1 import /from mimirsdk._gen.mimir.v1 import /' "$f"
	rm -f "$f.bak"
done
touch "$out/__init__.py" "$out/mimir/__init__.py" "$out/mimir/v1/__init__.py"
echo "$version" > "$out/SERVER_VERSION"

# mimirsdk.types re-exports every message and enum by name.
uv run --quiet --no-project --with 'protobuf==6.31.1' --with httpx -- python scripts/gen_types.py
