import asyncio
import json
import sys
import os
import traceback
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))


async def execute_notebook_file():
    root_dir = Path(__file__).resolve().parent.parent
    nb_path = root_dir / "notebooks" / "Document_Intelligence_Demo.ipynb"
    if not nb_path.exists():
        print(f"Error: {nb_path} does not exist.")
        return

    nb_data = json.loads(nb_path.read_text(encoding="utf-8"))
    
    exec_globals = {
        "__name__": "__main__",
        "__file__": str(nb_path),
    }

    os.chdir(str(nb_path.parent))

    exec_count = 0
    print("Executing notebook cells...\n")

    for cell in nb_data["cells"]:
        if cell["cell_type"] == "code":
            exec_count += 1
            cell["execution_count"] = exec_count
            code = "".join(cell["source"])
            
            print(f"--- Executing Code Cell {exec_count} ---")
            
            from io import StringIO
            stdout_buf = StringIO()
            orig_stdout = sys.stdout
            sys.stdout = stdout_buf

            cell_outputs = []

            try:
                if "await " in code:
                    wrapped_code = "async def __cell_coro():\n" + "\n".join("    " + line for line in code.splitlines()) + "\n"
                    exec(wrapped_code, exec_globals)
                    coro = exec_globals["__cell_coro"]()
                    await coro
                else:
                    exec(code, exec_globals)
                
                output_str = stdout_buf.getvalue()
                if output_str:
                    cell_outputs.append({
                        "name": "stdout",
                        "output_type": "stream",
                        "text": output_str.splitlines(keepends=True),
                    })
                print(f"[OK] Cell {exec_count} executed successfully.")
            except Exception as e:
                output_str = stdout_buf.getvalue()
                err_msg = f"{output_str}\nError executing cell {exec_count}: {e}\n{traceback.format_exc()}"
                print(f"[FAIL] Cell {exec_count} failed: {e}")
                cell_outputs.append({
                    "name": "stderr",
                    "output_type": "stream",
                    "text": err_msg.splitlines(keepends=True),
                })
            finally:
                sys.stdout = orig_stdout

            cell["outputs"] = cell_outputs

    os.chdir(str(root_dir))
    
    # Save executed notebook
    nb_path.write_text(json.dumps(nb_data, indent=2), encoding="utf-8")
    print(f"\nSuccessfully executed all {exec_count} cells and saved outputs to {nb_path}!")


if __name__ == "__main__":
    asyncio.run(execute_notebook_file())
