--[[
This is a bare minimum S2E config file to demonstrate the use of libs2e with PyKVM.
Please refer to the S2E documentation for more details.
This file was automatically generated at 2021-04-22 11:19:01.032559
]]--

s2e = {
    logging = {
        -- Possible values include "all", "debug", "info", "warn" and "none".
        -- See Logging.h in libs2ecore.
        console = "debug",
        logLevel = "debug",
    },
    -- All the cl::opt options defined in the engine can be tweaked here.
    -- This can be left empty most of the time.
    -- Most of the options can be found in S2EExecutor.cpp and Executor.cpp.
    kleeArgs = {
		"--verbose-on-symbolic-address=true",
		"--verbose-state-switching=true",
		"--verbose-fork-info=true",
		"--print-mode-switch=false",
		"--fork-on-symbolic-address=false",--no self-modifying code and load libs for IoT firmware
		"--suppress-external-warnings=true"
    },
}

--rom start should be equal to vtor
mem = {
	rom = {
		 {0x08000000,0x40000},
	},
	ram = {
		 {0x20000000,0x40000},
	},
}

init = {
   vtor = 134217728,
}

-- Declare empty plugin settings. They will be populated in the rest of
-- the configuration file.
plugins = {}
pluginsConfig = {}

-- Include various convenient functions
dofile('library.lua')

-------------------------------------------------------------------------------
-- This plugin contains the core custom instructions.
-- Some of these include s2e_make_symbolic, s2e_kill_state, etc.
-- You always want to have this plugin included.

add_plugin("BaseInstructions")

add_plugin("Vmi")
pluginsConfig.Vmi = {
    baseDirs = {
        "/root/uEmu-real_firmware/fuzzingtest"
    }
}

add_plugin("RawMonitor")
-- The custom instruction will notify RawMonitor of all newly loaded modules
pluginsConfig.RawMonitor = {

    kernelStart = 0x00000000,
}

-------------------------------------------------------------------------------
-- Keeps for each state/process an updated map of all the loaded modules.
add_plugin("ModuleMap")
pluginsConfig.ModuleMap = {

    logLevel="debug"
}
-------------------------------------------------------------------------------
-- Tracks execution of specific modules.
-- Analysis plugins are often interested only in small portions of the system,
-- typically the modules under analysis. This plugin filters out all core
-- events that do not concern the modules under analysis. This simplifies
-- code instrumentation.
-- Instead of listing individual modules, you can also track all modules by
-- setting configureAllModules = true

add_plugin("ModuleExecutionDetector")
pluginsConfig.ModuleExecutionDetector = {

    trackExecution=true,
    logLevel="debug"
}


-------------------------------------------------------------------------------
-- This is the main execution tracing plugin.
-- It generates the ExecutionTracer.dat file in the s2e-last folder.
-- That files contains trace information in a binary format. Other plugins can
-- hook into ExecutionTracer in order to insert custom tracing data.
--
-- This is a core plugin, you most likely always want to have it.

add_plugin("ExecutionTracer")

-------------------------------------------------------------------------------
-- This plugin records events about module loads/unloads and stores them
-- in ExecutionTracer.dat.
-- This is useful in order to map raw program counters and pids to actual
-- module names.

add_plugin("ModuleTracer")

add_plugin("StateSwitchTracer")

