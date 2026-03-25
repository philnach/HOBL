@echo off

echo Building scenario documentation...
cmd /c ..\..\hobl.cmd -e utilities.open_source.build_scenarios_doc

echo Building tools documentation...
cmd /c ..\..\hobl.cmd -e utilities.open_source.build_tools_doc

echo Building MkDocs site...
..\..\python_embed\Scripts\mkdocs.exe build
