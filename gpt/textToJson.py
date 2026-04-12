import json

input_path = "dataset.txt"
output_path = "autism_slm_dataset.jsonl"

with open(input_path, "r", encoding="utf-8") as infile, open(output_path, "w", encoding="utf-8") as outfile:
    for line in infile:
        line = line.strip()
        if not line:
            continue
        # Remove quotes and split on the first comma between question/answer
        if line.startswith('"') and line.endswith('"'):
            line = line[1:-1]
        parts = line.split('","')
        if len(parts) != 2:
            continue
        instruction, response = parts
        data = {
            "instruction": instruction.strip(),
            "response": response.strip()
        }
        json.dump(data, outfile, ensure_ascii=False)
        outfile.write("\n")

print(f"[✅] Saved dataset to {output_path}")

