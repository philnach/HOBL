import os
import time

import torch
import torch.optim as optim
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter

from tqdm import tqdm
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer

from peft import LoraConfig, TaskType, get_peft_model

class AlpacaData():
    def __init__(self, tokenizer, data_type='train', max_length=512):
        dataset = load_dataset("yahma/alpaca-cleaned", split="train")
        total_samples = len(dataset)
        split_idx = int(0.8 * total_samples)

        if data_type == 'train':
            self.data = dataset.select(range(split_idx))
        else:
            self.data = dataset.select(range(split_idx, total_samples))

        self.tokenizer = tokenizer
        self.max_length = max_length
        print(f"Loaded {len(self.data)} samples for {data_type}")

    def __getitem__(self, idx):
        item = self.data[idx]
        instruction = item["instruction"]
        input_text = item.get("input", "")
        response = item["output"]

        # Format according to Phi-4's chat template - INCLUDING the response for training
        if input_text.strip():
            prompt = f"<|user|>\n{instruction}\n{input_text}\n<|assistant|>\n{response}"
        else:
            prompt = f"<|user|>\n{instruction}\n<|assistant|>\n{response}"

        # Tokenize the prompt
        encodings = self.tokenizer(
            prompt,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )

        input_ids = encodings.input_ids.squeeze()
        attention_mask = encodings.attention_mask.squeeze()
        labels = input_ids.clone()

        # Find the position where assistant begins to respond
        assistant_token_id = self.tokenizer.convert_tokens_to_ids("<|assistant|>")
        assistant_positions = (input_ids == assistant_token_id).nonzero(as_tuple=True)[0]

        if len(assistant_positions) > 0:
            # Get the position after the <|assistant|> token
            assistant_pos = assistant_positions[-1] + 1
            # Set labels for prompt part to -100 (ignored in loss calculation)
            labels[:assistant_pos] = -100

        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels
        }

    def __len__(self):
        return len(self.data)


def main():

    import argparse
    parser = argparse.ArgumentParser(description="Fine-tune a model with LoRA.")
    parser.add_argument('--model', type=str, default='microsoft/Phi-4-mini-instruct', help='HuggingFace model name (default: microsoft/Phi-4-mini-instruct)')
    args, _ = parser.parse_known_args()

    model_name = args.model

    if torch.cuda.is_available():
        device = "cuda"
    elif torch.mps.is_available():
        device = "mps"  # Apple Silicon (M1/M2/M3) GPU
    else:
        device = "cpu"

    print(f"Using device: {device}")
    print(f"Using model: {model_name}")

    batch_size = 8
    grad_steps = 16
    num_epochs = 3
    learning_rate = 5e-5
    max_length = 512

    lora_config = LoraConfig(
        r=8,
        lora_alpha=32,
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj"
        ],
        lora_dropout=0.05,
        bias="none",
        task_type=TaskType.CAUSAL_LM
    )

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer.pad_token = tokenizer.eos_token

    # Add special tokens for chat format
    special_tokens_dict = {"additional_special_tokens": ["<|user|>", "<|assistant|>"]}
    num_added_tokens = tokenizer.add_special_tokens(special_tokens_dict)
    print(f"Added {num_added_tokens} special tokens to tokenizer")

    base_model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto")

    # Resize the embeddings if new tokens are added
    if num_added_tokens > 0:
        base_model.resize_token_embeddings(len(tokenizer))

    model = get_peft_model(base_model, lora_config)

    # Freeze all non-LoRA parameters.
    model.requires_grad_(False)
    for name, param in base_model.named_parameters():
        if "lora_" in name:
            param.requires_grad = True

    optimizer = optim.AdamW(model.parameters(), lr=learning_rate, fused=True)
    train_dataset = AlpacaData(tokenizer, data_type='train', max_length=max_length)
    val_dataset = AlpacaData(tokenizer, data_type='validation', max_length=max_length)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, drop_last=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, drop_last=False)

    loss_idx = 0
    accumulated_loss = 0.0
    accumulation_counter = 0
    writer = SummaryWriter(log_dir="logs")
    os.makedirs("checkpoint", exist_ok=True)

    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0
        optimizer.zero_grad()
        print(f"\nEpoch {epoch + 1}/{num_epochs}")

        # === Training loop ===
        step_start_time = time.time()
        for idx, batch in enumerate(tqdm(train_loader, desc="Training")):
            batch = {k: v.to(device) for k, v in batch.items()}

            with torch.amp.autocast(device_type=device, dtype=torch.bfloat16):
                outputs = model(**batch)
                unscaled_loss = outputs.loss

            loss = unscaled_loss / grad_steps
            loss.backward()

            accumulated_loss += unscaled_loss.item()
            accumulation_counter += 1

            if (idx + 1) % grad_steps == 0:
                optimizer.step()
                optimizer.zero_grad()

                avg_loss = accumulated_loss / grad_steps
                running_loss += accumulated_loss
                writer.add_scalar("perf/train", avg_loss, loss_idx)
                loss_idx += 1

                # Log the time taken for the step
                step_end_time = time.time()
                step_duration = step_end_time - step_start_time
                samples_per_sec = grad_steps * batch_size / step_duration if step_duration > 0 else 0
                writer.add_scalar("perf/samples_per_sec", samples_per_sec, loss_idx)

                # Reset the accumulation
                accumulated_loss = 0.0
                accumulation_counter = 0
                step_start_time = time.time()

        avg_train_loss = running_loss / len(train_loader)
        print(f"Average Training Loss: {avg_train_loss:.4f}")
        model.eval()
        val_running_loss = 0.0

        # === Validation loop ===
        with torch.no_grad():
            for batch in tqdm(val_loader, desc="Validation"):
                batch = {k: v.to(device) for k, v in batch.items()}

                with torch.amp.autocast(device_type=device, dtype=torch.bfloat16):
                    outputs = model(**batch)
                    loss = outputs.loss

                val_running_loss += loss.item()

        avg_val_loss = val_running_loss / len(val_loader)
        print(f"Average Validation Loss: {avg_val_loss:.4f}")
        writer.add_scalar("loss/val", avg_val_loss, epoch)

        # === Save checkpoint ===
        ckpt_path = f"checkpoint/epoch_{epoch}.pth"
        torch.save({'model_state_dict': model.state_dict()}, ckpt_path)

        print(f"Checkpoint saved: checkpoint/epoch_{epoch}.pth")

        # === TensorBoard: log parameter histograms ===
        for name, param in model.named_parameters():
            if param.requires_grad and param.data is not None:
                writer.add_histogram(f"params/{name}", param.data.cpu().float(), epoch)
            if param.grad is not None:
                writer.add_histogram(f"grads/{name}", param.grad.cpu().float(), epoch)

        # === TensorBoard: log sample text generation ===
        model.eval()
        sample_prompt = "Write a short story about a robot learning to love."
        tokenized_input = tokenizer(
            f"<|user|>\n{sample_prompt}\n<|assistant|>",
            return_tensors="pt",
            truncation=True,
            max_length=128
        )
        input_ids = tokenized_input.input_ids.to(device)
        attention_mask = tokenized_input.attention_mask.to(device)
        with torch.no_grad():
            gen_ids = model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                max_length=256,
                do_sample=True,
                top_p=0.95,
                temperature=0.8,
                pad_token_id=tokenizer.eos_token_id
            )
        generated_text = tokenizer.decode(gen_ids[0], skip_special_tokens=False)
        writer.add_text("sample_generation", generated_text, epoch)

    writer.close()


if __name__ == "__main__":
    main()
