import argparse
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, TaskType, get_peft_model
import os

def main():
    parser = argparse.ArgumentParser(description="Test inference with fine-tuned model.")
    parser.add_argument('--gpu', action=argparse.BooleanOptionalAction, default=True, help='Use GPU for inference (default: True)')
    parser.add_argument('--prompt', type=str, required=True, help='Prompt for inference (in quotes)')
    args = parser.parse_args()

    # args.gpu is True if --gpu is passed or default, False if --no-gpu is passed
    device = 'cuda' if args.gpu and torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")

    model_name = "microsoft/Phi-4-mini-instruct"
    checkpoint_path = os.path.join("checkpoint", "epoch_0.pth")
    #checkpoint_path = os.path.join("model", "fine_tuned_model.pth")

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token
    special_tokens_dict = {"additional_special_tokens": ["<|user|>", "<|assistant|>"]}
    tokenizer.add_special_tokens(special_tokens_dict)

    # Load base model
    base_model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16 if device == 'cuda' else torch.float32,
        device_map="auto" if device == 'cuda' else None
    )
    base_model.resize_token_embeddings(len(tokenizer))

    # LoRA config (must match training)
    lora_config = LoraConfig(
        r=8,
        lora_alpha=32,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"
        ],
        lora_dropout=0.05,
        bias="none",
        task_type=TaskType.CAUSAL_LM
    )
    model = get_peft_model(base_model, lora_config)

    # Load checkpoint
    ckpt = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(ckpt['model_state_dict'], strict=False)
    model = model.to(device)
    model.eval()

    # Prepare prompt
    prompt = args.prompt
    formatted_prompt = f"<|user|>\n{prompt}\n<|assistant|>"
    tokenized = tokenizer(
        formatted_prompt,
        return_tensors="pt",
        truncation=True,
        max_length=128
    )
    input_ids = tokenized.input_ids.to(device)
    attention_mask = tokenized.attention_mask.to(device)

    # Use text streamer for real-time output and measure performance
    import time
    from transformers.generation.streamers import TextStreamer

    class StatsStreamer(TextStreamer):
        def __init__(self, tokenizer, **kwargs):
            super().__init__(tokenizer, **kwargs)
            self.token_count = 0
            self.start_time = None
            self.end_time = None
        def put(self, value):
            if self.start_time is None:
                self.start_time = time.time()
            self.token_count += 1
            super().put(value)
        def end(self):
            self.end_time = time.time()
            super().end()

    streamer = StatsStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
    with torch.no_grad():
        model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_length=256,
            do_sample=True,
            top_p=0.95,
            temperature=0.8,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
            use_cache=True,
            streamer=streamer
        )
    print()  # Newline after streaming

    # Output performance statistics
    if streamer.start_time is not None and streamer.end_time is not None:
        elapsed = streamer.end_time - streamer.start_time
        tokens = streamer.token_count
        tps = tokens / elapsed if elapsed > 0 else float('inf')
        print(f"\n--- Performance Statistics ---")
        print(f"Generated tokens: {tokens}")
        print(f"Elapsed time: {elapsed:.2f} seconds")
        print(f"Tokens per second: {tps:.2f}")

if __name__ == "__main__":
    main()
