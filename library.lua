--[[
Copyright (c) 2017 Cyberhaven

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
--]]

function table.contains(table, element)
  for _, value in pairs(table) do
    if value == element then
      return true
    end
  end
  return false
end

-- We want to group plugins by feature. Each feature has
-- an associated set of plugins. It may happen that different
-- features require overlapping sets of plugins. It is not
-- possible to have duplicate plugins in the plugins table,
-- so we use this function to add plugins only if needed.
function add_plugin(name)
    if table.contains(plugins, name) then
        return
    end

    table.insert(plugins, name)
end


function file_exists(name)
  local f=io.open(name,"r")
  if f~=nil then io.close(f) return true else return false end
end

function file_lines(name)
  if not file_exists(name) then return 0 end
  local cnt = 0
  for line in io.lines(name) do cnt = cnt + 1 end
  return cnt
end

-- Loads the specified lua file.
-- Files can be missing, malformed, etc. so we need to handle
-- exceptions properly.
function safe_load(name)
  print("lua: attempting to load " .. name)
  local status, err = pcall(dofile, name)
  if status then
    return true
  end

  print(err)
  return false
end

-- Loads the specified file if it is more recent
function safe_load_if_updated(name)
  ret = false
  local f = io.popen("stat -c %Y "..name)
  if f == nil then
     print('io.popen returned nil')
     return ret
  end

  local last_modified_str = f:read()
  if last_modified_str == nil then
     print('stat returned nil')
     return ret
  end

  local last_modified = tonumber(last_modified_str)
  print(name .. " last modified: ".. tostring(last_modified))

  local p = g_loaded_files[name]
  if p == nil or p < last_modified then
    ret = safe_load(name)
    g_loaded_files[name] = last_modified
  else
    print("  no modification detected")
  end

  return ret
end
