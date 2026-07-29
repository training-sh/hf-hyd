import papermill as pm

# pip install papermill

# we have cli as well, discuss later

# python pipeline.py

notebooks = [
    "step_1_add.ipynb",
    "step_2_mul.ipynb",
    "step_3_sub.ipynb"
]

for nb in notebooks:
    print(f"Running {nb}...")
    pm.execute_notebook(
        input_path=nb,
        output_path=f"output/{nb}",
        parameters={ }
    )

print("Pipeline completed.")