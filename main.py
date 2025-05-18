import os
import importlib.util
from telegram_utils import send_telegram_message

MODULES_DIR = "modules"
messages = []

# Loop through all .py files in /modules
for filename in os.listdir(MODULES_DIR):
    if filename.endswith(".py"):
        module_name = filename[:-3]  # remove ".py"
        module_path = os.path.join(MODULES_DIR, filename)

        # Dynamically load module
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        # Call its generate() method
        if hasattr(mod, "generate"):
            try:
                messages.append(mod.generate())
            except Exception as e:
                print(f"[ERROR] {module_name}.generate() failed: {e}")
        else:
            print(f"[WARN] {module_name} has no generate()")

# Send all generated messages to Telegram
for msg in messages:
    send_telegram_message(msg)
