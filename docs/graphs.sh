# sudo apt-get install graphviz
# sudo apt-get update

# All
find . -type f -name "*.py" \
-not -path "./.venv/*" \
-print | xargs uv run code2flow --output docs/call_graph_all.png

# All but test functions
find . -type f -name "*.py" \
-not -path "./.venv/*" \
-not -path "./src/test/*" \
-print | xargs uv run code2flow --output docs/call_graph_all_but_test.png

# Focus main
find . -type f -name "*.py" \
-not -path "./.venv/*" \
-print | xargs uv run code2flow --output docs/call_graph_main.png --target-function main::main --upstream-depth 10 --downstream-depth 10

# Focus clearance
find . -type f -name "*.py" \
-not -path "./.venv/*" \
-print | xargs uv run code2flow --output docs/call_graph_clearance.png --target-function clearance::main --upstream-depth 10 --downstream-depth 10

# Focus clearance
find . -type f -name "*.py" \
-not -path "./.venv/*" \
-print | xargs uv run code2flow --output docs/call_graph_tchap.png --target-function tchap::main --upstream-depth 10 --downstream-depth 10

# Focus clearance
find . -type f -name "*.py" \
-not -path "./.venv/*" \
-print | xargs uv run code2flow --output docs/call_graph_treat_replies.png --target-function treat_replies::main --upstream-depth 10 --downstream-depth 10
