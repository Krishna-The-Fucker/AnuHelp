# ============================================================
# 🤖 HANDLERS LOADER (ULTRA PRO MAX - FULL AUTO DYNAMIC)
# ============================================================

import logging
import importlib
import time
import os
import pkgutil


# ============================================================
# 🎨 LOGGING SETUP
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("ULTRA-BOT")


# ============================================================
# 🧠 MAIN LOADER (AUTO-DISCOVER & LOAD)
# ============================================================

def register_all_handlers(app, db, LOG_CHANNEL):

    logger.info(
        "🚀 Booting Ultra Bot System with Auto-Loader..."
    )

    start_time = time.time()
    loaded = 0
    failed = 0

    # 'handlers' package directory ko import aur scan karna
    try:
        import handlers
        package = handlers
    except ImportError as e:
        logger.error(f"❌ Handlers package not found! Error: {e}")
        return

    # Handlers folder ke andar ki saari files ko loop karna
    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        full_module_path = f"handlers.{module_name}"
        
        logger.info(f"🔄 Scanning module → {full_module_path}")

        try:
            mod = importlib.import_module(full_module_path)
            
            # Module ke andar saare attributes check karna ki koi register function hai ya nahi
            registered_any = False
            for attribute_name in dir(mod):
                if attribute_name.startswith("register_") or attribute_name in ["antiraid", "auto_antiraid", "anti_raid_join"]:
                    func = getattr(mod, attribute_name)
                    
                    if callable(func):
                        start = time.time()
                        try:
                            # Arguments ke mutabiq function call karna
                            # Agar function ko db aur LOG_CHANNEL ki zaroorat hai toh wo pass honge, warna sirf app
                            try:
                                func(app, db, LOG_CHANNEL)
                            except TypeError:
                                try:
                                    func(app, db)
                                except TypeError:
                                    func(app)

                            end = time.time()
                            logger.info(f"✅ Loaded → {full_module_path}.{attribute_name} ({round(end-start, 3)}s)")
                            loaded += 1
                            registered_any = True
                        except Exception as e:
                            logger.error(f"❌ Error in {full_module_path}.{attribute_name} → {e}")
                            failed += 1

            if not registered_any:
                # Agar koi register function nahi mila toh shayad wo Pyrogram native Handlers add karne wali file ho
                for attr_name in dir(mod):
                    obj = getattr(mod, attr_name)
                    # Agar Pyrogram Handler object hai toh direct add kar do
                    if hasattr(obj, "callback") or type(obj).__name__ == "Handler":
                        try:
                            app.add_handler(obj)
                            logger.info(f"🔥 Added native handler from → {full_module_path}")
                            loaded += 1
                            registered_any = True
                        except:
                            pass

        except Exception as e:
            logger.error(f"❌ Failed to load module {full_module_path} → {e}")
            failed += 1

    # ========================================================
    # 📊 FINAL REPORT
    # ========================================================

    total_time = round(
        time.time() - start_time,
        2
    )

    logger.info(
        "\n" + "="*50
    )

    logger.info(
        "🚀 BOT AUTO-LOADING COMPLETE"
    )

    logger.info(
        f"✅ Total Handlers Loaded : {loaded}"
    )

    logger.info(
        f"❌ Failed/Skipped : {failed}"
    )

    logger.info(
        f"⏱ Total Time : {total_time}s"
    )

    logger.info(
        "="*50
    )
