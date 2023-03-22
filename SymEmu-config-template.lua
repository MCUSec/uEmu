--[[
This is a bare minimum S2E config file to demonstrate the use of libs2e with PyKVM.
Please refer to the S2E documentation for more details.
This file was automatically generated at {{ creation_time }}
]]--

s2e = {
    logging = {
        -- Possible values include "all", "debug", "info", "warn" and "none".
        -- See Logging.h in libs2ecore.
        console = "{{ loglevel }}",
        logLevel = "{{ loglevel }}",
    },
    -- All the cl::opt options defined in the engine can be tweaked here.
    -- This can be left empty most of the time.
    -- Most of the options can be found in S2EExecutor.cpp and Executor.cpp.
    kleeArgs = {
		"--verbose-on-symbolic-address={{ klee_info }}",
		"--verbose-state-switching={{ klee_info }}",
		"--verbose-fork-info={{ klee_info }}",
		"--print-mode-switch=false",
		"--fork-on-symbolic-address=false",--no self-modifying code and load libs for IoT firmware
		"--suppress-external-warnings=true"
    },
}

--rom start should be equal to vtor
mem = {
	rom = {
		{% for ro in rom %} {{ '{' }}{{ ro }}{{ '}' }}, {% endfor %}
	},
	ram = {
		{% for ra in ram %} {{ '{' }}{{ ra }}{{ '}' }}, {% endfor %}
	},
}

init = {
   vtor = {{ vtor }},
}

-- Declare empty plugin settings. They will be populated in the rest of
-- the configuration file.
plugins = {}
pluginsConfig = {}

-- Include various convenient functions
dofile('library.lua')


{% if loglevel == "debug" %}
-------------------------------------------------------------------------------
-- This is the main execution tracing plugin.
-- It generates the ExecutionTracer.dat file in the s2e-last folder.
-- That files contains trace information in a binary format. Other plugins can
-- hook into ExecutionTracer in order to insert custom tracing data.
--
-- This is a core plugin, you most likely always want to have it.

add_plugin("ExecutionTracer")

{% endif %}

add_plugin("ARMFunctionMonitor")
pluginsConfig.ARMFunctionMonitor = {
	functionParameterNum = {{ t2_function_parameter_num }},
	callerLevel = {{ t2_caller_level }},
}

add_plugin("SymbolicHardware")
pluginsConfig.SymbolicHardware = {
	CPUArchName = "{{ cpu_arch }}",
}

{% if peripheral_model_name == "uEmu" %}
add_plugin("PeripheralModelLearning")
pluginsConfig.PeripheralModelLearning = {
	useKnowledgeBase = {{ datasymmode }},
	useFuzzer = {{ datasymmode }},
	limitSymNum = {{ t3_max_symbolic_count }},
	maxT2Size = {{ t2_max_context }},
	allowNewPhs = true,
	autoModeSwitch = {{ datasymmode }},
	enableExtendedInterruptMode = "true",
	cacheFileName = "{{ cache_file_name }}",
	firmwareName = "{{ firmware_name }}",
}

add_plugin("InvalidStatesDetection")
pluginsConfig.InvalidStatesDetection = {
	usePeripheralCache = {{ datasymmode }},
	bb_inv1 = {{ bb_inv1 }},
	bb_inv2 = {{ bb_inv2 }},
	bb_terminate = {{ bb_terminate }},
	tbInterval = {{ irq_tb_break }},
	killPoints = {
        {% for k in kill_points %}
        {{ k }},{% endfor %}
	},
	alivePoints = {
        {% for a in alive_points %}
        {{ a }},{% endfor %}
	}
}
add_plugin("uEmuExternalInterrupt")
pluginsConfig.uEmuExternalInterrupt = {
	BBScale = {{ bb_terminate }},
	disableSystickInterrupt = {{ disable_systick }},
	disableIrqs = {
        {% for i in disable_irqs %}
        {{ i }},{% endfor %}
	},
	tbInterval = {{ irq_tb_break }},
	{% if disable_systick == "true" %} systickBeginPoint = {{ systick_begin_point }}, {% endif %}
}
{% endif %}

{% if peripheral_model_name == "SEmu" %}
add_plugin("NLPPeripheralModel")
pluginsConfig.NLPPeripheralModel= {
	NLPfileName = "{{ nlp_file_name }}",
}

add_plugin("ExternalInterrupt")
pluginsConfig.ExternalInterrupt ={
	disableSystickInterrupt = {{ disable_systick }},
	{% if disable_systick == "true" %}systickBeginPoint = {{ systick_begin_point }},{% endif %}
	disableIrqs = {
        {% for i in disable_irqs %}
        {{ i }},{% endfor %}
	},
}
{% endif %}
add_plugin("Pipe")
pluginsConfig.Pipe = {
	modelName = "{{ peripheral_model_name }}",
	{% if enable_tc == "true" %}
	testcaseName = "{{ testcase_name }}",
	{% endif %}
}

