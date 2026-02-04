from proccesor_regex import classify_with_regex
from proccesor_bert import classify_with_bert

# Try to import LLM processor, but handle gracefully if it fails
try:
    from proccesor_llm import classify_with_llm

    LLM_AVAILABLE = True
except Exception as e:
    print(f"Warning: LLM processor not available: {e}")
    LLM_AVAILABLE = False

    def classify_with_llm(log_msg):
        return "Unclassified"


def classify(logs):
    labels = []
    for source, log_msg in logs:
        label = classify_log(source, log_msg)
        labels.append(label)
    return labels


def classify_log(source, log_msg):
    if source == "LegacyCRM":
        if LLM_AVAILABLE:
            try:
                label = classify_with_llm(log_msg)
            except Exception as e:
                print(f"LLM classification failed: {e}. Using fallback methods.")
                label = classify_with_regex(log_msg)
                if not label:
                    label = classify_with_bert(log_msg)
        else:
            print("LLM not available, using fallback methods for LegacyCRM logs.")
            label = classify_with_regex(log_msg)
            if not label:
                label = classify_with_bert(log_msg)
    else:
        label = classify_with_regex(log_msg)
        if not label:
            label = classify_with_bert(log_msg)
    return label


def classify_csv(input_file):
    import pandas as pd
    import os

    # Check if input file exists
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file '{input_file}' not found")

    # Ensure output directory exists
    os.makedirs("resources", exist_ok=True)

    df = pd.read_csv(input_file)

    # Validate required columns
    if "source" not in df.columns or "log_message" not in df.columns:
        raise ValueError("Input CSV must contain 'source' and 'log_message' columns")

    # Perform classification
    df["target_label"] = classify(list(zip(df["source"], df["log_message"])))

    # Save the modified file
    output_file = "resources/output.csv"
    df.to_csv(output_file, index=False)

    return output_file


if __name__ == "__main__":
    try:
        output_file = classify_csv("resources/test.csv")
        print(f"Classification completed successfully. Output saved to: {output_file}")
    except Exception as e:
        print(f"Error during classification: {e}")
