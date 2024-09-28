from playwright._impl._driver import (
    compute_driver_executable,  # type: ignore
    get_driver_env,
)

env = get_driver_env()
for key, vel in env.items():
    if 'playwright' in key.lower():
        print(key, val)
