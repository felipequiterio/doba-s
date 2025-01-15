import os
import time
import asyncio
import ollama
import logging
import subprocess
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()
MODEL = os.getenv("OLLAMA_MODEL")


# Function to get GPU stats using nvidia-smi
def get_gpu_stats():
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=memory.used,memory.total,utilization.gpu",
                "--format=csv,noheader,nounits",
            ],
            stdout=subprocess.PIPE,
            text=True,
        )
        memory_used, memory_total, gpu_utilization = result.stdout.strip().split(", ")
        return int(memory_used), int(memory_total), int(gpu_utilization)
    except Exception as e:
        logging.error(f"Error retrieving GPU stats: {e}")
        return None, None, None


async def async_inference(message):
    logging.info(f"Starting async inference: {message}")

    start_time = time.time()
    memory_used_before, memory_total, gpu_util_before = get_gpu_stats()

    if memory_used_before is not None:
        logging.info(
            f"Before inference - VRAM Used: {memory_used_before}MB / {memory_total}MB, GPU Utilization: {gpu_util_before}%"
        )

    stream = ollama.chat(
        model=MODEL, messages=[{"role": "user", "content": message}], stream=True
    )
    for chunk in stream:
        logging.info(f"Chunk: {chunk['message']['content']}")

    memory_used_after, _, gpu_util_after = get_gpu_stats()
    if memory_used_after is not None:
        logging.info(
            f"After inference - VRAM Used: {memory_used_after}MB / {memory_total}MB, GPU Utilization: {gpu_util_after}%"
        )

    end_time = time.time()
    logging.info(
        f"Inference completed for message: {message}. Duration: {end_time - start_time:.2f} seconds"
    )


async def main():
    # Run two inferences asynchronously
    await asyncio.gather(
        async_inference("What is the capital of France?"),
        async_inference(
            "How to measure the distance from Earth to the Moon? Explain in detail"
        ),
    )


if __name__ == "__main__":
    asyncio.run(main())
