local fs = class:getAPI("filesystem", 1)
local json = class:getAPI("json", 0)
local cfg = json.decode(fs.readAll("out/flcfg.json"))
for name, v in pairs(cfg.filesystems) do
    print("creating dir for " .. name .. 'at: ' .. v.mnt)
    fs.create("out" .. v.mnt)
end