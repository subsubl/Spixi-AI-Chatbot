# Pin submodule SHAs

This file records the currently checked-out commit SHAs for the `Ixian-Core` and `QuIXI` submodules as a recommended pin. Use `scripts/update-submodules.ps1` to update or reset to these SHAs.

- `Ixian-Core`: 0d4665b7bacb622579b8480c29cf72267366a943
- `QuIXI`: 02f51dd2b13b28dcdf10319ab92bf3348774df46

If you want to update a submodule to a newer commit:

1. Enter the submodule directory: `cd Ixian-Core`
2. Fetch and checkout the desired commit: `git fetch && git checkout <new-sha>`
3. Return to the superproject and commit the updated gitlink: `git add Ixian-Core && git commit -m "Update Ixian-Core submodule to <new-sha>"`
