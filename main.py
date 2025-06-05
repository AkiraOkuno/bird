import os
import importlib.util
from telegram_utils import send_telegram_message

MODULES_DIR = "modules"
messages = []
errors = []

for filename in os.listdir(MODULES_DIR):
    #if filename.endswith(".py"):
    if filename in ["random_website.py"]:
        module_name = filename[:-3]
        module_path = os.path.join(MODULES_DIR, filename)

        try:
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)

            if hasattr(mod, "generate"):
                try:
                    result = mod.generate()
                    if result:
                        messages.append(result)
                except Exception as e:
                    error_msg = f"[{module_name}] generate() failed:\n{str(e)}"
                    print(error_msg)
                    errors.append(error_msg)
        except Exception as e:
            error_msg = f"[{module_name}] import failed:\n{str(e)}"
            print(error_msg)
            errors.append(error_msg)

# Send successful messages
for msg in messages:
    send_telegram_message(msg)

# Send error summaries
if errors:
    error_report = "\n\n".join(errors)
    send_telegram_message(f"⚠️ Some modules failed:\n\n{error_report}")
    
