import json, sys
d = json.load(open(sys.argv[1]))
print("php:", d["require"]["php"], "| framework:", d["require"]["laravel/framework"], "| sail:", d.get("require-dev", {}).get("laravel/sail"))
